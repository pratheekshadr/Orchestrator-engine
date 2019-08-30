FROM alpine:3.7
MAINTAINER Pratheeksha DR <pratheeksha987@gmail.com>

# to install packages
RUN apk add --no-cache bash git nginx uwsgi uwsgi-python py3-pip \
	&& pip3 install --upgrade pip \
	&& pip3 install flask \
    && pip3 install simplejson \
    && pip3 install requests

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV TEAM_ID=CC_259_269_280_730 


# Run app.py when the container launches
CMD ["python3", "run_json.py"]
CMD ["python3", "app.py"]

