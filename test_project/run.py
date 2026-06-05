from app import create_app

app = create_app()

if __name__ == '__main__':
    from rss_parser import fetch_rss_feeds
    from apscheduler.schedulers.background import BackgroundScheduler
    import atexit

    scheduler = BackgroundScheduler()

    scheduler.add_job(func=fetch_rss_feeds, trigger="date")
    scheduler.add_job(func=fetch_rss_feeds, trigger="interval", minutes=30)

    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())

    app.run(debug=True, host='0.0.0.0', port=5000)