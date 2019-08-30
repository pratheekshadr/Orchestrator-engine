import os
from flask import Flask, jsonify, request, render_template
from flask import Response
import shutil, time, requests, hashlib, re, json, base64, datetime

app = Flask(__name__)

APP_ROUTE = os.path.dirname(os.path.abspath(__file__))


@app.route("/api/v1/_count", methods = ["GET","POST","DELETE"])
def _count():

    if request.method == "GET":
        with open('db.json') as f:
            db = json.load(f)

            count = db['req_count']

            if count == 0:
                return jsonify([0]), 200 
            else:
                return jsonify([count]), 200
    elif request.method == "POST":
        return jsonify([]), 405
    elif request.method == "DELETE":
        with open('db.json') as f:
            db = json.load(f)
            db['req_count'] = 0

        with open('db.json','w') as f:
            json.dump(db, f)
            
        return jsonify({}), 200
    
    else:
        return jsonify({}), 405


@app.route("/api/v1/users", methods = ["GET", "POST", "DELETE"])
@app.route("/api/v1/users/<string:UserName>", methods = ["POST", "DELETE", "GET"])
def users(UserName=None):
    with open('db.json') as f:
        db = json.load(f)
        db['req_count'] += 1

    with open('db.json','w') as f:
        json.dump(db, f)
        
    db = {}
    with open('db.json') as f:
        db = json.load(f)

    #get, post, delete for second url
    if UserName:

        if request.method == "POST":
            return jsonify({}), 405
        if request.method == "GET":
            return jsonify({}), 405

        #to remove username
        if request.method == "DELETE":
            found = 0
            try:
                for i_name in range(len(db['user_details'])):
                    if db['user_details'][i_name]['username'] == UserName:
                        found = 1
                        del (db['user_details'][i_name])
                        break
                if found:
                    with open('db.json','w') as f:
                        json.dump(db, f)
                    #success
                    return jsonify({}), 200
                else:
                    #username not found
                    return jsonify({}), 400
            except:
                return jsonify({}), 400

        
        else:
            return jsonify({}), 405
            

    #get post delete for first url
    #to add new user
    elif request.method == "POST":
        try:
            u_name = request.json['username']
            pwd = request.json['password']
            
            SHA_1 = re.compile(r"[0-9a-f]{40}")
            if SHA_1.search(pwd):
                
                not_found = 1
                for i_name in range(len(db['user_details'])):
                    if db['user_details'][i_name]['username'] == u_name:
                        not_found = 0
                        #name already exisits
                        return jsonify({}), 400
                        
                if (not_found):
                    d = {'username':u_name, 'password': pwd}
                    db['user_details'].append(d)
                    
                    with open('db.json','w') as f:
                        json.dump(db, f)
                #success
                return jsonify({}), 201
            else:
                #key not on format
                return jsonify({}), 400
        except:
            return jsonify({}), 400
            


    #list all users
    elif request.method == 'GET':
        l =[]
        for i in range(len(db['user_details'])):
            l.append(db['user_details'][i]['username'])

        if len(l)==0:
            return jsonify([]), 204
        return jsonify(l), 200
    
    elif request.method =="DELETE":
        return jsonify({}), 405
    else:
        return jsonify({}), 405

if __name__ == "__main__":
    app.run(host = '0.0.0.0',port=80, debug = True)

