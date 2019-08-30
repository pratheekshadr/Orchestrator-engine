#program to clear the data stored in file
import json


data = {}
data['user_details'] = []
data['req_count'] = 0

with open('db.json','w') as f:
    json.dump(data, f)

with open('db.json') as f:
    d = json.load(f)
    print(d)
 

