import gc
import os
import datetime
from flask import Flask, render_template, flash, url_for, redirect, session, request
from helpers.user_check import NewUserModel
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
    template = Authorization.register_page()
    return template


@app.route("/register_record_voice")
def register_record_voice():
    return render_template('register_record_voice.html')


@app.route('/register_record_voice_audio', methods=['POST'])
def register_save_audio():
    next_filename = f"{session['email']}_{datetime.datetime.now().strftime('%y%m%d%H%M%S-%f')}"
    with open(os.path.join(UPLOAD_FOLDER, next_filename), 'wb+') as f:
        f.write(request.data)

    if os.path.isfile(os.path.join(UPLOAD_FOLDER, next_filename)):
        file_saved_flag = os.path.isfile(os.path.join(UPLOAD_FOLDER, next_filename))
        os.remove(os.path.join(UPLOAD_FOLDER, next_filename))
        file_deleted_flag = os.path.isfile(os.path.join(UPLOAD_FOLDER, next_filename))
        return f"File saved: {file_saved_flag}, file exist after delete: {file_deleted_flag}"
    else:
        return "File not saved!"


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


@app.route("/authenticate/", methods=['GET', 'POST'])
def authentication():
    template = Authentication.check_email()
    return template


@app.route("/record_voice")
def record_voice():
    return render_template('record_voice.html')


@app.route('/audio', methods=['POST'])
def audio():
    with open(os.path.join(UPLOAD_FOLDER, 'audio.wav'), 'wb+') as f:
        f.write(request.data)
    # proc = run(['ffprobe', '-of', 'default=noprint_wrappers=1', os.path.join(UPLOAD_FOLDER, 'audio.wav')], text=True,
    #           stderr=PIPE)
    # return f"File saved: {os.path.isfile(os.path.join(UPLOAD_FOLDER, 'audio.wav'))}"
    if os.path.isfile(os.path.join(UPLOAD_FOLDER, 'audio.wav')):
        session['authenticated'] = True

        file_saved_flag = os.path.isfile(os.path.join(UPLOAD_FOLDER, 'audio.wav'))
        # os.remove(os.path.join(UPLOAD_FOLDER, 'audio.wav'))

        file_deleted_flag = os.path.isfile(os.path.join(UPLOAD_FOLDER, 'audio.wav'))
        return f"File saved: {file_saved_flag}, file exist after delete: {file_deleted_flag}"
    else:
        return "File not saved!"


@app.route('/check_session/')
def check_session():
    if 'logged_in' not in session:
        return redirect(url_for('register'))

    new_user = NewUserModel()
    new_user.set_of_text_ids = new_user.get_initial_list_of_texts()

    # return str(len(new_user.set_of_text_ids))

    while len(new_user.set_of_text_ids) < new_user.num_of_required_texts:
        new_user.set_of_text_ids, new_user.set_of_texts_full = new_user.get_missing_texts()

    # return str(len(new_user.set_of_text_ids)) + str(new_user.num_of_required_texts)

    new_user.set_number_of_missing_samples = new_user.get_missing_samples()
    session['recordings'] = new_user.set_number_of_missing_samples
    session['texts'] = new_user.set_of_texts_full

    # return str(new_user.set_of_text_ids) + str(new_user.set_number_of_missing_samples)

    for each_key, each_value in session['recordings'].items():
        return render_template('register_record_voice.html',  message=(each_key, each_value, session['texts'][each_key], session['merchant_id'], session['user_id']))
        # return redirect(url_for('register_record_voice', message="test_string"))

    #return session['recordings']

    # return "Session checker!"


# ONLY Error handling below #
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(405)
def method_not_found(e):
    return render_template("errors/405.html"), 405


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
