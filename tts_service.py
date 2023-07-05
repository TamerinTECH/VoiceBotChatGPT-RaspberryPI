import json
import struct
import os
import time
import boto3
import pygame
import requests
import json
import sseclient


class TextToSpeechService:
    def __init__(self, mode="voice-clone"):
        #load AWS credentials from config file
        config = json.load(open("config.json"))
        self.mode = mode

        if mode == "voice-clone":
            self.playht_header = {
                'Authorization': "Bearer " + config["playht_token"],
                'X-User-ID': config["playht_user_id"],
                'Content-Type': 'application/json'
                }
            
            print("Getting voice id from play.ht...")
            #list cloned voices
            response = requests.request("GET", "https://play.ht/api/v2/cloned-voices", headers=self.playht_header)
            print(response.text)
            #get the first voice id (or later - add a check for the voice name ["name"])
            self.playht_voice_id = json.loads(response.text)[0]["id"]
        else:
            #use polly boto3 client with the crednetials
            self.polly = boto3.client('polly',
                                        aws_access_key_id=config["aws_access_key_id"],
                                        aws_secret_access_key=config["aws_secret_access_key"],
                                        region_name=config["aws_region"])



    def speak(self, text):

        if self.mode == "voice-clone":
            payload = json.dumps({
                "voice": self.playht_voice_id,
                "text": text,   
                })
            #copy playht_header to the request
            headers = self.playht_header
            headers['Accept']= 'text/event-stream'

            print("Sending request to play.ht...")
            response = requests.request("POST", "https://play.ht/api/v2/tts", headers=headers, data=payload)

            client = sseclient.SSEClient(response)

            output_url = None
            for event in client.events():
                print(event.data)
                try:
                    data_json = json.loads(event.data)
                    if event.data == '[DONE]' or 'url' in data_json:
                        output_url = data_json['url']
                        print("Found output url: " + output_url)
                        break
                except:
                    pass

            #download the file
            print("Downloading file from: " + output_url)
            response = requests.request("GET", output_url)
            with open('output.mp3', 'wb') as f:
                f.write(response.content)

        else:
            response = self.polly.synthesize_speech(VoiceId='Matthew',
                                                    OutputFormat='mp3',
                                                    Text=text)
            with open('output.mp3', 'wb') as f:
                f.write(response['AudioStream'].read())
        
        #play using pygame
        pygame.mixer.init()     
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass

        os.remove("output.mp3")

