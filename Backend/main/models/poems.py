from .. import db
from sqlalchemy.sql import func
from datetime import datetime


class Poem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.now())
    # Un Poema es escrito por un Usuario
    user = db.relationship('User', back_populates="poems", uselist=False, single_parent=True)
    # Un Poema tiene n reviews
    reviews = db.relationship('Review', back_populates="poem", uselist=True, single_parent=True, cascade = 'all, delete-orphan')

    def to_json(self):
        reviews = [review.to_json_short() for review in self.reviews]
        json_string = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'time_created': str(self.time_created.strftime("%d-%m-%Y")),
            'reviews_count': len(reviews),
        }
        return json_string

    def to_json_short(self):
        reviews = [review.to_json_short() for review in self.reviews]
        #print(reviews[0])
        n = 0
        for _ in reviews:
            #prom_rating = reviews[n]['rating'] + prom_rating
            print(reviews[n]['rating'])
            n += 1
        json_string = {
            'id':self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'time_created': str(self.time_created.strftime("%d-%m-%Y")),
            'reviews_count': len(reviews),
            #'rating': reviews
        }
        return json_string

    @staticmethod
    def from_json(json_string):
        id = json_string.get('id')
        user_id = json_string.get('user_id')
        title = json_string.get('title')
        content = json_string.get('content')
        return Poem(id=id, user_id=user_id, title=title, content=content)
