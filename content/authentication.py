from flask import request, session, redirect, url_for, render_template, flash
import requests
import gc


class Authentication:

    @staticmethod
    def check_email():
        error = ''
        try:
            if request.method == 'POST':
                url = f"https://vbiometrics-docker.azurewebsites.net/get_text_phrase/{request.form['email']}"
                response = requests.get(url)

                if response.status_code not in (200, 201):
                    error = "Email not found! Try again!"

                else:
                    session['authorized'] = True
                    gc.collect()
                    return redirect(url_for("dashboard"))

            gc.collect()
            return render_template("authenticate.html", error=error)

        except Exception as e:
            flash(e)
            error = "Error!"
            return render_template("authenticate.html", error=error)
