# Orchestrator-engine

The project is focused on building a container orchestrator that can perform load balancing, fault tolerance, and auto-scaling.
This project is implemented as microservices on the AWS EC2 instances.

There are two EC2 instances, Users and Acts
The microservices(instances or docker containers) will talk to each other via their respective REST interfaces.
Files are being used as backend database.

The following functionalities are implemted using REST APIs:
	1. Add and delete User
	2. Add and delete Category
	3. List Categories
	4. List number of acts under a category
	5. Upload and delete an act
	6. Upvote an act
 
 Custom container orchestrator engine will:
   1. Be able to start and stop Acts containers programmatically, and allocate ports for them on localhost. 
   2. Load balance all incoming HTTP requests (to the Acts EC2 instance) equally between all running Acts containers in a round-robin fashion.
   3. Monitor the health of each container through a health check API(Fault Tolerance)
      If a container is found to be unhealthy, stop the container and start a new one to replace it(using the same Acts docker image). 
      The replacement container must listen on the same port that the unhealthy container was listening on.
   4. Increase the number of Acts containers if the network load increases above a certain threshold(AUTO SCALING).
       At every 2 minute interval, depending on how many requests were received, the orchestrator must increase or decrease the number of Acts containers:
        a. If the number of requests is less than 20, then only 1 Acts container must be running.
        b. If the number is >= 20 and < 40, then 2 Acts containers must be running.
        c. If the number is >= 40 and < 60, then 3 Acts containers must be running.
        d. and so on...
            
The orchestrator engine will run inside the Acts EC2 instance, listen on port 80 of the public IP, and load balance all HTTP incoming requests equally to every Acts container.
When first request comes to the orchestrator, it creates and starts two background threads,
  1. Health check thread : It makes call to all active container for every 1 sec to check if they are healthy or not. 
                           If not, it stops the container and starts another container on same port.
  2. Request count thread : It keeps track of number of requests made in past 2mins.

Forward request function : It takes all incoming requests from application load balancer and forwards to the container in round robin manner.

All acts container share same database(json file) which is connected to acts instance. 
Even after stopping the containers, data will be persistent.
