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
        migration = sys.argv[1].zfill(4)
        do_migration(migration)
