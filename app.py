import gc
from flask import Flask, render_template, flash, request, url_for, redirect, session
from wtforms import Form, validators, StringField, PasswordField, BooleanField
from content_management import Content
from dbconnect import connection
from passlib.hash import sha256_crypt

TOPIC_DICT = Content()

app = Flask(__name__)
app.secret_key = b'crushyna'


# TODO: It might be actually good idea to define separate directory for every function down below

def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap


@app.route('/')
def home_page():
    return render_template("main.html")


@app.route('/dashboard/')
def dashboard():
    flash("Well hello there!")
    return render_template("content_dashboard.html", TOPIC_DICT=TOPIC_DICT)


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [validators.Length(min=6, max=20)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Password must match.")])
    confirm = PasswordField('Repeat Password')

    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)',
                              [validators.DataRequired()])


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data

            # TODO: sha512 registration maybe?
            password = sha256_crypt.hash((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = (%s);", (username,))
            row_count = c.rowcount

            if row_count == 0:
                query = "INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s);"
                values = (username, password, email, "/introduction-to-python-programming/")
                c.execute(query, values)
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

            else:
                flash("That username is already taken, please choose another!")
                return render_template('register.html', form=form)

        else:
            return render_template('register.html', form=form)

    except Exception as e:
        return str(e)


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == 'POST':
            data = c.execute("SELECT * FROM users WHERE username = (%s);", (request.form['username'],))

            if c.rowcount != 0:  # if user exists
                data_password = c.fetchone()[2]  # get his password

                # TODO: if sha512 registration, then change here also
                if sha256_crypt.verify(request.form['password'], data_password):  # check his password
                    session['logged_in'] = True
                    session['username'] = request.form['username']

                    flash("You are now logged in")
                    return redirect(url_for("dashboard"))

                else:
                    error = "Invalid credentials, try again!"

            else:
                error = "Invalid credentials, try again!"

        gc.collect()
        return render_template('login.html', error=error)

    except Exception as e:
        flash(e)
        error = "Invalid credentials, try again!"
        return render_template("login.html", error=error)


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
    return render_template("404.html")


@app.errorhandler(405)
def method_not_found(e):
    return render_template("405.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
