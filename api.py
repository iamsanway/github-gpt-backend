from fastapi import FastAPI, Query
from github_api import get_user_repos, get_repo_readme
from dotenv import load_dotenv
import os
import httpx

# Load environment variables from .env file
load_dotenv()
nlpcloud_key = os.getenv("NLP_CLOUD_API_KEY")

# FastAPI app
app = FastAPI()

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
    context = f"GitHub summary for @{username}.\n"

    for repo in repos[:5]:  # Limit to top 5 repos
        context += f"\n- {repo['name']} ({repo['language']}) ⭐ {repo['stargazers_count']}, 🍴 {repo['forks_count']}\n"
        readme = get_repo_readme(username, repo["name"])
        if readme:
            context += f"README:\n{readme[:500]}\n"

    try:
        headers = {
            "Authorization": f"Token {nlpcloud_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "text": context,
            "min_length": 50,
            "max_length": 250
        }

        response = httpx.post(
            "https://api.nlpcloud.io/v1/bart-large-cnn/summarization",
            headers=headers,
            json=payload,
            timeout=20,
        )

        summary = response.json().get("summary_text")
        return {
            "username": username,
            "summary": summary
        }

    except Exception as e:
        return {"error": str(e)}
