import sys
import importlib
from migrations import Migration


def do_migration(migration_number):
    print(migration_number, type(migration_number))
    module = importlib.import_module(f'migrations.m_{migration_number}')
    function = getattr(module, 'migration')
    migration = Migration(function)
    migration.migrate()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Wrong number of arguments.')
    else:
        do_migration(sys.argv[1])
