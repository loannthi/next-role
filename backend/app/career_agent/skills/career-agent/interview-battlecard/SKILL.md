---
name: interview-battlecard
description: Apply this skill in Stage 5 to produce the day-of one-pager(s) the candidate carries into the interview. Reads the tailored resume + interview-coach prep + research report and emits a tight, scannable battlecard as a JSON source-of-truth plus a rendered PDF.
---

# Interview Battlecard

## When to use

Stage 5 of the career-agent workflow, only after the tailored resume and the interview-coach prep doc both exist. The battlecard is a derivative — it does not introduce new content, it compresses what's already in those two files into something the candidate can scan in 60 seconds before walking into a room.

## Inputs (read these first)

The main agent passes the resume slug and JD slug as part of the orchestration context. Read all three at `limit=1000`:

- `/tailored_resume/<resume-slug>/<jd-slug>.yaml` — for the candidate's strongest claims and headline metrics.
- `/interview_coach/<resume-slug>/<jd-slug>.md` — for the round taxonomy, STAR stories (use the 60-second versions), questions to ask back, and watch-outs.
- `/research/<resume-slug>/<jd-slug>.md` — for the 3 punchiest company facts.

## Outputs

Two siblings on disk; the JSON is the source of truth (LLM-written, user-editable), the PDF is the day-of artifact the candidate downloads and reviews.

```
/interview_battlecard/<resume-slug>/<jd-slug>.json
/interview_battlecard/<resume-slug>/<jd-slug>.pdf
```

Two-step flow, in this exact order:

1. `overwrite_file("/interview_battlecard/<resume>/<jd>.json", <json string>)` — write the JSON source.
2. `render_battlecard_pdf("/interview_battlecard/<resume>/<jd>.json")` — render the PDF beside it.

If the user later edits the JSON in Workspace > Files and asks for a re-render, call `render_battlecard_pdf` again on the same path. The tool is idempotent.

## JSON shape (strict)

The JSON object must validate against this shape exactly. The `rounds` array order must match the interview-coach prep doc; do not invent or skip rounds.

```json
{
  "document_title": "Interview Battle Card — <Candidate Name>",
  "rounds": [
    {
      "title": "<Round name> — <format>",
      "subtitle": "<Company> · <Role>",
      "introduction": ["<keyword 1>", "<keyword 2>", "..."],
      "stories_ready": [
        { "title": "<Story title>", "body": "<15-sec one-liner>" }
      ],
      "company_facts": ["<falsifiable fact 1>", "..."],
      "questions": ["<grounded question 1>", "..."],
      "watch_outs": ["<risk + 1-line mitigation 1>", "..."]
    }
  ]
}
```

Per round, target counts:

- `introduction`: 4–6 entries. Keywords / short phrases only, never full sentences. Memory anchors the candidate scans in 5 seconds to recall either the elevator or short version of the rehearsed self-intro.
- `stories_ready`: 3–5 entries. Each is `{title, body}`; `body` is the 15-second one-liner distilled from the interview-coach STAR — never paste the full STAR.
- `company_facts`: 3 entries.
- `questions`: 2 entries.
- `watch_outs`: 2 entries.

Tailor `introduction` to the round:

- **Recruiter / screen**: identity + headline strengths + why-this-company hook.
- **Technical rounds**: identity + concrete tech stack / systems built (e.g., "RAG, multi-agent orchestration, pgvector") + 1 flagship outcome.
- **Hiring manager / behavioral**: identity + leadership / ownership signals + motivation hook.
- **Culture / values / panel**: identity + behaviors and working style (e.g., "bias to ship", "customer-facing", "low-ego") + team-fit hook.

Different rounds may overlap heavily — that's expected. Lean the emphasis toward what the round will actually probe.

## Hard rules

- **No preamble, no filler, no commentary.** The JSON value is the deliverable. Do not write any markdown summary alongside it.
- **`introduction` items are keywords / short phrases.** Never full sentences, never the rehearsed pitch pasted verbatim.
- **`stories_ready[].body` is the 15-second one-liner**, not the full STAR.
- **`company_facts` must be falsifiable** (numbers, names, dates). "Innovative culture" is not a fact; "Series C, $80M raised Q3 2025 led by Sequoia" is.
- **`questions` must reference something specific from the research file** (named team member, recent product launch, a Glassdoor pattern). Generic questions like "what does success look like?" do not earn a slot.
- **No extra keys** beyond those listed. The PDF template ignores unknown keys silently — if you invent one, it just disappears.

## Example (2-round battlecard)

```json
{
  "document_title": "Interview Battle Card — Jane Doe",
  "rounds": [
    {
      "title": "Recruiter screen — 30-min phone",
      "subtitle": "Inferra · Senior AI Engineer",
      "introduction": [
        "Senior AI / full-stack eng, 8 yrs",
        "Production AI: agentic apps, RAG, knowledge graphs",
        "Led multi-agent RAG w/ long-term memory + evals",
        "Prior: data/ML platforms, lakehouse, pipelines",
        "Hook: forward-deployed, customer-facing, reusable AI patterns",
        "Why Inferra: cognitive ontology + agentic focus"
      ],
      "stories_ready": [
        { "title": "Migrated payments to Stripe in 6 weeks", "body": "solo, 0 incidents, $2M throughput" },
        { "title": "Hired the first 3 engineers at Acme", "body": "recruited, onboarded, scoped first sprint" },
        { "title": "Cut p99 latency 40%", "body": "replaced N+1 ORM calls with a batched loader" }
      ],
      "company_facts": [
        "Series C, $80M Q3 2025 led by Sequoia",
        "Hiring manager Maya Chen ex-Stripe payments lead, joined Jan 2026",
        "Recently launched Inferra v2 — embeddings infra at 1M req/s"
      ],
      "questions": [
        "How is Maya's payments-infra background shaping this team's roadmap?",
        "The Inferra v2 launch was Q1 — what's the next infra bet?"
      ],
      "watch_outs": [
        "Glassdoor flags long hours during launches — ask about on-call cadence",
        "Comp band public but unspecified for AI roles — anchor to senior infra range"
      ]
    },
    {
      "title": "Hiring-manager behavioral — 60 min with Maya",
      "subtitle": "Inferra · Senior AI Engineer",
      "introduction": [
        "Senior AI eng, builder + owner",
        "Ship end-to-end; comfortable owning ambiguity",
        "Led 0→1 systems and small teams (3 hires at Acme)",
        "Bias to ship, low-ego, write things down",
        "Why now: want customer-facing impact, not pure infra"
      ],
      "stories_ready": [
        { "title": "Owned Hero AI architecture end to end", "body": "broke a complex assistant into modular pieces and made the whole platform coherent" },
        { "title": "Resolved an outage cross-functionally", "body": "drove a 2-team postmortem, shipped a runbook + 3 follow-up PRs" },
        { "title": "Coached a junior through promotion", "body": "structured weekly 1:1s, scoped 2 quarter-long projects, hit promo bar" }
      ],
      "company_facts": [
        "Maya Chen joined Jan 2026 from Stripe Payments Infra",
        "Inferra reorg'd into 4 pods in Q4 2025 per Sequoia announcement",
        "Glassdoor: 3.6/5, 142 reviews, top complaint is launch-week hours"
      ],
      "questions": [
        "After the Q4 pod reorg, how have the boundaries between the Agents pod and Infra pod settled?",
        "What does the first 90 days look like for the FDE coming into Maya's pod?"
      ],
      "watch_outs": [
        "Don't oversell pure infra — Maya wants customer-facing FDEs; anchor on rollout + discovery stories",
        "Time-zone gap if I'm remote — open with a concrete async-collab plan"
      ]
    }
  ]
}
```

## Output handoff

After step 2 (`render_battlecard_pdf`) returns OK, return file JSON + PDF paths under `/interview_battlecard/<resume>/<jd>.{json,pdf}`." Don't dump the JSON.
