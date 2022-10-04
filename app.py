import requests
from flask import Flask, jsonify,request
import json

TOKEN = '5780584485:AAHHZ2r5hl-n1tii7xs8tnA59_CHskI--KU'

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])

def hello_world():
    if request.method == 'POST':
        data = request.get_json()
        print(f'DATA: {data}')
        return {'statusCode': 200, 'body': 'Success', 'data': data}
    else:
        return {'statusCode': 200, 'body': 'Success'}


if __name__ == '__main__':
    app.run(debug=True)