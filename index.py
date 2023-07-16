from flask import Flask, render_template, request

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import base64

app = Flask(__name__)

CLIENT_SECRET_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/send', methods=['POST'])
def send_email():
    # Get the email content from the form
    sender = request.form['from']
    recipient = request.form['to']
    message = request.form['message']


    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds.valid: creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds: 
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8000)
        # Save the credentials for the next run
        with open('token.json', 'w') as token: token.write(creds.to_json())

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    # Create the email message
    email = create_email(recipient, '', message)

    # Send the email
    send_message(service, 'me', email)

    return 'Email sent!'


def create_email(recipient, subject, message):
    email = f"From: me\r\nTo: {recipient}\r\nSubject: {subject}\r\n\r\n{message}"
    return {'raw': base64.urlsafe_b64encode(email.encode()).decode()}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        return message
    except Exception as e:
        print(f'An error occurred: {e}')
        return None




if __name__ == '__main__':
    # app.secret_key = 'super_secret_key'
    app.run(debug=True, host='0.0.0.0', port=8080)
