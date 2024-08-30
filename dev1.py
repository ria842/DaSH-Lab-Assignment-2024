import os
import requests
import json
import time
from groq import Groq

def read_input_file(file_path):
    with open(file_path, 'r') as file:
        prompts = file.readlines()
    return [prompt.strip() for prompt in prompts]

def save_responses_to_json(responses, output_file):
    with open(output_file, 'w') as file:
        json.dump(responses, file, indent=4)

def llm_call(query):
    time_sent = int(time.time())

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{query}",
            }
        ],
        model="llama3-8b-8192",
    )

    response = chat_completion.choices[0].message.content

    time_recvd = int(time.time())
    return {
        "Prompt": query,
        "Message": response,
        "TimeSent": time_sent,
        "TimeRecvd": time_recvd,
        "Source": "Groq"  
    }

queries = read_input_file("input.txt")
responses = []

for query in queries:
    data = llm_call(query)
    responses.append(data)

file = open("output.json", 'w')
json.dump(responses, file, indent=2)