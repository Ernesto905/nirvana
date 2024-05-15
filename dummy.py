"""Dummy file sending get-actions request to the backend"""

import requests

email = """
Hi team,

I'm having trouble with the latest build. It seems to be failing on the integration tests. Can someone take a look?

Thanks,

John
"""

user_id = 123

prompt = "Hey! What's your name?"

response = requests.post('http://localhost:5000/v1/chat', json={'message': prompt})

print(response.json())