from gevent import monkey
monkey.patch_all()
import sys
import json
from gevent.pywsgi import WSGIServer
from flask import send_file, Flask, request
from image_bb_extractor import ImageBBExtractor
from consts import *



app = Flask("Mock GIFS")

extractor = ImageBBExtractor(url="https://shekkerk.imgbb.com/")

@app.route('/v1/oauth/token', methods=['OPTIONS'])
def oauth():
    return json.dumps({"token_type": "bearer", "scope": "", "expires_in": sys.maxsize, "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NDgxNDE3NjgsImlzcyI6IjJfS3RIX1c1Iiwicm9sZXMiOlsiQ29udGVudF9SZWFkZXIiXX0.HZhwK9ajbxqU7pwGUxrzqSFVcQakb4w4S0NL2aqxHOc"})


def compose_response(response_content):
    response = app.response_class(
        response=json.dumps(response_content),
        status=200,
        mimetype='application/json'
    )
    response.headers['Access-Control-Allow-Headers'] = "Authorization,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type"
    response.headers['Access-Control-Allow-Methods'] = "GET,OPTIONS,POST,PUT,PATCH,DELETE"
    response.headers['Access-Control-Allow-Origin'] = "*"
    response.headers['Connection'] = "keep-alive"
    response.headers['X-Cache-SRCache'] = "HIT"
    return response


@app.route('/v1/reactions/populated', methods=['OPTIONS', 'GET'])
def categories():
    return compose_response(json.load(open("categories.json")))


@app.route('/v1/gfycats/search', methods=['OPTIONS', 'GET'])
def search():
    return compose_response(extractor.images_metadata)


http_server = WSGIServer(
    (HOST, PORT), app, keyfile='../../certs/gfycat.key', certfile='../../certs/gfycat.crt')

http_server.serve_forever()
