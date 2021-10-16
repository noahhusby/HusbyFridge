#!/usr/bin/env python

import os.path
import yaml

ROOT_PATH = os.path.realpath(os.path.join(__file__, '..', '..'))
USER_PATH = os.path.realpath(os.path.join(__file__, '..', '..', '..'))

with open('{}/src/config.yaml'.format(ROOT_PATH), 'r', encoding='utf8') as conf:
    configuration = yaml.load(conf, Loader=yaml.FullLoader)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = configuration['TextToSpeech']['Google_Cloud_TTS_Credentials_Path']

keywordfile = '{}/src/keywords_en.yaml'.format(ROOT_PATH)
with open(keywordfile, 'r', encoding='utf8') as conf:
    custom_action_keyword = yaml.load(conf, Loader=yaml.FullLoader)

outputfile = "/tmp/output.mp3"
language = 'en-US'
translanguage = 'en'