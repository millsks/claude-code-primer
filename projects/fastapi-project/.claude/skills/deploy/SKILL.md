---
name: deploy
description: Run the full deployment checklist for the fastapi-project — tests, Docker build, registry push, service update, health verification. Use this skill when the user says "deploy", "ship it", "push a release", "deploy to staging/production", "cut a release", or any request to move a build to a running environment.
argument-hint: <environment> [--tag <tag>]
compatibility: fastapi-project · Docker · pixi at project root
disable-model-invocation: false
license: MIT
metadata:
  author: Kevin Mills
  tags: deploy, docker, fastapi, ci, health-check
user-invokable: true
---

# deploy

Run the deployment checklist for fastapi-project: gate on tests, build and push a Docker image, update the target service, then confirm the health endpoint is responding.

## Arguments

`$ARGUMENTS` is expected as: `<environment> [--tag <tag>]`

| Argument | Required | Description |
|---|---|---|
| `<environment>` | yes | `staging` or `production` |
| `--tag <tag>` | no | Docker image tag; defaults to the current git short SHA |

If `$ARGUMENTS` is empty, ask the user for the target environment before proceeding.

## Required environment variables

These must be set in the shell before invoking this skill. Stop and tell the user if any are missing:

| Variable | Purpose |
|---|---|
| `REGISTRY` | Docker registry host (e.g. `ghcr.io/org`) |
| `IMAGE_NAME` | Image name; defaults to `fastapi-project` if unset |
| `SERVICE_NAME` | Name of the running service to update (e.g. `fastapi-project-staging`) |
| `HEALTH_URL` | Full URL of the health endpoint (e.g. `https://staging.example.com/health`) |

## Step 1 — Resolve tag and verify prerequisites

```bash
git rev-parse --short HEAD
```

If `--tag` was provided, use it. Otherwise use the short SHA from the command above as `$TAG`.

Confirm the working tree is clean:

```bash
git status --short
```

If there are uncommitted changes, stop and warn the user — deploying from a dirty tree makes the image unreproducible.

## Step 2 — Run the CI gate

```bash
pixi run ci
```

This runs pre-commit, build, mypy, ruff, and the full test suite with coverage. Do not proceed if any step fails. Report the exact failing step to the user.

## Step 3 — Build the Docker image

```bash
docker build \
  --tag "${REGISTRY}/${IMAGE_NAME:-fastapi-project}:${TAG}" \
  --tag "${REGISTRY}/${IMAGE_NAME:-fastapi-project}:latest" \
  --label "git.sha=${TAG}" \
  --label "deploy.env=${ENVIRONMENT}" \
  .
```

Confirm the build exits 0 before continuing.

## Step 4 — Push to registry

```bash
docker push "${REGISTRY}/${IMAGE_NAME:-fastapi-project}:${TAG}"
docker push "${REGISTRY}/${IMAGE_NAME:-fastapi-project}:latest"
```

Both tags must push successfully.

## Step 5 — Update the service

Update the running service to the new image. The exact command depends on the orchestrator in use; use whichever is available:

**Docker Swarm:**
```bash
docker service update \
  --image "${REGISTRY}/${IMAGE_NAME:-fastapi-project}:${TAG}" \
  "${SERVICE_NAME}"
```

**Kubernetes:**
```bash
kubectl set image deployment/"${SERVICE_NAME}" \
  app="${REGISTRY}/${IMAGE_NAME:-fastapi-project}:${TAG}"
kubectl rollout status deployment/"${SERVICE_NAME}"
```

If neither orchestrator is configured, tell the user what image tag was pushed and stop here — do not guess at the update mechanism.

## Step 6 — Verify health check

Wait for the service to stabilize (up to 60 seconds), then poll the health endpoint:

```bash
for i in $(seq 1 12); do
  STATUS=$(curl -sf "${HEALTH_URL}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null)
  if [ "$STATUS" = "ok" ]; then echo "healthy"; exit 0; fi
  echo "attempt $i: not ready — retrying in 5s"
  sleep 5
done
echo "health check failed after 60s"
exit 1
```

If the health check never returns `{"status": "ok"}`, report failure and tell the user to inspect service logs before rolling back.

## Step 7 — Report

Tell the user:

- Environment deployed to
- Image tag pushed (`$REGISTRY/$IMAGE_NAME:$TAG`)
- Health check URL and final status
- Suggested next step: tag the git commit as a release if deploying to production
