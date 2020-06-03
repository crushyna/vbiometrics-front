import gc

from flask import request, flash, session, url_for, redirect, render_template
from passlib.handlers.sha2_crypt import sha256_crypt

from content.forms.registration_form import RegistrationForm
from dbconnect import connection


class Authorization:

    @staticmethod
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

    @staticmethod
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
