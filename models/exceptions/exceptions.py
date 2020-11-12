"""A place to store the custom exceptions for models."""


class InsufficientFundsError(ValueError):
    detail = 'Insufficient funds.'
