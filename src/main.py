from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from src.database import SessionLocal, Restaurant

load_dotenv()

app = FastAPI(title="NYC Restaurant Vector Search API")

# Load model once at startup (cached locally after first download)
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RestaurantResponse(BaseModel):
    id: int
    title: str
    category: str
    review_comment: str
    popular_food: str
    online_order: bool
    number_of_reviews: int
    similarity: float

@app.get("/api/search", response_model=List[RestaurantResponse])
def search_restaurants(
    q: Optional[str] = None,
    restaurant_id: Optional[int] = None,
    online_order_only: bool = False,
    min_reviews: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    if not q and not restaurant_id:
        raise HTTPException(status_code=400, detail="Must provide either 'q' or 'restaurant_id'")

    if restaurant_id:
        # Mode 2: Find similar to an existing restaurant
        rest = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not rest:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        query_vector = list(rest.embedding)
    else:
        # Mode 1: Embed the natural language query
        query_vector = model.encode(q).tolist()

    filters = []
    if online_order_only:
        filters.append(Restaurant.online_order == True)
    if min_reviews > 0:
        filters.append(Restaurant.number_of_reviews >= min_reviews)

    stmt = select(
        Restaurant,
        Restaurant.embedding.cosine_distance(query_vector).label("distance")
    ).where(and_(*filters))

    if restaurant_id:
        stmt = stmt.where(Restaurant.id != restaurant_id)

    stmt = stmt.order_by("distance").limit(limit)
    results = db.execute(stmt).all()

    return [
        RestaurantResponse(
            id=r.Restaurant.id,
            title=r.Restaurant.title,
            category=r.Restaurant.category,
            review_comment=r.Restaurant.review_comment,
            popular_food=r.Restaurant.popular_food,
            online_order=r.Restaurant.online_order,
            number_of_reviews=r.Restaurant.number_of_reviews,
            similarity=round(1 - r.distance, 4)
        )
        for r in results
    ]

@app.get("/api/restaurants")
def list_restaurants(db: Session = Depends(get_db)):
    results = db.query(Restaurant.id, Restaurant.title)\
        .order_by(Restaurant.number_of_reviews.desc()).limit(500).all()
    return [{"id": r.id, "title": r.title} for r in results]
