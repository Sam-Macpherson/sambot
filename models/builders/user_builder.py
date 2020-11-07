from models import User
from models.currencies import Wallet


class UserBuilder:

    @staticmethod
    def build(**kwargs):
        user = User.create(**kwargs)
        Wallet.create(user=user)
        return user
