from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from scripts.db_models import db, GeoLocation, User
from scripts.decorators import check_token
import jwt
from datetime import datetime, timedelta
import requests


app = Flask(__name__)
# database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://j270:AFA7_ce40e3@psql01.mikr.us/db_j270'
db.init_app(app)
# next string we need to put database models into other file without errors
app.app_context().push()
# configuring secret key for our app
app.config['SECRET_KEY'] = 'Very Hard To Guess Secret Key'


@app.route('/')
def hello():
    return "Hello"


@app.route('/login')
def login():
    auth_info = request.authorization

    response = check_login_data(auth_info)
    if response != 'Ok':
        return jsonify({"response": response}), 401

    # encode token
    token = jwt.encode({'login': auth_info.username, 'exp': datetime.utcnow() + timedelta(hours=1)},
                       app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token})


@app.route('/signup', methods=['POST'])
def signup():
    request_data = request.get_json()
    # check if login not exists already
    if User.query.filter_by(login=request_data['login']).first():
        return jsonify({'response': 'This login is occupied'}), 401

    hashed_password = generate_password_hash(request_data['password'], method='sha256')
    new_user = User(login=request_data['login'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'response': 'New user created'})


@app.route('/location', methods=['GET'])
@check_token(secret_key=app.config['SECRET_KEY'])
def view_locations(user):
    locations = GeoLocation.query.all()
    locations_dict = {}
    for location in locations:
        locations_dict[location.id] = {
            'ip': location.ip, 'ip_type': location.type, 'continent': location.continent_name,
            'country': location.country_name, 'city': location.city, 'zip_code': location.zip,
            'longitude': location.longitude, 'latitude': location.latitude
        }

    return jsonify(locations_dict)


@app.route('/location/<ip>', methods=['POST'])
@check_token(secret_key=app.config['SECRET_KEY'])
def add_location(user, ip):
    location = requests.get(f'http://api.ipstack.com/{ip}?access_key=1c4aa5438b65c9f5ffca1913d34971f5').json()
    location_record = GeoLocation(
        ip, location['type'], location['continent_name'], location['country_name'], location['city'], location['zip'],
        location['latitude'], location['longitude']
    )
    db.session.add(location_record)
    db.session.commit()

    return jsonify({'response': 'Your location added'})


@app.route('/location/<location_id>', methods=['DELETE'])
@check_token(secret_key=app.config['SECRET_KEY'])
def delete_location(user, location_id):
    location = GeoLocation.query.get(location_id)

    if not location:
        return jsonify({"response": "There's no such location"})

    db.session.delete(location)
    db.session.commit()

    return jsonify({'response': 'Location deleted'})


def check_login_data(auth_info):
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


def get_location(location_id):
    location = GeoLocation.query.get(location_id)
    location_dict = {
            'ip': location.ip, 'ip_type': location.type, 'continent': location.continent_name,
            'country': location.country_name, 'city': location.city, 'zip_code': location.zip,
            'longitude': location.longitude, 'latitude': location.latitude
        }
    return location_dict


#localization = GeoLocation('122.3232.2676', 'ipv5', 'Polska', 'też Polska', 'Wrocek', '50-341', 53.2123133223, 76.5544444553)
#new_user = User(login='dzik', password='byk')
# remove whole table
#db.drop_all()
#db.create_all() # In case user table doesn't exists already. Else remove it.
#db.session.add(new_user)
#db.session.commit() # This is needed to write the changes to database
#print(User.query.all())
#print(GeoLocation.query.filter_by(ip='122.3232.2').first())
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
