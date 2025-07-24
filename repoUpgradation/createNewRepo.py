import os
import shutil
from git import Repo, GitCommandError

def handle_remove_readonly(func, path, exc):
    import stat
    if isinstance(exc, PermissionError):
        os.chmod(path, stat.S_IWRITE)
        try:
            func(path)
        except Exception:
            pass
    else:
        raise exc


def update_hello_file_and_push(repo_url, branch_name, file_name="hello.txt", new_line="Elakiya here Testing again!"):
    repo_dir = "./temp_repo"
    
    file_path = os.path.join(repo_dir, file_name)

    # Clean up any existing temp repo
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir, onexc=handle_remove_readonly)

    try:
        print(f"⏳ Cloning repo: {repo_url}")
        repo = Repo.clone_from(repo_url, repo_dir)
        git = repo.git
        

        # Check if branch exists remotely
        remote_branches = [ref.name.split('/')[-1] for ref in repo.remotes.origin.refs]
        if branch_name in remote_branches:
            git.checkout(branch_name)
            print(f"✅ Checked out existing branch: {branch_name}")
        else:
            git.checkout('-b', branch_name)
            print(f"✅ Created and switched to new branch: {branch_name}")

        # Ensure the repo_dir exists before file operations
        os.makedirs(repo_dir, exist_ok=True)

        # Edit or create the hello.txt file
        if os.path.exists(file_path):
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{new_line}")
            print(f"✏️ Appended to existing file: {file_name}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_line)
            print(f"📄 Created new file: {file_name}")

        # Stage, commit, push
        repo.index.add([os.path.relpath(file_path, repo_dir)])
        repo.index.commit(f"Update {file_name} with new content")
        print("📦 Committed changes")

        origin = repo.remote(name='origin')
        origin.push(branch_name)
        print(f"🚀 Pushed changes to branch '{branch_name}'")

        return f"✅ Branch '{branch_name}' updated and '{file_name}' modified."

    except GitCommandError as e:
        return f"❌ Git error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"
    finally:
        # Ensure we're not inside the repo before deletion
        try:
            if os.getcwd().startswith(os.path.abspath(repo_dir)):
                os.chdir(os.path.dirname(os.path.abspath(repo_dir)))
        except Exception:
            pass

        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir, onexc=handle_remove_readonly)

# 🔁 Example usage
if __name__ == "__main__":
    repo_url = "https://github.com/ELAKIYA2000/Personal"  # Replace with your repo
    branch = "feature/elakiya-update"

    result = update_hello_file_and_push(repo_url, branch)
    print(result)
