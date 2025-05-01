
from app import create_app, db
app = create_app()
with app.app_context():
    print("用户数量:", db.session.query(db.Model.metadata.tables['users']).count())
