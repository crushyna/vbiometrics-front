import gc
import os
import datetime

import requests
from flask import Flask, render_template, flash, url_for, redirect, session, request
from helpers.user_check import NewUserModel, AuthenticatingUser
from content.authentication import Authentication
from content.authorization import Authorization
from content_management import Content

TOPIC_DICT = Content()

UPLOAD_FOLDER = 'wavefiles'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'wav'}

app = Flask(__name__)
app.secret_key = b'crushyna'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# TODO: It might be actually good idea to define separate directory for every function down below

def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))

    return wrap


@app.route('/')
def home_page():
    return render_template("main.html")


@app.route('/dashboard/')
def dashboard():
    return render_template("content_dashboard.html", TOPIC_DICT=TOPIC_DICT)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if 'in_recording_session' not in session:
        template = Authorization.register_page()
        return template
    else:
        return redirect(url_for('check_session'))


@app.route("/register_record_voice")
def register_record_voice():
    return render_template('register_record_voice.html')


@app.route('/register_record_voice_audio', methods=['POST'])
def register_save_audio():
    session['next_filename'] = f"{session['email']}_{datetime.datetime.now().strftime('%y%m%d%H%M%S-%f')}.wav"
    with open(os.path.join(UPLOAD_FOLDER, session['next_filename']), 'wb+') as f:
        f.write(request.data)

    if os.path.isfile(os.path.join(UPLOAD_FOLDER, session['next_filename'])):
        file_saved_flag = os.path.isfile(os.path.join(UPLOAD_FOLDER, session['next_filename']))

        # send to back-end
        url_upload_wavefile = f"https://vbiometrics-docker.azurewebsites.net/upload_wavefile/{session['next_filename']}"
        files = [('file', open(os.path.join(UPLOAD_FOLDER, session['next_filename']), 'rb'))]

        response_send_wavefile = requests.request("POST", url_upload_wavefile, files=files)
        if response_send_wavefile.status_code == 400:
            return "error while sending wavefile to back-end server!", 400

        url_array_upload = f"https://vbiometrics-docker.azurewebsites.net/array_upload/" \
                           f"{session['next_recording_data'][2]}/{session['next_recording_data'][3]}" \
                           f"/{session['next_recording_data'][0]}/{session['next_filename']}" \
                           f"/{session['next_recording_data'][5]}"

        response_array_upload = requests.request("POST", url_array_upload)
        if response_array_upload.status_code == 400:
            return "error while sending npy file to database!", 400
        elif response_array_upload.status_code == 500:
            return "error while sending npy file to database", 500

        # delete from web browser cache:
        files = False
        os.remove(os.path.join(UPLOAD_FOLDER, session['next_filename']))

        # check if deleted:
        file_deleted_flag = os.path.isfile(os.path.join(UPLOAD_FOLDER, session['next_filename']))

        return f"File saved: {file_saved_flag}, file exist after delete: {file_deleted_flag}, send to backend status code: {str(response_send_wavefile.status_code)}, upload npy status code: {str(response_array_upload.status_code)}"
    else:
        return "File not saved!"


@app.route("/authenticate/", methods=['GET', 'POST'])
def authentication():
    template = Authentication.check_email()
    return template


@app.route("/record_voice")
def record_voice():
    return render_template('record_voice.html')


@app.route('/audio', methods=['POST'])
def audio():
    session['input_filename'] = f"{session['email']}_{datetime.datetime.now().strftime('%y%m%d%H%M%S-%f')}.wav"
    with open(os.path.join(UPLOAD_FOLDER, session['input_filename']), 'wb+') as f:
        f.write(request.data)

    # check if file is created correctly
    if os.path.isfile(os.path.join(UPLOAD_FOLDER, session['input_filename'])):
        file_saved_flag = os.path.isfile(os.path.join(UPLOAD_FOLDER, session['input_filename']))

        # send to back-end
        url_upload_wavefile = f"https://vbiometrics-docker.azurewebsites.net/upload_wavefile/{session['input_filename']}"
        files = [('file', open(os.path.join(UPLOAD_FOLDER, session['input_filename']), 'rb'))]

        response_send_wavefile = requests.request("POST", url_upload_wavefile, files=files)
        if response_send_wavefile.status_code == 400:
            return "error while sending wavefile to back-end server!", 400

        # send for verification
        session['authentication_results'] = AuthenticatingUser.verify_user(session['input_filename'])

        # delete from web browser cache:
        files = False
        # os.remove(os.path.join(UPLOAD_FOLDER, session['input_filename']))

        # check if deleted:
        file_deleted_flag = os.path.isfile(os.path.join(UPLOAD_FOLDER, session['input_filename']))

        return f"File saved: {file_saved_flag}, file exist after delete: {file_deleted_flag}"


@app.route('/authenticate/results/')
def authenticate_results():
    return render_template('authentication_results.html')


@app.route('/check_session/')
def check_session():
    # if user is not logged in
    if 'logged_in' not in session:
        return redirect(url_for('register'))

    new_user = NewUserModel()
    user_check = new_user.get_text_info_by_user_id()

    # if user does not require any more recordings to perform
    if user_check['status'] == 'success':
        if 'in_recording_session' in session:
            del session['in_recording_session']

        final_result_json, final_result_code = new_user.generate_images(set(session['text_ids_set']))
        if final_result_code not in (200, 201):
            return "Error when uploading image files!"

        session.clear()
        gc.collect()
        session['logged_in'] = True
        flash("Registration successful.")
        flash("You are now logged in.")
        return redirect(url_for('dashboard'))

    session['in_recording_session'] = True

    data = (new_user.next_step_text_id,
            new_user.next_step_phrase,
            new_user.merchant_id,
            new_user.user_id,
            new_user.next_step_text_id,
            new_user.next_step_filename)
    session['next_recording_data'] = data
    return redirect(url_for('register_record_voice'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    template = Authorization.login_page()
    return template


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('dashboard'))


# ONLY Error handling below #
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(405)
def method_not_found(e):
    return render_template("errors/405.html"), 405


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
