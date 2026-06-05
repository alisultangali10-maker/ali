TRANSLATIONS = {
    'site_name': {
        'ru': 'Жаңалықтар KZ',
        'kk': 'Жаңалықтар KZ',
        'en': 'Zhanalyktar KZ'
    },
    'home': {
        'ru': 'Главная',
        'kk': 'Басты бет',
        'en': 'Home'
    },
    'search': {
        'ru': 'Поиск',
        'kk': 'Іздеу',
        'en': 'Search'
    },
    'search_placeholder': {
        'ru': 'Поиск новостей...',
        'kk': 'Жаңалықтарды іздеу...',
        'en': 'Search news...'
    },
    'read_more': {
        'ru': 'Подробнее',
        'kk': 'Толығырақ',
        'en': 'Read more'
    },
    'no_news': {
        'ru': 'Новостей пока нет.',
        'kk': 'Жаңалықтар әзірге жоқ.',
        'en': 'No news available.'
    },
    'views': {
        'ru': 'Просмотры',
        'kk': 'Қаралымдар',
        'en': 'Views'
    },
    'all_news': {
        'ru': 'Все новости',
        'kk': 'Барлық жаңалықтар',
        'en': 'All news'
    },
    # Category codes translation
    'cat_general': {
        'ru': 'Главное',
        'kk': 'Басты',
        'en': 'General'
    },
    'cat_politics': {
        'ru': 'Политика',
        'kk': 'Саясат',
        'en': 'Politics'
    },
    'cat_sport': {
        'ru': 'Спорт',
        'kk': 'Спорт',
        'en': 'Sport'
    },
    'cat_economy': {
        'ru': 'Экономика',
        'kk': 'Экономика',
        'en': 'Economy'
    },
    'cat_tech': {
        'ru': 'Технологии',
        'kk': 'Технологиялар',
        'en': 'Technology'
    },
    'cat_world': {
        'ru': 'В мире',
        'kk': 'Әлемде',
        'en': 'World'
    },
    'cat_auto': {
        'ru': 'Авто',
        'kk': 'Авто',
        'en': 'Auto'
    },
    'cat_culture': {
        'ru': 'Культура',
        'kk': 'Мәдениет',
        'en': 'Culture'
    },
    'login_admin': {
        'ru': 'Вход для админа',
        'kk': 'Әкімші кіру',
        'en': 'Admin login'
    }
}

def get_translation(lang, key):
    return TRANSLATIONS.get(key, {}).get(lang, key)
