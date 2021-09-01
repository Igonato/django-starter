# Django Starter

Near-zero configuration project template. Complete with all the necessary
development tools and deployment solutions.

Multiple versions with incremental changes:

-   **ref** - Django 3.2.6 `django-admin startproject` output for reference,
-   **env** - production-ready settings through the environment variables,
-   **min** - essential development tools and setup,
-   **master** - batteries-included starter.

| Branch | ref                | env                | min                | Badges                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------ | ------------------ | ------------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| env    | [diff][ref_env]    | -                  | -                  | [![Django CI](https://github.com/Igonato/django-starter-env/actions/workflows/django.yml/badge.svg)][env_ci]                                                                                                                                                                                                                                                                                                                                                                 |
| min    | [diff][ref_min]    | [diff][env_min]    | -                  | [![Django CI](https://github.com/Igonato/django-starter-min/actions/workflows/django.yml/badge.svg)][min_ci] [![codecov](https://codecov.io/gh/Igonato/django-starter-min/branch/master/graph/badge.svg?token=fwKGZIYWoL)](https://codecov.io/gh/Igonato/django-starter-min) [![Dependabot](https://api.dependabot.com/badges/status?host=github&repo=Igonato/django-starter-min)](#)                                                                                        |
| master | [diff][ref_master] | [diff][env_master] | [diff][min_master] | [![Django CI](https://github.com/Igonato/django-starter/actions/workflows/django.yml/badge.svg)][ci] [![CodeQL](https://github.com/Igonato/django-starter/actions/workflows/codeql-analysis.yml/badge.svg)][ql] [![codecov](https://codecov.io/gh/Igonato/django-starter/branch/master/graph/badge.svg?token=sjg69emIfX)](https://codecov.io/gh/Igonato/django-starter) [![Dependabot](https://api.dependabot.com/badges/status?host=github&repo=Igonato/django-starter)](#) |

[ref_env]: https://github.com/Igonato/django-starter/compare/ref...env
[ref_min]: https://github.com/Igonato/django-starter/compare/ref...min
[ref_master]: https://github.com/Igonato/django-starter/compare/ref...master
[env_min]: https://github.com/Igonato/django-starter/compare/env...min
[env_master]: https://github.com/Igonato/django-starter/compare/env...master
[min_master]: https://github.com/Igonato/django-starter/compare/min...master
[env_ci]: https://github.com/Igonato/django-starter-env/actions/workflows/django.yml
[min_ci]: https://github.com/Igonato/django-starter-min/actions/workflows/django.yml
[ci]: https://github.com/Igonato/django-starter/actions/workflows/django.yml
[ql]: https://github.com/Igonato/django-starter/actions/workflows/codeql-analysis.yml

## Requirements

-   Python 3.6+ ([automated tests][ci] run using three latest minor versions).
-   [Pipenv] dependency management tool (Hint: You can `pip install pipenv`).

[pipenv]: https://pipenv.pypa.io/en/latest/

## Quick Start

You can click on "Use this template" at the top right or fork/clone the repo
using Git:

```bash
git clone git@github.com:Igonato/django-starter.git projectname
cd projectname
git remote set-url origin git@github.com:teamname/projectname.git

# Copy local settings from the example and edit if necessary
cp .env.example .env

# Set up a virtual environment and install dependencies
pipenv install --dev

# Run migrations
pipenv run migrate

# Start a development server
pipenv run serve

# Run tests once
pipenv run test

# Run tests and watch for changes
pipenv run test-watch
```

## What's Inside?

### Inherited From the "Env" Starter

See the [diff][ref_env] with a vanilla `django-admin startproject` output.

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

[deployment checklist]: https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

### This Starter Adds

See the [diff][ref_min] with a vanilla `django-admin startproject` output,
or here is the [diff][env_min] with [Igonato/django-starter-env].

-   [Pipenv] for dependency management,
-   `.editorconfig` and `.isort.cfg` for editor configuration,
-   [pytest] with `pytest-cov`, `pytest-django`, `pytest-xdist`, etc...
    for unit testing,
-   [Django Debug Toolbar],
-   [Django Extensions],
-   Custom User model - often needed and AUTH_USER_MODEL needs to be set
    before creating any migrations or running migrate for the first time
    ([Docs](https://docs.djangoproject.com/en/dev/topics/auth/customizing/]))

[igonato/django-starter-env]: https://github.com/Igonato/django-starter-env
[pytest]: https://docs.pytest.org/
[django debug toolbar]: https://django-debug-toolbar.readthedocs.io/
[django extensions]: https://django-extensions.readthedocs.io/

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
-   [Pipenv] dependency management tool (Hint: You can `pip install pipenv`).

[pipenv]: https://pipenv.pypa.io/en/latest/

## Installation

```bash
# Clone the repo
git clone git@github.com:teamname/projectname.git
cd projectname

# Copy local settings from the example and edit if necessary
cp .env.example .env

# Set up a virtual environment and install dependencies
pipenv install --dev

# Run migrations
pipenv run migrate
```

## Development

You can start the Django development server by using the `serve` script:

```bash
pipenv run serve
```

Run tests once:

```bash
pipenv run test
```

Run tests and watch for file changes:

```bash
pipenv run test-watch
```

Start an interactive shell:

```bash
pipenv run shell
```

Open a Jupyter notebook:

```bash
pipenv run notebook
```

Note: with the current versions of Django and Django Extensions in order to work
with models in the interactive mode you will need to add the following code at
the start:

```python
import os
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
```
