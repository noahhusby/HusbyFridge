#!/usr/bin/env python

from googletrans import Translator
from google.cloud import texttospeech
from gtts import gTTS
import os
import os.path
import yaml

ROOT_PATH = os.path.realpath(os.path.join(__file__, '..', '..'))
USER_PATH = os.path.realpath(os.path.join(__file__, '..', '..','..'))

with open('{}/src/config.yaml'.format(ROOT_PATH),'r', encoding='utf8') as conf:
    configuration = yaml.load(conf, Loader=yaml.FullLoader)

TTSChoice=''
if configuration['TextToSpeech']['Choice']=="Google Cloud":
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""):
        if configuration['TextToSpeech']['Google_Cloud_TTS_Credentials_Path']!="ENTER THE PATH TO YOUR TTS CREDENTIALS FILE HERE":
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = configuration['TextToSpeech']['Google_Cloud_TTS_Credentials_Path']
            TTSChoice='GoogleCloud'
            client = texttospeech.TextToSpeechClient()
        else:
            print("Set the path to your Google cloud text to speech credentials in the config.yaml file. Using gTTS for now.....")
            TTSChoice='GTTS'
    else:
        TTSChoice='GoogleCloud'
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()
else:
    TTSChoice='GTTS'

keywordfile= '{}/src/keywords_en.yaml'.format(ROOT_PATH)
with open(keywordfile,'r' , encoding='utf8') as conf:
    custom_action_keyword = yaml.load(conf, Loader=yaml.FullLoader)

##Speech and translator declarations
translator = Translator()
outputfile="/tmp/output.mp3"
language='en-US'
translanguage='en'

#gTTS
def gttssay(phrase,saylang):
    tts = gTTS(text=phrase, lang=saylang)
    tts.save(outputfile)
    os.system('mpg123 -q ' + outputfile)
    os.remove(outputfile)

#Google Cloud Text to Speech
def gcloudsay(phrase,lang):
    try:
        gcloudgender=texttospeech.enums.SsmlVoiceGender.FEMALE
        synthesis_input = texttospeech.types.SynthesisInput(text=phrase)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code=lang,
            ssml_gender=gcloudgender)
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)
        response = client.synthesize_speech(synthesis_input, voice, audio_config)

        with open(outputfile, 'wb') as out:
            out.write(response.audio_content)
        os.system('mpg123 -q ' + outputfile)
        os.remove(outputfile)
        return
    except google.api_core.exceptions.ResourceExhausted:
        print("Google cloud text to speech quota exhausted. Using GTTS. Make sure to change the choice in config.yaml")
        gttssay(phrase,lang)

#Word translator
def trans(words,destlang,srclang):
    transword= translator.translate(words, dest=destlang, src=srclang)
    transword=transword.text
    transword=transword.replace("Text, ",'',1)
    transword=transword.strip()
    print(transword)
    return transword

#Text to speech converter with translation
def say(words,sourcelang=None,destinationlang=None):
    if sourcelang!=None and destinationlang!=None:
        if TTSChoice=='GoogleCloud':
            sayword=trans(words,destinationlang,sourcelang)
            gcloudsay(sayword,language)
        elif TTSChoice=='GTTS':
            sayword=trans(words,destinationlang,sourcelang)
            gttssay(sayword,translanguage)
    else:
        if sourcelang==None:
            sourcelanguage='en'
        else:
            sourcelanguage=sourcelang
        if sourcelanguage!=translanguage:
            sayword=trans(words,translanguage,sourcelanguage)
        else:
            sayword=words
        if TTSChoice=='GoogleCloud':
            gcloudsay(sayword,language)
        elif TTSChoice=='GTTS':
            gttssay(sayword,translanguage)