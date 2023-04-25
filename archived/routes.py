import requests

from flask import render_template, redirect, url_for, request, flash, make_response, Blueprint
from client_tcp import Client

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    if 'token' not in request.cookies:
        return redirect(url_for('routes.signup'))
    return redirect(url_for('routes.home'))

@routes.route('/home')
def home():
    if 'token' not in request.cookies:
        return redirect(url_for('routes.login'))
    return render_template('home.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = {'username': request.form['username'], 'password': request.form['password']}
        print("before")
        response = requests.post('http://localhost:3001/api/login', json=data)
        print("after")
        if response.status_code == 200:
            token = response.json().get('token')
            response = make_response(redirect(url_for('routes.home')))
            response.set_cookie('token', token)
            return response
        else:
            flash(f"Cannot login: {response.text}")
            return render_template('login.html')
    if 'token' in request.cookies:
        return redirect(url_for('routes.home'))
    return render_template('login.html')

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        response = requests.post('http://localhost:3001/api/signup', json={'username': request.form['username'], 'password': request.form['password']})
        if response.status_code == 200:
            return redirect(url_for('routes.home'))
        else:
            flash(f"Cannot signup: {response.json()['error']}")
            return render_template('signup.html')
    if 'token' in request.cookies:
        return redirect(url_for('routes.home'))
    return render_template('signup.html')
    

@routes.route('/logout', methods=['POST'])
def logout():
    token = request.cookies.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('http://localhost:3001/api/logout', headers=headers)
    if response.status_code == 200:
        response = make_response(redirect(url_for('routes.home')))
        response.delete_cookie('token')
        return response
    else:
        flash(f'Unable to logout: {response.text}')
        return redirect(url_for('routes.home'))
    
@routes.route('/message', methods=['POST'])
def message():
    client = Client()
    client.start()
    message = request.form['message']
    client.send_message(message)
    flash(f"Message sent successfully")
    return redirect(url_for('routes.home'))



@routes.route('/submit_vote', methods=['POST'])
def submit_vote():
    # encrypt the vote
    # calculate v and v'
    # send both to both collectors

    response = requests.post('http://localhost:3001/api/signup', json={'username': request.form['username'], 'password': request.form['password']})
    if response.status_code == 200:
        return redirect(url_for('routes.home'))
    else:
        flash(f"Cannot signup: {response.json()['error']}")
        return render_template('signup.html')