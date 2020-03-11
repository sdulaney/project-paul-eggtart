from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    render_template
)
from forum_forms import comment_form, rating_form
from load import database
import datetime


######################################################################################
######################################################################################
########################### T.A. NAMES, GLOBAL VARIABLES #############################
######################################################################################
######################################################################################


def get_ta_list():
    ta_list = [
        "paul-eggert",
        "tian-ye",
        "jeff-bezos",
        "tim-cook",
        "elon-musk",
        "faker-hung",
        "jack-ma",
        "michael-pie",
        "lebron-james"
    ]

    return ta_list

def name_to_string(ta_name):
    dictionary = {
        "paul-eggert": "Paul R. Eggert",
        "tian-ye": "Tian Ye",
        "jeff-bezos": "Jeff Bezos",
        "tim-cook": "Tim Cook",
        "elon-musk": "Elon Musk",
        "faker-hung": "Faker Hung",
        "jack-ma": "Jack Ma",
        "michael-pie": "Michael Pie",
        "lebron-james": "Lebron James"
    }

    return dictionary[ta_name]


######################################################################################
######################################################################################
############# T.A. FORUM FORM HANDLING FUNCTIONS (SET/GET DATABSE) ###################
######################################################################################
######################################################################################


def get_ta_info(ta_object, ta_name):
    comments = parse_ta_comments(ta_object)
    ratings = parse_ta_ratings(ta_object)
    classes = get_ta_classes(ta_object)
    display_name = name_to_string(ta_name)
    return (display_name, comments, ratings, classes)

def parse_ta_comments(ta_object):
    comments = []

    for _, val in ta_object.val().items():
        if val.get("comment") != None and val.get("comment_datetime") != None:
            str_datetime = val["comment_datetime"]
            str_datetime = datetime.datetime.fromisoformat(str_datetime).strftime("%m/%d/%Y, %H:%M:%S")
            comments.append((val["comment"], str_datetime))
    
    return comments

def parse_ta_ratings(ta_object):
    ratings = [0, [0, 0, 0]]

    for _, val in ta_object.val().items():
        if val.get("rating") != None:
            ratings[0] += 1
            ratings[1][0] += val["rating"]["clarity"]
            ratings[1][1] += val["rating"]["helpfulness"]
            ratings[1][2] += val["rating"]["availability"]

    if ratings[0] > 0:
        ratings[1][0] = str(round(ratings[1][0] / ratings[0], 2))
        ratings[1][1] = str(round(ratings[1][1] / ratings[0], 2))
        ratings[1][2] = str(round(ratings[1][2] / ratings[0], 2))
    else:
        ratings[1] = ['?', '?', '?']

    return ratings[1]

def get_ta_classes(ta_object):
    classes = []

    for _, val in ta_object.val().items():
        if val.get("class") != None:
            classes.append(val["class"])

    return classes

def submit_comment(db, ta_name, my_comment):
    comment_datetime = datetime.datetime.now().isoformat()
    db.child('TA').child(ta_name).push({
        "comment": my_comment.comment.data,
        "comment_datetime": comment_datetime
    })

def submit_rating(db, ta_name, my_rating):
    db.child('TA').child(ta_name).push({
        "rating": {
            "clarity": my_rating.clarity.data, 
            "helpfulness": my_rating.helpfulness.data, 
            "availability":my_rating.availability.data
        }
    })

def ta_match(db, cur_user_id, ta_name):
    ta_viewable_list = db.child('users').child(cur_user_id).child('viewable_ta').get()
    for _, val in ta_viewable_list.val().items():
        if val['name'] == ta_name:
            return True
    return False

def can_rate(db, cur_user_id, ta_name):
    ta_viewable_list = db.child('users').child(cur_user_id).child('viewable_ta').get().val()
    for key, val in ta_viewable_list.items():
        if val['name'] == ta_name and not val['rated']:
            val['rated'] = True
            db.child('users').child(cur_user_id).child('viewable_ta').update(ta_viewable_list)
            return True
    return False