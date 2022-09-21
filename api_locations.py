from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from scripts.db_models import db, GeoLocation, User
from scripts.decorators import check_token
from sqlalchemy.exc import OperationalError, IntegrityError
import jwt
from datetime import datetime, timedelta
import requests


app = Flask(__name__)
# database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://j270:AFA7_ce40e3@psql01.mikr.us/db_j270'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://j270:AFe40e3@psql01.mikr.us/db_j270'
db.init_app(app)
# next string we need to put database models into other file without errors
app.app_context().push()
# configuring secret key for our app
app.config['SECRET_KEY'] = 'Very Hard To Guess Secret Key'
CORS(app)


@app.route('/')
def hello():
    return "Hello"


@app.route('/login')
def login():
    """
    Function for logging in. Checks login data, and, if it's correct, generates encoded jwt token.
    Also checks if there is valid connection with database.
    :return: json with jwt token or json with login error name.
    """
    auth_info = request.authorization
    try:
        response = check_login_data(auth_info)
    except OperationalError:
        response = "Database connection failed"

    if response != 'Ok':
        return jsonify({"response": response}), 401

    # encode token
    token = jwt.encode({'login': auth_info.username, 'exp': datetime.utcnow() + timedelta(hours=1)},
                       app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'response': '', 'token': token})


@app.route('/signup', methods=['POST'])
def signup():
    """
    Registration function. Creates new user and adds him to database. Checks if there is valid connection with database.
    :return: json with confirmation of registration or responce that login is occuped.
    """
    request_data = request.get_json()
    hashed_password = generate_password_hash(request_data['password'], method='sha256')
    new_user = User(login=request_data['login'], password=hashed_password)
    # check database conection
    try:
        db.session.add(new_user)
        db.session.commit()
    except OperationalError:
        return jsonify({'response': 'Database connection failed'}), 401
    # integrity error appears when we are trying to add to database another value with same unique key
    except IntegrityError:
        db.session.rollback()
        return jsonify({'response': 'This login is occupied'}), 401

    return jsonify({'response': 'New user created'})


@app.route('/location', methods=['GET'])
@check_token(secret_key=app.config['SECRET_KEY'])
def view_locations(user):
    """
    Shows content of localization's database. Available only for logged in users.
    :param user: User object, taken from check_token decorator.
    :return: JSON with locations.
    """
    locations = GeoLocation.query.all()
    locations_dict = {}
    for location in locations:
        locations_dict[location.id] = {
            'id': location.id, 'ip': location.ip, 'ip_type': location.type, 'continent': location.continent_name,
            'country': location.country_name, 'city': location.city, 'zip_code': location.zip,
            'longitude': location.longitude, 'latitude': location.latitude
        }

    return jsonify(locations_dict)


@app.route('/location/<ip>', methods=['POST'])
@check_token(secret_key=app.config['SECRET_KEY'])
def add_location(user, ip):
    """
    Check ip data on ipstack and adds it to database. Available only for logged in users.
    :param user: User object, taken from check_token decorator.
    :param ip: ip adress to check parameters.
    :return: JSON with confirmation.
    """
    location = requests.get(f'http://api.ipstack.com/{ip}?access_key=1c4aa5438b65c9f5ffca1913d34971f5').json()
    location_record = GeoLocation(
        ip, location['type'], location['continent_name'], location['country_name'], location['city'], location['zip'],
        location['latitude'], location['longitude']
    )
    try:
        db.session.add(location_record)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'response': 'IP adress already exists'}), 401

    return jsonify({'response': 'Your location added'})


@app.route('/location/<location_id>', methods=['DELETE'])
@check_token(secret_key=app.config['SECRET_KEY'])
def delete_location(user, location_id):
    """
    Removes location from database. Available only for logged in users.
    :param user: User object, taken from check_token decorator.
    :param location_id: Id of location to remove.
    :return: JSON with confirmation.
    """
    location = GeoLocation.query.get(location_id)

    if not location:
        return jsonify({"response": "There's no such location"})

    db.session.delete(location)
    db.session.commit()

    return jsonify({'response': 'Location deleted'})


def check_login_data(auth_info):
    """
    Checks if login data is correct and if there is such user in database.
    :param auth_info: Authentication data.
    :return: Error name or 'Ok' sentence.
    """
    # check data completeness
    if not auth_info or not auth_info.username or not auth_info.password:
        return 'Empty login/password'
    # check login
    user = User.query.filter_by(login=auth_info.username).first()
    if not user:
        return "There's no such user"
    # check password
    if not check_password_hash(user.password, auth_info.password):
        return 'Wrong password'

    return 'Ok'

# recreate whole database
#db.drop_all()
#db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
