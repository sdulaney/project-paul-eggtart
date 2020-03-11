# organizational purposes
import sys
sys.path.append('./router_logic')

# imports
import datetime
from flask import (
    current_app,
    Blueprint,
    request,
    redirect,
    url_for,
    render_template,
    Flask,
    escape,
    flash
)
from forum_forms import comment_form, rating_form
from TA_functions import *
from reset_password_form import PasswordForm
from signup_db import SignUpForm
from login_db import LoginForm
from email_db import EmailForm, send_password_reset_email
from search import searchBar, closest_match
from profile.profile import User
from load import database
from itsdangerous import URLSafeTimedSerializer
from flask_login import login_user, login_required, login_manager, current_user, logout_user
from purchase import purchase_form
from wtforms import ValidationError

from flask_talisman import Talisman, ALLOW_FROM


# define the database
db = database()

router = Blueprint(
    'router',
    __name__,
    template_folder='../templates'
)



@router.route('/TA/<ta_name>', methods=['GET', 'POST'])
@login_required
def TA(ta_name):
    ta_object = db.child("TA").child(ta_name).get()

    # adding comment to forum
    my_comment = comment_form()
    if my_comment.validate_on_submit():
        submit_comment(db, ta_name, my_comment)
        return redirect('/TA/'+ta_name)

    # adding rating to TA
    my_rating = rating_form()
    if my_rating.validate_on_submit():
        if can_rate(db, current_user.id, ta_name):
            submit_rating(db, ta_name, my_rating)
        return redirect('/TA/'+ta_name)

    # render the template
    if ta_match(db, current_user.id, ta_name):
        return render_template('ta_page.html', ta_info=get_ta_info(ta_object, ta_name), redirect='/TA/'+ta_name,
            comment_form=my_comment, rating_form=my_rating, ta_jpg= ta_name+".jpg")
    return render_template('search.html', form=search)

@router.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    search = searchBar()
    if search.validate_on_submit():
        user = User()
        name, score = closest_match(search.ta_name.data)[0]
        num_views = user.number_views()

        if num_views is not None:
            if num_views <= 0 and not user.ta_viewable(name):
                return redirect('/purchase_credits')
            # if match score less than 90, don't redirect and waste a view
            if score < 90:
                return render_template('search.html', form=search)
            else:
                user.handle_viewlist(name)
                return redirect('/TA/'+ name)

    return render_template('search.html', form=search)

@router.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', login_form=LoginForm(), signup_form=SignUpForm())

@router.route('/login', methods=['POST'])
def login():
    login_form = LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        user = User()
        user.email = login_form.email.data
        user.password = login_form.password.data
        login_result = login_form.login(user)
        if login_result >= 0:
            user.id = login_result
            login_user(user)
            return redirect(url_for('router.search'))
        if login_result == -1:
            flash("Incorrect email or password")
        if login_result == -3:
            return redirect(url_for('router.reset_password'))
    return render_template('index.html', login_form=LoginForm(), signup_form=SignUpForm())

@router.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('router.home'))

@router.route('/signup', methods=['POST'])
def signup():
    signup_form = SignUpForm()
    if signup_form.validate_on_submit():
        if signup_form.verify_email(signup_form.email_addr.data):
            if not signup_form.check_existing_email(db, signup_form.email_addr.data):
                flash('An existing account has already been created with that email address. Please login or contact pauleggtarts@gmail.com for support.')
                return redirect('/')
            signup_form.create_unauthenticated_user(db, signup_form)
            flash('Thanks for registering! Please check your email for a confirmation email.', 'success')
            return redirect('/')
        else:
            flash('Email sign up invalid. Emails must be a UCLA verified email.')
    else:
        for error in signup_form.errors:
            for e in signup_form.errors[error]:
                flash(e)
    return render_template('index.html', login_form=LoginForm(), signup_form=SignUpForm())

@router.route('/profile', methods=['GET'])
@login_required
def profile():
    current_session_user = db.child("users").child(current_user.id).get().val()
    id = int(current_session_user['id'])
    user, ta_list = User().get_user(db, id)
    context = {
        "user": user,
        "ta_list": ta_list
    }
    return render_template('profile.html', **context)

@router.route('/profile/edit', methods=['GET'])
@login_required
def profile_edit():
    id = request.args.get('id', None)
    parameters = User().get_parameters()
    user, _ = User().get_user(db, id)
    context = {
        "parameters": parameters,
        "user": user
    }
    return render_template('profile_edit.html', **context)

@router.route('/profile/edit', methods=['POST'])
@login_required
def profile_edit_add():
    status = User().update_user(request.form)
    if status == "Success":
        return redirect('/profile')
    else:
        id = request.form.get('id', None)
        user, _ = User().get_user(db, id)
        context = {
            "parameters": User().get_parameters(),
            "user": user
        }
        return render_template('profile_edit.html', **context)

@router.route('/reauthenticate', methods=['GET', 'POST'])
def reauthenticate():
    form = EmailForm()
    signup = SignUpForm()
    if form.validate_on_submit():
        found = False
        users = db.child("users").get()
        for u in users.each():
            data = u.val()
            if data['email'] == form.email.data:
                found = True
                if data['authenticated'] is False:
                    signup.send_confirmation_email(form.email.data)
                    flash('Please check your email for an account confirmation link.', 'success')
                else:
                    flash('This account is already authenticated. Please sign in', 'error')
                    return redirect(url_for('router.home'))
                break
        if found is False:
            flash('Invalid email address!', 'error')
            return render_template('reauthenticate.html', form=form)
    return render_template('reauthenticate.html', form=form)

@router.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = EmailForm()
    if form.validate_on_submit():
        found = False
        users = db.child("users").get()
        for u in users.each():
            data = u.val()
            if data['email'] == form.email.data:
                found = True
                if data['authenticated'] is True:
                    send_password_reset_email(form.email.data)
                    flash('Please check your email for a password reset link.', 'success')
                else:
                    flash('Your email address must be confirmed before attempting a password reset.', 'error')
                    return redirect(url_for('router.home'))
                break
        if found is False:
            flash('Invalid email address!', 'error')
            return render_template('password_reset_email.html', form=form)
    return render_template('password_reset_email.html', form=form)

@router.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('router.home'))
 
    form = PasswordForm()
 
    if form.validate_on_submit():
        found = False
        users = db.child("users").get()
        for u in users.each():
            data = u.val()
            if data['email'] == email:
                curr_user = User()
                found = True
                id = data['id']
                curr_pass = data['password']
                if curr_user.decrypt(curr_pass, form.password.data):
                    flash('new password cannot be a previous password')
                    return render_template('reset_password_with_token.html', form=form, token=token)
                
                payload = {}
                payload['password'] = curr_user.encrypt(form.password.data)
                db.child("users").child(id).update(payload)
                curr_user.update_password_reset(id)
                break
        flash('Your password has been updated!', 'success')
        return redirect(url_for('router.home'))
    return render_template('reset_password_with_token.html', form=form, token=token)

@router.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired. :(', 'error')
        return redirect(url_for('router.home'))

    users = db.child("users").get()
    user = None
    for u in users.each():
        data = u.val()
        if data['email'] == email:
            user = data
    
    if user['authenticated']:
        flash('Account already confirmed. Please login.', 'info')
    else:
        db.child("users").child(user['id']).update({"authenticated": True})
        flash('Thank you for confirming your email address!')
    return redirect(url_for('router.home'))

@router.route('/purchase_credits', methods=['GET', 'POST'])
@login_required
def verify_card():
    form = purchase_form()
    if form.validate_on_submit() and form.little.data:
        # If payment was made successfully
        if form.process_payment(form.card.data):
            flash('Payment Processed successfully!')
            user = db.child("users").child(current_user.id).get().val()
            # update the number of views
            new_views = user["remaining_views"] + 10
            db.child("users").child(current_user.id).update({"remaining_views": new_views})
        else:
            flash('Bad credit card')
    return render_template('purchase.html', form=form)