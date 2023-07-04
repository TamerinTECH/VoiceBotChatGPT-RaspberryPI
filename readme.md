# Raspberry Pi Voice Bot ChatGPT

[Link to the demo video](https://youtube.com/shorts/6NRtFTbH-e0?feature=share)

## Introduction

This project is a voice-activated Raspberry Pi based system that listens for a wake word, "picovoice". Upon hearing the wake word, the system starts recording audio input until it detects silence. It then sends this audio input to OpenAI for transcription and further processing. The response from OpenAI is then converted to speech using Amazon Polly, a text-to-speech service, and played back to the user.

## Project Structure

The project is divided into four main python files:

1. **main.py**: The main script that integrates all other modules, listens for the wake word, manages the audio recording, and handles the interaction with OpenAI and AWS Polly.

2. **tts_service.py**: Handles the text-to-speech conversion using Amazon Polly.

3. **input_listener.py**: Handles the audio recording and silence detection.

4. **chat_gpt_service.py**: Manages the interaction with OpenAI's GPT-3 model.

There is also a configuration file, **config.json**, which stores important parameters and keys.

## Prerequisites

This project requires Python 3.8 or higher. It also requires specific Python packages which are listed in the `requirements.txt` file. Install the required packages with the command:

```
pip install -r requirements.txt
```

In addition to these packages, this project also uses:

- [Porcupine](https://picovoice.ai/products/porcupine/) (Picovoice's wake word engine): This is used to listen for the wake word.
- [OpenAI](https://openai.com/): This is used to transcribe and process the audio input. You will need an API key from OpenAI to use this service.
- [Amazon Polly](https://aws.amazon.com/polly/): This is used to convert the response from OpenAI into speech. You will need AWS credentials to use this service.

## Configuration

All the keys and important parameters are stored in the `config.json` file. This includes:

- OpenAI API key (`openai_key`): Used for interacting with OpenAI.
- Porcupine Access Key (`pv_access_key`): Used for wake word detection.
- AWS credentials (`aws_access_key_id`, `aws_secret_access_key`): Used for text-to-speech conversion with Amazon Polly.
- Silence threshold (`silence_threshold`): The RMS threshold below which the input is considered silent.
- Silence duration (`silence_duration`): The duration of silence (in seconds) after which the recording is stopped.
- Sound card name (`sound_card_name`): The name of the sound card used for audio input.

## Running the Project

To run the project, execute the `main.py` script:

```
python main.py
```

# Obtaining Required Keys

This project requires keys from OpenAI, Picovoice, and AWS. Here is how to obtain them:

1. **OpenAI Key**: Sign up at [openai.com](https://www.openai.com/) and follow the instructions [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) to obtain your secret API key.

2. **Picovoice Key**: Sign up for free at [picovoice.ai](https://picovoice.ai/) to obtain your key.

3. **AWS Keys**: Sign up at [AWS](https://aws.amazon.com/). You need to create an IAM user and obtain the access key and secret. Make sure to assign a policy that allows the user to use the Polly service.

After obtaining these keys, add them to your `config.json` file.

# Silence Detection

The InputListener class is responsible for listening to the user's input and detecting silence. It uses the Root Mean Square (RMS) value of the audio signal to decide whether the user is speaking or not.

The threshold for silence can be adjusted in the `config.json` file using the `silence_threshold` parameter. The `silence_duration` parameter determines how long the silence must continue before the system decides that the user has finished speaking.

The correct values for these parameters may depend on the specific microphone and environment you are using. If you are unsure about the correct values, you can run the program and observe the RMS values that are printed to the console after the wake word is detected. Here is an example:

```
RMS: 347
RMS: 452
RMS: 458
RMS: 575
RMS: 392
RMS: 444
RMS: 474
RMS: 552
RMS: 304
RMS: 535
RMS: 456
RMS: 417
RMS: 226
RMS: 516
RMS: 523
RMS: 219
RMS: 296
RMS: 508
RMS: 375
RMS: 229
RMS: 439
```

By observing these values, you can get a sense of which RMS values correspond to speech and which correspond to silence, and adjust the `silence_threshold` and `silence_duration` parameters accordingly.

# Tested Environment and Installation Instructions

This project has been tested on a RaspberryPi 4 using Raspberry Pi OS 64 bit (version 6.1, released on May 3rd, 2023). The SHA of the release is e7c0c89db32d457298fbe93195e9d11e3e6b4eb9e0683a7beb1598ea39a0a7aa.

We used the ReSpeaker 2-Mics Pi HAT as the sound card. More information about this sound card can be found [here](https://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT_Raspberry/).

## Raspberry Pi Setup

Below are the commands to set up the project on your Raspberry Pi:

1. **Install the ReSpeaker 2-Mics Pi HAT sound card**

```bash
sudo apt-get update -y
sudo apt-get install portaudio19-dev libatlas-base-dev -y
git clone https://github.com/seeed-studio-projects/seeed-voicecard.git
cd seeed-voicecard
sudo ./install.sh
sudo reboot now
```

2. **Clone the VoiceBotChatGPT-RaspberryPI repository**

```bash
git clone https://github.com/TamerinTECH/VoiceBotChatGPT-RaspberryPI.git
cd VoiceBotChatGPT-RaspberryPI
```

3. **Upgrade pip and install the required Python packages**

```bash
pip install --upgrade pip setuptools wheel
pip3 install -r requirements.txt
```

Now, your Raspberry Pi is set up to run the project. Remember to add your API keys to the `config.json` file before running the `main.py` script.

# Setting Up the Default Audio Output Device

In some instances, you may need to manually select the default audio output device. Here is how you can do it:

1. Open the Raspberry Pi configuration settings:

```bash
sudo raspi-config
```

2. Navigate through the menu options as follows:

```
1. System options  
S2. Audio
```

3. Select the desired audio output option. In our case, it was the `bcm2835-i2s...` option corresponding to the ReSpeaker sound card.

After you've selected the appropriate option, the system should use this device as the default for audio output.

## Startup

Upon starting the application, the first 5 seconds will be used to automatically detect the silence threshold. During this time, it is recommended to stay quiet so the system can accurately capture the baseline ambient noise level in your environment.

The detected silence threshold will be used throughout the session to determine periods of silence. This allows the system to adjust to different noise environments and ensures more accurate detection of when a user has finished speaking.

To start the application, you simply run the main script. During the initial silence detection phase, you might want to avoid speaking or creating any significant noise so as not to interfere with the threshold detection.

Once the silence threshold is set, the application is ready to listen for your commands. If you've opted to use the LED indicator and have correctly set the `led_pin` in your `config.json` file, the LED will light up when the system is actively listening to your commands.

Remember, this silence threshold detection is performed every time the application starts. If you find the application is not accurately detecting the end of commands, it might be worth restarting the application in a quieter environment to get a more accurate silence threshold.

## Limitations

Please note that this project was developed for hackathon and demo purposes. Therefore, there is no guarantee for its performance or functionality. For additional information, please contact the company [TamerinTECH](https://www.tamerin.tech) - [voicebot@tamerin.tech](mailto:voicebot@tamerin.tech)

## Acknowledgements

This documentation was written by ChatGPT with some supervision by the author


