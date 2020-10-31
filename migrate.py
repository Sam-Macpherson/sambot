import os
import sys
import importlib
from migrations import Migration


def do_migration(migration_number):
    print(f'migrating {migration_number}', end='...')
    module = importlib.import_module(f'migrations.m_{migration_number}')
    function = getattr(module, 'migration')
    migration = Migration(function)
    migration.migrate()
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
