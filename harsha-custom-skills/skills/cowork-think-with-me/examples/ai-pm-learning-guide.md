# Worked Example: AI Learning Guide for PM-Engineers

**Trigger:** User says "Create a learning guide for AI as a PM-engineer"

**Complexity assessed:** Complex (multi-stakeholder, multi-dimensional, career-defining decision). Full session folder created.

---

## Phase 1: Reframe

**User:** Create a learning guide for AI as a PM-engineer.

**Claude:** Before we build, let's be precise about what we're actually deciding. "Learning guide" is the artifact. The real decision is: *what should a PM-engineer at a fintech actually learn about AI, and in what order?*

That decision has a lot of axes we should map before writing a single word. The guide you get depends entirely on what we pick. This will take 10-15 minutes — worth it?

**User:** Yes, let's do it.

---

## Phase 2: Axes

**Claude:** I see five axes where the guide can vary. Let me name them and test them with you:

1. **Scope axis** — From "understand AI concepts" to "build AI systems end-to-end"
2. **Career stage axis** — From "I'm just getting started" to "I want to be the AI decision-maker in my org"
3. **Modality axis** — From "reading and frameworks" to "building things that break"
4. **Tool vs. concept balance** — From "learn to use ChatGPT better" to "understand transformers from first principles"
5. **Time horizon axis** — From "I need to be credible in 2 weeks" to "I want a 12-month depth build"

Are there axes I'm missing? For example: does the guide need to be specific to fintech/lending, or general AI?

**User:** Add fintech specificity as an axis. And I'm thinking this is for someone early-career who has maybe 3-4 hours a week.

**Claude:** Good. That constraint collapses some options and surfaces others. Six axes total, noted in AXES.md.

---

## Phase 3: Option Enumeration

**Claude:** I'm going to generate the option space across all six axes. I'll flag the ones you likely haven't considered.

**Expert panel for this problem:** PM (anchor), Engineering Lead (evaluates what's actually buildable vs. theoretical), Growth Analyst (career positioning is a growth problem), Research Lead (learning science — how skills actually transfer).

---

### The 10 Topics — What Should the Guide Cover?

**Topic 1: How to write effective AI prompts (prompt engineering)**
The obvious one. Most guides start here. It's real but overemphasized at the expense of everything below.

**Topic 2: How to evaluate AI vendor claims**
When a vendor says "our model has 94% accuracy" — what does that mean, and how do you audit it? Critical for a PM who will sit in vendor demos. Almost no learning guides cover this.

**Topic 3: How to build with AI APIs (GPT, Claude, Gemini)**
Writing actual code that calls an API, handles errors, manages rate limits, and ships something. The PM-engineer identity requires this, not just conceptual understanding.

**Topic 4: How to design AI-first product experiences**
UX patterns specific to AI: progressive disclosure of uncertainty, graceful degradation when the model is wrong, trust calibration over time. This is UX design, not ML engineering.

**Topic 5: How to communicate AI uncertainty to stakeholders**
A model that is 85% accurate is not "working 85% of the time" — it fails in correlated, non-random ways. Translating this to a risk or ops team without losing credibility is a learnable skill.

**Topic 6: How to evaluate model quality for your specific problem**
Benchmark datasets are not your data. How to set up an evaluation harness, choose the right metric (precision vs. recall matters differently in credit vs. fraud), and know when a model is good enough.

**Topic 7: How to use AI as a daily work multiplier**
Not ChatGPT prompting — but systematic workflows. Using AI to write PRDs faster, analyze user research, draft SQL, debug product issues. The 10x PM productivity angle.

**Topic 8: How to spot AI washing in the market**
Every fintech vendor in 2025 claims to be AI-powered. Learning to distinguish ML pipelines that work from feature flags dressed as intelligence. Competitive intelligence skill.

**Topic 9: How RAG and vector databases work (without a PhD)**
Retrieval-Augmented Generation is how most fintech AI products actually work internally. Understanding the architecture makes you a better product owner for these systems.

**Topic 10: How to think about AI risk in regulated industries**
Model explainability requirements for credit decisions (RBI, fair lending), bias audit frameworks, what happens when a model is challenged in court. Fintech-specific and almost entirely absent from general AI learning guides.

---

## Phase 4: Ranking

**Ranking criteria and weights (swing weight method):**
- Career leverage: how much does this change what Harsha can do in 12 months? (40%)
- Time-to-competence: achievable in 3-4 hrs/week? (30%)
- Fintech specificity: does this matter more at Kissht vs. generic PM? (20%)
- Uniqueness: does every other PM already know this? (10%)

**Stack-rank:**

### Rank 1: How to build with AI APIs (#3)
**Best case:** Can ship a working internal tool in 4-6 weeks. Proof by demonstration.
**Worst case:** Spends weeks on tutorials and never ships anything real; tutorial hell.
**Why this rank:** The PM-engineer identity only lands if there's something to show. Concepts without code is just a PM who reads newsletters.
**Who would hate this:** PMs who want to stay strategy-side. Engineering leads who feel threatened by a PM who can build.

### Rank 2: How to evaluate model quality for your problem (#6)
**Best case:** Becomes the person in the room who can challenge vendor claims with actual evidence. Career-defining differentiator in fintech.
**Worst case:** Gets deep into evaluation methodology and can't translate it into a decision; analysis paralysis.
**Why this rank:** Fintech has high-stakes model decisions (credit, fraud). A PM who can evaluate models is worth more than one who can only prompt them.
**Who would hate this:** Vendors whose claims don't survive scrutiny.

### Rank 3: How to communicate AI uncertainty (#5)
**Best case:** Becomes the bridge between data science and risk/compliance. Gets invited to the rooms that matter.
**Worst case:** Learns the vocabulary but can't apply it in real-time stakeholder conversations; sounds like they're reading from a slide.
**Why this rank:** Every fintech PM has this problem. No one teaches it. High uniqueness score.
**Who would hate this:** Data scientists who want to keep this translation job for themselves.

### Rank 4: How to design AI-first product experiences (#4)
**Best case:** Designs a product where users actually trust the AI output — measurable in adoption and support tickets.
**Worst case:** Over-engineers UX for uncertainty when most users just want a number; adds friction.
**Why this rank:** Directly applicable to LAP/Ring products. But requires building (#1) to practice it — so sequentially later.
**Who would hate this:** Teams that want to ship fast and iterate.

### Rank 5: How to think about AI risk in regulated industries (#10)
**Best case:** Ahead of the regulatory curve when RBI increases scrutiny of AI credit decisions.
**Worst case:** Regulatory frameworks change faster than learning; becomes out-of-date.
**Why this rank:** High fintech specificity, but slow-burn value. Not a week-one topic.
**Who would hate this:** Product teams on tight roadmap timelines who see compliance as a blocker.

### Rank 6: How to evaluate AI vendor claims (#2)
**Best case:** Saves the company from a bad vendor contract.
**Worst case:** Becomes the skeptic who slows down procurement without adding alternatives.
**Why this rank:** High value but narrow application window — only useful during vendor evaluations.
**Who would hate this:** Vendor sales teams.

### Rank 7: How AI daily work multiplier (#7)
**Best case:** 20-30% time savings on recurring PM work within weeks.
**Worst case:** Optimizes tools before optimizing workflow; saves time on the wrong tasks.
**Why this rank:** Real value, but it is table stakes in 2025. Every PM is learning this. Low uniqueness score.
**Who would hate this:** No one hates this, which is a sign it's not differentiated.

### Rank 8: How RAG and vector databases work (#9)
**Best case:** Can have an informed conversation with engineering about architecture trade-offs.
**Worst case:** Learns enough to be dangerous — starts opining on system design without enough depth.
**Why this rank:** Good background knowledge, but the ROI is low for 3-4 hrs/week. Better to learn by building (#1) than by reading.
**Who would hate this:** Engineers who find half-informed PM architecture opinions more trouble than they're worth.

### Rank 9: Prompt engineering (#1)
**Best case:** Writes better prompts and saves 30 minutes a day.
**Worst case:** Spends weeks on prompt craft when model fine-tuning or RAG would be the better solution.
**Why this rank:** Real skill, but lowest career leverage. Every PM in India is learning this in 2025. Insufficient differentiation.
**Who would hate this:** No one, which is the problem — it's the safe, low-risk, low-differentiation choice.

### Rank 10 (worst): How to spot AI washing (#8)
**Best case:** Reads market landscape faster at conferences.
**Worst case:** Develops cynicism that makes it harder to evaluate genuine AI advances; misses real opportunities.
**Why this rank:** Derivative of evaluation skills (#2, #6). If you can evaluate models well, you can spot AI washing. No need to learn it separately. A standalone topic here is padding.
**Who would hate this:** The author of the guide who built a whole module around this.

---

## Phase 5: Decision Doc Snippet

### Selected: Top 5 Topics (in learning sequence)

1. Build with AI APIs — foundational, everything else follows from shipping something
2. Evaluate model quality — the fintech-specific differentiator
3. Communicate AI uncertainty — the stakeholder bridge
4. Design AI-first experiences — applied UX for what you build
5. AI risk in regulated industries — long-term career insurance

**Rejected topics with specific reasons:**
- Prompt engineering (standalone): Derivative of building (#1). Emerges naturally when you build.
- AI washing detection: Derivative of model evaluation (#2). Redundant as a standalone module.
- RAG/vector databases: Too theoretical for 3-4 hrs/week. Better as a "read when relevant" reference.

**Unexplored adjacent spaces (flagged for future):**
- How to hire and manage AI engineers as a PM
- How to write AI-specific acceptance criteria for user stories
- How to run experiments on model changes without breaking user trust

**Residual uncertainty:**
- We don't know if Kissht's current tech stack enables API-level experimentation. If it doesn't, topic #1 may need to shift to personal projects rather than work projects.
- The 3-4 hrs/week constraint assumes consistent weeks. Fintech PMs rarely have consistent weeks.

**User override log:** None in this session.

---

*Session complete. Decision doc written. Ready to build the actual guide using this as the input.*
