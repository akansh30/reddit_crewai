from fastapi import FastAPI, HTTPException
from models import SearchRequest, UserProfile
from reddit_api import fetch_posts

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is working! Use /create_request/ to send your search request."}

@app.post("/create_request/", response_model=list[UserProfile])
async def create_request(search_request: SearchRequest):
    try:
        profiles = await fetch_posts(
            subreddit=search_request.subreddit,
            keywords=search_request.keywords,
            limit=search_request.limit
        )
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
