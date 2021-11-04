
import requests
from bson import ObjectId

from flask import Flask, render_template, jsonify, request, redirect, url_for
from bson.json_util import loads, dumps
import jwt
import datetime
import hashlib

from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
# git에 올라가면 안되는 내용!
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'lightTable'

client = MongoClient('3.35.47.11', 27017, username="light", password="table")
db = client.collections

# 회원가입
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

# 로그인
@app.route('/sign_in', methods=['POST'])
def sign_in():
    userid_receive = request.form['userid_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'userid': userid_receive, 'password': pw_hash})
    # 유저 정보가 있으면
    if result is not None:
        payload = {
         'id': userid_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 첫 페이지- 로그인
@app.route('/')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/main')
def show_menu():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = (payload["id"])
        user_info = db.users.find_one({"userid": userid}, {"_id": 0})
        recipe_list = list(db.recipe.find({}, {'_id': 0}))
        return render_template('main.html', user = user_info, recipe_list = recipe_list)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 메인페이지
# db에서 재료 가져오기/ 키워트 클릭 시 카드출력
@app.route('/main/type', methods=['GET'])
def show_card():
    keywordData = request.args.get('type')
    menu_card = list(db.recipe.find({'type': {'$regex': keywordData}}))
    return jsonify({'menu_card': dumps(menu_card)})


# 상세페이지
#상세페이지 요소 삽입(jinja2)
@app.route('/detail')
def title():
    id_address = request.args.get('id') #url에서 파라미터값 가져오기
    recipeData = db.recipe.find_one({'_id':ObjectId(id_address)})
    # print(recipeData)
    return render_template("detail.html", recipeData=recipeData)


@app.route('/comment', methods=['POST'])
def write_comment():
    comment_receive = request.form['comment_give']
    title_give = request.form['title_give']
    print(comment_receive)
    print(title_give)
    doc = {
        'comment':comment_receive,
        'title':title_give
    }

    db.comments.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


@app.route('/comment_show', methods=['POST'])
def showcomment():
    title_give = request.form['title_give']
    print(title_give)
    comments = list(db.comments.find({'title':title_give}, {'_id': False}))
    print(comments)
    return jsonify({'comment': comments})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
