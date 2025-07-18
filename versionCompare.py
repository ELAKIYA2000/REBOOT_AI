import json
import semver
import requests
from urllib.parse import urlparse

# Load JSON array
with open("dependency.json", "r") as f:
    dependencies = json.load(f)

# Function to fetch GitHub changelog
def fetch_github_changelog(repo_url):
    try:
        parsed = urlparse(repo_url)
        parts = parsed.path.strip("/").split("/")
        owner, repo = parts[0], parts[1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"

        response = requests.get(api_url)
        if response.status_code == 200:
            releases = response.json()
            print("\n📜 Recent GitHub Releases:")
            for release in releases[:3]:  # Show top 3
                print(f"- {release['tag_name']}: {release['name']}")
                print(f"  {release['body'][:200]}...\n")  # Truncate for brevity
        else:
            print("❌ Failed to fetch releases from GitHub.")
    except Exception as e:
        print(f"❌ Error: {e}")

# Loop through each dependency
for data in dependencies:
    dep = data["dependency"]
    current = semver.VersionInfo.parse(data["current_version"])
    latest = semver.VersionInfo.parse(data["latest_version"])
    repo_url = data.get("repo_url")

    print(f"\n🔍 Checking compatibility for '{dep}'")
    print(f"Current version: {current}")
    print(f"Latest version:  {latest}")

    if latest.major > current.major:
        print("⚠️ Major version upgrade — likely breaking changes.")
    elif latest.minor > current.minor:
        print("✅ Minor upgrade — usually safe.")
    elif latest.patch > current.patch:
        print("🔧 Patch upgrade — safe to apply.")
    else:
        print("🟢 Already up to date.")

    if repo_url:
        fetch_github_changelog(repo_url)
