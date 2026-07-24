# Cluster Reactor

Cluster Reactor is a small internal ops console with a FastAPI backend, PostgreSQL persistence, and a Streamlit frontend.

## Local development

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and adjust values if needed.
4. Run the backend with `uvicorn app.main:app --app-dir backend --reload`.
5. Run the frontend with `streamlit run frontend/app.py`.

## Docker Compose

The repository includes a three-service stack:

- `postgres` on port `5432`
- `backend` on port `8000`
- `frontend` on port `8501`

Bring everything up with:

```bash
docker compose up --build
```

Useful endpoints after startup:

- API root: `http://127.0.0.1:8000/`
- API readiness: `http://127.0.0.1:8000/readyz`
- Streamlit UI: `http://127.0.0.1:8501`

## Tests

Run the current test suite with:

```bash
source .venv/bin/activate
pytest -q
```

## Jenkins

The repository includes a root `Jenkinsfile` for a straightforward CI pipeline.

Pipeline stages:

- check out the repository
- create a temporary virtual environment
- install dependencies from `requirements.txt`
- run `pytest -q` and publish JUnit test results to Jenkins
- validate `docker-compose.yml` with `docker compose config`
- resolve branch-based Docker build policy
- build the Docker stack automatically on `main`, `develop`, and `release/*`
- allow manual Docker builds on any other branch when `RUN_DOCKER_BUILD=true`

Jenkins agent prerequisites:

- `python3`
- Docker CLI with Compose support
- a reachable Docker daemon when `RUN_DOCKER_BUILD` is enabled

Suggested pipeline mode:

```bash
RUN_DOCKER_BUILD=false
```

With that default:

- `main`, `develop`, and `release/*` still build containers automatically
- feature branches skip Docker builds unless the parameter is enabled

Enable the parameter only on agents that are allowed to build containers.

### Running it in Jenkins UI

1. In Jenkins, select `New Item`.
2. Choose `Pipeline` for a single branch job, or `Multibranch Pipeline` if you want branch discovery.
3. Point the job at your Git repository.
4. Keep the script path as `Jenkinsfile`.
5. Save the job, then click `Build Now` or `Build with Parameters`.

### What you see visually

- `Stage View` shows each pipeline stage and where a failure happened.
- `Console Output` shows the live logs for test execution and Docker steps.
- `Test Result` appears after the build and shows passed/failed pytest cases from the published JUnit XML.
- `Artifacts` includes the rendered Compose file and other archived pipeline files.

For the best branch-by-branch UI, use a Jenkins `Multibranch Pipeline` job so each Git branch gets its own pipeline view automatically.
