import requests
from flask import Flask, jsonify,request
import json

TOKEN = '5780584485:AAHHZ2r5hl-n1tii7xs8tnA59_CHskI--KU'
NOTION_BEAR_TOKEN = 'secret_2yCYSZ3nvxL0BNPjN6bU8NBOSRtdIHgXkxOwUq48PFL'
DATABASE_LINK = 'https://www.notion.so/dc9c9681720a4941a317e75312ab9d69?v=f97c78618a924a2488c38c31f6b2f333'

app = Flask(__name__)

sample_response =  {
    'update_id': 6068183, 
    'message': 
        {'message_id': 1, 
        'from': {'id': 1399917123, 'is_bot': False, 'first_name': 'Lol', 'last_name': 'Yeet', 'username': 'yeetorbeyeeted69', 'language_code': 'en'}, 
        'chat': {'id': 1399917123, 'first_name': 'Lol', 'last_name': 'Yeet', 'username': 'yeetorbeyeeted69', 'type': 'private'}, 
        'date': 1664881469, 
        'text': '/start', 
        'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]
        }
}

def welcome_message(item):
    print(item)
    if item['text'].lower() == 'hi':
        msg = 'hello'
        chat_id = item['chat']['id']
        user_id = item["from"]["id"]
        username = item['from']["username"]
        welcome_msg = f'{msg} {username}'

        to_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={welcome_msg}&parse_mode=HTML'
        resp = requests.get(to_url)

@app.route("/", methods=['GET','POST'])
def hello_world():
    if request.method == 'POST':
        data = request.get_json()
        print(f'DATA: {data}')
        if 'message' in data:
            data = data['message']
            welcome_message(data)
            return {'statusCode': 200, 'body': 'Success', 'data': data}
        else:
            return {'statusCode': 404, 'body': 'User has left the chat room and deleted the chat', 'data': data}
    else:
        return {'statusCode': 200, 'body': 'Success'}


if __name__ == '__main__':
    app.run(debug=True)

