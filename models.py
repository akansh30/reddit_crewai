from pydantic import BaseModel
from typing import List, Literal,Optional

class SearchRequest(BaseModel):
    request_name: str
    purpose: str 
    keywords: Optional[List[str]] = None
    duration_days: Optional[int] = 30  
    subreddit: str
    limit: int = 10

class UserProfile(BaseModel):
    username: str
    profile_url: str
    influence_score: float
    relevant_topics: List[str]
    active_subreddits: List[str]
    expertise_level: Literal["low", "medium", "high"]
    activity_level: Literal["low", "medium", "high"]
    engagement_quotient: float
    estimated_reach: int
    relevance_score: float
