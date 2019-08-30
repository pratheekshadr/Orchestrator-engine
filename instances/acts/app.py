import os
from flask import Flask, jsonify, request, render_template
from flask import Response
import shutil, time, requests, hashlib, re, json, base64, datetime
import sys

app = Flask(__name__)

APP_ROUTE = os.path.dirname(os.path.abspath(__file__))
crash = 0
req_count = 0


@app.route("/api/v1/_health", methods = ["GET","POST","DELETE"])
def _health():
    
    global crash
    if crash==1:
        return Response(status = 500)

    if request.method == "GET":
        
        if crash==1:
            return Response(status = 500)
        else:
            try:
                with open('db.json', 'r') as f:
                    file_content = f.read()
                    return Response(status = 200)
                if not file_content:
                    #print("no data in file ")
                    return Response(status = 200)
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
                print(500)
                return Response(status = 500)
            except: #handle other exceptions such as attribute errors
                #print("Unexpected error:", sys.exc_info()[0])
                return Response(status = 500)
    else:
        return Response(status = 405)


@app.route("/api/v1/_crash", methods = ["GET","POST","DELETE"])
def _crash(): 
    global crash
    crash=1 
    return Response(status = 200)


@app.route("/api/v1/_count", methods = ["GET","POST","DELETE"])
def _count():
    global crash
    if crash==1:
        return jsonify({}), 500
    
    global req_count
    if request.method == "GET":

           
        count = req_count
        if count == 0:
            return jsonify([0]), 200 
        else:
            return jsonify([count]), 200

    elif request.method == "POST":
        return jsonify([]), 405
    elif request.method == "DELETE":
        req_count = 0
        return jsonify({}), 200
    else:
        return jsonify({}), 405


@app.route("/api/v1/count", methods = ["GET","POST","DELETE"] )
def count():
    global crash
    if crash==1:
        return jsonify({}), 500

    global req_count
    req_count += 1
    with open('db.json') as f:
        db = json.load(f)
        db['req_count'] += 1

    with open('db.json','w') as f:
        json.dump(db, f)

    if request.method == "GET":


        with open('db.json') as f:
            db = json.load(f)
            
            count = 0 
            for i in range(len(db['cat_details'])):
                count += db['cat_details'][i]['count']
            
            return jsonify([count]), 200
    elif request.method == "POST":
        return jsonify([]), 405

    elif request.method == "DELETE":
        return jsonify([]), 405


@app.route("/api/v1/categories", methods = ["GET", "POST", "DELETE"])
@app.route("/api/v1/categories/<string:categoryName>", methods = ["GET", "POST", "DELETE"])
def categories(categoryName=None):
    global crash
    if crash==1:
        return jsonify({}), 500

    global req_count
    req_count += 1
    with open('db.json') as f:
        db = json.load(f)
        db['req_count'] += 1

    with open('db.json','w') as f:
        json.dump(db, f)

    
	#to delete a category
    if categoryName:	
        
        if request.method == "POST":
            return jsonify({}), 405
        if request.method == "GET":
            return jsonify({}), 405

        cat_name = categoryName

        d={}
        with open('db.json') as f:
            db = json.load(f)

        found = 0 
        if len(db['cat_details']):
            for i in range(len(db['cat_details'])):
                name = db['cat_details'][i]['category']
                if name == cat_name:
                    found = 1   
    
        #category name not found
        if not(found):
            return jsonify({}), 400
        else:
            db = {}
            with open('db.json') as f:
                db = json.load(f)
			
            for i in range(len(db['cat_details'])):
                if db['cat_details'][i]['category'] == cat_name:
                    for actid in db['cat_details'][i]['act_ids']:

                        for j in range(len(db['image_details'])):
                            if db['image_details'][j]['actId'] == actid:
                                del db['image_details'][j]
                                break

                    del  db['cat_details'][i]
                    break

            with open('db.json','w') as f:
                json.dump(db, f)

            return jsonify({}), 200

    #list all categories
    if request.method == "GET":
        db = {}
        d={}
        with open('db.json') as f:
            db = json.load(f)
    
        if len(db['cat_details']):
            for i in range(len(db['cat_details'])):
                name = db['cat_details'][i]['category']
                d[name] = int(db['cat_details'][i]['count'])   
            return jsonify(d), 200
        else:
            #no category found
            return jsonify({}), 204

	#to add new categories
    if request.method == "POST":
        
        cat_name =[i for i in request.json][0]

        d={}
        with open('db.json') as f:
            db = json.load(f)

        found = 0 
        if len(db['cat_details']):
            for i in range(len(db['cat_details'])):
                name = db['cat_details'][i]['category']
                if name == cat_name:
                    found = 1   

        if found:
            return jsonify({}), 400
        else:
            #os.mkdir(cat_target)
            db = {}
            with open('db.json') as f:
                db = json.load(f)
            new_cat = {}
            new_cat['category'] = cat_name
            new_cat["act_ids"] = []
            new_cat["count"] = 0
            db["cat_details"].append(new_cat)
            
            with open('db.json','w') as f:
                json.dump(db, f)
            #new category added
            return jsonify({}), 201

    else:
        return jsonify({}), 405


@app.route("/api/v1/categories/<string:categoryName>/acts/size", methods = ["GET"])
def size(categoryName=None):

    global crash
    if crash==1:
        return jsonify({}), 500

    with open('db.json') as f:
        db = json.load(f)
        db['req_count'] += 1

    with open('db.json','w') as f:
        json.dump(db, f)
    
    global req_count
    req_count += 1

    #list number of acts under a category
    cat_name = categoryName
    db = {}
    with open('db.json') as f:
        db = json.load(f)
    
    for i in range(len(db['cat_details'])):
        if str(db['cat_details'][i]['category']) == str(cat_name):
            count = db['cat_details'][i]['count']
            if int(count) == 0:
                return jsonify([0]), 204
            else:
                return jsonify([count]), 200

    #cat not found    
    return jsonify([]), 400
   

@app.route("/api/v1/acts", methods = ["POST", "GET", "DELETE"])
@app.route("/api/v1/acts/<int:actId>", methods = ["POST", "GET", "DELETE"])
@app.route("/api/v1/categories/<string:categoryName>/acts", methods = ["GET", "POST"])
@app.route("/api/v1/categories/<string:categoryName>/acts?start=<string:startRange>&end=<string:endRange>", methods = ["GET", "POST"])
def acts(actId=None, categoryName = None):

    global crash

    if crash==1:
        return jsonify({}), 500

    global req_count
    req_count += 1

    with open('db.json') as f:
        db = json.load(f)
        db['req_count'] += 1

    with open('db.json','w') as f:
        json.dump(db, f)


    #listing acts
    if categoryName!= None:
    
        if request.method == "POST":
            return jsonify({}), 405
        if request.method == "DELETE":
            return jsonify({}), 405

        startRange = request.args.get('start', default = 0, type = int)
        endRange = request.args.get('end', default = 0, type = int)


        #list first 100 acts
        if ((not(startRange)) and (not(endRange))):
            
            cat_name = categoryName
            db = {}
            with open('db.json') as f:
                    db = json.load(f)

            found = 0 
            if len(db['cat_details']):
                for i in range(len(db['cat_details'])):
                    name = db['cat_details'][i]['category']
                    if name == cat_name:
                        found = 1 
            #category name not found  
            if not(found):
                return jsonify([]), 400

            d = []
            tot_count = 100
            count = 0
            for i in range(len(db['cat_details'])):
                if db['cat_details'][i]['category'] == cat_name:

                    #if category doesnt have any acts in it
                    if len(db['cat_details'][i]['act_ids']) == 0:
                        return jsonify([]), 204

                    for k in range(len(db['image_details'])-1, -1, -1):
                        if cat_name == db['image_details'][k]['category']: 
                            if count >= 100:
                                return jsonify({}), 413
                            new_d = {}
                            new_d['username']  = db['image_details'][k]['username']
                            new_d['actId']     = db['image_details'][k]['actId']
                            new_d['timestamp'] = db['image_details'][k]['timestamp']
                            new_d['categoryName']  = db['image_details'][k]['category']
                            new_d['caption']   = db['image_details'][k]['caption']
                            new_d['upvotes']   = db['image_details'][k]['upvotes']
                            new_d['imgB64'] = db['image_details'][k]['binary_format']
                            d.append(new_d)
                            count += 1
                            
            if len(d)==0:
                #is empty
                return jsonify([]), 400
            else:
                return jsonify(d), 200


        #list acts within specified range
        elif endRange and startRange:
            tot_count = endRange - startRange + 1
            cat_name = categoryName
            db = {}
            with open('db.json') as f:
                    db = json.load(f)

            found = 0 
            if len(db['cat_details']):
                for i in range(len(db['cat_details'])):
                    name = db['cat_details'][i]['category']
                    if name == cat_name:
                        found = 1 
            #category name not found  
            if not(found):
                return jsonify([]), 400
               
            d = []
            count = 1
            img_count = 0

            for i in range(len(db['cat_details'])):
                if db['cat_details'][i]['category'] == cat_name:
                    ele = db['cat_details'][i]['count']

                    if ele == 0:
                        return jsonify([]), 204
                    
                    if tot_count > 101:
                        return jsonify([]), 413
                    else:
                        if startRange + tot_count > ele:
                            return jsonify({}), 400
                        for k in range(len(db['image_details'])-1, -1, -1):
                            if cat_name == db['image_details'][k]['category']: 

                                if img_count >= tot_count:
                                    return jsonify(d), 200

                                if count > 100:
                                    return jsonify({}), 413

                                if count > (startRange-1):
                                    new_d = {}
                                    new_d['username']  = db['image_details'][k]['username']
                                    new_d['actId']     = db['image_details'][k]['actId']
                                    new_d['timestamp'] = db['image_details'][k]['timestamp']
                                    new_d['categoryName']  = db['image_details'][k]['category']
                                    new_d['caption']   = db['image_details'][k]['caption']
                                    new_d['upvotes']   = db['image_details'][k]['upvotes']
                                    new_d['imgB64'] = db['image_details'][k]['binary_format']
                                    d.append(new_d)
                                    img_count += 1
                                count += 1

                    if len(d) == 0:
                        return jsonify([]), 400
                    return jsonify(d), 200

    #adding and deleting acts
    else:
        db = {}
        with open('db.json') as f:
            db = json.load(f)

        #delete an act
        if request.method == "DELETE":
        
            if request.json != None:
                return jsonify({}), 405
            not_found = 1

            for i in range(len(db['image_details'])):
                if db['image_details'][i]['actId'] == actId:
                    not_found = 0
                    cat_name = db['image_details'][i]['category']
                    for j in range(len(db['cat_details'])):
                        if db['cat_details'][j]['category'] == cat_name:
                            db['cat_details'][j]['act_ids'].remove(actId)
                            db['cat_details'][j]['count'] -= 1
                            break
                    del db['image_details'][i]
                    break

            with open('db.json','w') as f:
                json.dump(db, f)	        
            
            if not_found:
                #actId not found
                return jsonify({}), 405
            else:
                #success
                return jsonify({}), 200

        #upload new act
        elif request.method == "POST":
            l = ['actId', 'categoryName', 'username', 'caption', 'timestamp','imgB64']
        
            try:
    
                for k in request.json:
                
                    if k not in l:
                        
                        return jsonify({}), 400
            except:
                
                return jsonify({}), 405
        
    
            act_id = request.json['actId']
            cat_name = request.json['categoryName']
            user_name = request.json['username']
            caption = request.json['caption']
            timestamp = request.json['timestamp']

            base = request.json['imgB64']
            
            check1 =  re.compile(r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
            check2 = 1
            try:
                datetime.datetime.strptime(timestamp, '%d-%m-%Y:%S-%M-%H')
            except:
                check2 = 0

            if  check2: 
                #check1 if user is present
                found1 = 0 
                
                r = requests.get(url = "http://Project-312796716.us-east-1.elb.amazonaws.com/api/v1/users")
                if user_name in r.json():
    
                    found1 = 1
                        
                #check1 if actId is present
                found2 = 0
                for i in range(len(db['image_details'])):
                    if db['image_details'][i]['actId'] == act_id:
                        found2 = 1
        
                        break

                if (found1 == 1) and (found2 == 0):
                    cat_found = 0 
                    if len(db['cat_details']):
                        for i in range(len(db['cat_details'])):

                            name = db['cat_details'][i]['category']
                        
                            if name == cat_name:
                
                                cat_found = 1 

                    #category name not found  
                    if not(cat_found):
                    
                        return jsonify([]), 400

                    new_image = {}
                    new_image['actId'] = act_id
                    new_image['category'] = cat_name
                    new_image['caption'] = caption
                    new_image['upvotes'] = 0
                    new_image['binary_format'] = base
                    new_image['username'] = user_name
                    new_image['timestamp'] = timestamp
                    db['image_details'].append(new_image)
                    db['image_details'].sort(key= lambda x: x['actId'])	
                    db['image_details'].sort(key=lambda x:time.mktime(time.strptime(x['timestamp'], '%d-%m-%Y:%S-%M-%H')))
                

                   
                    for i in range(len(db['cat_details'])):
                        if db['cat_details'][i]['category'] == cat_name:
                            db['cat_details'][i]['count'] += 1
                            db['cat_details'][i]['act_ids'].append(act_id)
                            break       
                            
                    with open('db.json','w') as f:
                        json.dump(db, f)	
                    
                    return jsonify({}), 201

                else:
                    if found1 == 0:
                        #user not found
                        return jsonify({}), 400
                       
                    if found2 == 1:
                        #change actId 
                        return jsonify({}), 400
                       
            else:

                #image not in base64 or timestamp not in proper format
                return jsonify({}), 400
                
        else:
            #get request
            return jsonify({}), 405
                

@app.route("/api/v1/acts/upvote", methods = ["POST"])	
def upvote():

    global crash
    if crash==1:
        return jsonify({}), 500

    global req_count
    req_count += 1

    with open('db.json') as f:
        db = json.load(f)
        db['req_count'] += 1

    with open('db.json','w') as f:
        json.dump(db, f)
        
    not_found = 1
    db = {}
    with open('db.json') as f:
        db = json.load(f)
    try:
        act_id =(request.json)[0]

        for i in range(len(db['image_details'])):
            if db['image_details'][i]['actId'] == act_id:
                not_found = 0
                db['image_details'][i]['upvotes'] += 1
                break

        with open('db.json','w') as f:
            json.dump(db, f)
        if not_found:
            #act id not found
            return jsonify({}), 400
        else:
            #upvoted
            return jsonify({}), 200
            
    except:
        return jsonify({}), 400



             
if __name__ == "__main__":
    app.run(host = '0.0.0.0',port=80, debug = True)

