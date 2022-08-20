from .. import db


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    poem_id = db.Column(db.Integer, db.ForeignKey('poem.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user = db.relationship('User', back_populates="reviews", uselist=False, single_parent=True)
    poem = db.relationship('Poem', back_populates="reviews", uselist=False, single_parent=True)

    def to_json(self):
        json_string = {
            'id': self.id,
            'user_id': self.user_id,
            'poem_id': self.poem_id,
            'rating': self.rating,
            'comment': self.comment,
        }
        return json_string

    def to_json_short(self):
        json_string = {
            'rating': self.rating,
            'comment': self.comment,
        }
        return json_string

    @staticmethod
    def from_json(json_string):
        id = json_string.get('id')
        user_id = json_string.get('user_id')
        poem_id = json_string.get('poem_id')
        rating = json_string.get('rating')
        comment = json_string.get('comment')
        return Review(id=id, user_id=user_id, poem_id=poem_id, rating=rating, comment=comment)
