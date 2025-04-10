import sys
import traceback

from flask import Flask, render_template, request, jsonify, session
from api.users import create_user, login_user, set_or_verify_master_password, set_fb_username
from datetime import datetime
from test import pika
from metapriv.bot_operations import BOT
from metapriv.bot_ops import BotOps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    """Renders default text"""
    return render_template('index.html')

@app.route('/create-user', methods=['POST'])
def create_user_endpoint():
    """API endpoint to create a new user"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Assuming create_user returns a user ID if successful, None otherwise
    result = create_user(username, password)
    if result:
        return jsonify({'message': 'User created successfully', 'user_id': result}), 201
    else:
        return jsonify({'error': 'Failed to create user'}), 500
    
@app.route('/login', methods=['POST'])
def login_endpoint():
    """API endpoint for user login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = login_user(username, password)
    if len(user) == 1:
        user = user[0]
        session['user_id'] = user[0]  
        session['username'] = username
        session['is_master_enable'] = True if user[3] is not None else False
        session['enabled'] = datetime.now()
        return jsonify({'message': 'Login successful', 'is_master_enable': False}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/master', methods=['GET', 'POST'])
def master_password():
    master_enabled = session.get('is_master_enable', False)
    if request.method == 'POST':
        # Handling form data submitted via POST request
        # masterPassword has to be >16 character long. 16/24/32/
        data = request.get_json()
        master_password = data.get('masterPassword')
        
        if not master_password:
            return jsonify({'error': 'Master password is required'}), 400
        
        # Assume you have a function `set_or_verify_master_password`
        # that returns True if password is set/verified successfully, or False otherwise
        result = set_or_verify_master_password(session.get('user_id'), master_password)

        if result:
            if not session['is_master_enable']:
                session['is_master_enable'] = True  # Update session to reflect master password is set/verified
                session['master_password'] = master_password
                return jsonify({'message': 'Master password set/verified successfully'}), 200
            else:
                session['master_password'] = master_password
                return jsonify({'message': 'Master Password verification successful. Account unlocked!'}), 200
        else:
            if master_enabled:
                return jsonify({'error': 'Master password is incorrect. Try again!'}), 401
            else:
                return jsonify({'error': 'Failed to set/verify master password'}), 401

    # If it's a GET request, just show the form
    return render_template('master-password.html', master_enabled=master_enabled)

@app.route('/fb-auth', methods=['GET', 'POST'])
def fb_auth():
    if request.method == 'POST':
        data = request.get_json()
        fb_username = data.get('fb_username')
        fb_password = data.get('fb_password')
        
        # TODO: MUST CHANGE.
        session['fb_username'] = fb_username
        session['fb_password'] = fb_password
        
        if not fb_username:
            return jsonify({'error': 'username is required'}), 400
        
        result = set_fb_username(session.get('user_id'), fb_username)
        # TODO: set/fetch the fb_username and password in auth. 
        print(result)
        if result:
            return jsonify({'message': 'FB auth successfully'}), 200
        else:
            return jsonify({'error': 'FB auth failed'}), 400
        
    return render_template('fb-auth.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/bot_ops', methods=['POST'])
def bot_ops():
    try:
        # test function.
        # pika()
        # TODO: this should start on a new thread/ sommething
        # master = session['master_password']
        master = "1234567890123456".encode()
        eff_privacy = 100
        try:
            # BOT().start_bot(eff_privacy=eff_privacy, key = master)
            BotOps().start_bot(eff_privacy=eff_privacy, key = master)             
            return jsonify({'message': 'Bot started successfully!'}), 200
        except Exception as exc:
            tb = traceback.format_exc()
            # Optionally, print the traceback to the console
            print("An error occurred: ", tb)
            # Send the traceback to the frontend for debugging
            return jsonify({'error': 'An unexpected error occurred', 'traceback': tb}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5555
    app.run(debug=True, host='127.0.0.1', port=5555)
