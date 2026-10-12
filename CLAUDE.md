# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A single-page Flask app that generates a list of random passwords. Live demo: https://passwords.greg.ca. All application code is in `services/web/project/__init__.py`, and the only page is `services/web/project/templates/home.html`.

## Running

Production (gunicorn on container port 5000, published on host port 8085). The gunicorn command has `--no-control-socket` because the app doesn't use gunicorn's `gunicornc` control tool, and the `app` user can't create its default socket in `/home/app/.gunicorn`:

```bash
docker compose up -d --build
```

Development uses local-only files that are excluded through `.git/info/exclude`, not `.gitignore`: `docker-compose.DEV.yml`, `services/web/Dockerfile.DEV`, `to-dev.sh`, and `to-prod.sh`. `./to-dev.sh` swaps the DEV compose file and Dockerfile into place (renaming the production ones to `*.PROD`), and `./to-prod.sh` swaps them back. The active environment's files are always `docker-compose.yml` and `services/web/Dockerfile`, and the committed ones are the production versions, so check which environment is active (`ls docker-compose.*.yml`) before editing or committing either one. Run `./to-prod.sh` before committing, or the tracked files will show up as modified. The DEV compose file runs `python manage.py run -h 0.0.0.0` on port 5000 with `services/web/` mounted at `/app`, so code changes reload live. Alongside it, `tailwindcss --watch=always` rebuilds `project/assets/app.css` into the mounted directory (`--watch=always` because the container's stdin is closed, which would otherwise stop the watcher). That file ends up owned by root on the host.

Without Docker (needs the [Tailwind standalone CLI](https://github.com/tailwindlabs/tailwindcss/releases) to build the CSS), from `services/web/`:

```bash
tailwindcss -i project/styles/app.css -o project/assets/app.css --watch &
flask --app project run
```

## Lint and tests

There are no tests. Linting runs only inside the Docker build stage (`flake8==7.4.1 --ignore=E501,W503,F401`), so a flake8 error fails `docker compose build`. To check locally, from `services/web/`:

```bash
uvx --python 3.14 flake8==7.4.1 --ignore=E501,W503,F401 project manage.py
```

The root `.venv` has no Flask installed. To exercise the routes without Docker, use Flask's test client under the Docker image's Python and pins, from `services/web/`: `uv run --no-project --python 3.14 --with Flask==3.1.3 --with Werkzeug==3.1.9 python -c "from project import app; ..."`.

## How it works

- `GET /` renders the form. `POST /` reads `number_of_passwords` (default 30, max 1000), `password_length` (default 16, max 256), and the `exclude_special` checkbox (value `"1"` drops the special characters from the pool), then returns the passwords as a bare `<BR>`-joined string, not a template. This is deliberate: keep the results unstyled (no template, CSS, or dark mode), and don't suggest styling them.
- `manage.py` wraps `app` in a `FlaskGroup`; gunicorn loads `manage:app`.
- Flask's static folder is renamed to `assets/` and served at `/assets/...`, but templates still reference it through `url_for('static', ...)`.
- **CSS:** Tailwind 4 and daisyUI 5 are built at Docker build time, not loaded from a CDN. The Tailwind standalone CLI (version and per-architecture SHA-256s pinned as `ARG`s in the Dockerfile builder stage) compiles `project/styles/app.css` into `project/assets/app.css` (gitignored), which the final stage copies in. `app.css` uses `source(none)` and `@source "../templates"`, so Tailwind scans only the templates: a class used only from Python or JS won't be in the build unless it also appears in a template. daisyUI is the vendored plugin `project/styles/daisyui-<version>.mjs`, with only the `bumblebee` (light) and `business` (dark) themes enabled. To upgrade either one, update the Dockerfile `ARG`s (and `Dockerfile.DEV`), or replace the `.mjs` file and its reference in `app.css`.
- **Dark mode:** automatic only, with no toggle, JavaScript, or `data-theme` attribute. `bumblebee --default, business --prefersdark` in `project/styles/app.css` puts `business` inside `@media (prefers-color-scheme: dark)` on `:root:not([data-theme])`, so adding `data-theme` to `<html>` would lock the page to one theme. A `color-scheme` meta tag in `home.html` tells the browser about both modes before the CSS loads. Use daisyUI theme colours (`base-content`, `base-200`, and so on), not hard-coded colour classes (`text-gray-*`, `bg-white`), so both modes keep working. Tailwind's `dark:` variant uses the same media query, so per-mode tweaks go there (the Generate button is `btn-accent dark:btn-primary`). Dark-mode overrides of theme variables live in an unlayered rule at the end of `project/styles/app.css`: a darker `--color-primary` for the button, and `bumblebee`'s `--radius-*` corner sizes so both modes match. Being unlayered, it beats daisyUI's layered theme.
- `home.html` optionally includes `templates/custom.headers` (`ignore missing`). The file is git-ignored and is meant for per-deployment extras such as analytics tags.
