from app import db, Transaction, app

with app.app_context():
    db.create_all()
    print('Database created!')