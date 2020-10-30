
class Migration:
    """A paper-thin wrapper for running migrations."""
    def __init__(self, migration=None):
        self._migration = migration

    def migrate(self):
        self._migration()
