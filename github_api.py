import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")

# Use the token in request headers if available
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

def get_user_repos(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} {response.text}")
    return response.json()

def get_repo_readme(username, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    headers = HEADERS.copy()
    headers["Accept"] = "application/vnd.github.v3.raw"
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None
