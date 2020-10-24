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
        if not Environment.instance().DEBUG or \
                Environment.instance().DEBUG_CHANNEL_ID == \
                context.channel.id:
            await function(context)
    wrapper.__name__ = function.__name__
    return wrapper
