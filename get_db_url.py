from app import app, db
with app.app_context():
    print('engine url:', db.engine.url)
    print('engine url file:', getattr(db.engine.url, 'database', None))
    # print all tables known to SQLAlchemy
    print('metadata tables:', [t.name for t in db.metadata.sorted_tables])
