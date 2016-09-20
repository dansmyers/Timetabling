# Course Timetabling System

## Setup

Clone into your Cloud9 workspace.

```
prompt$ git clone http://github.com/dansmyers/timetabling
```

Install flask and SQLAlchemy.

```
prompt$ pip install flask
prompt$ pip install flask_sqlalchemy
```

## Database

The database is stored in `db/schedule.db`. Remove this file to delete the existing database. To initialize an empty database, use

```
prompt$ python create_tables.py
```

## Running

```
prompt$ python timetabling_server.py
```

Navigate to `http://workspacename-username.c9users.io`, where `workspacename` is the name of the workspace that you are using for the timetabling project and `username` is you Cloud9 username.
