#!/bin/bash

# Switch to ubuntu user

sudo su ubuntu

# Change to /home/ubuntu directory

cd /home/ubuntu

# Stop all containers

sudo docker stop $(sudo docker ps -a -q)

# Remove all the containers

sudo docker rm $(sudo docker ps -a -q) # or: sudo docker container prune

# Remove job-resume-scanner image

sudo docker rmi job-resume-scanner --force

# Remove resume-optimizer image

sudo docker rmi resume-optimizer --force

# Remove resume-builder image

sudo docker rmi resume-builder --force