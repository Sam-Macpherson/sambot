from playhouse.migrate import *

from models import Guild, TriggeredResponse

"""
This migration alters the TriggeredResponse object to use a foreign
key reference to Guild instead of storing a Guild's ID as an 
integer.

1. Add the FK(Guild) to the TriggeredResponse table
2. 
For every triggered response:
    find the guild which matches the stored guild_id
    store the guild in the new FK field
3. Remove the guild_id field from the TriggeredResponse table
"""


def migration():
    database = SqliteDatabase('sambot.db')
    migrator = SqliteMigrator(database)

    # Step 1
    guild_fk = ForeignKeyField(
        Guild,
        Guild.guild_id,
        backref='triggered_responses',
        null=True,
    )
    # migrate(
    #     migrator.add_column('triggeredresponse', 'guild', guild_fk)
    # )
    # Step 2
    triggered_responses = TriggeredResponse.select()
    for triggered_response in triggered_responses:
        instance = triggered_response.get()
        guild_id = instance.guild_id
        guild = Guild.get_or_none(guild_id=guild_id)
        if not guild:
            # Should never see this.
            print(f'The guild for this triggered response was not found.'
                  f'TR: {instance.id}, guild_id: {guild_id}')
        else:
            instance.guild = guild
            instance.save()
    # Step 3
    migrate(
        migrator.drop_column('triggeredresponse', 'guild_id')
    )
