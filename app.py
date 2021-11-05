
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
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_ FOLDER'] = "./static/profile_pics"

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
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24 * 3)  # 로그인 24시간 유지
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

# 로그인 성공시 메인페이지로 이동.
@app.route('/main')
def show_menu():
    token_receive = request.cookies.get('mytoken')
    print(token_receive)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = (payload["id"])
        user_info = db.users.find_one({"userid": userid})
        recipe_list = list(db.recipe.find({}))
        return render_template('main.html', user = user_info, recipe_list = recipe_list)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
# 메인 페이지 재료 클릭시 재료별 카드출력
@app.route('/main/type', methods=['GET'])
def show_card():
    keyword = request.args.get('type')
    menu_card = list(db.recipe.find({'type': {'$regex': keyword}}))
    return jsonify({'menu_card': dumps(menu_card)})

@app.route('/detail')
def title():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = (payload["id"])

        id_address = request.args.get('id') #url에서 파라미터값 가져오기
        recipeData = db.recipe.find_one({'_id':ObjectId(id_address)})
        user_info = db.users.find_one({'userid': userid})
        return render_template("detail.html", user = user_info, recipe=recipeData)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# //////////////////////////댓글/////////////////////////////
@app.route('/posting', methods=['POST'])
def posting():
    comment_receive = request.form["comment_give"]
    print(comment_receive, "댓글")
    date_receive = request.form["date_give"]
    date_receive = repr(date_receive)
    print(date_receive, "날짜")
    title_give = request.form['title_give']
    print(title_give, "타이틀")
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = (payload["id"])
        user_info = db.users.find_one({"userid": userid})
        print(user_info,"유저인포")
        doc = {
            'user_name':user_info['username'],
            "comment": comment_receive,
            "date": date_receive,
            'title': title_give
        }
        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("show_menu"))

# 댓글 클라이언트로 보내주기 / //////////////////////
@app.route("/get_posts", methods=['POST'])
def get_posts():
    title_give = request.form['title_give']
    print(title_give+"두번째 타이틀")
    posts = list(db.posts.find({'title':title_give}, {'_id': False}))
    print(posts,"포스트리스트")

    return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
