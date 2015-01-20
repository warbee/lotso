from app import db
import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(1000))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    role_id = db.Column(db.Integer, default=0)
    status = db.Column(db.String(255))
    cycle_date = db.Column(db.DateTime)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.email

    def __repr__(self):
        return '<id %r>' % self.id

class Bag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    gold_marbles = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<id %r>' % self.id

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    gold_marbles = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    title = db.Column(db.String(255))
    desc = db.Column(db.String(4000))
    link = db.Column(db.String(1000))

    def __repr__(self):
        return '<id %r>' % self.id