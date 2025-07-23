from fastapi import HTTPException
import requests
from git import Repo, GitCommandError
import os
import shutil
import stat

from flask import Flask, request, jsonify

app = Flask(__name__)

def handle_remove_readonly(func, path, exc):
    if isinstance(exc, PermissionError):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise exc


def update_hello_file_and_push(repo_url, branch_name, file_name, new_line):
    repo_dir = "./temp_repo"
    file_path = os.path.join(repo_dir, file_name)

    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir, onexc=handle_remove_readonly)

    try:
        repo = Repo.clone_from(repo_url, repo_dir)
        git = repo.git

        # Check if branch exists remotely
        remote_branches = [ref.name.split('/')[-1] for ref in repo.remotes.origin.refs]
        if branch_name in remote_branches:
            git.checkout(branch_name)
        else:
            git.checkout('-b', branch_name)

        os.makedirs(repo_dir, exist_ok=True)

        # Modify or create the file
        if os.path.exists(file_path):
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{new_line}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_line)

        relative_path = os.path.relpath(file_path, repo_dir)
        repo.index.add([relative_path])
        repo.index.commit(f"Update {file_name} with new content")

        origin = repo.remote(name='origin')
        origin.push(branch_name)

        return f"✅ Branch '{branch_name}' updated and '{file_name}' modified."

    except GitCommandError as e:
        raise HTTPException(status_code=500, detail=f"Git error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Move out and delete
        try:
            if os.getcwd().startswith(os.path.abspath(repo_dir)):
                os.chdir(os.path.dirname(os.path.abspath(repo_dir)))
        except Exception:
            pass

        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir, onexc=handle_remove_readonly)


@app.route('/update-repo', methods=['POST'])
def update_repo():
    req = request.get_json()
    repo_url=req["repo_url"]
    branch_name=req["branch_name"]
    file_name=req["file_name"]
    new_line=req["new_line"]
    result = update_hello_file_and_push(
       repo_url, branch_name, file_name, new_line
    )
    return {"message": result}


if __name__ == "__main__":
    app.run(port=8000)