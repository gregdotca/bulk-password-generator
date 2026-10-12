#!/usr/bin/env python3
import secrets
import string
from flask import Flask, render_template, request

app = Flask(__name__, static_folder="assets")

APP_TITLE = "Bulk Password Generator"

DEFAULT_NUMBER_OF_PASSWORDS = 30
MAX_NUMBER_OF_PASSWORDS = 1000
DEFAULT_PASSWORD_LENGTH = 16
MAX_PASSWORD_LENGTH = 256


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", app_title=APP_TITLE)


@app.route("/", methods=["POST"])
def home_post():
    number_of_passwords = request.form["number_of_passwords"]
    password_length = request.form["password_length"]
    try:
        exclude_special = request.form["exclude_special"]
    except Exception:
        exclude_special = 0

    number_of_passwords = parse_count(number_of_passwords, DEFAULT_NUMBER_OF_PASSWORDS, MAX_NUMBER_OF_PASSWORDS)
    password_length = parse_count(password_length, DEFAULT_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)

    return generate_password_list(number_of_passwords, password_length, exclude_special)


def parse_count(value, default, maximum):
    # Blank, non-numeric, or non-positive input falls back to the default,
    # and anything above the maximum is capped so one request can't tie up a worker
    try:
        count = int(value)
    except ValueError:
        return default

    if count < 1:
        return default

    return min(count, maximum)


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
        password_list.append(generate_password(password_length, exclude_special))

    return "<BR>".join(password_list)


if __name__ == "__main__":
    app.run()
