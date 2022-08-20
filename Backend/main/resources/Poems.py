from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import PoemModel, ReviewModel, UserModel
from sqlalchemy import func
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required
from main.auth.decorators import admin_required
from datetime import datetime

class Poem(Resource):
    # este no estoy muy  seguro si el jwt debe de ser obligatorio u opcional xd
    #@jwt_required(optional=False)
    def get(self, id):
        poem = db.session.query(PoemModel).get_or_404(id)
        return poem.to_json()

    @jwt_required(optional=False)
    def put(self, id):
        user_id = get_jwt_identity()
        poem = db.session.query(PoemModel).get_or_404(id)
        claims = get_jwt()
        data = request.get_json().items()
        if poem.user_id == user_id or claims['admin']:
            for key, value in data:
                setattr(poem, key, value)
            db.session.add(poem)
            db.session.commit()
            return poem.to_json(), 201
        else:
            return 'No permitido', 403

    @admin_required
    def delete(self, id):
        user_id = get_jwt_identity()
        poem = db.session.query(PoemModel).get_or_404(id)
        claims = get_jwt()
        if poem.user_id == user_id or claims['admin']:
            db.session.delete(poem)
            db.session.commit()
            return '', 204
        else:
            return 'No permitido', 403


class Poems(Resource):
    # Obtener lista de poemas
    @jwt_required()
    def get(self):
        page = 1
        per_page = 5
        user_id = get_jwt_identity()
        # Obtener valores del poemas
        poems = db.session.query(PoemModel)
        filters = request.get_json()
        if filters:
            for key, value in filters.items():
                if key == "page":
                    page = int(value)
                if key == "per_page":
                    per_page = int(value)
                if user_id:
                    if key == "date_gte":
                        poems = poems.filter(PoemModel.time_created >= datetime.strptime(value, '%d-%m-%Y'))
                    if key == "date_lte":
                        poems = poems.filter(PoemModel.time_created <= datetime.strptime(value, '%d-%m-%Y'))
                    if key == "title":
                        poems = poems.filter(PoemModel.title == value)
                    if key == "review_gte":
                        poems = poems.outerjoin(PoemModel.reviews).group_by(PoemModel.id).having(func.avg(ReviewModel.rating)>= value)
                    if key == "review_lte":
                        poems = poems.outerjoin(PoemModel.reviews).group_by(PoemModel.id).having(func.avg(ReviewModel.rating)<= value)       
                    if key == "order_by_review":
                        if value == 'review_desc':
                            poems = poems.order_by(PoemModel.review.desc())
                        if value == 'review_asc':
                            poems = poems.order_by(PoemModel.review)
                    if key == "order_by_title":
                        if value == 'title_desc':
                            poems = poems.order_by(PoemModel.title.desc())
                        if value == 'title_asc':
                            poems = poems.order_by(PoemModel.title)
                    if key == "order_by_time_created":
                        if value == 'time_created_desc':
                            poems = poems.order_by(PoemModel.time_created.desc())
                        if value == 'time_created_asc':
                            poems = poems.order_by(PoemModel.time_created)
                else:
                    poems = poems.outerjoin(PoemModel.reviews).group_by(PoemModel.id).order_by(PoemModel.time_created, func.count(ReviewModel.rating))
        poems = poems.paginate(page, per_page, True, 20)
        return jsonify({'poems': [poem.to_json_short() for poem in poems.items],
                        'total': poems.total, 'pages': poems.pages, 'page': page})

    @jwt_required()
    def post(self):
        poem = PoemModel.from_json(request.get_json())
        user_id = get_jwt_identity()
        poem.user_id = user_id # el del token va a ser el que hizo el poema
        user = db.session.query(UserModel).get_or_404(user_id)
        poem_count = len(user.poems)
        review_count = len(user.reviews)
        if poem_count != 0:
            div = review_count/poem_count
            rest = 3-review_count%3
        if poem_count == 0 or div >=3 :
            db.session.add(poem)
            db.session.commit()
            return poem.to_json_short(), 201
        else:
            return f'You dont have enough reviews, you need {rest}', 405
