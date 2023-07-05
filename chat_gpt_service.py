import json
from input_listener import InputListener
import struct
import os
import openai
import time


config = json.load(open("config.json"))
openai.api_key = config["openai_key"]
if "openai_org" in config:
    openai.organization = config["openai_org"]


class ChatGPTService:
    def __init__(self, prompt="You are a helpful assistant."):
        self.history = [{"role": "system", "content": prompt}]

    def _get_history_token_size(self):
        tokens = 0
        for x in self.history:
            tokens += len(x["content"].split(" "))
        return tokens

    def send_to_chat_gpt(self, message):
        self.history.append({"role": "user", "content": message})

        #check if the total tokens length exceed the total of 16k tokens
        while self._get_history_token_size() > 16000:
            print("ChatGPT History too long, removing oldest message")
            #remove the oldest message - except the first one (system role)
            if len(self.history) > 2:
                self.history.pop(1)
            else:
                break

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k", messages=self.history
        )
        self.history.append({"role": "assistant", "content": response["choices"][0]["message"]["content"]})
        return str.strip(response["choices"][0]["message"]["content"])
