#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 29 12:29:07 2018

@author: Sanjana Kapoor
"""

from flask import Flask
from flask import render_template
from pymongo import MongoClient
from similarDoc import SimilarDoc
import json
from bson import json_util
from bson.json_util import dumps
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'DocTopicVectors'
COLLECTION_NAME = 'tVectors'

connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collection = connection[DBS_NAME][COLLECTION_NAME]

second_connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
second_collection = second_connection['EnronEmailData']['emails']

nearestNeighbors = SimilarDoc()


@app.route("/data")
def index():
    return render_template("index.html")


@app.route("/similar/<single_id>")
def findSimilarVectors(single_id):
    """
    Return a list of _id's that are most similar to the original id
    """
    topic_result, distances = nearestNeighbors.similar_from_id(single_id, 5)
    topic_result = json.dumps(topic_result, default = json_util.default)
    print(topic_result)
    return topic_result


@app.route("/DocTopicVectors/tVectors/<single_id>")
def docTopicVectors_tVectors(single_id):
    """
    Return the row from the DocumentTopicVector database that corresponds to the given id
    """
    topic_result = collection.find_one({'_id': single_id})
    topic_result = json.dumps(topic_result, default = json_util.default)
    connection.close()
    return topic_result
    

@app.route("/EnronEmailData/emails/<single_id>")
def secondEnronEmailData_emails(single_id):
    """
    Return the row from the SecondEnronEmailData database that corresponds to the given id
    """
    email_result = second_collection.find_one({'_id': single_id})
    print(single_id)
    print(email_result)
    email_result = json.dumps(email_result, default = json_util.default)
#    second_connection.close()
    print(email_result)
    return email_result

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)