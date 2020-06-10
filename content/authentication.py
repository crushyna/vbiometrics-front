from flask import request, session, redirect, url_for, render_template, flash
import requests
import gc


class Authentication:

    @staticmethod
    def check_email():
        if 'authorized' in session:
            return redirect(url_for("record_voice"))
        else:
            error = ''
            try:
                if request.method == 'POST':
                    url = f"https://vbiometrics-docker.azurewebsites.net/get_text_phrase/{request.form['email']}/{request.form['merchant_id']} "
                    response = requests.get(url)

                    if response.status_code not in (200, 201):
                        error = "Email not found! Try again!"

                    else:
                        session['authorized'] = True
                        session['logged_in'] = True
                        session['email'] = request.form['email']
                        gc.collect()
                        return redirect(url_for("record_voice"))

                gc.collect()
                return render_template("authenticate.html", error=error)

            except Exception as e:
                flash(e)
                error = "Error!"
                return render_template("authenticate.html", error=error)

    @staticmethod
    def record_voice():
        return render_template('record_voice.html')
