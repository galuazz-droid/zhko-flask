from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, IntegerField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class ShiftForm(FlaskForm):
    date = DateField('Дата', validators=[DataRequired()])
    shift_number = IntegerField('№ смены', validators=[DataRequired()])
    clinic_id = SelectField('Клиника', coerce=int, validators=[DataRequired()])
    
    counter_start = DecimalField('Показания ККТ на начало', places=2, validators=[DataRequired()])
    counter_end = DecimalField('Показания ККТ на конец', places=2, validators=[DataRequired()])

    cash_in = DecimalField('НАЛ', places=2, default=0)
    card_in = DecimalField('БЕЗНАЛ', places=2, default=0)
    qr_in = DecimalField('QR', places=2, default=0)
    cash_return = DecimalField('Возврат Наличными', places=2, default=0)
    card_return = DecimalField('Возврат Карта', places=2, default=0)

    cash_start = DecimalField('Остаток наличных на начало', places=2, validators=[DataRequired()])
    # cash_end — рассчитывается, не вводится

    incassation = DecimalField('Инкасация', places=2, default=0)
    salary = DecimalField('Зарплата', places=2, default=0)
    exchange = DecimalField('Размен', places=2, default=0)
    pko = DecimalField('ПКО', places=2, default=0)
    rko = DecimalField('РКО', places=2, default=0)

    receipt_number = StringField('№ Квитанции')
    submitted_by = StringField('Сдал', validators=[DataRequired()])

    submit = SubmitField('Сохранить')