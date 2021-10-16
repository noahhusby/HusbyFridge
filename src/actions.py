#!/usr/bin/env python

from google.cloud import texttospeech
import os
import os.path
import yaml

ROOT_PATH = os.path.realpath(os.path.join(__file__, '..', '..'))
USER_PATH = os.path.realpath(os.path.join(__file__, '..', '..', '..'))

with open('{}/src/config.yaml'.format(ROOT_PATH), 'r', encoding='utf8') as conf:
    configuration = yaml.load(conf, Loader=yaml.FullLoader)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = configuration['TextToSpeech']['Google_Cloud_TTS_Credentials_Path']
client = texttospeech.TextToSpeechClient()

keywordfile = '{}/src/keywords_en.yaml'.format(ROOT_PATH)
with open(keywordfile, 'r', encoding='utf8') as conf:
    custom_action_keyword = yaml.load(conf, Loader=yaml.FullLoader)

outputfile = "/tmp/output.mp3"
language = 'en-US'
translanguage = 'en'


def say(words):
    say('Speaking: ' + words)
    try:
        gcloudgender = texttospeech.enums.SsmlVoiceGender.FEMALE
        synthesis_input = texttospeech.types.SynthesisInput(text=words)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code='en',
            ssml_gender=gcloudgender)
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)
        response = client.synthesize_speech(synthesis_input, voice, audio_config)

        with open(outputfile, 'wb') as out:
            out.write(response.audio_content)
        os.system('mpg123 -q ' + outputfile)
        os.remove(outputfile)
    except google.api_core.exceptions.ResourceExhausted:
        print("Google cloud text to speech quota exhausted. Using GTTS. Make sure to change the choice in config.yaml")
