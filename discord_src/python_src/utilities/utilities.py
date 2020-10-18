"""
A location to store generic helpers and utilities.
"""
from typing import Union


def truthy(var: Union[str, int]):
    """
    Uses the given string variable and determines the truth
    value it represents.
    Truthy values: t, true, 1, yes
    Anything that is not truthy is falsy.
    """
    truthy_values = ['t', 'true', 1, 'yes']
    if isinstance(var, str):
        var = var.lower()
    return var in truthy_values
