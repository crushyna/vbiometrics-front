import gc
import requests
from flask import request, flash, session, url_for, redirect, render_template, json
from content.forms.registration_form import RegistrationForm
from helpers.hashfunctions import HashFunctions


class Authorization:

    @staticmethod
    def register_page():
        try:
            form = RegistrationForm(request.form)

            if request.method == "POST" and form.validate():
                email = form.email.data
                merchant_id = form.merchant_id.data
                password = form.password.data

                url = f"https://vbiometrics-docker.azurewebsites.net/check_if_user_exists/{merchant_id}/{email}"
                response = requests.request("GET", url)

                if response.status_code not in (200, 201):  # if user DOES NOT exist

                    url = "https://vbiometrics-docker.azurewebsites.net/add_new_user/"
                    payload = {"user_email": email,
                               "merchant_id": int(merchant_id),
                               "password": HashFunctions.calculate_sha512(password)}
                    headers = {'Content-Type': 'application/json'}
                    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

                    if response.status_code in (200, 201):  # if user added successfully
                        user_id = response.json()['message']['data']['userId']
                        session['logged_in'] = True
                        session['email'] = email
                        session['user_id'] = user_id
                        session['merchant_id'] = merchant_id
                        session['text_ids_set'] = []
                        session['in_registration_process'] = True

                        return redirect(url_for('check_session'))

                    elif response.status_code == 409:
                        flash("User with this email already exists!")
                        return redirect(url_for('register'))

                    else:
                        error = response.json()
                        flash(f"error {error}")
                        return redirect(url_for('register'))

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
                           "password": HashFunctions.calculate_sha512(request.form['password'])}
                headers = {'Content-Type': 'application/json'}
                response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

                if response.status_code in (200, 201):
                    session['logged_in'] = True
                    session['email'] = request.form['email']

                    flash("You are now logged in")
                    return redirect(url_for("dashboard"))

                else:
                    error = "Invalid credentials, try again!"
                    session.clear()
                    return render_template('login.html', error=error)

            gc.collect()
            return render_template('login.html', error=error)

        except Exception as e:
            flash(e)
            error = "Invalid credentials or request method, try again!"
            return render_template("login.html", error=error)
