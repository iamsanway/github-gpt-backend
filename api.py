from fastapi import FastAPI, Query
from github_api import get_user_repos, get_repo_readme
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
client = OpenAI(api_key=openai_api_key)

@app.get("/")
def root():
    return {"message": "GitHub Scanner backend is live 🎯"}

@app.get("/scan")
def scan_github(username: str = Query(...)):
    repos = get_user_repos(username)
    result = {
        "username": username,
        "repo_count": len(repos),
        "repos": []
    }
    for repo in repos:
        name = repo["name"]
        stars = repo["stargazers_count"]
        forks = repo["forks_count"]
        language = repo["language"]
        updated = repo["updated_at"]
        readme = get_repo_readme(username, name)
        result["repos"].append({
            "name": name,
            "language": language,
            "stars": stars,
            "forks": forks,
            "updated": updated,
            "readme_preview": (readme[:300].strip() + "...") if readme else None
        })
    return result

@app.get("/summary")
def generate_summary(username: str = Query(...)):
    repos = get_user_repos(username)
    context = f"GitHub profile summary for @{username}.\n\n"

    for repo in repos[:5]:  # limit to top 5 repos
        name = repo["name"]
        stars = repo["stargazers_count"]
        forks = repo["forks_count"]
        language = repo["language"]
        updated = repo["updated_at"]
        readme = get_repo_readme(username, name)

        context += f"\n📁 {name} ({language}) ⭐ {stars} | 🍴 {forks} | Last updated: {updated}\n"
        if readme:
            context += f"README:\n{readme[:500]}\n"

    # Ask OpenAI to summarize
    messages = [
        {
            "role": "system",
            "content": "You are an expert tech recruiter. Generate a concise, professional summary of a developer's GitHub profile. Highlight programming languages, strengths, project types, and any notable features. Avoid fluff."
        },
        {
            "role": "user",
            "content": context
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # ✅ SAFE CHOICE

            messages=messages,
            max_tokens=300
        )
        summary = response.choices[0].message.content.strip()
        return {
            "username": username,
            "summary": summary
        }
    except Exception as e:
        return {"error": str(e)}
