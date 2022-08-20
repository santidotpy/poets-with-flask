from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import UserModel, PoemModel, ReviewModel
from sqlalchemy import func
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required
from main.auth.decorators import admin_required

class User(Resource):

    @jwt_required(optional=True)
    def get(self, id):
        user = db.session.query(UserModel).get_or_404(id)
        token_id = get_jwt_identity()
        claims = get_jwt()
        if token_id == user.id or claims['admin']: # aca el claims puede ser que sea {} vacia
            return user.to_json()
        else:
            return user.to_json_short()

    @jwt_required()
    def put(self, id):
        token_id = get_jwt_identity()
        user = db.session.query(UserModel).get_or_404(id)
        data = request.get_json().items()
        if token_id == user.id:
            for key, value in data:
                setattr(user, key, value)
            db.session.add(user)
            db.session.commit()
            return user.to_json(), 201
        else:
            return 'Only owner can modify', 403

    @admin_required
    def delete(self, id):
        user = db.session.query(UserModel).get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204


class Users(Resource):
    def get(self):
        page = 1
        per_page = 5
        users = db.session.query(UserModel)
        filters = request.get_json()
        if filters:
            for key, value in filters.items():
                if key == "page":
                    page = int(value)
                if key == "per_page":
                    per_page = int(value)
                # anda
                if key == "name":
                    users = users.filter(UserModel.name.like("%"+value+"%"))
                #anda
                if key == "poems_count":
                    users = users.outerjoin(UserModel.poems).group_by(UserModel.id).having(func.count(PoemModel.id)>=value)
                #anda
                if key == "review_count":
                    users = users.outerjoin(UserModel.reviews).group_by(UserModel.id).having(func.count(ReviewModel.id)>=value)
                #anda
                if key == "order_by_name":
                    if value == 'name_desc':
                        users = users.order_by(UserModel.name.desc())
                    if value == 'name_asc':
                        users = users.order_by(UserModel.name)
                #anda
                if key == "order_by_poems_count":
                    if value == 'poems_count_desc':
                        users = users.outerjoin(UserModel.poems).group_by(UserModel.id).order_by(func.count(PoemModel.id).desc())
                    if value == 'poems_count_asc':
                        users = users.outerjoin(UserModel.poems).group_by(UserModel.id).order_by(func.count(PoemModel.id))
        users = users.paginate(page, per_page, True, 20)
        return jsonify({'users': [user.to_json_short() for user in users.items],
                        'total': users.total, 'pages': users.pages, 'page': page})
    

    def post(self):
        user = UserModel.from_json(request.get_json())
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            return 'Formato no correcto ' + str(e), 400
        return user.to_json(), 201
