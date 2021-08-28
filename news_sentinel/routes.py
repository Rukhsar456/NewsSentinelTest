from news_sentinel.models import User, News, Vote
from news_sentinel import *
from flask import request, render_template, redirect, flash, url_for
from news_sentinel.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, logout_user, login_required, current_user
from news_sentinel.models import News, Vote
from fetch_news import get_news
from sqlalchemy import exc, desc
from flask_mail import Message


def get_new_news():
    news = News.query.order_by(desc(News.id)).all()
    return news


@app.route('/', methods=['POST', 'GET'])
def home():
    news = get_new_news()
    votes = Vote.query.all()
    return render_template('index.html', news=news, votes=votes, current_user=current_user)


@app.route('/check', methods=['POST'])
def check():
    title = request.form['title']
    author = request.form['author']
    query = get_all_query(title, author)
    pred = pipeline.predict(query)
    dic = {1: 'real', 0: 'fake'}
    status = {1: 'success', 0: 'error'}
    return render_template('res.html', res=dic[pred[0]], status=status[pred[0]])


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.email.data or form.password.data:
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome, {user.username}', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check credentials again.', 'danger')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. Now you can log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/refresh_news')
def refresh_news():
    rows = get_news()
    flash(f'News Updated.{rows} news rows added', 'success')
    return redirect(url_for('home'))


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    news_id = request.args.get('news_id')
    vote = request.args.get('vote')
    vote = int(vote)
    if vote == 1:
        label = 'Real'
    else:
        label = 'Fake'
    if not current_user.is_authenticated:
        flash('To vote the news as real or fake, you must be logged in. Please login or signup to vote.', 'info')
        return redirect(url_for('login'))
    else:
        # flash('You can vote.', 'success')
        return render_template('vote.html', news_id=news_id, current_user=current_user, vote=vote, label=label)


@app.route('/castVote', methods=['POST'])
def cast_vote():
    user_id = request.form.get('user_id')
    news_id = request.form.get('news_id')
    vote_casted = request.form.get('vote')

    new_vote = Vote(vote=vote_casted, news_id=news_id, user_id=user_id)
    db.session.add(new_vote)
    try:
        db.session.commit()
        flash('Your vote has been casted. Thank you for contributing.', 'success')
        return redirect(url_for('home'))
    except exc.SQLAlchemyError as e:
        flash('There was some error casting you vote, please try again.', 'danger')
        return redirect(url_for('home'))


def send_email(user):
    token = user.get_reset_token()
    message = Message('Password Reset Request',
                      sender='newssentinel2@gmail.com',
                      recipients=[user.email])
    message.body = f''' To reset your password, click on following link 
{url_for('reset_token', token=token, _external=True)} 
    
If you did not make this request, please simply ignore this.
    '''
    mail.send(message)


@app.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))

    return render_template('reset_request.html', form=form)


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This is invalid token. This may have happened because of time limit.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been changes. Now you can log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form)
