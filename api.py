from github_api import get_user_repos, get_repo_readme

def scan_github(username):
    repos = get_user_repos(username)
    print(f"\n🔍 Found {len(repos)} public repositories for @{username}\n")

    for repo in repos:
        name = repo["name"]
        stars = repo["stargazers_count"]
        forks = repo["forks_count"]
        language = repo["language"]
        updated = repo["updated_at"]
        readme = get_repo_readme(username, name)

        print(f"📁 {name} ({language}) ⭐ {stars} | 🍴 {forks} | Last updated: {updated}")
        if readme:
            print("📖 README preview:")
            print(readme[:300].strip() + "...\n")
        else:
            print("⚠️ No README found.\n")

if __name__ == "__main__":
    username = input("Enter GitHub username: ").strip()
    scan_github(username)
