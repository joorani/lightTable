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

@app.route('/detail')
def detail():
    return render_template("detail.html")


## 메인페이지
# db에서 재료 가져오기
@app.route('/main', methods=['GET'])
def show_menu():
    keywordData = request.args.get('ingredients')
    menu_card = list(db.project1.find({'ingredients': {'$regex': keywordData}}, {'_id': 0}))
    return jsonify({'menu_card': menu_card})

# db에서 유저이름 가져오기(jinja2)
@app.route('/')
def user_name():
    # DB에서 저장된 name 찾아서 main 상단에 나타내기
    name = db.유저정보db.find({})
    return render_template("main.html", name=name)




## 상세페이지
# db에서 제목 가져오기(jinja2)
@app.route('/')
def title():
    # DB에서 저장된 title 찾아서 main title에 나타내기
    title = db.유저정보db.find({})
    return render_template("detail.html", name=title)





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
