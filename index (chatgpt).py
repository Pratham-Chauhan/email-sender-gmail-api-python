import base64
from flask import Flask, render_template, request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

app = Flask(__name__)

# Load client secrets from a file (you need to obtain this file from the Google Cloud Console)
CLIENT_SECRET_FILE = 'credentials.json'

# The scopes required for the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# The redirect URI authorized in the Google Cloud Console
REDIRECT_URI = 'http://localhost:5000/auth/callback'

# Gmail API version
API_VERSION = 'v1'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_email():
    # Get the email content from the form
    recipient = request.form['recipient']
    subject = request.form['subject']
    message = request.form['message']

    # Load credentials from the session
    credentials = Credentials.from_authorized_user_info(session['credentials'])

    # Build the Gmail API service
    service = build('gmail', API_VERSION, credentials=credentials)

    # Create the email message
    email = create_email(recipient, subject, message)

    # Send the email
    send_message(service, 'me', email)

    return 'Email sent!'

def create_email(recipient, subject, message):
    """Create an email message"""
    email = f"From: me\r\nTo: {recipient}\r\nSubject: {subject}\r\n\r\n{message}"
    return {'raw': base64.urlsafe_b64encode(email.encode()).decode()}

def send_message(service, user_id, message):
    """Send an email message"""
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True)
