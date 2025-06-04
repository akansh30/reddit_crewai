from crewai import Task, Crew
from crew_agents import request_parser, post_summarizer, influence_scorer
from reddit_api import fetch_posts

import json

def parse_request_to_subreddits_keywords(purpose: str):
    task = Task(
        description=f"Given this user search purpose: '{purpose}', list relevant subreddits and keywords to search.",
        expected_output="JSON list with 'subreddits' and 'keywords' arrays",
        agent=request_parser
    )
    crew = Crew(agents=[request_parser], tasks=[task])
    result = crew.kickoff()   

    print("Crew Output (parse_request_to_subreddits_keywords):", result)

    if hasattr(result, "output"):  
        result_str = result.output
    else:
        result_str = str(result)

    import json
    output = json.loads(result_str)
    return output["subreddits"], output["keywords"]

def run_pipeline(search_request):
    subreddits, keywords = parse_request_to_subreddits_keywords(search_request.purpose)
    keywords.extend(search_request.extra_keywords)

    posts = []
    for sub in subreddits:
        posts += fetch_posts(sub, keywords, limit=30, time_filter="month")

    tasks = []
    for post in posts[:10]:
        desc = f"Summarize this Reddit post text:\n\n{post['selftext'] or post['title']}"
        task = Task(description=desc, expected_output="Summary text", agent=post_summarizer)
        tasks.append(task)

    summarizer_crew = Crew(agents=[post_summarizer], tasks=tasks)
    summaries = summarizer_crew.kickoff()

    print("Crew Output (summaries):", summaries)

    summarized_posts = []
    for post, summary in zip(posts[:10], summaries):
        summarized_posts.append({**post, "summary": summary})

    users = {}
    for p in summarized_posts:
        username = p["author"]
        users.setdefault(username, []).append(p)

    user_profiles = []
    for username, user_posts in users.items():
        desc = f"Score user influence for user with posts: {user_posts}"
        task = Task(description=desc, expected_output="A float influence score", agent=influence_scorer)
        crew = Crew(agents=[influence_scorer], tasks=[task])
        score = crew.kickoff()

        print(f"Crew Output (influence score for {username}):", score)

        user_profiles.append({
            "username": username,
            "profile_url": f"https://reddit.com/user/{username}",
            "influence_score": float(score) if score else 0,
            "relevant_topics": keywords,
            "active_subreddits": list(set(p["subreddit"] for p in user_posts))
        })

    return user_profiles
