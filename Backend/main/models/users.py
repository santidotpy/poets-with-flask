from email.policy import default
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    poems = db.relationship(
        'Poem', back_populates="user", uselist=True, cascade='all, delete-orphan', single_parent=True)
    reviews = db.relationship(
        'Review', back_populates="user", uselist=True, cascade='all, delete-orphan', single_parent=True)


    @property
    def plain_password(self):
        raise AttributeError('Password no permitida')

    @plain_password.setter
    def plain_password(self, password):
        self.password = generate_password_hash(password)

    def validate_pass(self, password):
        # bien True mal False
        return check_password_hash(self.password, password)

    def to_json(self):
        poems = [poem.to_json_short() for poem in self.poems]
        reviews = [review.to_json_short() for review in self.reviews]
        json_string = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'admin': self.admin,
            'poems_count': len(poems),
            'poems': poems,
            'reviews_count': len(reviews),
            'reviews': reviews,
        }
        return json_string

    # agrego el id para poder verlo mejor en la lista de users y facilitar las consultas
    def to_json_short(self):
        poems = [poem.to_json_short() for poem in self.poems]
        reviews = [review.to_json_short() for review in self.reviews]
        json_string = {
            'id':self.id,
            'name': self.name,
            'poems_count': len(poems),
            'reviews_count': len(reviews),
        }
        return json_string

    @staticmethod
    def from_json(json_string):
        id = json_string.get('id')
        name = json_string.get('name')
        email = json_string.get('email')
        password = json_string.get('password')
        admin = json_string.get('admin')
        return User(id=id, name=name, email=email, plain_password=password, admin=admin)
