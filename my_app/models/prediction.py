from my_app import db


class Prediction(db.Model):
    __tablename__ = "prediction"

    id = db.Column(db.Integer, primary_key=True)
    confidence = db.Column(db.Float)
    history_id = db.Column(db.Integer, db.ForeignKey("history.id", ondelete="CASCADE"))
    bird_id = db.Column(db.Integer, db.ForeignKey("birds.id"))

    def __repr__(self):
        return f"Prediction(id={self.id}, confidence={self.confidence}, history_id={self.history_id}, bird_id={self.bird_id})"

    def to_json(self):
        return {
            "id": self.id,
            "confidence": self.confidence,
            "history_id": self.history_id,
            "bird_id": self.bird_id,
        }

    def delete_prediction(self):
        db.session.delete(self)
        db.session.commit()
