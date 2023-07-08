from my_app import db
from my_app.models.prediction import Prediction


class History(db.Model):
    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    url = db.Column(db.String(255))

    def __repr__(self):
        return f"<History {self.id}>"

    def to_json(self):
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d"),
            "user_id": self.user_id,
            "url": self.url,
        }

    def delete_history(self):
        predictions = Prediction.query.filter_by(history_id=self.id).all()
        for prediction in predictions:
            prediction.delete_prediction()

        db.session.delete(self)
        db.session.commit()
