from flask import Flask, request, jsonify, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Client(db.Model):
    clientID = db.Column(db.Integer, primary_key=True, unique=True)
    redirect = db.Column(db.String(150), unique=True)

    def __init__(self, clientID, redirect):
        self.clientID = clientID
        self.redirect = redirect


class ClientSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('clientID','redirect')


client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)


@app.route("/login/")
def index():
    params = request.args
    #add client if not already added
    if (db.session.query(Client.clientID).filter_by(clientID=request.args.get("client_id")).scalar() is None) :
        new_client = Client(request.args.get('client_id'), request.args.get('redirect_uri'))
        db.session.add(new_client)
        db.session.commit()
    #send to index page
    return render_template("index.html", params = params)

@app.route("/read", methods=["GET"])
def read():
    all_clients = Client.query.all()
    result = clients_schema.dump(all_clients)
    return jsonify(result.data)

# endpoint to get client detail by id
@app.route("/read/<clientID>", methods=["GET"])
def clientdetail(clientID):
    client = Client.query.get(clientID)
    #redirect_delete(clientID)     
    return client_schema.jsonify(client)

# endpoint to get client detail by id
@app.route("/complete/<clientID>", methods=["GET"])
def complete_redirect(clientID):
    #Grab authorization code from FB (in url string)
    code = str(request.args.get("code"))
    #Grab redirect uri
    redirectURI = Client.query.filter_by(clientID=clientID).first().redirect
    redirectURI += "?code=" + code

    #Go to redirectURI with code
    return redirect(redirectURI)

if __name__ == '__main__':
    app.run(debug=True)