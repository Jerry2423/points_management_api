from app import db, Transaction, app

with app.app_context():
    db.drop_all()
    print('Database cleaned!')