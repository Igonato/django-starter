#!/bin/sh
# Wait for the database to be ready

if [ "$DB_ENGINE" != "django.db.backends.sqlite3" ]
then
    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done
fi
exec "$@"
