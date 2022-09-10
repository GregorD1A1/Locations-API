

def check_token(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        else:
            return jsonify({'response': 'No token here'}), 401

        try:
            token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except InvalidSignatureError:
            return jsonify({'response': 'Wrong token'}), 401
        except ExpiredSignatureError:
            return jsonify({'response': 'Token expired'}), 401

        user = User.query.filter_by(login=token_data['login']).first()

        return function(user, *args, **kwargs)

    return decorator
