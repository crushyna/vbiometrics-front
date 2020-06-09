from wtforms import Form, StringField, PasswordField, validators, BooleanField


class RegistrationForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=40),
                                          validators.Email(message="Email address syntax error!")])
    merchant_id = StringField('Merchant ID', [validators.Length(min=6, max=6)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Password must match.")])
    confirm = PasswordField('Repeat Password')

    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jun 08, 2020)',
                              [validators.DataRequired()])
