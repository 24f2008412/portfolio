import os
from github import Github, GithubException

def _create_or_update_file(repo, path, message, content):
    """
    Helper function to create or update a file in a repository.
    """
    try:
        contents = repo.get_contents(path, ref="main")
        repo.update_file(contents.path, message, content, contents.sha, branch="main")
        print(f"Updated file: {path}")
    except GithubException as e:
        if e.status == 404:
            repo.create_file(path, message, content, branch="main")
            print(f"Created file: {path}")
        else:
            raise

def create_and_push_to_repo(token: str, repo_name: str, files: dict, brief: str):
    """
    Creates a new public GitHub repository, uploads files, and enables GitHub Pages.
    """
    g = Github(token)
    user = g.get_user()

    # Create the repository
    try:
        repo = user.create_repo(repo_name, private=False, auto_init=True)
    except GithubException as e:
        if e.status == 422 and "name already exists" in e.data["errors"][0]["message"]:
            repo = user.get_repo(repo_name)
        else:
            raise e

    # Add/Update LICENSE
    license_content = get_license_content("MIT")
    _create_or_update_file(repo, "LICENSE", "Create or update LICENSE", license_content)

    # Add/Update README.md
    readme_content = f"""
# {repo_name}

{brief}

## Setup

...

## Usage

...

## Code Explanation

...

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
"""
    _create_or_update_file(repo, "README.md", "Create or update README.md", readme_content)

    # Add/Update generated files
    for path, content in files.items():
        _create_or_update_file(repo, path, f"Create or update {path}", content)

    # Enable GitHub Pages
    import requests
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.switcheroo-preview+json"
    }
    data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    response = requests.post(f"https://api.github.com/repos/{user.login}/{repo_name}/pages", json=data, headers=headers)
    if response.status_code not in [201, 409]: # 201 Created, 409 Conflict (already enabled)
        response.raise_for_status()


    branch = repo.get_branch("main")
    return repo.html_url, branch.commit.sha, f"https://{user.login}.github.io/{repo_name}/"


def get_repo_file_content(token: str, repo_name: str, file_path: str):
    """
    Fetches the content of a file from a GitHub repository.
    """
    g = Github(token)
    user = g.get_user()
    repo = user.get_repo(repo_name)
    try:
        contents = repo.get_contents(file_path, ref="main")
        return contents.decoded_content.decode("utf-8")
    except GithubException as e:
        if e.status == 404:
            return None # File not found
        else:
            raise e

def get_license_content(license_name="mit"):
    """
    Returns the content of a standard license.
    """
    if license_name.lower() == "mit":
        return """
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    return ""