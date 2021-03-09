import json
from threading import Thread
from time import sleep
import unittest

from app import app
import requests

# NOTE: Make sure you run 'pip3 install requests' in your virtualenv

# URL pointing to your local dev host
LOCAL_URL = "http://localhost:5000"

# Sample testing data
SAMPLE_POST = {"title": "Hello, World!", "link": "cornellappdev.com", "username": "appdev"}
SAMPLE_COMMENT = {"text": "First comment", "username": "appdev"}


# Request endpoint generators
def gen_posts_path(post_id=None):
    base_path = f"{LOCAL_URL}/api/posts"
    return base_path + "/" if post_id is None else f"{base_path}/{str(post_id)}/"


def gen_comments_path(post_id, comment_id=None):
    base_path = f"{LOCAL_URL}/api/posts/{str(post_id)}/comments"
    return base_path + "/" if comment_id is None else f"{base_path}/{str(comment_id)}/"


class TestRoutes(unittest.TestCase):

    # -- POSTS ---------------------------------------------

    def test_get_initial_posts(self):
        res = requests.get(gen_posts_path())
        assert res.json()["success"]

    def test_create_post(self):
        res = requests.post(gen_posts_path(), data=json.dumps(SAMPLE_POST))
        post = res.json()["data"]
        assert res.json()["success"]
        assert post["title"] == SAMPLE_POST["title"]
        assert post["link"] == SAMPLE_POST["link"]
        assert post["username"] == SAMPLE_POST["username"]
        assert post["upvotes"] == 1

        res = requests.get(gen_posts_path())
        posts = res.json()["data"]
        post = posts[-1]
        assert post["title"] == SAMPLE_POST["title"]
        assert post["link"] == SAMPLE_POST["link"]
        assert post["username"] == SAMPLE_POST["username"]
        assert post["upvotes"] == 1

    def test_delete_post(self):
        res = requests.post(gen_posts_path(), data=json.dumps(SAMPLE_POST))
        post_id = res.json()["data"]["id"]
        res = requests.delete(gen_posts_path(post_id))
        assert res.json()["success"]

    def test_post_id_increments(self):
        res = requests.post(gen_posts_path(), data=json.dumps(SAMPLE_POST))
        post_id = res.json()["data"]["id"]

        res2 = requests.post(gen_posts_path(), data=json.dumps(SAMPLE_POST))
        post_id2 = res2.json()["data"]["id"]
        assert post_id + 1 == post_id2

    def test_get_invalid_post(self):
        res = requests.get(gen_posts_path(1000))
        assert not res.json()["success"]
        assert res.json()["error"]

    def test_delete_invalid_post(self):
        res = requests.delete(gen_posts_path(1000))
        assert not res.json()["success"]
        assert res.json()["error"]

    # -- COMMENTS ------------------------------------------

    def test_post_comment(self):
        res = requests.post(gen_posts_path(), data=json.dumps(SAMPLE_POST))
        post_id = res.json()["data"]["id"]
        res = requests.post(gen_comments_path(post_id), data=json.dumps(SAMPLE_COMMENT))
        assert res.json()["success"]

        res = requests.get(gen_comments_path(post_id))
        assert res.json()["success"]
        comments = res.json()["data"]
        assert len(comments) == 1
        assert comments[0]["text"] == SAMPLE_COMMENT["text"]
        assert comments[0]["username"] == SAMPLE_COMMENT["username"]

    def test_edit_comment(self):
        res = requests.post(gen_posts_path(), data=json.dumps(SAMPLE_POST))
        post_id = res.json()["data"]["id"]
        res = requests.post(gen_comments_path(post_id), data=json.dumps(SAMPLE_COMMENT))
        comment_id = res.json()["data"]["id"]
        res = requests.post(gen_comments_path(post_id, comment_id), data=json.dumps({"text": "New text"}))
        data = res.json()
        assert data["success"]
        assert data["data"]["text"] == "New text"

    def test_get_comments_invalid_post(self):
        res = requests.get(gen_comments_path(1000))
        assert not res.json()["success"]
        assert res.json()["error"]

    def test_post_invalid_comment(self):
        res = requests.post(gen_comments_path(1000), data=json.dumps(SAMPLE_COMMENT))
        assert not res.json()["success"]
        assert res.json()["error"]


def run_tests():
    sleep(1.5)
    unittest.main()


if __name__ == "__main__":
    thread = Thread(target=run_tests)
    thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
