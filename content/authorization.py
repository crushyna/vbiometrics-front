import gc
from time import sleep

import requests
from flask import request, flash, session, url_for, redirect, render_template, json
from passlib.handlers.sha2_crypt import sha512_crypt
from content.forms.registration_form import RegistrationForm


class Authorization:

    @staticmethod
    def register_page():
        try:
            form = RegistrationForm(request.form)

            if request.method == "POST" and form.validate():
                email = form.email.data
                merchant_id = form.merchant_id
                password = form.password.data

                url = f"https://vbiometrics-docker.azurewebsites.net/get_text_phrase/{email}"
                response = requests.request("GET", url)

                if response.status_code not in (200, 201):  # if user DOES NOT exist

                    url = "https://vbiometrics-docker.azurewebsites.net/add_new_user/"
                    payload = {"user_email": email,
                               "merchant_id": merchant_id,
                               "password": sha512_crypt.hash(password)}
                    headers = {'Content-Type': 'application/json'}
                    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

                    if response.status_code in (200, 201):  # if user added successfully
                        gc.collect()
                        session['logged_in'] = True
                        session['email'] = email

                    else:
                        flash("Wrong password or server error!")
                        return redirect(url_for('dashboard'))

                else:
                    flash("That email is already taken, please choose another!")
                    return render_template('register.html', form=form)

            else:
                return render_template('register.html', form=form)

        except Exception as e:
            return str(e)

    @staticmethod
    def login_page():
        error = ''
        try:
            if request.method == 'POST':
                url = "https://vbiometrics-docker.azurewebsites.net/user_login/"
                payload = {"merchant_id": request.form['merchant_id'],
                           "user_email": request.form['email'],
                           "password": sha512_crypt.hash(request.form['password'])}
                headers = {'Content-Type': 'application/json'}
                response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

                if response.status_code in (200, 201):
                    session['logged_in'] = True
                    session['email'] = request.form['email']

                    flash("You are now logged in")
                    sleep(2)
                    return redirect(url_for("dashboard"))

                else:
                    error = "Invalid credentials, try again!"

            gc.collect()
            return render_template('login.html', error=error)

        except Exception as e:
            flash(e)
            error = "Invalid credentials or request method, try again!"
            return render_template("login.html", error=error)
