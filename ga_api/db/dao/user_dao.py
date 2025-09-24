from ga_api.db.dao.abstract_dao import AbstractDAO
from ga_api.db.models.users import User


class UserDAO(AbstractDAO[User]):
    def __init__(self, session):
        super().__init__(User, session)
