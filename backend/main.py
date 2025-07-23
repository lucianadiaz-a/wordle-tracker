from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Game
from schemas import UserLogin, WordleResult
from datetime import date
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://thriving-melomakarona-9c203c.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}

@app.post("/api/submit")
def submit_result(result: WordleResult, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == result.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(Game).filter(Game.date == date.today(), Game.player_id == db_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already submitted")

    game = Game(
        date=date.today(),
        player_id=db_user.id,
        score=result.score,
        raw_result=result.raw_result
    )
    db.add(game)
    db.commit()
    return {"message": "Result submitted"}

@app.get("/api/scores")
def get_scores(db: Session = Depends(get_db)):
    users = db.query(User).all()
    games = db.query(Game).all()

    scores = {
        user.username: {"wins": 0, "streak": 0}
        for user in users
    }

    # Build game map by date
    from collections import defaultdict
    game_map = defaultdict(dict)
    for game in games:
        game_map[game.date][game.player.username] = game

    # Sort dates and evaluate
    sorted_dates = sorted(game_map.keys())
    prev_winner = None
    for d in sorted_dates:
        day_games = game_map[d]
        if len(day_games) < 2:
            continue  # skip incomplete games

        p1, p2 = day_games.values()
        if p1.score < p2.score:
            winner = p1.player.username
            loser = p2.player.username
        elif p2.score < p1.score:
            winner = p2.player.username
            loser = p1.player.username
        else:
            prev_winner = None
            continue  # tie, reset streaks

        scores[winner]["wins"] += 1
        scores[winner]["streak"] = scores[winner]["streak"] + 1 if prev_winner == winner else 1
        scores[loser]["streak"] = 0
        prev_winner = winner

    return scores

@app.get("/api/history")
def get_history(db: Session = Depends(get_db)):
    from collections import defaultdict

    games = db.query(Game).all()
    history = []

    game_map = defaultdict(dict)
    for game in games:
        game_map[game.date][game.player.username] = game

    for date, entries in sorted(game_map.items(), reverse=True)[:7]:
        if "player1" in entries and "player2" in entries:
            p1 = entries["player1"]
            p2 = entries["player2"]

            if p1.score < p2.score:
                winner = "player1"
            elif p2.score < p1.score:
                winner = "player2"
            else:
                winner = "tie"

            history.append({
                "date": date.isoformat(),
                "player1": f"{p1.score}/6",
                "player2": f"{p2.score}/6",
                "winner": winner
            })

    return history
