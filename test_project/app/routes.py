from flask import Blueprint, render_template, request, session, redirect, jsonify, url_for
from app.models import News, Category
from app import db
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Make sure lang is set
    if 'lang' not in session:
        session['lang'] = 'ru'
        
    category_code = request.args.get('category')
    search_query = request.args.get('q')
    
    query = News.query.order_by(News.created_at.desc())
    
    if category_code:
        cat = Category.query.filter_by(code=category_code).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
            
    if search_query:
        # Search in all language titles and contents
        term = f"%{search_query}%"
        query = query.filter(
            or_(
                News.title_ru.ilike(term),
                News.title_kk.ilike(term),
                News.title_en.ilike(term),
                News.content_ru.ilike(term),
                News.content_en.ilike(term),
                News.content_kk.ilike(term)
            )
        )
        
    news_list = query.all()
    categories = Category.query.all()
    
    # If we are on the main landing page (no filter, no search), 
    # we want to provide news grouped by category for the "newspaper" layout.
    news_by_category = {}
    if not category_code and not search_query:
        for cat in categories:
            # Get latest 4 news for each category
            news_by_category[cat.code] = News.query.filter_by(category_id=cat.id).order_by(News.created_at.desc()).limit(4).all()
    
    return render_template('index.html', 
                          news_list=news_list, 
                          categories=categories, 
                          current_cat=category_code,
                          news_by_category=news_by_category)

@main.route('/news/<int:news_id>')
def news_detail(news_id):
    news_item = News.query.get_or_404(news_id)
    # Increment views
    news_item.views += 1
    db.session.commit()
    return render_template('news.html', news=news_item)

@main.route('/set_lang/<lang_code>')
def set_lang(lang_code):
    if lang_code in ['kk', 'ru', 'en']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('main.index'))

@main.route('/api/news/latest')
def api_latest_news():
    """
    Endpoint for JS polling to get newest articles without reloading
    """
    since_timestamp = request.args.get('since')
    if not since_timestamp:
        return jsonify([])
        
    from datetime import datetime
    try:
        since_dt = datetime.fromisoformat(since_timestamp)
        new_news = News.query.filter(News.created_at > since_dt).order_by(News.created_at.desc()).all()
        return jsonify([n.to_dict() for n in new_news])
    except Exception as e:
        return jsonify([])
