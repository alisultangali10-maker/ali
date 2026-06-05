from app import create_app, db
from app.models import User, Category

app = create_app()

with app.app_context():
    db.create_all()

    # Create default categories if none
    if Category.query.count() == 0:
        categories = [
            'cat_general', 'cat_politics', 'cat_sport', 
            'cat_economy', 'cat_tech', 'cat_world', 
            'cat_auto', 'cat_culture'
        ]
        for c in categories:
            cat = Category(code=c)
            db.session.add(cat)
        db.session.commit()
        print("Категории успешно добавлены.")

    # Create default admin user
    if User.query.filter_by(username='admin').first() is None:
        admin_user = User(username='admin')
        admin_user.set_password('admin')
        db.session.add(admin_user)
        db.session.commit()
        print("Пользователь admin создан с паролем admin.")

    print("База данных инициализирована.")
