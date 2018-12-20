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

#TODO: clientID is current the Facebook APP ID, I need to replace it with some kind of unique identifier from google to determine who is logged in. Unsure how 
#supermetrics does this yet.

@app.route("/login")
def index():

    #add client if not already added
    # clientID = db.session.query(Client.clientID).filter_by(clientID=request.args.get("client_id")).scalar()
    params = request.args
    clientID = request.args.get('client_id')
    clientEMail = request.args.get('client_email')
    redirectURI = request.args.get('redirect_uri')

    if (clientID is None or redirectURI is None or clientEMail is None) :
        return "Invalid Arguments"

    client = mongodb.users.find_one({"clientEMail" : clientEMail})
    if (client is None) :
        mongodb.users.insert_one({"clientEMail": clientEMail, "redirect": redirectURI })
        return render_template("new_user.html", params = params)
    else: 
        return render_template("existing_user.html", params= params)

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
@app.route("/read/<clientEMail>", methods=["GET"])
def clientDetail(clientEMail):
    client = mongodb.users.find_one({"clientEMail": clientEMail})
    return Response(json_util.dumps(client), mimetype='application/json')

@app.route("/delete/<clientEMail>", methods=["GET"])
def clientDelete(clientEMail):
    clientID = request.args.get("client_id")
    clientEMail = request.args.get("client_email")
    redirectURI = request.args.get("redirect_uri")
    state = request.args.get("state")
    if (clientID is None or redirectURI is None or clientEMail is None or state is None) :
        return "Invalid Arguments"

    mongodb.users.delete_one({"clientEMail": clientEMail})
    return redirect("login?client_id=" + clientID + "&client_email=" + clientEMail + "&redirect_uri=" + redirectURI) + "&state=" + state

# endpoint to get client detail by id
@app.route("/complete", methods=["GET"])
def complete_redirect():
    #Grab authorization code from FB (in url string)
    clientEMail = str(request.args.get("client_email"))
    code = str(request.args.get("code"))
    print(code)
    if (code == "None" or clientEMail == "None"):
        return "Invalid Arguments"

    #Grab redirect uri
    redirectURI = mongodb.users.find_one({"clientEMail" : clientEMail})['redirect']
    redirectURI += "?code=" + code

    #Go to redirectURI with code
    # return redirectURI
    return redirect(redirectURI)

if __name__ == '__main__':
    app.run(debug=True)