import os
from flask import Flask, jsonify, request, render_template
from flask import Response
import requests
import time, docker, subprocess
import flask
import threading


APP_ROUTE = os.path.dirname(os.path.abspath(__file__))

app = flask.Flask(__name__)

functions = flask.Flask('functions')

global change, curr
global count
global curr_cont_count
global start 
global active_ports 


#list to keep track of port numbers that are allocating to containers
active_ports = []
#to check if the request is the first request or not
start = 0
#to keep track of number of request 
count = 0 
#to keep track of number of containers running
curr_cont_count = 1
#to denote orchestrator to send request to first container
change = 0 
#container number to which current request should go
curr = 0

@functions.route('/', defaults={'path': ''})
@functions.route('/<path:path>', methods=['GET', 'POST', 'DELETE'])
def forward_request(path):
    global start, count, change, curr

    #if call is made to "/", to check if orcheastrator is running or not
    if path == '':
        return jsonify({}), 200
    
    #to check if the request send by load labalncer is first request or not
    if start == 0:
        try:
            #remove all stopped containers, just to make sure that it wont give error while creating new containers of same name
            run_cmd = "sudo docker container rm $(sudo docker ps -aq)"
            #to run command in bash shell
            subprocess.call(run_cmd, shell=True)
        except:
            pass
        #append 8000 to active ports, as first container(acts0) is running on localhost 8000 
        active_ports.append('8000')
        #create a thread for the function which checks if containers are runnning properly or not
        health_check_thread = threading.Thread(target=health_check)
        #create a thread for the function which checks number of requests that were made in past 2mins
        req_check_thread    = threading.Thread(target=req_check)
        #start both the threads
        health_check_thread.start()
        req_check_thread.start()
        #make start as 1 so that threads wont be created when other requests come
        start = 1

    #start sending request from first container
    if change == 0:
        change = 1
        curr = 0
    else:
        #to send request in round robin manner
        curr = curr % len(active_ports)

    #url to which the request should go
    url = "http://"+ip_addr+":" + str(active_ports[curr]) +"/"+path
    #increase the request count
    count += 1
    
    #send request to the respective continer based on the method  
    if request.method == "POST":
        r = requests.post(url = url, json = request.json)
        
    if request.method == "GET":  
        r = requests.get(url = url)
        
    if request.method == "DELETE":
        r = requests.delete(url = url )
        
    #to make next request go to next container
    curr += 1
    
    #return the respose and repsonse code got by the container
    return Response(r), r.status_code
    
def stop_container(name):
    global active_ports, change
    #start sending request from first container
    change = 0
    #remove port number from active port list
    active_ports.pop()

    #run shell command to stop and remove container 
    docker_run = "sudo docker stop " + name
    subprocess.call(docker_run, shell=True)
    docker_run = "sudo docker rm "+ name
    subprocess.call(docker_run, shell=True)
    
    return 

def start_container(name, port):
    global active_ports, change
    #run shell command to create and link volume to the container 
    docker_run = "sudo docker run --name "+ name + " -d  -v /home/ubuntu/project/database/db.json:/app/db.json -p "+ str(port) +":80 acts" 
    subprocess.call(docker_run, shell=True)
    #add port number to active port list
    active_ports.append(str(port))
    #start sending requests from first container
    change = 0
    return 

def health_check():
    while True:
        client = docker.from_env()
        #get all the running containers
        for container in client.containers():
            #get ip address of instaance and port number of the container
            ip_addr = container['Ports'][0]['IP'] 
            port = container['Ports'][0]['PublicPort']
            #send health check request to container
            url = "http://"+ip_addr+":" + str(port) +"/api/v1/_health"
            r = requests.get(url = url)

            #if container is down, stop that container and start new container with same name on same port
            if r.status_code == 500:
                name = container['Names'][0].strip("/")
                stop_container(name)
                start_container(name, port)
        #wait for a second
        time.sleep(1)

def req_check():
    while True:
        global count, change
        global curr_cont_count

        #get number of containers that should be running based on number of requests got in past 2mins
        no_of_cont = (count // 20) + 1
        
        #make request count as 0
        count = 0

        client = docker.from_env()
        #if more number of containers are needed, create new containers
        if no_of_cont > curr_cont_count:
            while no_of_cont - curr_cont_count:
                cont_no = len(client.containers())
                name = "acts" + str(cont_no)
                port = "800"  + str(cont_no)
                start_container(name, port)
                curr_cont_count += 1
        #if more number of containers are running, stop recently created containers
        elif no_of_cont < curr_cont_count:
            while curr_cont_count - no_of_cont:
                cont_no = len(client.containers())
                name = "acts" + str(cont_no-1)
                stop_container(name)
                curr_cont_count -= 1
        #wait of two minutes
        time.sleep(2*60)


if __name__ == "__main__":
    ip_addr ="127.0.0.1"
    functions.run(host = '0.0.0.0',port=80, debug = True)

