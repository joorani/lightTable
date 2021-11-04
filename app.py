import requests

from flask import Flask, render_template, jsonify, request, redirect, url_for
from bson.json_util import loads, dumps, ObjectId
import jwt, datetime, hashlib
from datetime import datetime, timedelta

from pymongo import MongoClient

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
@app.route('/detail')
def login():
    msg = request.args.get("msg")
    return render_template('detail.html', msg=msg)

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


# //////////////////////////댓글을 db에 저장하기
@app.route('/detail/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        userid = (payload["id"])
        user_info = db.users.find_one({"userid": userid}, {"_id": 0})
        print(user_info)
        comment_receive = request.form["comment_give"]
        print(comment_receive)
        date_receive = request.form["date_give"]
        print(type(date_receive))
        doc = {
            "userid": user_info["userid"],
            "comment": comment_receive,
            "date": date_receive
        }
        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("show_menu"))

# 댓글 클라이언트로 보내주기 / //////////////////////
@app.route("/detail/get_posts", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.posts.find({}).sort("date", -1).limit(100))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "userid": payload['id']}))
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("show_menu"))

# /////////////////좋아요 받아서 저장하기
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"userid": payload["id"]})
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
        return redirect(url_for("show_menu"))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
