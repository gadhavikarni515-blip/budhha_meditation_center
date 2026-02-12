from app import app
from models import db, Program

with app.app_context():
    programs = Program.query.all()
    for p in programs:
        print(f'{p.id}: {p.name} - image: {p.image}')
