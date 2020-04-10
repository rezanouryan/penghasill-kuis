from .auth_forms import SignupForm, LoginForm
from app.models import User, db
from flask import Blueprint, redirect
from flask import request, url_for, render_template, current_app, flash
from flask_login import login_required, current_user, login_user, logout_user
from app import login_manager

# Set up blueprint
auth_bp = Blueprint('auth_bp', __name__, template_folder='templates', static_folder='static')

@auth_bp.route('/auth', methods=['GET'])
def main_auth():
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/auth/login', methods=['GET', 'POST'])
def login():
    """
    User sign-in page.

    GET: Serve sign-in page.
    POST: If submitted credentials are valid, redirect user to the logged-in homepage.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.main'))


    login_form = LoginForm(request.form)
    if request.method == 'POST':
        if login_form.validate_on_submit():
            username = login_form.username.data
            password = login_form.password.data
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main_bp.main'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_bp.login'))

    return render_template('login.html',
                            title='Login',
                            form=login_form,
                            template='sign-page',
                            body='Sign up for a user account.')


@auth_bp.route('/auth/signup', methods=['GET', 'POST'])
def signup():
    """
    User sign-up page.

    GET: Serve sign-up page.
    POST: If submitted credentials are valid, redirect user to the logged-in homepage.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.main'))

    signup_form = SignupForm(request.form)
    if request.method == 'POST':
        if signup_form.validate_on_submit():
            first_name = signup_form.first_name.data
            last_name = signup_form.last_name.data
            username = signup_form.username.data
            password = signup_form.password.data
            existing_user = User.query.filter_by(username=username).first()
            if existing_user is None:
                user = User(first_name=first_name, login_name=login_name,
                            username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()  # Create new user
                login_user(user)  # Log in as newly created user
                return redirect(url_for('main_bp.dashboard'), code=400)
            flash('A user already exists with that email address.')
            return redirect(url_for('auth_bp.signup'))


    return render_template('signup.html',
                            title='Create an Account',
                            form=signup_form,
                            template='sign-page',
                            body='Sign up for a user account.')

@auth_bp.route('/logout', methods=['GET'])
@auth_bp.route('/auth/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))



