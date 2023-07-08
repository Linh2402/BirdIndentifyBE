from my_app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from my_app.models.history import History


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.Date, default=date.today)
    role = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, gmail={self.email})"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def delete_user(self):
        histories = History.query.filter_by(user_id=self.id).all()
        for history in histories:
            history.delete_history()

        db.session.delete(self)
        db.session.commit()
