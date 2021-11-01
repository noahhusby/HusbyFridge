#
# MIT License
#
# Copyright 2021 noahhusby
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import print_function

import faulthandler

faulthandler.enable()
import argparse
import json
import os.path
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/pi/google_tts_credentials.json'
import subprocess
import logging
import serial
import google.oauth2.credentials
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

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
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,
                    filename='/tmp/HusbyFridge.log')
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

ROOT_PATH = os.path.realpath(os.path.join(__file__, '..', '..'))
USER_PATH = os.path.realpath(os.path.join(__file__, '..', '..', '..'))

language = 'en-US'
translanguage = 'en'

# Start connection to Arduino
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.flush()


class Myassistant():

    def __init__(self):
        self.alarm = None
        self.assistant = None

    def process_event(self, event):
        print("[" + str(event.type) + "] " + str(event.args))

        if event.type == EventType.ON_ALERT_STARTED:
            if event.args['alert_type'] == 0:
                self.set_lighting('alarm')
            else:
                self.set_lighting('timer')

        if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            subprocess.Popen(["aplay", "{}/src/resources/wake.wav".format(ROOT_PATH)], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.set_lighting('listening')

        if event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT or event.type == EventType.ON_NO_RESPONSE:
            self.set_lighting('off')

        if event.type == EventType.ON_RESPONDING_STARTED and event.args and not event.args['is_error_response']:
            self.set_lighting('speaking')

        if event.type == EventType.ON_RESPONDING_FINISHED:
            self.set_lighting('off')

        if event.type == EventType.ON_ALERT_FINISHED:
            self.set_lighting('off')

        if event.type == EventType.ON_RENDER_RESPONSE:
            self.set_lighting('speaking')

        if event.type == EventType.ON_ASSISTANT_ERROR:
            self.set_lighting('error')

        if event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            self.set_lighting('off')

    def main(self):
        subprocess.run(["amixer", "-c", "2", "sset", "Headphone", "100%"])
        subprocess.run(["aplay", "-Dplug:gaudio", "{}/src/resources/startup.wav".format(ROOT_PATH)])
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
        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s ' + Assistant.__version_str__())

        args = parser.parse_args()
        with open(args.credentials, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))

        device_model_id = None
        try:
            with open(args.device_config) as f:
                device_config = json.load(f)
                device_model_id = device_config['model_id']
        except FileNotFoundError:
            pass

        if not args.device_model_id and not device_model_id:
            raise Exception('Missing --device-model-id option')

        device_model_id = args.device_model_id or device_model_id
        with Assistant(credentials, device_model_id) as assistant:
            self.assistant = assistant
            events = assistant.start()
            device_id = assistant.device_id

            print(HEADER)
            print('Device Model ID:', device_model_id)
            print('Device ID:', device_id + '\n')

            for event in events:
                self.process_event(event)

    def set_lighting(self, activity):
        if self.alarm is not None:
            self.alarm.kill()
        activity = activity.lower()
        if activity == 'listening':
            ser.write(b"LISTENING\n")
        elif activity == 'speaking':
            ser.write(b"SPEAKING\n")
        elif activity == 'off' or activity == 'unmute':
            ser.write(b"OFF\n")
        elif activity == 'on' or activity == 'mute' or activity == 'error':
            ser.write(b"MUTE\n")
        elif activity == 'alarm':
            ser.write(b"ALARM\n")
            self.alarm = subprocess.Popen(["mpg123", "--loop", "100", "{}/src/resources/alarm.mp3".format(ROOT_PATH)],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif activity == 'on':
            ser.write(b"ON\n")
        elif activity == 'timer':
            ser.write(b"TIMER\n")


if __name__ == '__main__':
    try:
        Myassistant().main()
    except Exception as error:
        logging.exception(error)
