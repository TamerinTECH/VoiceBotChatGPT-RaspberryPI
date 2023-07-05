import time
import audioop
import pyaudio

import logging
from systemd import journal

log = logging.getLogger('GPTVoiceAssistant')
log.addHandler(journal.JournaldLogHandler())
log.setLevel(logging.DEBUG)


class ThresholdDetector:
    def __init__(self, sample_duration=5):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.sample_duration = sample_duration
        self.audio = pyaudio.PyAudio()

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

    def detect_threshold(self):
        self.start()
        rms_values = []
        start_time = time.time()
        log.info("Start detecting threshold...")
        while True:
            data = self.stream.read(self.chunk)
            rms = audioop.rms(data, 2)
            log.debug(f"RMS value: {rms}")
            rms_values.append(rms)
            if time.time() - start_time > self.sample_duration:
                log.info("Sample duration completed, stop detecting")
                break
        self.stop()

        # Calculate the average RMS value as the silence threshold
        average_rms = sum(rms_values) / len(rms_values)
        log.info(f"The average RMS value is {average_rms}")
        return average_rms

if __name__ == "__main__":
    detector = ThresholdDetector()
    silence_threshold = detector.detect_threshold()
