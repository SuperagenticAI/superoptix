# Public SuperOptiX A2A endpoint

The published SuperOptiX agent: an Agent Card at a well-known URL plus a small
service that answers A2A calls. It exposes two deterministic catalogue skills —
no model provider keys, no user code, no persistent storage.

| Skill | What it answers |
| --- | --- |
| `framework-a2a-readiness` | Whether a named agent framework supports A2A, which spec line it targets, and what is missing for 1.0 |
| `agent-card-review` | Scores a submitted Agent Card for conformance and discoverability |

## The two pieces, and why you need both

An Agent Card is a static JSON document, but the URLs inside it must answer A2A
calls. **A card pointing at nothing is worse than no card** — other agents
discover you, call you, and fail, and that failure is attributed to your agent.

So this is not a choice between "host on Render" and "serve JSON from the
website". It is both, and they must agree:

1. **The card** is served at `https://superoptix.ai/.well-known/agent-card.json`.
   Static file, no runtime. This is the discovery path.
2. **The service** runs the ASGI app below and answers the calls the card
   advertises. The card's `url` and `supportedInterfaces[].url` must point here.

This mirrors how SuperQode does it: the card lives on the marketing domain
(`super-agentic.ai/.well-known/agent-card.json`) while the service runs on
Render, and the service serves its own copy of the card too.

## Where to host it

Measured on the live Render endpoint and on the container locally, 31 August 2026:

| | Cold start | Idle cost |
| --- | --- | --- |
| Render free | **42.5 s** | free |
| Cloud Run, `minScale: 0` | **1.7 s** | free within the monthly request allowance |
| Cloud Run, `minScale: 1` | none | a few dollars a month |

Warm requests on Render return in 0.4 s, so the 42.5 s is entirely start-up:
the free tier stops the container and a cold request pays a full application
boot behind a proxy wake-up.

That number decides the host. A2A clients apply timeouts, and a registry
fetching an Agent Card with a 30 second timeout records the agent as
unreachable rather than slow. The container starts in 1.7 s, which is inside
those timeouts, so scale-to-zero is usable and the free tier is viable for an
endpoint called infrequently.

## Deploying to Cloud Run

The image is the `Dockerfile` at the repository root. It has been built and run
locally with the same environment Cloud Run provides.

It sits at the root rather than in this directory because Cloud Build uses the
Dockerfile's directory as the build context, and the image copies
`pyproject.toml` and `superoptix/` from the repository root.

### 1. Prepare the project

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

### 2. Deploy

The `Dockerfile` lives at the repository root (Cloud Build uses that directory
as the build context). A `cloudbuild.yaml` at the root sets
`options.logging: CLOUD_LOGGING_ONLY`, which a user-managed trigger service
account requires. On the Cloud Build trigger: Type Autodetected or Cloud Build
configuration file, uncheck "Send build logs to GitHub", and keep the service
account. The trigger is tag-based, so a push to `main` does not deploy.

Deploy from the repo root:

```bash
gcloud run deploy superoptix-a2a \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 4 \
  --memory 512Mi \
  --set-env-vars SUPEROPTIX_A2A_PUBLIC_URL=https://a2a.superoptix.ai,SUPEROPTIX_TELEMETRY=false
```

A git tag on `main` is what rebuilds the live service. Pushing to `main` alone
does not.

`--source` builds with Cloud Build, so no registry or pipeline is needed. The
command prints a `*.run.app` URL. Test on that before touching DNS:

```bash
curl -s https://YOUR-SERVICE.run.app/.well-known/agent-card.json | jq .name
```

`deploy/a2a/service.yaml` holds the same configuration declaratively for
`gcloud run services replace`. That path does **not** grant public invoker;
add `allUsers` as `roles/run.invoker` (or keep using `--allow-unauthenticated`
on `gcloud run deploy`).

### 3. Map the subdomain

```bash
gcloud run domain-mappings create \
  --service superoptix-a2a \
  --domain a2a.superoptix.ai \
  --region europe-west1
```

The command prints the DNS record to add. For a subdomain that is a CNAME on
the `a2a` host pointing at `ghs.googlehosted.com`. Cloud Run issues the TLS
certificate once the record resolves, which usually takes minutes but can take
longer.

At the registrar, turn off domain forwarding and any parked page on the
subdomain. Both shadow DNS records and leave you debugging a placeholder.

### Render settings, and their Cloud Run equivalent

| Render | Cloud Run |
| --- | --- |
| Build Command | The `RUN` layer in the Dockerfile |
| Start Command | The `CMD` in the Dockerfile |
| Environment variables | `--set-env-vars`, or Secret Manager for credentials |
| Region | `--region` |
| Health Check Path | `startupProbe` in `service.yaml` |
| Auto-Deploy on commit | A Cloud Build trigger, or re-run `gcloud run deploy` |
| Build Filters | Trigger `includedFiles` |

## Migrating from Render

Change the address before changing the host. The Agent Card is fetched and
cached by registries, so moving both at once gives two failure modes and no way
to separate them.

1. Point the card at the new address while Render still serves it. Set
   `SUPEROPTIX_A2A_PUBLIC_URL=https://a2a.superoptix.ai` on the Render service,
   redeploy, and add a CNAME from `a2a` to the Render hostname. Callers now
   record an address you control.
2. Deploy to Cloud Run and verify on the `run.app` URL.
3. Repoint the CNAME to Cloud Run. Nothing holding a cached card re-fetches,
   because the advertised URL did not change.
4. Keep Render running until Cloud Run has served real traffic. Rolling back is
   then a DNS change.

### Two things that behave differently on Cloud Run

The filesystem is ephemeral and per-instance. The public endpoint holds task
state in memory and writes nothing, so it is unaffected. An adapted agent that
persists to disk needs storage that survives a restart.

Instances are recycled. In-memory A2A task state does not survive scale-down, so
a caller polling `GetTask` after an idle period may find the task gone. This
starts mattering when push notifications are implemented.

### Image size

The image is large because `dspy` is a core `pyproject.toml` dependency, so
`pip install ".[a2a]"` still pulls LiteLLM, NumPy, botocore and tokenizers. The
public endpoint does not call a model. Cold start is already 1.7 s; shrinking
the image is a build-time concern, not a latency one.

## Publish the card

`agent-card.json` in this directory is generated. Regenerate after changing the
skills or the service URL:

```bash
python -c "
import json
from superoptix.protocols.a2a.public import build_public_agent_card
print(json.dumps(build_public_agent_card(), indent=2))
" > deploy/a2a/agent-card.json
```

Then serve it from the website at exactly `/.well-known/agent-card.json` with
`Content-Type: application/json`. Discovery clients do not follow redirects
reliably, so publish it at the canonical path rather than redirecting to it.

### Which domain

Use the apex marketing domain — `superoptix.ai/.well-known/agent-card.json` —
not a subdomain. A2A discovery convention is to look up the well-known path on
the organisation's domain, and a card on `a2a.superoptix.ai` is one that nobody
looks for. Keep the *service* on Cloud Run at `a2a.superoptix.ai`; keep the
*card* on the domain people already know.

## Verify before announcing

```bash
# 1. The card parses and scores well — reviewed by our own skill
python -c "
import json
from superoptix.protocols.a2a.public import agent_card_review, build_public_agent_card
print(agent_card_review(json.dumps(build_public_agent_card()))['response'])
"

# 2. The advertised endpoints actually answer
curl -s https://superoptix.ai/.well-known/agent-card.json | python -m json.tool
curl -s -X POST https://a2a.superoptix.ai/message:send \
  -H 'content-type: application/json' \
  -d '{"message":{"role":"ROLE_USER","parts":[{"text":"Does CrewAI support A2A?"}]}}'
curl -s -X POST https://a2a.superoptix.ai/a2a/jsonrpc \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"role":"user","parts":[{"kind":"text","text":"Does CrewAI support A2A?"}]}}}'
```

## Known gap

The card is **unsigned**. Signed Agent Cards are the A2A 1.0 mechanism for
proving a card came from the domain owner, and our own `agent-card-review` skill
flags this on our own card (roadmap item C3). SuperQode's published card is
currently unsigned too. Sign both, or say plainly that neither is signed yet.
