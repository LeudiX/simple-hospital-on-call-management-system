# Common commands for  set up a base project in django

## Create virtual env

py -m venv **venv-name**

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