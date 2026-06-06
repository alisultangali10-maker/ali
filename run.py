from app import create_app, db
from app.models import User, Category

app = create_app()

# 🔥 ДОБАВИТЬ ЭТО БЛОК
with app.app_context():
    db.create_all()

    # create admin if not exists
    admin = User.query.filter_by(username='admin').first()

    if not admin:
        admin = User(username='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("ADMIN CREATED")

# 🔥 END INIT BLOCK


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
