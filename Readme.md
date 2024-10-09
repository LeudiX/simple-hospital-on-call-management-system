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
-Migrate with *py manage.py migrate*


## View the schema

-Download sqlit3 tools, install it and setting it up as enviroment variables in you path
-Type sqlite3 *dbname* in your terminal
-After entering to the sqlite3 CLI, type *.tables* to see the hole schema
-Type .schema *tablename* to see the table schema

## Create superuser

-Type *python manage.py createsuperuser*

TODO:
-Add consultations management on admin session
-Hide add users button on user management
-Add search filter bar and pagination to users management (Or use datatables instead)
-Change color of active field to red when user get deactivated
-Add a mass removal for users management
-Add links to Common and Urgency services for authenticated and enrolled users only
-Check Vital Signs validation when creating a new consultation by doctor
