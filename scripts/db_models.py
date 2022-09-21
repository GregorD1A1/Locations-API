from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class GeoLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(40), unique=True)
    type = db.Column(db.String(4))
    continent_name = db.Column(db.String(20))
    country_name = db.Column(db.String(30))
    city = db.Column(db.String(50))
    zip = db.Column(db.String(6))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __init__(self, ip, ip_type, continent, country, city, zip_code, latitude, longitude):
        self.ip = ip
        self.type = ip_type
        self.continent_name = continent
        self.country_name = country
        self.city = city
        self.zip = zip_code
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f'Localisation {self.ip}'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return f'User {self.login}'
