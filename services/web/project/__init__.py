#!/usr/bin/env python3
import secrets
import string
from flask import Flask, make_response, render_template, request
from markupsafe import escape

app = Flask(__name__, static_folder="assets")

APP_TITLE = "Bulk Password Generator"

DEFAULT_NUMBER_OF_PASSWORDS = 30
MAX_NUMBER_OF_PASSWORDS = 1000
DEFAULT_PASSWORD_LENGTH = 16
MAX_PASSWORD_LENGTH = 256


@app.route("/", methods=["GET"])
def home():
    return render_template(
        "home.html",
        app_title=APP_TITLE,
        max_number_of_passwords=MAX_NUMBER_OF_PASSWORDS,
        max_password_length=MAX_PASSWORD_LENGTH,
    )


@app.route("/", methods=["POST"])
def home_post():
    number_of_passwords = request.form.get("number_of_passwords", "")
    password_length = request.form.get("password_length", "")
    exclude_special = request.form.get("exclude_special")

    number_of_passwords = parse_count(number_of_passwords, DEFAULT_NUMBER_OF_PASSWORDS, MAX_NUMBER_OF_PASSWORDS)
    password_length = parse_count(password_length, DEFAULT_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)

    response = make_response(generate_password_list(number_of_passwords, password_length, exclude_special))
    # Keep the passwords out of the browser's cache and history
    response.headers["Cache-Control"] = "no-store"
    return response


def parse_count(value, default, maximum):
    # Blank, non-numeric, non-whole, or non-positive input falls back to the default,
    # and anything above the maximum is capped so one request can't tie up a worker.
    # Parsed as a float because number fields can submit values like "1e2"
    try:
        number = float(value)
    except ValueError:
        return default

    if not number.is_integer() or number < 1:
        return default

    return min(int(number), maximum)


def generate_password(password_length, exclude_special):
    password_list = []

    if exclude_special == "1":
        character_pool = string.ascii_letters + string.digits
    else:
        character_pool = (string.ascii_letters + string.digits + "!#$%&'()+,-.:;=?@[]^_{|}~")

    for _ in range(int(password_length)):
        password_list.append(secrets.choice(character_pool))

    return "".join(password_list)


def generate_password_list(number_of_passwords, password_length, exclude_special):
    password_list = []

    for _ in range(int(number_of_passwords)):
        # Escape each password so the browser can't read "&#9", "&lt", and so on
        # as character references and show a different password
        password_list.append(escape(generate_password(password_length, exclude_special)))

    return "<BR>".join(password_list)


if __name__ == "__main__":
    app.run()
