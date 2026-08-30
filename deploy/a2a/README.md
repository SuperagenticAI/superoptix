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

## Deploy the service

```bash
# From the repo root
render blueprint launch          # uses deploy/a2a/render.yaml
```

Or point Render at `deploy/a2a/render.yaml` from the dashboard. Manual settings:

- **Build**: `pip install ".[a2a]"`
- **Start**: `uvicorn superoptix.protocols.a2a.public.app:app --host 0.0.0.0 --port $PORT`
- **Health check**: `/.well-known/agent-card.json`

Set `SUPEROPTIX_A2A_PUBLIC_URL` to the public URL Render assigns. If it does not
match, the card advertises an address callers cannot reach.

Run it locally the same way:

```bash
pip install -e ".[a2a]"
uvicorn superoptix.protocols.a2a.public.app:app --reload
curl localhost:8000/.well-known/agent-card.json
```

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
looks for. Keep the *service* on Render (or a subdomain); keep the *card* on the
domain people already know.

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
curl -s -X POST https://superoptix.onrender.com/message:send \
  -H 'content-type: application/json' \
  -d '{"message":{"role":"ROLE_USER","parts":[{"text":"Does CrewAI support A2A?"}]}}'
```

## Known gap

The card is **unsigned**. Signed Agent Cards are the A2A 1.0 mechanism for
proving a card came from the domain owner, and our own `agent-card-review` skill
flags this on our own card (roadmap item C3). SuperQode's published card is
currently unsigned too. Sign both, or say plainly that neither is signed yet.
