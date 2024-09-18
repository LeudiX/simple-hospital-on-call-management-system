# Common commands for  set up a base project in django

## Create virtual env

py -m venv **venv-name**

## Activate your venv
source myvenv/bin/activate

##Install Django
pip install django

## Install requirements.txt

pip install -r requirements.txt

## Create requirements. In case you want

pip freeze > **filename-ext**

## Update a dependency

pip install --upgrade **dependency-name**

## In case you work with environ library for hide your enviroment variables :

*Important:* The convention must be 
**
SECRET_KEY=my_secret_key_value
DEBUG=True
**
Also your .env file must be located in the same folder of settings.py

## Migrations Issues

-In case you're facing troubles(or make a mistake with migrations) in this 
project, i recommend delete all the migrations files, pycache or just the db.
-After do it. Change some field in your models or comment
-Run *py manage.py makemigrations appname --dry-run --verbosity 3*
-Apply you migrations in every app separately
-Migrate