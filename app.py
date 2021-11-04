import requests

from flask import Flask, render_template, jsonify, request, redirect, url_for
from bson.json_util import loads, dumps
import jwt, datetime, hashlib
from datetime import datetime, timedelta

from pymongo import MongoClient

app = Flask(__name__)
# git에 올라가면 안되는 내용!
#app.config["TEMPLATES_AUTO_RELOAD"] = True
#app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

#SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.projectdb
collection = db.collection



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
def detail1(keyword):
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

# //////////////////////////댓글을 db에 저장하기
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        print(type(date_receive))
        doc = {
            "username": user_info["username"],
            "comment": comment_receive,
            "date": date_receive
        }
        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 댓글 클라이언트로 보내주기 / //////////////////////
@app.route("/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.posts.find({}).sort("date", -1).limit(100))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# /////////////////좋아요 받아서 저장하기
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
