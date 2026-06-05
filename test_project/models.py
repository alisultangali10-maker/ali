from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

def to_kz_time(dt):
    if not dt:
        return None

    # если нет timezone — считаем UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(ZoneInfo("Asia/Almaty"))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    # The name of the category will be handled via translations based on 'code'
    news = db.relationship('News', backref='category', lazy='dynamic')

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    title_kk = db.Column(db.String(200), nullable=False)
    title_ru = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    
    content_kk = db.Column(db.Text, nullable=False)
    content_ru = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    
    summary_kk = db.Column(db.Text, nullable=True)
    summary_ru = db.Column(db.Text, nullable=True)
    summary_en = db.Column(db.Text, nullable=True)
    
    image_filename = db.Column(db.String(200), nullable=True)
    
    source_name = db.Column(db.String(100), nullable=True)
    original_url = db.Column(db.String(500), unique=True, nullable=True)
    
    views = db.Column(db.Integer, default=0)



    from datetime import datetime, timezone

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    def to_dict(self):
        return {
            'id': self.id,
            'category_code': self.category.code if self.category else '',
            'title_kk': self.title_kk,
            'title_ru': self.title_ru,
            'title_en': self.title_en,
            'content_kk': self.content_kk,
            'content_ru': self.content_ru,
            'content_en': self.content_en,
            'summary_kk': self.summary_kk,
            'summary_ru': self.summary_ru,
            'summary_en': self.summary_en,
            'image_filename': self.image_filename,
            'source_name': self.source_name,
            'original_url': self.original_url,
            'views': self.views,
            'created_at': to_kz_time(self.created_at).strftime("%H:%M")
        }


