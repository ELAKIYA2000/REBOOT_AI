from flask import Flask, request, jsonify
import semver
import requests
from urllib.parse import urlparse

app = Flask(__name__)

def fetch_github_changelog(repo_url):
    try:
        parsed = urlparse(repo_url)
        parts = parsed.path.strip("/").split("/")
        owner, repo = parts[0], parts[1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"

        response = requests.get(api_url)
        if response.status_code == 200:
            releases = response.json()
            changelog = "\n📜 Recent GitHub Releases:\n"
            for release in releases[:3]:
                changelog += f"- {release['tag_name']}: {release['name']}\n"
                changelog += f"  {release['body'][:200]}...\n\n"
            return changelog
        else:
            return "❌ Failed to fetch releases from GitHub.\n"
    except Exception as e:
        return f"❌ Error fetching changelog: {e}\n"

@app.route('/check-compatibility', methods=['POST'])
def check_compatibility():
    dependencies = request.get_json()
    if not isinstance(dependencies, list):
        return "Invalid input format. Expected a list of dependencies.", 400

    result = ""
    for data in dependencies:
        try:
            dep = data["dependency"]
            current = semver.VersionInfo.parse(data["current_version"])
            latest = semver.VersionInfo.parse(data["latest_version"])
            repo_url = data.get("repo_url")

            result += f"\n🔍 Checking compatibility for '{dep}'\n"
            result += f"Current version: {current}\n"
            result += f"Latest version:  {latest}\n"

            if latest.major > current.major:
                result += "⚠️ Major version upgrade — likely breaking changes.\n"
            elif latest.minor > current.minor:
                result += "✅ Minor upgrade — usually safe.\n"
            elif latest.patch > current.patch:
                result += "🔧 Patch upgrade — safe to apply.\n"
            else:
                result += "🟢 Already up to date.\n"

            if repo_url:
                result += fetch_github_changelog(repo_url)
        except Exception as e:
            result += f"❌ Error processing '{data}': {e}\n"

    return result, 200

if __name__ == '__main__':
    app.run(debug=True)
