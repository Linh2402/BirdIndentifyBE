from my_app import db


class Bird(db.Model):
    __tablename__ = "birds"

    id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(50))
    vietnamese_name = db.Column(db.String(50))
    scientific_name = db.Column(db.String(50))
    bird_order = db.Column(db.String(50))
    family = db.Column(db.String(50))
    description = db.Column(db.Text)
    distribution = db.Column(db.Text)
    diet = db.Column(db.Text)
    conservation_status = db.Column(db.String(100))
    class_name = db.Column(db.String(50))
    height = db.Column(db.String(50))
    weight = db.Column(db.String(50))

    def __repr__(self):
        return f"<Bird {self.common_name}>"

    def to_json(self):
        bird_json = {
            "id": self.id,
            "common_name": self.common_name,
            "vietnamese_name": self.vietnamese_name,
            "scientific_name": self.scientific_name,
            "bird_order": self.bird_order,
            "family": self.family,
            "description": self.description,
            "distribution": self.distribution,
            "diet": self.diet,
            "conservation_status": self.conservation_status,
            "class_name": self.class_name,
            "height": self.height,
            "weight": self.weight,
        }

        return bird_json
