# AI Chat Bot

🔥Authors: [@VictorS67](https://github.com/VictorS67), [@JunmingZhang](https://github.com/JunmingZhang) and me

## 1. Introduction

This application is an exploratory web-app for users who want to have an instant chat with a chatbot to help them with their mood and mental health. Instead of using human-written scripts, the chatbot is created based on the OpenAI’s GPT-3 model, which is a large language model for various Natural Language Processing tasks such as understanding human’s words, generating appropriate texts, etcs. One benefit of chatting with this application is that users can have multiple conversations without worrying about changing topics among conversations. The user data is stored in AWS s3 and Dynamo DB.

## 2. Usage


https://user-images.githubusercontent.com/23529452/209798639-dca70b68-3df9-4a8f-9fb9-4351a968abef.mp4


## 3. Quick Start

### 3.1 Configure 

```shell
.
|-- app/
|    |  
|    |-- config/
|    |    |-- openai_config_template.yaml
|    |    └── aws_config_template.yaml
|    └──...
└── ...
```
#### 3.1.2 openai configuration

- 1. Rename  `openai_config_template.yaml` with `opneai_config.yaml`
- 2. Sign up an [OpenAI](https://openai.com/) account if you don't have one. Fill in the OpenAI api key in `opneai_config.yaml`.

#### 3.1.3 aws configuration

- 1. Rename  `aws_config_template.yaml` with `aws_config.yaml`
- 2. Sign up an [AWS](https://aws.amazon.com/) account if you don't have one. Fill in the fields `AK`, `SK`, `region`, `bucket_name` following the instructions in the `aws_config.yaml` 

⚡️Note: `opneai_config.yaml` and `aws_config.yaml` are in `.gitignore` so that you don't need to worry about leaking credentials

### 3.2 Run 

#### Running in the container

- 1. Install [docker engine](https://docs.docker.com/engine/install/)
- 2. Build the image and deploy the container on docker. Further, you could deploy it anywhere, e.g. container service of the cloud providers
```shell
docker build . -t chatbot              # build the image with the tag chatbot
docker run -p 5000:5000 chatbot        # run the image in the container. Port 5000 inside container maps with port 5000 outside container
```

#### Running locally or on VMs

```shell
pip3 install -r requirements.txt       # or install with other tools except 'pip3'
python run.py
```

### 3.3 Start Chatting with AI 

Visit `http://<your ip>:5000/` in your browser. ( e.g. `http://localhost:5000/` if you run App or container in your computer. )
