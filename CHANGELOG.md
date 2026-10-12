# Changelog

## 2026-10-11

- Build Tailwind 4.3.3 and daisyUI 5.7.46 CSS at Docker build time instead of loading them from jsDelivr. The page used the in-browser Tailwind compiler, a floating `daisyui@5` tag, and a separate themes file pinned to `5.0.0`, so every visitor downloaded and ran a third-party compiler, and upstream releases could change the styling without any change here. The build now produces a single minified `app.css` (about 27 KB) with only the classes the template uses and the `bumblebee` theme.
  - `services/web/Dockerfile:17-31,39-40,75`: the builder stage downloads the Tailwind standalone CLI (checksum-verified, amd64 and arm64) and builds the CSS; the final stage copies in `app.css`.
  - `services/web/project/styles/app.css`: new Tailwind input file.
  - `services/web/project/styles/daisyui-5.7.46.mjs`: vendored daisyUI plugin, checked against the release's SHA-256.
  - `services/web/project/templates/home.html:8`: load `app.css` locally instead of the three CDN files.
  - `.gitignore`: ignore the generated `project/assets/app.css`.
  - `CLAUDE.md`: document the CSS build and the dev watcher.
- Add `<!doctype html>`, `lang="en"`, and a viewport meta tag to the page, and remove two classes and a click handler that did nothing. Without a doctype the browser rendered the page in quirks mode, which Tailwind's base styles don't expect; without `lang` screen readers had to guess the language; and without a viewport tag phones showed a zoomed-out desktop layout. `form` isn't a daisyUI class and `justify-left` isn't a Tailwind class (it's `justify-start`), so neither did anything. The Generate button's `onclick="$('#loading').show();"` called jQuery, which the page doesn't load, to show a `#loading` element that doesn't exist, so every click logged a `$ is not defined` error. File changed: `services/web/project/templates/home.html:1-4,15-16,24`.
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
