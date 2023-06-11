import json
from chat_gpt_service import ChatGPTService
from input_listener import InputListener
import pvporcupine
import struct
import os
import pyaudio
import openai
import time

config = json.load(open("config.json"))
openai.api_key = config["openai_key"]
if "openai_org" in config:
    openai.organization = config["openai_org"]

class WakeWordDetector:
    def __init__(self, library_path, model_path, keyword_paths):
        self.chat_gpt_service = ChatGPTService()
        #load access key from config
        pv_access_key= config["pv_access_key"]

        self.handle = pvporcupine.create(
                                         keywords=["picovoice"],
                                         access_key=pv_access_key,
                                         #library_path=library_path,
                                         #model_path=model_path,
                                         #keyword_paths=keyword_paths,
                                         sensitivities=[0.5])

        self.pa = pyaudio.PyAudio()
        self.listener = InputListener()
        self._init_audio_stream()
        


    def _init_audio_stream(self):
        self.audio_stream = self.pa.open(rate=self.handle.sample_rate,
                                         channels=1,
                                         format=pyaudio.paInt16,
                                         input=True,
                                         frames_per_buffer=self.handle.frame_length)

    def run(self):
        try:
            while True:
                pcm = self.audio_stream.read(self.handle.frame_length)
                pcm = struct.unpack_from("h" * self.handle.frame_length, pcm)
                porcupine_keyword_index = self.handle.process(pcm)
                if porcupine_keyword_index >= 0:
                    print("Wake word detected!")
                    self.audio_stream.close()
                    self.audio_stream = None

                    audio_path = self.listener.listen()
                    print("Transcribing...")

                    audio_file = open(audio_path, "rb")

                    transcript = openai.Audio.translate("whisper-1", audio_file)
                    print(transcript)
                    
                    response = self.chat_gpt_service.send_to_chat_gpt(transcript["text"])
                    print(response)

                    #delete file
                    os.remove(audio_path)
                    self._init_audio_stream()

        except KeyboardInterrupt:
            pass
        finally:
            if self.audio_stream is not None:
                self.audio_stream.close()
            if self.pa is not None:
                self.pa.terminate()
            self.handle.delete()

if __name__ == '__main__':
    library_path = '/path/to/porcupine/library'
    model_path = '/path/to/porcupine/model'
    keyword_paths = ['/path/to/porcupine/keyword']

    detector = WakeWordDetector(library_path, model_path, keyword_paths)
    detector.run()
