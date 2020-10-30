from playhouse.migrate import *

from models import Guild, TriggeredResponse

"""
This migration alters the TriggeredResponse object to store a
type, one of (text, image), and an image blob.
"""


def migration():
    database = SqliteDatabase('sambot.db')
    migrator = SqliteMigrator(database)

    type_field = IntegerField(
        choices=(
            (1, 'TEXT'),
            (2, 'IMAGE')
        ),
        null=True
    )
    image_field = BlobField(null=True)
    # Step 1: remove non-null constraint on response, add both fields.
    migrate(
        migrator.drop_not_null('triggeredresponse', 'response'),
        migrator.add_column('triggeredresponse', 'type', type_field),
        migrator.add_column('triggeredresponse', 'image', image_field)
    )
    # Step 2: assign all existing triggered responses a type.
    triggered_responses = TriggeredResponse.select()
    for tr in triggered_responses:
        if tr.type is None:
            if tr.response is not None:
                tr.type = 1
            elif tr.image is not None:
                tr.type = 2
            tr.save()
    # Step 3: Add null constraint to type
    migrate(
        migrator.add_not_null('triggeredresponse', 'type')
    )
    # Step 4: Add triggered_image_cooldown to Guild, and rename
    # triggered_response_cooldown to triggered_text_cooldown on Guild.
    triggered_image_cooldown_field = IntegerField(default=0)
    migrate(
        migrator.add_column('guild',
                            'triggered_image_cooldown',
                            triggered_image_cooldown_field),
        migrator.rename_column('guild',
                               'triggered_response_cooldown',
                               'triggered_text_cooldown')
    )
