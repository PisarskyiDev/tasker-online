![Logo of the project](static/assets/img/logo-6-1.png)

# Name of the project
> It Company Task Manager



## Check it out!


Live version: [It company task manager](https://parra-bellum.space)

## Developing

First step is a download from git this project, to download paste this commands:

```shell
git clone https://github.com/Soobig666/it-company-task-manager.git

cd it-company-task-manager

sudo apt install python3-venv

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver   # starts Django server
```

### Deploying / Publishing

For deploy with project, when you finish edit, or you want to deploy to test it, \
you can use this steps:

1. First step, you need to install [Docker](https://docker.com)

2. Second step is set in .env file all variables what do you need to deploy

3. Third step is build Docker image:
```shell
docker build -t 'you_image_name' . 
```
4. Fours step is up Docker image with gunicorn & nginx:
```shell
docoker compose up
```


## Features

What's all the bells and whistles this project can perform?
* Create tasks, delete, update tasks
* Set deadlines and follow up on them
* Assign different performers to perform tasks that are typical for their skill



## Links

- Repository: https://github.com/Soobig666/it-company-task-manager/
- Project homepage: https://github.com/Soobig666/it-company-task-manager/blob/main/templates/catalog/index.html
