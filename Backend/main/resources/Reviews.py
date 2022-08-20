from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import ReviewModel, PoemModel
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required
from main.auth.decorators import admin_required
from main.mail.mail_related import send_mail


class Review(Resource):

    def get(self, id):
        review = db.session.query(ReviewModel).get_or_404(id)
        return review.to_json()


    @admin_required
    def delete(self, id):
        review = db.session.query(ReviewModel).get_or_404(id)
        db.session.delete(review)
        db.session.commit()
        return 'Review deleted', 204


class Reviews(Resource):

    def get(self):
        page = 1
        per_page = 5
        reviews = db.session.query(ReviewModel)
        filters = request.get_json()
        if filters:
            for key, value in filters.items():
                if key == "page":
                    page = int(value)
                if key == "per_page":
                    per_page = int(value)
                #anda
                if key == "userId":
                    reviews = reviews.filter(ReviewModel.user_id == value)
                #anda
                if key == "poemId":
                    reviews = reviews.filter(ReviewModel.poem_id == value)
                #anda
                if key == "rating":
                    reviews = reviews.filter(ReviewModel.rating == value)
        reviews = reviews.paginate(page, per_page, True, 20)
        return jsonify({'reviews': [review.to_json_short() for review in reviews.items],
                        'total': reviews.total, 'pages': reviews.pages, 'page': page})


    @jwt_required()
    def post(self):
        """El envio de mail funciona pero larga un error a la hora de hacer el post, 
        se se intenta de nuevo este respone bien con que no puede volver a realizar una review en el mismo poema"""

        reviewer_id =  get_jwt_identity()
        reviews = db.session.query(ReviewModel).all()
        review_same_user = False

        review = ReviewModel.from_json(request.get_json())
        review.user_id = reviewer_id

        for item in reviews:
            if item.user_id == reviewer_id and item.poem_id == review.poem_id:
                review_same_user = True
                break
        poem = db.session.query(PoemModel).get_or_404(review.poem_id)
        user_poem_id = poem.user_id
        if reviewer_id != user_poem_id and not review_same_user:
            try:
                db.session.add(review)
                db.session.commit()
                response = send_mail([review.poem.user.email], 'Your poem got a review!', 'new_review', review=review)
                return review.to_json(), 201
            except Exception as e:
                #db.session.rollback()
                return str(e), 409
        else:
            return 'Self-reviewing or making more reviews on this poem is not allowed', 403
