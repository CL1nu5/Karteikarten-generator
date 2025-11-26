from ollama import Client
from util.config_reader import ConfigLoader

config = ConfigLoader().to_dict()


client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + config['OLLAMA_API_KEY']}
)

messages = [
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
]

for part in client.chat('kimi-k2-thinking', messages=messages, stream=True):
  print(part['message']['content'], end='', flush=True)