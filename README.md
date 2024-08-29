# job-resume


1. docker build -t job-resume-scanner .
2. docker run --env OPENAI_API_KEY=fakeopenaikey -d -p 80:80 job-resume-scanner


## Endpoints

1. /generate
   1. Field - resume 
2. /analyze 
   1. Field - resume (file) and career_name


## Swagger Endpoint
1. http://127.0.0.1:80/docs