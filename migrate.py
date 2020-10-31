import os
import sys
import importlib
from migrations import Migration

"""
A python script to apply migrations to the 'sambot.db' SQLite database.

Usage:
$ python migrate.py <migration_number>

migration_number is any integer. Migration file names have the form:
m_x.py where x is the migration number. If x < 1000, it is padded
on the left with zeroes until it reaches 4 digits in length. Migration
files must contain 1 attribute, a function called `migration`, which
will be executed by this script.

When running migrate.py, you may provide any integer and the script
will automatically pad on the left for you. For example:

$ python migrate.py 1 

is equivalent to
$ python migrate.py 0001

but not equivalent to 
$ python migrate.py 000001

which would fail to execute.
"""


def do_migration(migration_number):
    print(f'migrating {migration_number}', end='...')
    module = importlib.import_module(f'migrations.m_{migration_number}')
    function = getattr(module, 'migration')
    Migration(function).migrate()
    print(f'done')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Wrong number of arguments.')
    else:
        if sys.argv[1].lower() == 'make':
            number_of_migrations = len([
                name for name in os.listdir('migrations')
                if os.path.isfile(os.path.join('migrations', name))
                and name.startswith('m_')
            ])
            new_migration = str(number_of_migrations + 1).zfill(4)
            lines = [
                f'from playhouse.migrate import *\n',
                f'\n',
                f'\n',
                f'"""\n'
                f'Migration {new_migration}.\n',
                f'Add a description here.\n',
                f'"""\n'
                f'\n',
                f'\n',
                f'def migration():\n',
                f'\tdatabase = SqliteDatabase(\'sambot.db\')\n',
                f'\tmigrator = SqliteMigrator(database)\n',
                f'\t# Write migration here.\n',
                f'\t\n',
            ]
            with open(f'migrations/m_{new_migration}.py', 'w') as f:
                f.writelines(lines)
        else:
            migration = sys.argv[1].zfill(4)
            do_migration(migration)
