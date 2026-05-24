---
name: interview-battlecard
description: Apply this skill in Stage 5 to produce the day-of one-pager(s) the candidate carries into the interview. Reads the tailored resume + interview-coach prep + research report and emits a tight, scannable battlecard with one page per round.
---

# Interview Battlecard

## When to use

Stage 5 of the career-agent workflow, only after the tailored resume and the interview-coach prep doc both exist. The battlecard is a derivative — it does not introduce new content, it compresses what's already in those two files into something the candidate can scan in 60 seconds before walking into a room.

## Inputs (read these first)

The main agent passes the resume slug and JD slug as part of the orchestration context. Read all three at `limit=1000`:

- `/tailored_resume/<resume-slug>/<jd-slug>.yaml` — for the candidate's strongest claims and headline metrics.
- `/interview_coach/<resume-slug>/<jd-slug>.md` — for the round taxonomy, STAR stories (use the 60-second versions), questions to ask back, and watch-outs.
- `/research/<resume-slug>/<jd-slug>.md` — for the 3 punchiest company facts.

## Output format

A single markdown file at `/interview_battlecard/<resume-slug>/<jd-slug>.md`. Inside, **one page per interview round**, separated by exactly `\n---\n`. The round list and order must match the interview-coach prep doc; do not invent or skip rounds.

Each page is ~30–35 lines, five sections in this fixed order:

```
# <Round name> — <format>

## Introduction
- <keyword / highlight 1>
- <keyword / highlight 2>
- <keyword / highlight 3>
- ...
(4–6 short bullets — keywords and phrases only, NOT full sentences. The candidate uses these as memory anchors for the 60s / 30s self-intro they rehearsed in the prep doc.)

## Stories ready
- **<Story title>** — <one-liner, ~15 sec, lifted from the prep doc>
- ...
(3–5 bullets)

## Company facts to drop
- <punchy fact 1, with a number or named person if possible>
- <punchy fact 2>
- <punchy fact 3>

## Questions to ask
- <one question, grounded in research>
- <one question, grounded in research>

## Watch-outs
- <risk + 1-line mitigation>
- <risk + 1-line mitigation>
```

## Hard rules

- **No preamble, no filler, no commentary.** No "here's your battlecard for…". The first byte of the file is `#`.
- **No headers beyond the five above.** No subheadings, no bullets explaining bullets.
- **Introduction** is keywords / short phrases only — never full sentences, never the rehearsed pitch pasted in verbatim. The interview-coach prep doc contains two rehearsed versions (an elevator pitch and a short version); this section distills both into memory anchors the candidate can scan in 5 seconds to recall either version. Tailor the bullets to the round:
  - **Recruiter / screen**: identity + headline strengths + why-this-company hook.
  - **Technical rounds**: identity + concrete tech stack / systems built (e.g., "RAG, multi-agent orchestration, pgvector") + 1 flagship outcome.
  - **Hiring manager / behavioral**: identity + leadership / ownership signals + motivation hook.
  - **Culture / values / panel**: identity + behaviors and working style (e.g., "bias to ship", "customer-facing", "low-ego") + team-fit hook.
  Different rounds may overlap heavily — that's expected. Lean the emphasis toward what the round will actually probe.
- **Stories ready** uses the 15-second one-liner version distilled from the interview-coach prep's STAR. Don't paste full STAR.
- **Company facts** must be falsifiable (numbers, names, dates). "Innovative culture" is not a fact; "Series C, $80M raised Q3 2025 led by Sequoia" is.
- **Questions to ask** must reference something specific from the research file (named team member, recent product launch, a Glassdoor pattern). Generic questions like "what does success look like?" do not earn a slot.

## Example skeleton (a 2-round battlecard)

```
# Recruiter screen — 30-min phone

## Introduction
- Senior AI / full-stack eng, 8 yrs
- Production AI: agentic apps, RAG, knowledge graphs
- Led multi-agent RAG w/ long-term memory + evals
- Prior: data/ML platforms, lakehouse, pipelines
- Hook: forward-deployed, customer-facing, reusable AI patterns
- Why Inferra: cognitive ontology + agentic focus

## Stories ready
- **Migrated payments to Stripe in 6 weeks** — solo, 0 incidents, $2M throughput
- **Hired the first 3 engineers at Acme** — recruited, onboarded, scoped first sprint
- **Cut p99 latency 40%** — replaced N+1 ORM calls with a batched loader

## Company facts to drop
- Series C, $80M Q3 2025 led by Sequoia
- Hiring manager Maya Chen ex-Stripe payments lead, joined Jan 2026
- Recently launched Inferra v2 — embeddings infra at 1M req/s

## Questions to ask
- How is Maya's payments-infra background shaping this team's roadmap?
- The Inferra v2 launch was Q1 — what's the next infra bet?

## Watch-outs
- Glassdoor flags long hours during launches — ask about on-call cadence

---

# Hiring-manager behavioral — 60 min with Maya

## Introduction
- Senior AI eng, builder + owner
- Ship end-to-end; comfortable owning ambiguity
- Led 0→1 systems and small teams (3 hires at Acme)
- Bias to ship, low-ego, write things down
- Why now: want customer-facing impact, not pure infra

## Stories ready
- ...
```

## Output handoff

After writing the file, return one short line to the user: "Battlecard saved to `/interview_battlecard/<resume>/<jd>.md` — N pages, one per round." Don't dump the markdown.
