import time
import audioop
import pyaudio
import boto3
import wave
import uuid
import os

import logging
from systemd import journal

log = logging.getLogger('GPTVoiceAssistant')
log.addHandler(journal.JournaldLogHandler())
log.setLevel(logging.DEBUG)


class InputListener:
    def __init__(self, silence_threshold=75, silence_duration=1.5):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.audio = pyaudio.PyAudio()
        self.frames = []

    def start(self):
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def save_audio_to_file(self, audio_data):
        # Generate a random file name
        file_name = str(uuid.uuid4()) + ".wav"
        file_path = os.path.join("", file_name)  # /path/to/save/directory', file_name)

        # if the file already exists, delete it
        if os.path.exists(file_path):
            os.remove(file_path)

        # Save the audio data to the file
        wf = wave.open(file_path, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(audio_data)
        wf.close()

        return file_path

    def listen(self):
        self.start()
        silence_start_time = None
        log.info("Start recording...")
        while True:
            data = self.stream.read(self.chunk)
            self.frames.append(data)
            rms = audioop.rms(data, 2)
            log.debug(f"RMS: {rms}")  # Debugging print
            if rms < self.silence_threshold:
                if silence_start_time is None:
                    silence_start_time = time.time()
                elif time.time() - silence_start_time > self.silence_duration:
                    log.info("Silence detected, stop recording")
                    break
            else:
                silence_start_time = None
        self.stop()

        # Save the audio data to a file and return the file path
        audio_data = b"".join(self.frames)
        file_path = self.save_audio_to_file(audio_data)

        # Clear out self.frames
        self.frames = []

        return file_path

    def transcribe(self, audio_data):
        client = boto3.client("transcribe")
        response = client.start_transcription_job(
            TranscriptionJobName="MyTranscriptionJob",
            Media={"MediaFileUri": audio_data},
            MediaFormat="wav",
            LanguageCode="en-US",
        )
        while True:
            status = client.get_transcription_job(
                TranscriptionJobName="MyTranscriptionJob"
            )
            if status["TranscriptionJob"]["TranscriptionJobStatus"] in [
                "COMPLETED",
                "FAILED",
            ]:
                break
            log.debug("Not ready yet...")
            time.sleep(5)
        log.info(status)
