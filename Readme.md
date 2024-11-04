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

- In case you're facing troubles(or make a mistake with migrations) in this 
project, i recommend delete all the migrations files, pycache or just the db.
- After do it. Change some field in your models or comment
- Run *py manage.py makemigrations appname --dry-run --verbosity 3*
- Migrate with *py manage.py migrate*


## View the schema

- sqlit3 tools, install it and setting it up as enviroment variables in you path
- Type sqlite3 *dbname* in your terminal
- After entering to the sqlite3 CLI, type *.tables* to see the hole schema
- Type .schema *tablename* to see the table schema

## Create superuser

-Type *python manage.py createsuperuser*

## TODO and solved tasks:
- Add service stats on main page (Number of doctors, patients attended, doctors team ) 
- Check Vital Signs validation when creating a new consultation by doctor
- Check consultations inconsistencies with users deleted in system
- Add profile access to admin on system management
- Consider implementing a more robust file management strategy, like checking file types and sizes, to ensure that application handles image uploads securely and efficiently
- Add Vital Signs management on admin session with sorting, pagination and filtering


### Solved issue with profile_picture field CustomUser model related also with media files default url in database

- Go to console and type *py manage.py shell*
- For this especific cased i have to remove this field, so i write in console the following:

```python
from apps.users.models import CustomUser  # Adjusted the path to CustomUser model 

#### Filter users with profile_picture set to the default image path
users_with_default_image = CustomUser.objects.filter(profile_picture='profile_pics/default_profile_picture2.png')

#### Set profile_picture to None for each user with the default image
for user in users_with_default_image:
    user.profile_picture = None
    user.save()

print(f"Updated {users_with_default_image.count()} users to use the static default profile picture.")
```
- Then type *Enter* and write `exit()` in shell
- Make migrations in users 
- Migrate
- Run again
    
    