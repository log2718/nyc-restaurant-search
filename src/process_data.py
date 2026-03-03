import pandas as pd
import os
import time
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from src.database import SessionLocal, Restaurant, init_db

load_dotenv()

# Load the local embedding model (downloads once, then cached)
print("Loading local embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.")

def _parse_online_order(val):
    if pd.isna(val):
        return False
    return str(val).strip().lower() == 'yes'

def _parse_number_of_reviews(val):
    if pd.isna(val) or val == 'No':
        return 0
    if isinstance(val, str):
        val = val.replace(',', '').split(' ')[0]
        try:
            return int(val)
        except ValueError:
            return 0
    return int(val)

def generate_embeddings_batch(texts):
    # sentence_transformers returns a numpy array, convert to list for pgvector
    return model.encode(texts, show_progress_bar=False).tolist()

def process_data(csv_path: str, limit: int = None):
    init_db()
    
    df = pd.read_csv(csv_path)
    if limit:
        df = df.head(limit)
        print(f"Limiting to first {limit} rows.")
    
    # Drop rows where Title is "No" or NaN (junk rows)
    df = df[df['Title'].notna() & (df['Title'] != 'No')]
    
    session = SessionLocal()
    try:
        # Check if already populated to avoid full duplicate re-runs
        if session.query(Restaurant).first():
            print("Database already populated. Skipping data ingest.")
            return

        print(f"Processing {len(df)} records...")
        
        batch_size = 128  # sentence-transformers handles large batches efficiently
        records_to_insert = []
        texts_to_embed = []
        
        for index, row in df.iterrows():
            title = str(row['Title'])
            category = str(row['Catagory']) if pd.notna(row['Catagory']) else ""
            review_comment = str(row['Reveiw Comment']) if pd.notna(row['Reveiw Comment']) else ""
            popular_food = str(row['Popular food']) if pd.notna(row['Popular food']) else ""
            
            number_of_reviews = _parse_number_of_reviews(row['Number of review'])
            online_order = _parse_online_order(row['Online Order'])

            combined_text = f"Category: {category}. Reviews: {review_comment}. Popular Food: {popular_food}."
            texts_to_embed.append(combined_text)
            
            records_to_insert.append({
                "title": title,
                "category": category,
                "review_comment": review_comment,
                "popular_food": popular_food,
                "online_order": online_order,
                "number_of_reviews": number_of_reviews
            })
            
            if len(texts_to_embed) == batch_size or index == len(df) - 1:
                batch_num = (index + 1) // batch_size + 1
                print(f"  Embedding batch (up to row {index + 1})...")
                embeddings = generate_embeddings_batch(texts_to_embed)
                
                for record, emb in zip(records_to_insert, embeddings):
                    session.add(Restaurant(**record, embedding=emb))
                
                session.commit()
                records_to_insert = []
                texts_to_embed = []
                
        print(f"Done! {len(df)} restaurants loaded into the database.")
    finally:
        session.close()

if __name__ == "__main__":
    process_data("trip advisor restaurents  10k - trip_rest_neywork_1.csv")
