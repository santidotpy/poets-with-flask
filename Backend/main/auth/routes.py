from os import access
from flask import request, jsonify, Blueprint
from .. import db
from main.models import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token


auth = Blueprint('auth', __name__, url_prefix='/auth')

# modifico user con name ya que asi lo tenemos nosotros en la db
#@jwt_required este no se si va aca
@auth.route('/login', methods=['POST'])
def login():
    user = db.session.query(UserModel).filter(UserModel.name == request.get_json().get('name')).first_or_404()
    if user.validate_pass(request.get_json().get('password')):
        access_token = create_access_token(identity=user)
        data = {'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'access_token': access_token
                }
        return data, 200
    else:
        return 'Incorrect Password', 401
