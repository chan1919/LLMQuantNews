
from app.database import SessionLocal
from app.models import News

db = SessionLocal()
try:
    count = db.query(News).count()
    print(f"Total news: {count}")

    if count &gt; 0:
        recent = db.query(News).order_by(News.crawled_at.desc()).limit(3).all()
        for n in recent:
            print(f"- {n.title[:50]}... analyzed={n.is_analyzed}")
finally:
    db.close()
