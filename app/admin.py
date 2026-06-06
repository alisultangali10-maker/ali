from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, News, Category
from app import db
import os
import uuid
from werkzeug.utils import secure_filename
from flask import redirect, url_for
from rss_parser import fetch_rss_feeds

admin_bp = Blueprint('admin', __name__)

# ================= LOGIN =================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Неправильный логин или пароль')

    return render_template('admin/login.html')


# ================= LOGOUT =================
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


# ================= DASHBOARD =================
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_news = News.query.count()
    total_views = db.session.query(db.func.sum(News.views)).scalar() or 0
    categories_count = Category.query.count()

    return render_template(
        'admin/dashboard.html',
        total_news=total_news,
        total_views=total_views,
        categories_count=categories_count
    )


# ================= NEWS LIST =================
@admin_bp.route('/news')
@login_required
def news_list():
    news_items = News.query.order_by(News.created_at.desc()).all()
    categories = Category.query.all()

    return render_template('admin/news_list.html',
                           news_items=news_items,
                           categories=categories)


# ================= ADD NEWS =================
@admin_bp.route('/news/add', methods=['GET', 'POST'])
@login_required
def news_add():
    categories = Category.query.all()

    if request.method == 'POST':

        title_kk = request.form.get('title_kk')
        title_ru = request.form.get('title_ru')
        title_en = request.form.get('title_en')
        content_kk = request.form.get('content_kk')
        content_ru = request.form.get('content_ru')
        content_en = request.form.get('content_en')
        category_id = request.form.get('category_id')

        # IMAGE UPLOAD
        image_file = request.files.get('image')

        if not image_file or not image_file.filename:
            flash('Необходимо загрузить изображение!')
            return redirect(request.url)

        ext = os.path.splitext(image_file.filename)[1]
        image_filename = str(uuid.uuid4()) + ext

        path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
        image_file.save(path)

        new_news = News(
            title_kk=title_kk,
            title_ru=title_ru,
            title_en=title_en,
            content_kk=content_kk,
            content_ru=content_ru,
            content_en=content_en,
            category_id=category_id,
            image_filename=image_filename
        )

        db.session.add(new_news)
        db.session.commit()

        flash('Новость успешно добавлена!')
        return redirect(url_for('admin.news_list'))
    


    return render_template('admin/news_form.html',
                           categories=categories,
                           news=None)


# ================= EDIT NEWS =================
@admin_bp.route('/news/edit/<int:news_id>', methods=['GET', 'POST'])
@login_required
def news_edit(news_id):
    news_item = News.query.get_or_404(news_id)
    categories = Category.query.all()

    if request.method == 'POST':

        news_item.title_kk = request.form.get('title_kk')
        news_item.title_ru = request.form.get('title_ru')
        news_item.title_en = request.form.get('title_en')
        news_item.content_kk = request.form.get('content_kk')
        news_item.content_ru = request.form.get('content_ru')
        news_item.content_en = request.form.get('content_en')
        news_item.category_id = request.form.get('category_id')

        # IMAGE UPLOAD
        image_file = request.files.get('image')

        if image_file and image_file.filename:
            ext = os.path.splitext(image_file.filename)[1]
            image_filename = str(uuid.uuid4()) + ext

            path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)

            image_file.save(path)
            news_item.image_filename = image_filename

        db.session.commit()

        flash('Новость успешно обновлена!')
        return redirect(url_for('admin.news_list'))

    return render_template('admin/news_form.html',
                           categories=categories,
                           news=news_item)


# ================= DELETE NEWS =================
@admin_bp.route('/news/delete/<int:news_id>')
@login_required
def news_delete(news_id):
    news_item = News.query.get_or_404(news_id)

    db.session.delete(news_item)
    db.session.commit()

    flash('Новость удалена!')
    return redirect(url_for('admin.news_list'))


# ================= RSS =================
import threading
from rss_parser import fetch_rss_feeds

@admin_bp.route('/news/fetch_rss')
@login_required
def news_fetch_rss():

    try:
        thread = threading.Thread(target=fetch_rss_feeds)
        thread.start()

        flash('RSS запущен в фоне (сайт не зависает)', 'success')

    except Exception as e:
        flash(f'Ошибка при запуске RSS: {e}', 'error')

    return redirect(url_for('admin.news_list'))


# ================= DATABASE VIEW =================
@admin_bp.route('/database')
@login_required
def database():
    news = News.query.order_by(News.id.desc()).limit(100).all()
    return render_template('admin/database.html', news=news)
