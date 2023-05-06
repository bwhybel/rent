from flask_login import UserMixin, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email
