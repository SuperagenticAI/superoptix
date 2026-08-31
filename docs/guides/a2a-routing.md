# Routing quality

An A2A gateway moves traffic to an agent that already has a card. Whether other
agents choose to call that agent is decided by the card itself: a caller reads
`skills[].description`, `examples` and `tags` and picks. Those strings are the
routing interface.

This page covers measuring how well an agent can be routed to, and improving it
with GEPA.

## Why it is measurable

Routing outcomes are observable, so description quality produces a number.
The following four skills differ only in how each describes itself. The queries
are identical.

Vague:

```
billing   "Handle a customer query"
refunds   "Handle a customer request"
tech      "Help the customer with the product"
accounts  "Assist a customer"
```

Specific:

```
billing   "Resolve invoice disputes, duplicate charges, payment failures and
           subscription price questions"
refunds   "Decide and process refund and money-back requests, including returns
           and partial refunds"
tech      "Debug product crashes, upload errors, broken integrations that stop
           syncing, and login failures"
accounts  "Change workspace seats, account settings, permissions and the email
           on a login"
```

Scored against eight queries written in caller vocabulary:

| Catalogue | Invocation | Discovery |
| --- | --- | --- |
| Vague | 12.5% | 75% |
| Specific | 100% | 100% |

## The three metrics

`score_routing` reports three rates, because being invisible and being
confusable are different problems with different fixes.

**Discovery** — the skill appeared in the top three candidates. A skill that is
never surfaced cannot be called, whatever else is true of it.

**Invocation** — the skill was the top choice. This corresponds to a caller
reaching the right agent.

**Confusion** — of the cases a skill lost, the proportion lost to a sibling
rather than to nothing. A high rate means two descriptions do not distinguish
themselves from each other; a low rate with poor invocation means the
description does not cover the vocabulary callers use.

```python
from superoptix.protocols.a2a.routing import (
    LexicalRouter, catalogue_from_cards, score_routing,
)

skills = catalogue_from_cards([card_a, card_b, card_c])
report = score_routing(LexicalRouter(), skills, cases)

print(report.summary())
print(report.per_skill)
print(report.misroutes)      # query, expected, what won instead
```

## Routers

A router stands in for the calling agent. Two are provided.

`LexicalRouter` scores TF-IDF cosine similarity over each skill's routing text.
It is deterministic and needs no model provider, which makes baselines
reproducible and lets the metric run in CI. It measures whether a description
carries terms that separate the skill from its neighbours.

`LLMRouter` asks a model to choose, which is closer to how a real caller
behaves. It takes any callable accepting a prompt and returning text.

The interface is pluggable for a specific reason. Optimising descriptions
against the same router that scores them measures that router's reading habits
rather than interoperability. Pass a different router as `validation_router` to
re-score the result:

```python
result = optimize_routing(
    skills, cases,
    reflection_lm=lm,
    router=LexicalRouter(),
    validation_router=LLMRouter(lm=other_model),
)
print(result.summary())
```

An improvement that survives the swap is real. One that does not has taught you
something more useful than a number.

## Optimising with GEPA

`optimize_routing` runs GEPA over the card's routing surface. Only
`skills[].description` and `skills[].examples` are candidates, matching what the
adapt intermediate representation declares optimisable. Identity and protocol
fields are outside its reach, so optimisation cannot change what an agent claims
to be.

```python
from superoptix.protocols.a2a.routing.optimize import optimize_routing

result = optimize_routing(
    skills,
    cases,
    reflection_lm=lm,
    max_metric_calls=200,
)

print(result.baseline_score, result.optimized_score)
print(result.optimized_descriptions)
```

On the vague catalogue above, this raises invocation from 12.5% to 75%.

Failed cases are returned to GEPA as text naming what won instead:

```
Misrouted: 'I want my money back for last month' went to billing:billing
instead of refunds:refunds. Those two descriptions do not distinguish
themselves from each other for this kind of request.
```

Reflecting on why a routing decision failed is what makes the technique work
here, and it is the same shape as GEPA's `gskill`, which optimises coding-agent
skill files against bug-fix pass rates.

## Building an evaluation set

Cases pair a query with the skill that should win it:

```python
from superoptix.protocols.a2a.routing.queries import RoutingCase

cases = [
    RoutingCase("I was charged twice for the same invoice", "billing:billing", "src"),
    RoutingCase("the app crashes when I upload a file", "tech:tech", "src"),
]
```

`generate_cases` will derive cases from a catalogue, and `hard=True` withholds
each skill's own name so a query cannot win by echoing the title.

**The generated set is a smoke test, not a benchmark.** Every field on a card is
either the description under optimisation or was derived from it, so a query
generated from the card tends to reward the text it is meant to evaluate.
`gskill` avoids this because SWE-smith mines tasks from a repository, which is
ground truth independent of the artifact being optimised. No equivalent free
source exists here.

Two sources produce a meaningful evaluation set:

**Model-generated queries.** Ask a model for realistic caller phrasings per
skill, using the agent's domain rather than its description. Faster to obtain,
and carries the bias of whichever model wrote them.

**Recorded traffic.** Instrument real A2A calls and label the outcome. Slower to
accumulate, and the only source that cannot be accused of circularity. It also
doubles as an adoption signal.

Until one of those is in place, treat reported gains as directional.

## Reference

| Object | Module |
| --- | --- |
| `LexicalRouter`, `LLMRouter`, `SkillRef` | `superoptix.protocols.a2a.routing.router` |
| `RoutingCase`, `generate_cases`, `catalogue_from_cards` | `superoptix.protocols.a2a.routing.queries` |
| `score_routing`, `RoutingReport` | `superoptix.protocols.a2a.routing.metrics` |
| `optimize_routing`, `make_evaluator` | `superoptix.protocols.a2a.routing.optimize` |
