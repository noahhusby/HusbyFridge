#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import faulthandler
faulthandler.enable()
import argparse
import json
import os.path
import pathlib2 as pathlib
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/pi/google_tts_credentials.json'
import subprocess
import logging
import serial
import google.oauth2.credentials
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
from google.assistant.library.device_helpers import register_device

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


WARNING_NOT_REGISTERED = """
    This device is not registered. This means you will not be able to use
    Device Actions or see your device in Assistant Settings. In order to
    register this device follow instructions at:

    https://developers.google.com/assistant/sdk/guides/library/python/embed/register-device
"""

HEADER = """

--------------------------------------------------------------

  _    _           _           ______    _     _            
 | |  | |         | |         |  ____|  (_)   | |           
 | |__| |_   _ ___| |__  _   _| |__ _ __ _  __| | __ _  ___ 
 |  __  | | | / __| '_ \| | | |  __| '__| |/ _` |/ _` |/ _ |
 | |  | | |_| \__ \ |_) | |_| | |  | |  | | (_| | (_| |  __/
 |_|  |_|\__,_|___/_.__/ \__, |_|  |_|  |_|\__,_|\__, |\___|
                          __/ |                   __/ |     
                         |___/                   |___/      
                         
--------------------------------------------------------------

"""

# Remove old logs
if os.path.isfile('/tmp/HusbyFridge.log'):
    os.system('sudo rm /tmp/HusbyFridge.log')

logging.root.handlers = []
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG , filename='/tmp/HusbyFridge.log')
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

ROOT_PATH = os.path.realpath(os.path.join(__file__, '..', '..'))
USER_PATH = os.path.realpath(os.path.join(__file__, '..', '..','..'))

language = 'en-US'
translanguage = 'en'

# Start connection to Arduino
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.flush()

class Myassistant():

    def __init__(self):
        self.interrupted=False
        self.can_start_conversation=False
        self.assistant=None
        self._input_device_index = None
        self.interpreter=False
        self.interpconvcounter=0
        self.interpcloudlang1=language
        self.interpttslang1=translanguage
        self.interpcloudlang2=''
        self.interpttslang2=''
        self.singleresposne=False
        self.singledetectedresponse=''

    def signal_handler(self,signal, frame):
        self.interrupted = True

    def interrupt_callback(self):
        return self.interrupted

    def process_event(self,event):
        """Pretty prints events.
        Prints all events that occur with two spaces between each new
        conversation and a single space between turns of a conversation.
        Args:
            event(event.Event): The current event to process.
        """
        print("[" + str(event.type) + "] " + str(event.args))

        if event.type == EventType.ON_START_FINISHED:
            self.can_start_conversation = True

        if event.type == EventType.ON_ALERT_STARTED:
            self.can_start_conversation = True
            assistantindicator('alarm')

        if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            subprocess.Popen(["aplay", "{}/src/resources/wake.wav".format(ROOT_PATH)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.can_start_conversation = False
            assistantindicator('listening')

        if (event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT or event.type == EventType.ON_NO_RESPONSE):
            self.can_start_conversation = True
            assistantindicator('off')

        if (event.type == EventType.ON_RESPONDING_STARTED and event.args and not event.args['is_error_response']):
            assistantindicator('speaking')

        if (event.type == EventType.ON_RESPONDING_FINISHED):
            assistantindicator('off')

        if (event.type == EventType.ON_ALERT_FINISHED):
            assistantindicator('off')

        if (event.type == EventType.ON_RENDER_RESPONSE):
            assistantindicator('speaking')

        #if (event.type == EventType.ON_DEVICE_ACTION):
        #    print('action')

        if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
            if self.singleresposne:
                self.assistant.stop_conversation()
                self.singledetectedresponse = event.args["text"]
                assistantindicator('off')

        if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
                event.args and not event.args['with_follow_on_turn']):
            self.can_start_conversation = True
            assistantindicator('off')

    def register_device(self,project_id, credentials, device_model_id, device_id):
        """Register the device if needed.
        Registers a new assistant device if an instance with the given id
        does not already exists for this model.
        Args:
           project_id(str): The project ID used to register device instance.
           credentials(google.oauth2.credentials.Credentials): The Google
                    OAuth2 credentials of the user to associate the device
                    instance with.
           device_model_id: The registered device model ID.
           device_id: The device ID of the new instance.
        """
        base_url = '/'.join([DEVICE_API_URL, 'projects', project_id, 'devices'])
        device_url = '/'.join([base_url, device_id])
        session = google.auth.transport.requests.AuthorizedSession(credentials)
        r = session.get(device_url)
        print(device_url, r.status_code)
        if r.status_code == 404:
            print('Registering....')
            r = session.post(base_url, data=json.dumps({
                'id': device_id,
                'model_id': device_model_id,
                'client_type': 'SDK_LIBRARY'
            }))
            if r.status_code != 200:
                raise Exception('failed to register device: ' + r.text)
            print('\rDevice registered.')

    def main(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--device-model-id', '--device_model_id', type=str,
                            metavar='DEVICE_MODEL_ID', required=False,
                            help='the device model ID registered with Google')
        parser.add_argument('--project-id', '--project_id', type=str,
                            metavar='PROJECT_ID', required=False,
                            help='the project ID used to register this device')
        parser.add_argument('--nickname', type=str,
                        metavar='NICKNAME', required=False,
                        help='the nickname used to register this device')
        parser.add_argument('--device-config', type=str,
                            metavar='DEVICE_CONFIG_FILE',
                            default=os.path.join(
                                os.path.expanduser('~/.config'),
                                'googlesamples-assistant',
                                'device_config_library.json'
                            ),
                            help='path to store and read device configuration')
        parser.add_argument('--credentials', type=existing_file,
                            metavar='OAUTH2_CREDENTIALS_FILE',
                            default=os.path.join(
                                os.path.expanduser('~/.config'),
                                'google-oauthlib-tool',
                                'credentials.json'
                            ),
                            help='path to store and read OAuth2 credentials')
        parser.add_argument('--query', type=str,
                        metavar='QUERY',
                        help='query to send as soon as the Assistant starts')
        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s ' + Assistant.__version_str__())

        args = parser.parse_args()
        with open(args.credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))

        device_model_id = None
        last_device_id = None
        try:
            with open(args.device_config) as f:
                device_config = json.load(f)
                device_model_id = device_config['model_id']
                last_device_id = device_config.get('last_device_id', None)
        except FileNotFoundError:
            pass

        if not args.device_model_id and not device_model_id:
            raise Exception('Missing --device-model-id option')

        # Re-register if "device_model_id" is given by the user and it differs
        # from what we previously registered with.
        should_register = (
            args.device_model_id and args.device_model_id != device_model_id)

        device_model_id = args.device_model_id or device_model_id
        with Assistant(credentials, device_model_id) as assistant:
            self.assistant = assistant
            subprocess.Popen(["aplay", "{}/src/resources/startup.wav".format(ROOT_PATH)], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            events = assistant.start()
            device_id = assistant.device_id
            print(HEADER)
            print('device_model_id:', device_model_id)
            print('device_id:', device_id + '\n')

            # Re-register if "device_id" is different from the last "device_id":
            if should_register or (device_id != last_device_id):
                if args.project_id:
                    register_device(args.project_id, credentials,
                                    device_model_id, device_id, args.nickname)
                    pathlib.Path(os.path.dirname(args.device_config)).mkdir(
                        exist_ok=True)
                    with open(args.device_config, 'w') as f:
                        json.dump({
                            'last_device_id': device_id,
                            'model_id': device_model_id,
                        }, f)
                else:
                    print(WARNING_NOT_REGISTERED)

            for event in events:
                if event.type == EventType.ON_START_FINISHED and args.query:
                    assistant.send_text_query(args.query)
                self.process_event(event)

def assistantindicator(activity):
    activity=activity.lower()
    if activity=='listening':
        ser.write(b"LISTENING\n")
    elif activity=='speaking':
        ser.write(b"SPEAKING\n")
    elif (activity=='off' or activity=='unmute'):
        ser.write(b"OFF\n")
    elif (activity=='on' or activity=='mute'):
        ser.write(b"MUTE\n")
    elif (activity=='alarm'):
        ser.write(b"ALARM\n")
    elif (activity=='on'):
        ser.write(b"ON\n")


if __name__ == '__main__':
    try:
        Myassistant().main()
    except Exception as error:
        logging.exception(error)
