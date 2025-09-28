from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Clinic, Shift
from .forms import LoginForm, ShiftForm
from .utils import calculate_total_revenue, calculate_cash_end

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('shift_form'))
        flash('Неверный логин или пароль')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/shift', methods=['GET', 'POST'])
@login_required
def shift_form():
    form = ShiftForm()
    form.clinic_id.choices = [(c.id, c.name) for c in Clinic.query.all()]

    if form.validate_on_submit():
        # Расчёт
        total_rev = calculate_total_revenue(
            form.cash_in.data,
            form.card_in.data,
            form.qr_in.data,
            form.cash_return.data,
            form.card_return.data
        )
        cash_end = calculate_cash_end(
            form.cash_start.data,
            form.cash_in.data,
            form.incassation.data,
            form.salary.data,
            form.rko.data,
            form.pko.data,
            form.exchange.data
        )

        shift = Shift(
            user_id=current_user.id,
            clinic_id=form.clinic_id.data,
            date=form.date.data,
            shift_number=form.shift_number.data,
            counter_start=form.counter_start.data,
            counter_end=form.counter_end.data,
            cash_in=form.cash_in.data,
            card_in=form.card_in.data,
            qr_in=form.qr_in.data,
            cash_return=form.cash_return.data,
            card_return=form.card_return.data,
            cash_start=form.cash_start.data,
            cash_end=cash_end,
            incassation=form.incassation.data,
            salary=form.salary.data,
            exchange=form.exchange.data,
            pko=form.pko.data,
            rko=form.rko.data,
            receipt_number=form.receipt_number.data,
            submitted_by=form.submitted_by.data
        )
        db.session.add(shift)
        db.session.commit()
        flash('Смена сохранена!')
        return redirect(url_for('shift_form'))

    # Автозаполнение остатка на начало (из последней смены)
    last_shift = Shift.query.filter_by(user_id=current_user.id).order_by(Shift.date.desc()).first()
    if last_shift:
        form.cash_start.data = last_shift.cash_end

    return render_template('shift_form.html', form=form)