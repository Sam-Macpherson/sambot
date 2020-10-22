"""
A file to store function decorators.
"""
from environment import Environment


def debuggable(function):
    """Marks an on_message call as debuggable, so that it can only
    be used in the environment's DEBUG_CHANNEL, if DEBUG mode
    is set to True.
    """
    async def wrapper(context):
        if Environment.get_instance().DEBUG:
            print(f'Debugging {function.__name__}.')
        if not Environment.get_instance().DEBUG or \
                Environment.get_instance().DEBUG_CHANNEL_ID == \
                context.channel.id:
            await function(context)
        else:
            print('No action taken.')
    wrapper.__name__ = function.__name__
    return wrapper
