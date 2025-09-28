from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Clinic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.id'), nullable=False)
    clinic = db.relationship('Clinic', backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shift_number = db.Column(db.Integer, nullable=False)

    # Показания ККТ
    counter_start = db.Column(db.Numeric(15, 2), nullable=False)
    counter_end = db.Column(db.Numeric(15, 2), nullable=False)

    # Выручка
    cash_in = db.Column(db.Numeric(12, 2), default=0)
    card_in = db.Column(db.Numeric(12, 2), default=0)
    qr_in = db.Column(db.Numeric(12, 2), default=0)
    cash_return = db.Column(db.Numeric(12, 2), default=0)
    card_return = db.Column(db.Numeric(12, 2), default=0)

    # Остатки
    cash_start = db.Column(db.Numeric(12, 2), nullable=False)
    cash_end = db.Column(db.Numeric(12, 2), nullable=False)  # будет рассчитываться

    # Движения
    incassation = db.Column(db.Numeric(12, 2), default=0)
    salary = db.Column(db.Numeric(12, 2), default=0)
    exchange = db.Column(db.Numeric(12, 2), default=0)
    pko = db.Column(db.Numeric(12, 2), default=0)
    rko = db.Column(db.Numeric(12, 2), default=0)

    receipt_number = db.Column(db.String(50))
    submitted_by = db.Column(db.String(100))

    # Связи
    user = db.relationship('User', backref=db.backref('shifts', lazy=True))
    clinic = db.relationship('Clinic', backref=db.backref('shifts', lazy=True))