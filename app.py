import os
from flask import Flask, request, jsonify, render_template, redirect, Response
from flask_pymongo import PyMongo
import pymongo
from pymongo import MongoClient
from bson import json_util
from bson.json_util import dumps, CANONICAL_JSON_OPTIONS

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

client = MongoClient('localhost', 27017)
mongodb = client.authDB

@app.route("/login")
def index():

    #add client if not already added
    # clientID = db.session.query(Client.clientID).filter_by(clientID=request.args.get("client_id")).scalar()
    params = request.args
    clientID = request.args.get('client_id')
    redirectURI = request.args.get('redirect_uri')

    if (clientID is None or redirectURI is None) :
        return "Invalid Arguments"

    client = mongodb.users.find_one({"clientID" : clientID})
    if (client is None) :
        mongodb.users.insert_one({"clientID": clientID, "redirect": redirectURI })
        return render_template("new_user.html", params = params)
    else: 
        return render_template("existing_user.html")

@app.route("/read", methods=["GET"])
def read():
    #We define a python list 'result' to collect results from mongoDB
    #Note: a python 'list' is defined by [] while a python 'dictonary' is defined by {}, these are two different things
    result = []
    #The mongoDB find command returns a 'cursor' which can be iterated through to get data
    data = mongodb.users.find({})
    #Iterate through cursor
    for doc in data:
        result.append(doc)
    # print(result) for debug
    #json_util works with BSON objects, BSON is the JSON-like format that mongoDB uses
    #the mimetype parameter lets it output it in a nice, human readable format to the Flask page
    return Response(json_util.dumps(result), mimetype='application/json')

# endpoint to get client detail by id
@app.route("/read/<clientID>", methods=["GET"])
def clientdetail(clientID):
    print(clientID)
    client = mongodb.users.find_one({"clientID": clientID})
    print(client)
    return Response(json_util.dumps(client), mimetype='application/json')

# endpoint to get client detail by id
@app.route("/complete/<clientID>", methods=["GET"])
def complete_redirect(clientID):
    #Grab authorization code from FB (in url string)
    code = str(request.args.get("code"))
    print(code)
    if (code == "None"):
        return "Invalid Arguments"

    #Grab redirect uri
    redirectURI = mongodb.users.find_one({"clientID" : clientID})['redirect']
    redirectURI += "?code=" + code

    #Go to redirectURI with code
    return redirectURI
    # return redirect(redirectURI)

if __name__ == '__main__':
    app.run(debug=True)