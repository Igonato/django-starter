# Django "Env" Starter

[![Django CI](https://github.com/Igonato/django-starter-env/actions/workflows/django.yml/badge.svg)][ci]

The bare-bones and unassuming version of [Igonato/django-starter]. Check out that
repo for more versions, issues, and discussions. This repo is here exclusively
to be used as a template.

[ci]: https://github.com/Igonato/django-starter-env/actions/workflows/django.yml
[igonato/django-starter]: https://github.com/Igonato/django-starter

Minimalistic Django 3.2+ project starter. Kept close to the vanilla
`django-admin startproject` output, no weird folder structure, no 3rd-party
configuration tools, just a single `settings.py` with secure defaults and
environment variables for secrets and things that can differ between the
environments.

## Requirements

-   Python 3.6+ ([automated tests][ci] run using three latest minor versions).

## Quick Start

You can click on "Use this template" at the top right or fork/clone the repo
using Git:

```bash
git clone git@github.com:Igonato/django-starter-env.git projectname
cd projectname
git remote set-url origin git@github.com:teamname/projectname.git

# Set up a virtual environment*
python -m venv .venv
source .venv/bin/activate

# Install requirements
pip install Django

# Load development settings*
cp .env.example .env
set -o allexport; source .env; set +o allexport

# Run migrations
python manage.py migrate

# Run development server
python manage.py runserver

# *: these steps are different on Windows
```

## What's Inside?

See the [diff] with a vanilla `django-admin startproject` output.

Settings.py is changed to be secure by default (basically what you would
get by following the official [deployment checklist]), accept environment
variables for overrides (no 3rd-party configuration tools, just `os.environ`
with a few helper functions), and a couple of time/nerve-saving settings from
the personal experience:

-   Unset `SECRET_KEY` raises an exception,
-   SSL redirect and secure cookies by default,
-   Option to switch on/off cache and language middleware,
-   `APPEND_SLASH = False`. Faced with a 301 response on a POST request, API
    consumers behave unpredictably, so instead a 404 response is preferred
    since it produces an obvious error on every client when the trailing slash
    is missing,
-   `django.security.DisallowedHost` logger disabled. Some environments perform
    health-checks by poking your webserver at regular intervals using the
    machine's ip which spams the error, which will, in turn, spam your admin
    email. Address that first, if it applies to you, then you can re-enable the
    logger.

Additionally, the template comes with:

-   `.gitignore` file,
-   `.env.example` file with settings for a local development environment
    (you'll need to load it manually in your preferred way),
-   `README.md`. <kbd>Ctrl+F</kbd> "&#67;UT HERE" and delete everything above
    for a starting point for your project README,
-   `LICENSE` - 0BSD License for the template. You probably want to
    delete/replace the file.

[diff]: https://github.com/Igonato/django-starter/compare/ref...env
[deployment checklist]: https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

## Deployment

This version of the template doesn't assume any deployment environment, you can
use your favorite one. Regardless of your choice, don't forget to set
`SECRET_KEY` and `ALLOWED_HOSTS` variables. Also, after testing it for some
time you probably want to bump up `SECURE_HSTS_SECONDS` value to something more
meaningful.

---

<!----- CUT HERE ----->

# Project Name

<!-- [![Django CI](https://github.com/teamname/projectname/actions/workflows/django.yml/badge.svg)](https://github.com/teamname/projectname/actions/workflows/django.yml) -->

Project Name is built using [Django Web Framework].

[django web framework]: https://www.djangoproject.com/

## Requirements

-   Python 3.6+.

## Installation

```bash
# Clone the repo
git clone git@github.com:teamname/projectname.git
cd projectname

# Copy .env.example to .env and edit it if necessary
cp .env.example .env

# Set up a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the requirements
pip install -r requirements.txt

# Run the migrations
python manage.py migrate
```

## Development

You can start the Django development server by activating the virtual
environment and using the `runserver` command:

```bash
source .venv/bin/activate

python manage.py runserver
```
