import requests

from flask import Flask, render_template, jsonify, request, redirect
from bson.json_util import loads, dumps

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.projectdb
collection = db.collection

doc = {'img_url': 'https://recipe1.ezmember.co.kr/cache/recipe/2018/10/29/0dd4c2525a4585417e37cff57a7701d11_m.jpg',
       'title': '곤약조림', 'ingredients':'곤약, 간장','recipe':'곤약 넣고 조리기..'}
db.project1.insert_one(doc)


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/category', methods=['GET'])
def show_category():
    keywordData = request.args.get('hashtag')
    myquery = list(db.project1.find({'ingredients': {'$regex': keywordData}}, {'_id': 0}))
    return jsonify({'myquery': myquery})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
