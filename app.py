import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

posts = {
    0:{
        "id": 0,
        "upvotes": 1,
        "title": "My cat is the cutest!",
        "link": "https://i.imgur.com/jseZqNK.jpg",
        "username": "alicia98"     
    },
    1:{
        "id": 1,
        "upvotes": 3,
        "title": "Cat loaf",
        "link": "https://i.imgur.com/TJ46wX4.jpg",
        "username": "alicia99"
    }
}
post_number = 2

comments = {
    0: {
        0:{
            "id": 0,
            "upvotes": 1,
            "text": "Nice tail",
            "username": "realpaskal"
        }
    },
    1:{

        }
}

comment_number = 1

#get all posts
@app.route("/")
@app.route("/api/posts/")
def get_posts():
    res = {
        "success": True,
        "data": list(posts.values())
    }
    return json.dumps(res), 200

#create posts
@app.route("/api/posts/", methods=["POST"])
def create_post():
    global post_number
    body = json.loads(request.data)
    title = body.get("title")
    link = body.get("link")
    username = body.get("username")
    if not title or not link or not username:
        return json.dumps({"success": False, "error": "You did not enter the data correctly, post cannot be created"}), 404
    post = {"id": post_number, "upvotes": 1, "title": title, "link": link, "username": username}
    posts[post_number] = post
    comments[post_number] = {}
    post_number += 1
    return json.dumps({"success": True, "data": post}), 201

#get post
@app.route("/api/posts/<int:post_id>/")
def get_post(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"success": False, "error": "There is no such post"}), 404
    return json.dumps({"success": True, "data": post}), 201

#delete a post
@app.route("/api/posts/<int:post_id>/", methods=["DELETE"])
def delete_post(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"success": False, "error": "Post does not exist"}), 404
    del posts[post_id]
    del comments[post_id]
    return json.dumps({"success": True, "data": post}), 200

#get comments for a specific post
@app.route("/api/posts/<int:post_id>/comments/")
def get_comments(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"success": False, "error": "There is no post"}), 404
    data = comments.get(post_id)
    if not data:
        return json.dumps({"success": False, "error": "There is no comment"}), 404
    return json.dumps({"success": True, "data": list(data.values())}), 201

#post comment for specific post
@app.route("/api/posts/<int:post_id>/comments/", methods=["POST"])
def post_comments(post_id):
    global comment_number
    post = posts.get(post_id)
    if not post:
        return json.dumps({"success": False, "error": "The post does not exist"}), 404
    body = json.loads(request.data)
    text = body.get("text")
    username = body.get("username")
    if not text or not username:
        return json.dumps({"success": False, "error": "You did not enter the data correctly"}), 404
    comment = {"id": comment_number, "upvotes": 1, "text": text, "username": username}
    comments[post_id][comment_number] = comment
    comment_number += 1
    return json.dumps({"success": True, "data": comment}), 201

#edit comment for a specific post
@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>/", methods=["POST"])
def edit_comment(post_id, comment_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"success": False, "error": "The post does not exist"}), 404
    comment = comments[post_id].get(comment_id)
    if not comment:
        return json.dumps({"success": False, "error": "There is no comment"}), 404
    body = json.loads(request.data)
    text = body.get("text")
    if not text:
        return json.dumps({"success": False, "error": "You did not enter the data correctly"}), 404
    comment["text"] = text
    return json.dumps({"success": True, "data": comment}), 200




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
