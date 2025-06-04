import os
import asyncio
from dotenv import load_dotenv
import asyncpraw
from models import UserProfile

load_dotenv()

reddit = asyncpraw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def categorize_level(value: float, thresholds=(3, 7)) -> str:
    """
    Converts a numeric value to 'low', 'medium', or 'high' based on thresholds.
    """
    if value < thresholds[0]:
        return "low"
    elif value < thresholds[1]:
        return "medium"
    else:
        return "high"

def calculate_relevance(post, keywords):
    """
    Calculate a relevance score based on keyword match and engagement.
    """
    title_lower = post.title.lower()
    text_lower = post.selftext.lower()
    match_count = sum(1 for kw in keywords if kw.lower() in title_lower or kw.lower() in text_lower)

    keyword_match_score = match_count / len(keywords) if keywords else 0
    engagement_score = (post.score + post.num_comments) / 100.0  

    relevance_score = 0.6 * keyword_match_score + 0.4 * min(1.0, engagement_score)  
    return round(relevance_score, 2) 

async def fetch_posts(subreddit: str, keywords: list[str], limit=10, time_filter="month"):
    posts = []

    subreddit_obj = await reddit.subreddit(subreddit)

    for keyword in keywords:
        try:
            search_results = subreddit_obj.search(
                query=keyword,
                limit=limit,
                sort="relevance",
                time_filter=time_filter
            )
            async for post in search_results:
                posts.append(post)
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error fetching from {subreddit} with keyword '{keyword}': {e}")
            continue

    
    unique_posts = {}
    for post in posts:
        if post.id not in unique_posts:
            unique_posts[post.id] = post

    profiles = []
    for post in unique_posts.values():
        username = post.author.name if post.author else "N/A"
        profile_url = f"https://www.reddit.com/user/{username}" if username != "N/A" else "N/A"
        influence_score = float(post.score) if post.score else 0.0
        relevant_topics = keywords
        active_subreddits = [post.subreddit.display_name] if post.subreddit else []

        
        raw_expertise = influence_score / 20
        raw_activity = post.num_comments / 10

        expertise_level = categorize_level(raw_expertise)
        activity_level = categorize_level(raw_activity)

        engagement_quotient = (post.score + post.num_comments) / 100.0
        estimated_reach = int(post.score * 10) if post.score else 0

        relevance_score = calculate_relevance(post, keywords)

        profiles.append(
            UserProfile(
                username=username,
                profile_url=profile_url,
                influence_score=influence_score,
                relevant_topics=relevant_topics,
                active_subreddits=active_subreddits,
                expertise_level=expertise_level,
                activity_level=activity_level,
                engagement_quotient=engagement_quotient,
                estimated_reach=estimated_reach,
                relevance_score=relevance_score
            )
        )

    return profiles[:limit]
