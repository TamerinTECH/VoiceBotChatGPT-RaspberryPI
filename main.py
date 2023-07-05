import json
from chat_gpt_service import ChatGPTService
from input_listener import InputListener
import pvporcupine
import struct
import os
import pyaudio
import openai
from silence_detector import ThresholdDetector
from gpiozero import LED
import pygame
from kitt_prompt import prompt_template
import time
from tts_service import TextToSpeechService

import logging
from systemd import journal

log = logging.getLogger('GPTVoiceAssistant')
log.addHandler(journal.JournaldLogHandler())
log.setLevel(logging.DEBUG)


wakeup_keyword = "Hello KITT"

config = json.load(open("config.json"))
openai.api_key = config["openai_key"]
if "openai_org" in config:
    openai.organization = config["openai_org"]


class WakeWordDetector:
    def __init__(self, silence_threshold=100):
        try:
            self.led = LED(config["led_pin"])
            self.led.off()
        except:
            log.error("Could not initialize LED")
            self.led = None

        self.chat_gpt_service = ChatGPTService(prompt=prompt_template)
        # load access key from config
        pv_access_key = config["pv_access_key"]

        self.silence_threshold = silence_threshold
        self.handle = pvporcupine.create(
            keywords=[wakeup_keyword],
            access_key=pv_access_key,
            sensitivities=[1],
        )

        self.pa = pyaudio.PyAudio()
        # init listener, use values from config or default
        self.listener = InputListener(
            silence_threshold,  # config["silence_threshold"] if "silence_threshold" in config else 75,
            config["silence_duration"] if "silence_duration" in config else 1.5,
        )

        # get from config, or default
        sound_card_name = (
            config["sound_card_name"]
            if "sound_card_name" in config
            else "seeed-2mic-voicecard"
        )

        log.info("Looking for sound card...")
        # Find the device index of the sound card, if cannot find, wait 3 seconds and try again, for maximum of 10 times
        attempts = 0
        self.input_device_index = None
        while True and attempts < 10 and self.input_device_index is None:
            for i in range(self.pa.get_device_count()):
                device_info = self.pa.get_device_info_by_index(i)
                log.debug(device_info["name"])
                if sound_card_name in device_info["name"]:
                    log.info("Found sound card! Using device index: %d" % i)
                    self.input_device_index = i
                    break
            if self.input_device_index is None:
                attempts += 1
                if attempts > 10:
                    raise Exception("Could not find sound device")
                else:
                    log.warning("Sound card not found, waiting 5 seconds...")
                    time.sleep(5)

        self.speech = TextToSpeechService(mode="aws")  # self.input_device_index)

        self._init_audio_stream()

    def set_silence_threshold(self, silence_threshold):
        self.silence_threshold = silence_threshold

    def _toggle_led_power(self, state):
        if self.led is not None:
            self.led.on() if state else self.led.off()

    def set_led_blinking(self, on_time=0.5, off_time=0.5):
        if self.led is not None:
            self.led.on()
            self.led.blink(on_time, off_time)

    def _init_audio_stream(self):
        self.audio_stream = self.pa.open(
            rate=self.handle.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.handle.frame_length,
        )
        # input_device_index=self.input_device_index)

    def run(self):
        try:
            self._toggle_led_power(True) 
            log.info("Listening for wake word '%s' with silence threshold %d..." % (wakeup_keyword, self.silence_threshold))


            while True:
                pcm = self.audio_stream.read(self.handle.frame_length)
                pcm = struct.unpack_from("h" * self.handle.frame_length, pcm)
                porcupine_keyword_index = self.handle.process(pcm)
                if porcupine_keyword_index >= 0:
                    log.info("Wake word detected!")
                    self.set_led_blinking()
                    self.audio_stream.close()
                    self.audio_stream = None

                    audio_path = self.listener.listen()

                    self.set_led_blinking(0.3, 0.3)
                    log.info("Transcribing...")

                    audio_file = open(audio_path, "rb")

                    transcript = openai.Audio.translate("whisper-1", audio_file)
                    log.debug(transcript)

                    self.set_led_blinking(0.2, 0.2)
                    log.info("Sending to chat GPT...")
                    response = self.chat_gpt_service.send_to_chat_gpt(
                        transcript["text"]
                    )
                    log.debug(response)

                    log.info("Playing response...")
                    # play response
                    self.speech.speak(response)

                    # delete file
                    os.remove(audio_path)
                    self._init_audio_stream()

                    self._toggle_led_power(False)
                    self._toggle_led_power(True)
                    log.info("Listening for wake word...")

        except KeyboardInterrupt:
            pass
        finally:
            if self.audio_stream is not None:
                self.audio_stream.close()
            if self.pa is not None:
                self.pa.terminate()
            self.handle.delete()


if __name__ == "__main__":

    wake_word_detector = WakeWordDetector()

    # play startup music if configured in config
    if "startup_music" in config:
        log.info("Playing startup music...")
        pygame.mixer.init()
        pygame.mixer.music.load(config["startup_music"])
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass

    # start with playing sound, then detect silence for 5 seconds

    log.info("Detecting silence...")
    wake_word_detector.set_led_blinking(0.2, 0.2)
    threshold_detector = ThresholdDetector(5)
    silence_threshold = threshold_detector.detect_threshold()

    wake_word_detector.set_silence_threshold(silence_threshold)

    wake_word_detector.run()
