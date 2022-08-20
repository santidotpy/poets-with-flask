from flask import Flask
from dotenv import load_dotenv
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv, mknod
from flask_jwt_extended import JWTManager
from flask_mail import Mail


api = Api()
db = SQLAlchemy()
jwt = JWTManager()
mail_sender = Mail()

def create_app():
    app = Flask(__name__)
    load_dotenv()

    if not path.exists(getenv("DATABASE_PATH")+getenv("DATABASE_NAME")):
        mknod(getenv("DATABASE_PATH")+getenv("DATABASE_NAME"))

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////" + getenv("DATABASE_PATH") + getenv("DATABASE_NAME")
    db.init_app(app)

    #import main.resources as resources
    from main.resources import PoemsResource, PoemResource, UsersResource, UserResource, ReviewsResource, ReviewResource

    api.add_resource(PoemsResource, '/poems')
    api.add_resource(PoemResource, '/poem/<id>')

    api.add_resource(UsersResource, '/users')
    api.add_resource(UserResource, '/user/<id>')

    api.add_resource(ReviewsResource, '/reviews')
    api.add_resource(ReviewResource, '/review/<id>')


    api.init_app(app)
    app.config['JWT_SECRET_KEY'] = getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(getenv('JWT_ACCESS_TOKEN_EXPIRES'))
    jwt.init_app(app)
    from main.auth import routes
    app.register_blueprint(routes.auth) # aca no me acuerdo si era asi o auth.routes.auth

    # Mail configs
    app.config['MAIL_HOSTNAME'] = getenv('MAIL_HOSTNAME')
    app.config['MAIL_SERVER'] = getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = getenv('MAIL_USE_TLS')
    app.config['MAIL_USERNAME'] = getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = getenv('MAIL_PASSWORD')
    app.config['FLASKY_MAIL_SENDER'] = getenv('FLASKY_MAIL_SENDER')

    # inicializar en la app
    mail_sender.init_app(app)
    
    return app
