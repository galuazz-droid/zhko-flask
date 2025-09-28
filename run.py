from app import create_app, db
from app.models import User, Clinic

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Создать демо-клинику и пользователя, если нет
        if not Clinic.query.first():
            clinic = Clinic(name="Клиника №1")
            db.session.add(clinic)
            db.session.commit()
        if not User.query.first():
            user = User(username="admin")
            user.set_password("admin")
            user.clinic_id = 1
            db.session.add(user)
            db.session.commit()
    app.run(debug=True, host='0.0.0.0', port=5000)