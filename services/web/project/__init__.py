#!/usr/bin/env python3
import random
import string
from flask import Flask, render_template, request

app = Flask(__name__, static_folder="assets")

APP_TITLE = "Bulk Password Generator"


@app.route("/")
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

    number_of_passwords = 30 if not number_of_passwords else number_of_passwords
    password_length = 16 if not password_length else password_length

    return generate_password_list(number_of_passwords, password_length, exclude_special)


def generate_password(password_length, exclude_special):
    password_list = []

    if exclude_special == "1":
        character_pool = string.ascii_letters + string.digits
    else:
        character_pool = (
            string.ascii_letters + string.digits + "!#$%&'()+,-.:;=?@[]^_{|}~"
        )

    characters = list(character_pool)
    random.shuffle(characters)

    for i in range(int(password_length)):
        password_list.append(random.choice(characters))
    random.shuffle(password_list)

    return "".join(password_list)


def generate_password_list(number_of_passwords, password_length, exclude_special):
    password_list = []

    for _ in range(int(number_of_passwords)):
        password_list.append(generate_password(password_length, exclude_special))

    return "<BR>".join(password_list)


if __name__ == "__main__":
    app.run()
