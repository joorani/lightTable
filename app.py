
import requests

from flask import Flask, render_template, jsonify, request, redirect
from bson.json_util import loads, dumps
import jwt, datetime, hashlib

from pymongo import MongoClient

app = Flask(__name__)
# git에 올라가면 안되는 내용!
# app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

# SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.projectdb
collection = db.collection

doc = {'img_url': 'https://recipe1.ezmember.co.kr/cache/recipe/2018/10/29/0dd4c2525a4585417e37cff57a7701d11_m.jpg',
       'title': '돼지고기조림', 'ingredients':'돼지고기, 간장','recipe':'곤약 넣고 조리기..'}
db.project1.insert_one(doc)


@app.route('/')
def main():
    return render_template("main.html")

@app.route('/detail')
def detail():
    return render_template("detail.html")
# login 페이지
@app.route('/main')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_info = db.users.find_one({"userid": payload["userid"]})
        return render_template('index.html', user_info=user_info)
        # 로그인시간 만료, 정보 에러시 보여주는 페이지 생성해야함. index.html?? url_for에 연결.
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    userid_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'userid': userid_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': userid_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/join/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    userid_receive = request.form['userid_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,
        "userid": userid_receive,
        "password": password_hash,
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

# 아이디 중복확인
@app.route('/join/check_dup', methods=['POST'])
def check_dup():
    userid_receive = request.form['userid_give']
    exists = bool(db.users.find_one({"userid": userid_receive}))
    return jsonify({'result': 'success', 'exists': exists})

## 메인페이지
# db에서 재료 가져오기
@app.route('/detail/<keyword>')
def detail(keyword):
    r = requests.get(f"https://owlbot.info/api/v4/dictionary/{keyword}", headers={"Authorization": "Token [내토큰]"})
    result = r.json()
    print(result)
    return render_template("detail.html", word=keyword, result=result)


## 메인페이지
# db에서 재료 가져오기/ 키워트 클릭 시 카드출력
@app.route('/main', methods=['GET'])
def show_menu():
    keywordData = request.args.get('ingredients')
    menu_card = list(db.project1.find({'ingredients': {'$regex': keywordData}}, {'_id': 0}))
    return jsonify({'menu_card': menu_card})

# db에서 유저이름 가져오기(jinja2)
@app.route('/')
def user_name():
    # DB에서 저장된 name 찾아서 main 상단에 나타내기
    name = db.유저정보db.find({})    # db 확인
    return render_template("main.html", name=name)

# db에서 title, img 가져오기(jinja2)
@app.route('/')
def recipecards():
    # DB에서 저장된 name 찾아서 main 상단에 나타내기
    ingredientsData = request.args.get('ingredients')
    recipeInfo = list(db.project1.find({'ingredients': {'$regex': ingredientsData}}, {'_id': 0}))
    return render_template("main.html", recipeInfo=recipeInfo)

## 상세페이지
# db에서 제목 가져오기(jinja2)
@app.route('/detail')
def title():
    # DB에서 저장된 title 찾아서 main title에 나타내기
    title = list(db.레시피db.find({}))
    return render_template("detail.html", title=title)

# 상세페이지에 제목가져오기
@app.route('/detail', methods=['GET'])
def show_detailWin():
    titleData = request.args.get('title')
    getdetailWin = list(db.레시피db.find({'title': {'$regex': titleData}}, {'_id': 0})) #db 확인
    return jsonify({'getdetailWin': getdetailWin})

# 코멘트 달기
@app.route('/comment', methods=['POST'])
def save_order():
    name_receive = request.form['name_give']
    comment_receive = request.form['comment_give']

    doc = {
        'name': name_receive,
        'comment': comment_receive,
    }

    print(doc)
    db.commetndb.insert_one(doc) #db 확인
    return jsonify({'msg': '등록 완료'})

# comment 목록보기(Read) API
@app.route('/comment', methods=['GET'])
def view_orders():
    commnetList = list(db.commetndb.find({},{'_id':False})) #db 확인
    return jsonify({'commnetList':commnetList})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
