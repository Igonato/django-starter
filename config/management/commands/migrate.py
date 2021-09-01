"""Automatically create a database when migrating if needed"""

import re
from copy import deepcopy

from django.conf import settings
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db import (
    DEFAULT_DB_ALIAS,
    ConnectionHandler,
    OperationalError,
    connections,
)


class Command(MigrateCommand):
    def handle(self, *args, **options):
        try:
            super().handle(*args, **options)
        except OperationalError as exception:
            if re.search(
                r'FATAL:  database "\S+?" does not exist', str(exception)
            ) or re.search(
                r'Unknown database \'\S+?\'', str(exception)
            ):
                selected_database = options["database"]
                database_config = settings.DATABASES[selected_database]
                if database_config.get("AUTO_CREATE") and self.create_db(
                    selected_database
                ):
                    super().handle(*args, **options)
                else:
                    raise
            else:
                raise

    def create_db(self, database):
        database_vendor = connections[database].vendor

        database_config = settings.DATABASES[database]
        database_config_copy = deepcopy(database_config)
        if database_vendor == "postgresql":
            database_config_copy["NAME"] = "postgres"
        elif database_vendor == "mysql":
            database_config_copy["NAME"] = "mysql"
        else:
            return False

        handler = ConnectionHandler({
            DEFAULT_DB_ALIAS: database_config_copy,
        })

        database_name = database_config["NAME"]
        with handler[DEFAULT_DB_ALIAS].cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {database_name}")

        self.stdout.write(f"Auto-created database '{database_name}'")
        return True
