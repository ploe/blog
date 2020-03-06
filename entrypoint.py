"""Entrypoint for Flask server"""
import os

from flask import Flask, jsonify

import articles

APP = Flask(__name__)

PATH = os.path.join('./examples/unittest/articles')
API = articles.Articles(PATH)

@APP.route("/api/articles", methods=['GET'])
def get_articles_collection():
    """Return a JSON array of Article slugs"""
    return jsonify(API.get_collection())


@APP.route("/api/articles/<basename>", methods=['GET'])
def get_articles_item(basename):
    """Return JSON object of item in basename"""
    return jsonify(API.get_item(basename))
