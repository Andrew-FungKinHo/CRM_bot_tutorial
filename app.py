from ast import parse
from genericpath import isfile
import requests
from flask import Flask, jsonify,request
import json
import os 
import time
import datetime


TOKEN = '5780584485:AAHHZ2r5hl-n1tii7xs8tnA59_CHskI--KU'
NOTION_BEAR_TOKEN = 'secret_2yCYSZ3nvxL0BNPjN6bU8NBOSRtdIHgXkxOwUq48PFL'
DATABASE_LINK = 'https://www.notion.so/dc9c9681720a4941a317e75312ab9d69?v=f97c78618a924a2488c38c31f6b2f333'
HEADERS = {
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
    "Authorization": "Bearer secret_2yCYSZ3nvxL0BNPjN6bU8NBOSRtdIHgXkxOwUq48PFL"
}
BANNED_USERNAMES = []
# 576894
BANNED_USER_IDS = []


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

# load all the username from the notion spreadsheet and return a dictionary in the format 
def loadUsernames():
    url = "https://api.notion.com/v1/databases/dc9c9681720a4941a317e75312ab9d69/query"

    payload = {"page_size": 100}

    response = requests.post(url, json=payload, headers=HEADERS)

    data = response.text
    # turn JSON string back into python dictionary
    parsed = json.loads(data)

    username_dict = {}

    for entry in parsed['results']:
        # check its username
        if entry['properties']['User']['title']:
            # check its product
            if entry['properties']['Product']['select']:
                # check its status
                if entry['properties']['Status']['select']:
                    # { username: (selected_product, status, page id) }
                    username_dict[entry['properties']['User']['title'][0]['text']['content']] = (entry['properties']['Product']['select']['name'],entry['properties']['Status']['select']['name'],entry['id'])
    return username_dict

def sendMessage(msg,item):
    chat_id = item['chat']['id']
    user_id = item["from"]["id"]
    username = item['from']["username"]

    new_msg = f'{msg} {username}'
    to_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={new_msg}&parse_mode=HTML'
    resp = requests.post(to_url)

def sendLocalSourceFiles(item, product):
    chat_id = item['chat']['id']
    directory = os.getcwd() + f'/sourceFiles/{product}'

    for filename in os.listdir(directory):
        f = os.path.join(directory,filename)
        # check if it is a file
        if os.path.isfile(f):
            doc = open(os.path.join(directory,filename), 'rb')
            files = {'document': doc}
            to_url = 'https://api.telegram.org/bot{}/sendDocument?chat_id={}&parse_mode=HTML'.format(TOKEN,chat_id)
            resp = requests.post(to_url,files=files)
            print(f'File:   {filename} is sent')
            time.sleep(0.75)

def turnStatusToClosed(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {
        "properties": {
            "Status": {"select": {"name": "Closed"}},
            "Date": {"date": {"start": datetime.datetime.today().strftime("%Y-%m-%d")}}
        }
    }


    response = requests.patch(url, headers=HEADERS, json=payload)

    print(response.text)

def addUserResponse(item,userStatus=""):
    url = "https://api.notion.com/v1/pages/"
    payload = {
        "parent": {
            "database_id": '30b44a61cc184d3b888d3f586b294d0d'
        },
        "properties": {
            "Message ID": {
                "number": item["message_id"]
            },
            "Username": {
                "title": [
                    {
                        "text": {
                            "content": f"@{item['from']['username']}"
                        }
                    }
                ]
            },
            "Message": {
                "rich_text": [
                    {
                        "text": {
                            "content": item['text']
                        }
                    }
                ]
            },
            "Remarks": {
                "rich_text": [
                    {
                        "text": {
                            "content": userStatus
                        }
                    }
                ]
            },
            "Message_datetime_in_UNIX": {
                "number": item['date'] * 1000
            },
            "User ID": {
                "number": item['from']['id']
            }
        }
    }
        
    response = requests.post(url, json=payload, headers=HEADERS)
    print(response.text)


def welcome_message(item):
    print(item)

    chat_id = item['chat']['id']
    user_id = item["from"]["id"]
    username = item['from']["username"]
    customers = loadUsernames()

    if 'text' in item:
        # check if the user has been banned
        if user_id in BANNED_USER_IDS or username in BANNED_USERNAMES:
            addUserResponse(item,userStatus="Banned user")
            sendMessage("You have been banned by this bot", item)
            return

        addUserResponse(item)
        if item['text'].lower() == '/start':
            if username in customers.keys():
                print(customers[username])
                if customers[username][1] == 'Pending':
                    sendMessage(f'sending {customers[username][0]} information',item)
                    sendLocalSourceFiles(item,customers[username][0])
                    # close their requests (turn their status from pending to closed)
                    turnStatusToClosed(customers[username][2])
                    return 
                elif customers[username][1] == 'Closed':
                    sendMessage(f'Your previous request has been closed. Please contact the admins for further information.',item)
                    return 
                else:
                    addUserResponse(item,userStatus="Unknown user")
                    sendMessage(f'Unknown user. Please contact the admins for further information.',item)
                    return
                    
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

