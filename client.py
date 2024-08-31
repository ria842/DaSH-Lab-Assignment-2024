
import socket
import threading
import sys
import json
import time

if len(sys.argv) != 2:
    print("Missing argument")
    sys.exit(1)

client_id = int(sys.argv[1])

with open('input.txt', 'r') as file:
    lines = file.readlines()

# Initialize Listening flag as a threading Event for thread-safe signaling
Listening = threading.Event()
Listening.set()
responses = []

def listen_for_server_messages(client_socket):
    while Listening.is_set():
        try:
            # Receive the length of the incoming message
            raw_msglen = recvall(client_socket, 4)
            if not raw_msglen:
                print("Server closed the connection.")
                break
            msglen = int.from_bytes(raw_msglen, byteorder='big')

            # Now, receive the entire message based on its length
            data = recvall(client_socket, msglen)
            data_json=json.loads(data.decode("utf-8"))
            data_json["Time_rec"]=time.time()
            responses.append(data_json)
            print(responses)
            #print(f"Received from server: {data.decode()}")
            with open(f"output_{client_id}.json", "w") as json_file:
                json.dump(responses, json_file, indent=4)
        except ConnectionResetError:
            print("Connection was closed by the server.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    client_socket.close()

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

# Create a socket connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12346))

# Start the listening thread
listen_thread = threading.Thread(target=listen_for_server_messages, args=(client_socket,))
listen_thread.start()


def send_rec_prompt(text):
    text_obj = {
        "client_id": client_id,
        "text": text,
        "time_sent": time.time()
    }
    message = json.dumps(text_obj).encode("utf-8")
    # Send the length of the message first
    client_socket.sendall(len(message).to_bytes(4, byteorder='big'))
    # Then send the actual message
    client_socket.sendall(message)

# Send all lines from the input file to the server
# for line in lines:
#     send_rec_prompt(line.strip())
time.sleep(5)
line = lines[client_id]
send_rec_prompt(line)

listen_thread.join()  # Wait for the listening thread to terminate

# Close the socket once the thread has safely stopped
client_socket.close()
print(responses)

