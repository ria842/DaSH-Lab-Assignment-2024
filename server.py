import socket
import threading
from groq import Groq
import json

groq_api_key = "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"

clients = []  # List to keep track of all connected clients


def get_llm_response(text):
    client = Groq(api_key=groq_api_key)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": text,
            }
        ],
        model="llama3-8b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    return chat_completion.choices[0].message.content


def send_message(socket, message):
    try:
        message = json.dumps(message).encode("utf-8")
        message_length = len(message)
        socket.sendall(message_length.to_bytes(4, byteorder="big"))
        socket.sendall(message)
    except BrokenPipeError:
        # Handle the case where the client has disconnected
        clients.remove(socket)


def receive_message(socket):
    raw_msglen = recvall(socket, 4)
    if not raw_msglen:
        return None
    msglen = int.from_bytes(raw_msglen, byteorder="big")
    return recvall(socket, msglen)


def recvall(socket, n):
    data = bytearray()
    while len(data) < n:
        packet = socket.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def broadcast_message(message, exclude_socket=None):
    """Broadcast a message to all connected clients except the sender."""
    for client_socket in clients:
        if client_socket != exclude_socket:
            send_message(client_socket, message)


def handle_client(client_socket, addr):
    print(f"Connection from {addr} has been established!")
    clients.append(client_socket)
    try:
        while True:
            data = receive_message(client_socket)
            if not data:
                break
            print(f"Received {data.decode()} from the client")
            data = json.loads(data.decode("utf-8"))
            response = get_llm_response(data["text"])
            response_obj = {
                "client_id": data["client_id"],
                "text": data["text"],
                "time_sent": data["time_sent"],
                "response": response,
            }
            # Broadcast the response to all clients except the sender
            broadcast_message(response_obj)
    finally:
        # Remove client from the list when they disconnect
        # clients.remove(client_socket)
        client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 12346))
    server_socket.listen(5)

    print("Server is listening on port 12346...")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, addr)
        )
        client_thread.start()


if __name__ == "__main__":
    main()
