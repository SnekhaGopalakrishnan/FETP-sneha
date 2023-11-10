import secrets
from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generating a random secret key

oauth = OAuth(app)

gmail = oauth.remote_app(
    'gmail',
    consumer_key='852826982331-teu9836h98t61cbmf1109lju4gf28ebj.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Add tokengetter decorator
@gmail.tokengetter
def get_gmail_oauth_token():
    return session.get('gmail_token')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return gmail.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('gmail_token', None)
    # Redirect to the home page
    return redirect(url_for('index'))
    # Redirect to Gmail sign-out URL
    #return redirect('https://mail.google.com/mail/u/0/?logout&hl=en')

@app.route('/login/authorized')
def authorized():
    print('Reached /login/authorized')
    response = gmail.authorized_response()

    print('OAuth response:', response)

    if response is None or response.get('access_token') is None:
        print('Authentication failed')
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['gmail_token'] = (response['access_token'], '')
    user_info = gmail.get('userinfo')

    print('User info:', user_info.data)

    # Extract information
    profile_picture = user_info.data.get('picture')
    user_name = user_info.data.get('name')
    user_email = user_info.data.get('email')

    return render_template('profile.html', profile_picture=profile_picture, user_name=user_name, user_email=user_email)

if __name__ == '__main__':
    app.run(debug=True)
