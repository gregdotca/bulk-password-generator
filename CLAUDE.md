# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A single-page Flask app that generates a list of random passwords. Live demo: https://passwords.greg.ca. All application code is in `services/web/project/__init__.py`, and the only page is `services/web/project/templates/home.html`.

## Running

Production (gunicorn on container port 5000, published on host port 8085). The gunicorn command has `--no-control-socket` because the app doesn't use gunicorn's `gunicornc` control tool, and the `app` user can't create its default socket in `/home/app/.gunicorn`:

```bash
docker compose up -d --build
```

Development uses local-only files that are excluded through `.git/info/exclude`, not `.gitignore`: `docker-compose.DEV.yml`, `services/web/Dockerfile.DEV`, `to-dev.sh`, and `to-prod.sh`. `./to-dev.sh` swaps the DEV compose file and Dockerfile into place (renaming the production ones to `*.PROD`), and `./to-prod.sh` swaps them back. The DEV compose file runs `python manage.py run -h 0.0.0.0` on port 5000 with `services/web/` mounted at `/app`, so code changes reload live. Run `./to-prod.sh` before committing, or the tracked `docker-compose.yml` and `Dockerfile` will show up as deleted or modified.

Without Docker, from `services/web/`: `flask --app project run` (or `python manage.py run`).

## Lint and tests

There are no tests. Linting runs only inside the Docker build stage (`flake8==7.4.1 --ignore=E501,W503,F401`), so a flake8 error fails `docker compose build`. To check locally, from `services/web/`:

```bash
uvx --python 3.14 flake8==7.4.1 --ignore=E501,W503,F401 project manage.py
```

The root `.venv` has no Flask installed. To exercise the routes without Docker, use Flask's test client under the Docker image's Python and pins, from `services/web/`: `uv run --no-project --python 3.14 --with Flask==3.1.3 --with Werkzeug==3.1.9 python -c "from project import app; ..."`.

## How it works

- `GET /` renders the form. `POST /` reads `number_of_passwords` (default 30, max 1000), `password_length` (default 16, max 256), and the `exclude_special` checkbox (value `"1"` drops the special characters from the pool), then returns the passwords as a bare `<BR>`-joined string, not a template.
- `manage.py` wraps `app` in a `FlaskGroup`; gunicorn loads `manage:app`.
- Flask's static folder is renamed to `assets/`, but templates still reference it through `url_for('static', ...)`.
- `home.html` styles with daisyUI 5 and the Tailwind browser build from jsDelivr, and has no local CSS or JS build step.
- `home.html` optionally includes `templates/custom.headers` (`ignore missing`). The file is git-ignored and is meant for per-deployment extras such as analytics tags.
