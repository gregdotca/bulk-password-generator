import html
import string

import pytest

from project import (
    DEFAULT_NUMBER_OF_PASSWORDS,
    DEFAULT_PASSWORD_LENGTH,
    MAX_NUMBER_OF_PASSWORDS,
    MAX_PASSWORD_LENGTH,
    app,
)

ALPHANUMERIC = set(string.ascii_letters + string.digits)
FULL_POOL = ALPHANUMERIC | set("!#$%&'()+,-.:;=?@[]^_{|}~")


@pytest.fixture
def client():
    return app.test_client()


def generate(client, number_of_passwords, password_length, exclude_special=None):
    form = {"number_of_passwords": number_of_passwords, "password_length": password_length}
    if exclude_special is not None:
        form["exclude_special"] = exclude_special
    response = client.post("/", data=form)
    assert response.status_code == 200
    # Unescape the HTML the way a browser would, to get the passwords as shown
    return [html.unescape(password) for password in response.get_data(as_text=True).split("<BR>")]


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Bulk Password Generator" in response.data


def test_form_fields_are_numbers_within_the_caps(client):
    page = client.get("/").get_data(as_text=True)
    assert f'type="number" min="1" max="{MAX_NUMBER_OF_PASSWORDS}" name="number_of_passwords"' in page
    assert f'type="number" min="1" max="{MAX_PASSWORD_LENGTH}" name="password_length"' in page


def test_results_are_not_cached(client):
    response = client.post("/", data={"number_of_passwords": 1, "password_length": 16})
    assert response.headers["Cache-Control"] == "no-store"


def test_number_and_length(client):
    passwords = generate(client, 5, 20)
    assert len(passwords) == 5
    assert all(len(password) == 20 for password in passwords)


def test_full_pool(client):
    passwords = generate(client, 50, 50)
    assert set("".join(passwords)) <= FULL_POOL


def test_exclude_special(client):
    passwords = generate(client, 50, 50, "1")
    assert set("".join(passwords)) <= ALPHANUMERIC


@pytest.mark.parametrize("value", ["", "abc", "0", "-5", "1.5", "nan", "inf", "1e400"])
def test_invalid_input_falls_back_to_defaults(client, value):
    passwords = generate(client, value, value)
    assert len(passwords) == DEFAULT_NUMBER_OF_PASSWORDS
    assert all(len(password) == DEFAULT_PASSWORD_LENGTH for password in passwords)


@pytest.mark.parametrize("value, expected", [("1e1", 10), ("12.0", 12), (" 7 ", 7)])
def test_number_field_formats(client, value, expected):
    passwords = generate(client, value, value)
    assert len(passwords) == expected
    assert all(len(password) == expected for password in passwords)


def test_values_above_the_maximum_are_capped(client):
    passwords = generate(client, MAX_NUMBER_OF_PASSWORDS + 1, MAX_PASSWORD_LENGTH + 1)
    assert len(passwords) == MAX_NUMBER_OF_PASSWORDS
    assert all(len(password) == MAX_PASSWORD_LENGTH for password in passwords)


def test_passwords_are_html_escaped(client, monkeypatch):
    # Without escaping, the browser would show "&#9" as a tab and "&lt" as "<"
    monkeypatch.setattr("project.generate_password", lambda length, exclude: "a&#9b&lt;c<d>")
    response = client.post("/", data={"number_of_passwords": 2, "password_length": 16})
    assert response.get_data(as_text=True) == "a&amp;#9b&amp;lt;c&lt;d&gt;<BR>a&amp;#9b&amp;lt;c&lt;d&gt;"
