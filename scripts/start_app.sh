#!/bin/bash

# Switch to ubuntu user

sudo su ubuntu


# JOB RESUME SCANNER

# Change to job-resume-scanner directory

cd /home/ubuntu/job2/job-resume/app

# Pull new code changes from github repo

git pull

# Build job-resumer-scanner app

sudo docker build -t job-resume-scanner .

# Retrieve secret from AWS Secrets Manager

SECRET=$(aws secretsmanager get-secret-value --secret-id "OPENAI_API_KEY" --region "us-east-1" --query 'SecretString' --output text| jq .OPENAI_API_KEY | tr -d '"')

# Start job-resume-scanner app

sudo docker run --env OPENAI_API_KEY=$SECRET -d -p 80:80 job-resume-scanner


# RESUME OPTIMIZER 

# Change to resume-optimizer directory

cd /home/ubuntu/resume-optimizer/app

# Pull new code changes from github repo

git pull

# Build resume-optimizer app

sudo docker build -t resume-optimizer .

# Retrieve secret from AWS Secrets Manager

SECRET=$(aws secretsmanager get-secret-value --secret-id "OPENAI_API_KEY" --region "us-east-1" --query 'SecretString' --output text| jq .OPENAI_API_KEY | tr -d '"')

# Start resume-optimizer app

sudo docker run --env OPENAI_API_KEY=$SECRET -d -p 5000:5000 resume-optimizer


# RESUME BUILDER 

# Change to resume-builder directory

cd /home/ubuntu/resume-builder/app

# Pull new code changes from github repo

git pull

# Build resume-builder app

sudo docker build -t resume-builder .

# Retrieve secret from AWS Secrets Manager

SECRET=$(aws secretsmanager get-secret-value --secret-id "OPENAI_API_KEY" --region "us-east-1" --query 'SecretString' --output text| jq .OPENAI_API_KEY | tr -d '"')

# Start resume-builder app

sudo docker run --env OPENAI_API_KEY=$SECRET -d -p 75:75 resume-builder

# TESTING Pipeline updates 2:55 PM WAT 3/5/24