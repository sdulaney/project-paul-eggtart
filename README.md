# RATE MY TA CS188 PROJECT

## Table of Contents
* [Introduction](#intro)
* [Getting Started](#getting-started)
* [Features](#features)
* [TA List](#ta-list)
* [Sources](#sources)

## Introduction
This project allows you to rate Teaching Assistants at UCLA. The project is set up using Python 3.

Our Link to Heroku is https://rate-my-ta.herokuapp.com/

## Getting started

### Setting up a Virtual Environment (MacOS/Linux) (optional)

```sh
$ python3 -m venv env
$ source env/bin/activate
```

https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

### Installing Dependencies

```sh
$ pip install -r requirements.txt
```

### Launching the Server

```sh
$ python3 app.py
```


## Features
### Account Management
- Creating a new account will give 3 'remaining views', the amount of TAs which the account can access
- During the 'look up' of a new TA, a 'remaining view' will be used up, the TA will be added to your list
- Attempting a direct lookup of a new TA will keep you on the search page (this will not use a token)

### Sign Up / Login
- Tracks which TAs are viewable by your account and how many more TAs may be added to that list
- Access restricted for viewing non-viewable TA pages, taken to credit purchasing page
- Verifies for @ucla.edu account upon sign-up
- Password encryption 

### Forum
- Comments are allowed for viewable TA's as many times as necessary
- Rating is allowed once per TA that is viewable by the account



## TA List
- Paul Eggert
- Tian Ye
- Jeff Bezos
- Tim Cook
- Elon Musk
- Faker Hung
- Jack Ma
- Michael Pie
- Lebron James



## Sources
- https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
- https://materializecss.com/
- https://wtforms.readthedocs.io/en/stable/
- https://pypi.org/project/wtforms-html5/


### Firebase documentation
- https://github.com/thisbejim/Pyrebase 