"""Dummy file sending chat request to the backend"""

import requests

def test_message(prompt: str):
    response = requests.post('http://localhost:5000/v1/chat', json={'message': prompt}).json()

    if response['status'] == 200:
        print(response['response'])
    else:
        raise Exception(response['response'])

if __name__ == '__main__':
    prompts = [
        "Hey, what's your name?",
    ]

    for prompt in prompts:
        try:
            test_message(prompt)
        except Exception as e:
            print(e)
        print()