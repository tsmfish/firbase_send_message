"""Server Side FCM sample.

Firebase Cloud Messaging (FCM) can be used to send messages to clients on iOS,
Android and Web.

This sample uses FCM to send two types of messages to clients that are subscribed
to the `news` topic. One type of message is a simple notification message (display message).
The other is a notification message (display notification) with platform specific
customizations. For example, a badge is added to messages that are sent to iOS devices.
"""

import argparse
import datetime
import json
import os

import requests
from oauth2client.service_account import ServiceAccountCredentials

PROJECT_ID = 'fir-testnoti-c842e'
BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = 'v1/projects/' + PROJECT_ID + '/messages:send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']


# [START retrieve_access_token]
def _get_access_token():
    """Retrieve a valid access token that can be used to authorize requests.

    :return: Access token.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'service-account.json', SCOPES)
    access_token_info = credentials.get_access_token()
    # print("access_token [%s]" % access_token_info.access_token)
    return access_token_info.access_token


# [END retrieve_access_token]

def _send_fcm_message(fcm_message):
    """Send HTTP request to FCM with given message.

    Args:
      fcm_message: JSON object that will make up the body of the request.
    """
    # [START use_access_token]
    headers = {
        'Authorization': 'Bearer ' + _get_access_token(),
        'Content-Type': 'application/json; UTF-8',
    }
    # [END use_access_token]
    resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)

    if resp.status_code == 200:
        print('Message sent to Firebase for delivery, response:')
        print(resp.text)
    else:
        print('Unable to send message to Firebase')
        print(resp.text)


def _build_common_message(type, fcm_token, auth_token):
    """Construct common notifiation message.

    Construct a JSON object that will be used to define the
    common parts of a notification message that will be sent
    to any app instance subscribed to the news topic.
    """
    return {
        'message': {
            'token': fcm_token,
            'notification': {
                'title': datetime.datetime.now().ctime(),
                'body': 'Notification from FCM',
            },
            "data": {
                'Type': type,
                'Token': auth_token
            }
        }
    }


def _build_override_message(type, fcm_token, auth_token):
    """Construct common notification message with overrides.

    Constructs a JSON object that will be used to customize
    the messages that are sent to iOS and Android devices.
    """
    fcm_message = _build_common_message()

    apns_override = {
        'payload': {
            'aps': {
                'badge': 1
            },
            'message': {
                'token': fcm_token,
                'notification': {
                    'title': datetime.datetime.now().ctime(),
                    'body': 'Notification from FCM',
                },
            },
            "data": {
              'Type': type,
              'Token': auth_token
            }
        },
        'headers': {
            'apns-priority': '10'
        }
    }

    android_override = {
        'notification': {
            'click_action': 'android.intent.action.MAIN'
        }
    }

    fcm_message['message']['android'] = android_override
    fcm_message['message']['apns'] = apns_override

    return fcm_message


def main():
    parser = argparse.ArgumentParser(description='use export FCM_TOKEN=\'\',\n'
                                                 'export AUTH_TOKEN=\'\',\n'
                                                 'to initialise tokens.\n')
    parser.add_argument('--message', help="FCM message type, can be: common-message, override-message")
    parser.add_argument('--type', help="field type in data part can be: [0..3]")
    args = parser.parse_args()
    if 'FCM_TOKEN' in os.environ.keys():
        fcm_token = os.environ['FCM_TOKEN']
    else:
        fcm_token = 'dFCFvFF_ScQ:APA91bEfN-2QXcKN4dDX_R-PBKDfQukOztgdvHf2E3q9CV_B4rbQZHOPtxEyPKqWsIx6FIyN_jArU-LP9cSAQTAfizqS_PvcOVSkGZUdKbicFzHCEeO7wu8RQrJEOy0Ln8egXMDVLa4T'
    if 'AUTH_TOKEN' in os.environ.keys():
        auth_token = os.environ['AUTH_TOKEN']
    else:
        auth_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImJiZDhkNDRmMDk5YzU3ZDQ1MTg4NTczNjk2ZTYyMDlmYzFiOGY1MzRkN2U2MmU3ZGQyMThkZGUzN2I1NjdkYmZjNzBlMTNhYmJjYzdjNGZhIn0.eyJhdWQiOiIyIiwianRpIjoiYmJkOGQ0NGYwOTljNTdkNDUxODg1NzM2OTZlNjIwOWZjMWI4ZjUzNGQ3ZTYyZTdkZDIxOGRkZTM3YjU2N2RiZmM3MGUxM2FiYmNjN2M0ZmEiLCJpYXQiOjE1ODUxNzAwMDcsIm5iZiI6MTU4NTE3MDAwNywiZXhwIjoxNTg2NDYyNDA3LCJzdWIiOiIzNDkxIiwic2NvcGVzIjpbXX0.gWvPEZsEL6qYHetyvAtMaQSRFI12oIzoR99cI87WqelDPY0gv2apElQruyyzmeqUlsX8AvG0S8D39PXbeCCYQADhdR8B9PRDEECNrYlhnvZ8BUNbmPWvO_bZoVlQIQiUdUV3f1QH79FU4LiaWhYFoSv57e12cBE5nDzlC4kg0K6vVvnPKdkvoGN4vUf-VbBVsztB8V0mgjlQ6CTBLvBXat-LFXKrU4MjbDRPAf6mcZsohlJdiTqeQNWUxSeFH4H2bmmgW7qnN2R7Nr6rSuBIezrVLfDfzLar-jitnCbBf-kCHlA3GDUrWIZpkrQj1Yjy_9z-PNKvolW1Qnkm4Sahqqsc68rCftdvkzE1Na2BpKEAwN5JMrrzfeoJIopYkaAdRjoUFE7LCbmDEzBsZfrxKjyv4fKt2F0GiYMVeOv7e_ARUYmGyhZ_U9c0cxN6HR-tlKGj4CG2-QEQgWvQ3bm4fCXeqb6ELgNCg7n1UeApt0F7NBL83fEgXm5IFUecMhtM4CHyCT3uMhNvqRjiMTUyrkaLN5vOJupK27zeT_qQp1j6cPwgksBZLntPhnvSghaiagTd4D65mBBWjPqeYAjL3DWOIp-oL7cwzUzZqIQ42IHPCI8J6vmO9aCyT5f5sgY2mUx-8TlDADMMNGba-QrQ1H6DRlQ0WeQ-l6CouL3VCxw'

    if args.message and args.message == 'common-message':
        common_message = _build_common_message(args.type, fcm_token, auth_token)
        print('FCM request body for message using common notification object:')
        print(json.dumps(common_message, indent=2))
        _send_fcm_message(common_message)
    elif args.message and args.message == 'override-message':
        override_message = _build_override_message(args.type, fcm_token, auth_token)
        print('FCM request body for override message:')
        print(json.dumps(override_message, indent=2))
        _send_fcm_message(override_message)
    else:
        print('''Invalid command. Please use one of the following commands:
python messaging.py --message=common-message
python messaging.py --message=override-message''')


if __name__ == '__main__':
    main()
