from flask import Flask, request, jsonify
import requests
import summarizer
from urllib.parse import urlparse

app = Flask(__name__)

@app.route('/fetch-changelog', methods=['POST'])
def fetch_changelog():
    data = request.get_json()
    group_id = data.get("groupId")
    artifact_id = data.get("artifactId")
    repo_url = data.get("repoUrl")

    if not group_id or not artifact_id:
        return jsonify({"error": "Missing groupId or artifactId"}), 400

    result = {
        "groupId": group_id,
        "artifactId": artifact_id,
        "maven_versions": [],
        "github_releases": []
    }

    try:
        result["maven_versions"] = fetch_maven_versions(group_id, artifact_id)
    except Exception as e:
        result["maven_error"] = str(e)

    if repo_url:
        try:
            result["github_releases"] = fetch_github_changelog(repo_url)
        except Exception as e:
            result["github_error"] = str(e)

    return jsonify(result), 200


def fetch_maven_versions(group_id, artifact_id, max_versions=3):
    group_path = group_id.replace('.', '/')
    search_url = f"https://search.maven.org/solrsearch/select?q=g:{group_id}+AND+a:{artifact_id}&rows={max_versions}&wt=json"

    response = requests.get(search_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch metadata from Maven Central.")

    data = response.json()
    docs = data.get("response", {}).get("docs", [])
    if not docs:
        raise Exception("No versions found on Maven Central.")

    return [doc.get("v") for doc in docs]


def fetch_github_changelog(repo_url, max_releases=3):
    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise Exception("Invalid GitHub repo URL.")

    owner, repo = parts[0], parts[1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch GitHub releases.")

    releases = response.json()
    if not releases:
        return [{"info": "No GitHub releases found."}]

    result = []
    for release in releases[:max_releases]:
        tag = release.get("tag_name", "N/A")
        name = release.get("name", "")
        body = release.get("body", "")
        #summary = body[:500].replace('\n', ' ') + "..." if body else "No details."
        summary=summarizer.summarize_with_gemini(body)

        result.append({
            "tag": tag,
            "name": name,
            "summary": summary,
        })

    return result


if __name__ == '__main__':
    app.run(debug=True)
