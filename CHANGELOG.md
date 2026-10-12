# Changelog

## 2026-10-11

- Update Python from 3.9 to 3.14, Flask from 2.3.0 to 3.1.3, Werkzeug from 2.3.0 to 3.1.9, gunicorn from 20.1.0 to 26.2.0, and flake8 from 3.9.1 to 7.4.1, and remove Flask-SQLAlchemy and psycopg2-binary. Python 3.9 reached end of life in October 2025, so it no longer gets security fixes. gunicorn 20.1.0 has a request-smuggling vulnerability (CVE-2024-1135, fixed in 22.0.0). The app never used a database, so the two database packages were only making the image bigger. gunicorn 26 also adds a control socket for its `gunicornc` tool, which this app doesn't use; the `app` user can't create it in `/home/app/.gunicorn`, so it's turned off with `--no-control-socket`. flake8 7 reports W503 (line break before a binary operator), which conflicts with W504 and current PEP 8 advice, so it's ignored alongside the existing E501 and F401.
  - `services/web/requirements.txt`: new versions, and drop Flask-SQLAlchemy and psycopg2-binary.
  - `services/web/Dockerfile:6,21,23,35`: `python:3.14.7-slim` for both stages, and flake8 7.4.1 with W503 ignored.
  - `docker-compose.yml:10`: add `--no-control-socket` to the gunicorn command.
  - `CLAUDE.md`: update the lint and test commands, note the control socket setting, and drop the note about the unused packages.
- Generate passwords with Python's `secrets` module instead of `random`. `random` is not cryptographically secure, so its output could in principle be predicted. The output format, defaults, and character pools are unchanged. The two `random.shuffle` calls were dropped, since they add nothing once each character is picked independently and securely.
- Cap each request at 1,000 passwords of up to 256 characters. There was no limit before, so one request for millions of passwords could keep a gunicorn worker busy until it timed out (200,000 passwords already took over 4 seconds). Larger values are lowered to the cap.
- Fall back to the defaults (30 passwords, 16 characters) when a field is non-numeric, zero, or negative. Before, non-numeric input raised a `ValueError` and returned a 500 error.
- Update the copyright notice in `LICENSE` and `README.md` to `Copyright (c) 2024-2026 Greg Chetcuti <greg@chetcuti.com>`.
- Add `CLAUDE.md` with guidance for Claude Code: how to run, switch to dev, and lint the app, and how the code fits together.
- Add this changelog.
