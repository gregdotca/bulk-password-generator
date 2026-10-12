# Changelog

## 2026-10-11

- Generate passwords with Python's `secrets` module instead of `random`. `random` is not cryptographically secure, so its output could in principle be predicted. The output format, defaults, and character pools are unchanged. The two `random.shuffle` calls were dropped, since they add nothing once each character is picked independently and securely.
- Cap each request at 1,000 passwords of up to 256 characters. There was no limit before, so one request for millions of passwords could keep a gunicorn worker busy until it timed out (200,000 passwords already took over 4 seconds). Larger values are lowered to the cap.
- Fall back to the defaults (30 passwords, 16 characters) when a field is non-numeric, zero, or negative. Before, non-numeric input raised a `ValueError` and returned a 500 error.
- Update the copyright notice in `LICENSE` and `README.md` to `Copyright (c) 2024-2026 Greg Chetcuti <greg@chetcuti.com>`.
- Add `CLAUDE.md` with guidance for Claude Code: how to run, switch to dev, and lint the app, and how the code fits together.
- Add this changelog.
