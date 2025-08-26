from fastapi import FastAPI, Query
from github_api import get_user_repos, get_repo_readme

app = FastAPI()

@app.get("/")
def root():
    return {"message": "GitHub Scanner backend is live 🎯"}

@app.get("/scan")
def scan_github(username: str = Query(..., description="GitHub username to scan")):
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
