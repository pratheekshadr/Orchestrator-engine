import json


data = {}
data['image_details'] = []
data['cat_details'] = []
data['image_path'] = []

data['image_details'] = []
data['req_count'] = 0
with open('db.json','w') as f:
    json.dump(data, f)

with open('db.json') as f:
    d = json.load(f)
    print(d)
 
import os
import shutil  
APP_ROUTE = os.path.dirname(os.path.abspath(__file__))
 
try:
	target = os.path.join(APP_ROUTE, 'images/')
	shutil.rmtree(target)
    	
except:
	print("done")

