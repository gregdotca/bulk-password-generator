---
rating: B3b
spec: "0.1"
updated: 2026-10-11
---

# AI Code Rating

**ACR B3b** (Maintainer: Experienced · AI Share: 51–75% · Oversight: Reviewed)

This project is rated with [AI Code Rating](https://aicoderating.com/spec/0.1/), spec version 0.1.

## How AI Was Used

The maintainer wrote Bulk Password Generator by hand in 2024: the Flask app, the password generator, the page template, and the Docker setup. In 2026 an AI coding agent switched password generation to Python's `secrets` module, added limits and input checks to the form handling, upgraded Python and the app's dependencies, added a step to the Docker build that compiles the page's CSS locally instead of loading it from a CDN, added automatic dark mode, fixed passwords being altered by the browser's HTML decoding, and wrote the project's tests. The maintainer chose the changes and the look, including the dark mode colours, and read all of the code the AI wrote.

The AI's changes are also reviewed by a second AI, and the two go back and forth until it doesn't find any more issues. That doesn't change the oversight level. Commits are marked with `Co-Authored-By: Claude Code` and, where Codex reviewed them, `Reviewed-By: Codex`.
