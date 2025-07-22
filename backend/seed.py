# seed.py
from database import SessionLocal
from models import User

db = SessionLocal()

demo_users = [
    {"username": "mari", "password": "mariloveslulu"},
    {"username": "lulu", "password": "lululovesmari"}
]

for user_data in demo_users:
    existing = db.query(User).filter_by(username=user_data["username"]).first()
    if not existing:
        user = User(username=user_data["username"], password=user_data["password"])
        db.add(user)

db.commit()
db.close()

print("Demo users added.")
