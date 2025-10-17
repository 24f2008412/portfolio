import os
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter, Retry

load_dotenv()

# Import utils
from .generator import generate_app
if os.getenv("USE_MOCK_GITHUB") == "True":
    from .mock_github_utils import create_and_push_to_repo, get_repo_file_content
else:
    from .github_utils import create_and_push_to_repo, get_repo_file_content


app = FastAPI()

# Pydantic model for the request body
class TaskRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: list[str]
    evaluation_url: str
    attachments: list[dict]

@app.post("/api-endpoint")
async def process_task(request: TaskRequest):
    # Verify the secret
    if request.secret != os.getenv("SHARED_SECRET"):
        raise HTTPException(status_code=403, detail="Invalid secret")

    existing_files = None
    if request.round > 1:
        try:
            index_content = get_repo_file_content(os.getenv("GITHUB_TOKEN"), request.task, "index.html")
            if not index_content:
                raise HTTPException(status_code=404, detail="Could not find index.html for round 2")

            existing_files = {"index.html": index_content}

            if "sum-of-sales" in request.task:
                data_content = get_repo_file_content(os.getenv("GITHUB_TOKEN"), request.task, "data.csv")
                if not data_content:
                    raise HTTPException(status_code=404, detail="Could not find data.csv for round 2")
                existing_files["data.csv"] = data_content
            elif "markdown-to-html" in request.task:
                md_content = get_repo_file_content(os.getenv("GITHUB_TOKEN"), request.task, "input.md")
                if not md_content:
                    raise HTTPException(status_code=404, detail="Could not find input.md for round 2")
                existing_files["input.md"] = md_content

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"GitHub operation failed: {e}")


    try:
        files = generate_app(request.task, request.brief, request.attachments, existing_files)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create or update the repo and push the files
    try:
        repo_url, commit_sha, pages_url = create_and_push_to_repo(
            os.getenv("GITHUB_TOKEN"),
            request.task,
            files,
            request.brief
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub operation failed: {e}")

    # Send the notification to the evaluation URL
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        notification_payload = {
            "email": request.email,
            "task": request.task,
            "round": request.round,
            "nonce": request.nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        response = s.post(request.evaluation_url, json=notification_payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {e}")

    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)