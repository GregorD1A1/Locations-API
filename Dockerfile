# base image from dockerhub
FROM python:3.8

# set docker image directory
WORKDIR /api_docker

# copy everything in that directory
COPY . .

# install dependencies
RUN pip install -r requirements.txt

# entry command to start container
CMD [ "python", "./API.py" ]
