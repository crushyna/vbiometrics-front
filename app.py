import gc
import os

from flask import Flask, render_template, flash, url_for, redirect, session, request

from content.authentication import Authentication
from content.authorization import Authorization
from content_management import Content

TOPIC_DICT = Content()

app = Flask(__name__)
app.secret_key = b'crushyna'

UPLOAD_FOLDER = 'wavefiles'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


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
    flash("Well hello there!")
    return render_template("content_dashboard.html", TOPIC_DICT=TOPIC_DICT)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    template = Authorization.register_page()
    return template


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
        os.remove(os.path.join(UPLOAD_FOLDER, 'audio.wav'))
        file_deleted_flag = os.path.isfile(os.path.join(UPLOAD_FOLDER, 'audio.wav'))
        return f"File saved: {file_saved_flag}, file deleted after saving: {file_deleted_flag}"
    else:
        return "File not saved!"


# ONLY Error handling below #
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html")


@app.errorhandler(405)
def method_not_found(e):
    return render_template("errors/405.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
