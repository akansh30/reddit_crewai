from crewai import Agent, LLM

llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.5, max_completion_tokens=512)

request_parser = Agent(
    role="Request Parser",
    goal="Extract relevant subreddits and keywords from a user search request",
    backstory="Expert at understanding user needs and mapping them to Reddit topics",
    llm=llm,
    verbose=False,
)

post_summarizer = Agent(
    role="Post Summarizer",
    goal="Summarize Reddit posts into concise, meaningful summaries",
    backstory="Skilled at digesting social media content and extracting essence",
    llm=llm,
    verbose=False,
)

influence_scorer = Agent(
    role="Influence Scorer",
    goal="Estimate user's influence score based on their posts and comments",
    backstory="Data analyst who quantifies social influence",
    llm=llm,
    verbose=False,
)
