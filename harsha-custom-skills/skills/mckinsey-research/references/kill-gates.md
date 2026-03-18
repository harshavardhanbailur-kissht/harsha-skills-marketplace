# Kill Gates — Topic Worthiness Assessment

## Origin

McKinsey MGI applies a rigorous triage process to research proposals, rejecting
topics where the firm cannot add genuinely new empirical value — the principle being
"we've nothing to add." This prevents wasted effort on topics that would produce
confirmatory rather than novel findings. The same discipline applies here: not every
question deserves maximum-depth research.

## Kill Gate 1: Initial Assessment

Ask these questions BEFORE any research investment:

### Question 1: Can we add genuinely new value?
- Is this topic already well-covered by authoritative sources?
- Would our research CONFIRM existing knowledge or DISCOVER new insights?
- Is there a genuine gap in understanding that research could fill?

**Kill if**: Topic is well-established with strong consensus and no gaps.
**Proceed if**: Genuine uncertainty, conflicting evidence, or unexplored angle.

### Question 2: Is the question specific enough?
- Can we define clear success criteria for the research?
- Is the scope bounded (not "tell me everything about AI")?
- Can we decompose into answerable sub-questions?

**Kill if**: Question is too vague to produce actionable findings.
**Redirect if**: Help user narrow the question, then reassess.

### Question 3: Does the topic warrant the requested depth?
- Is the user making a decision based on this research?
- What are the stakes of being wrong?
- Does Standard scrutiny suffice, or is Enhanced/Maximum needed?

**Use Standard for**: Factual lookups, well-established topics, low stakes.
**Use Enhanced for**: Important decisions, contested topics, skill creation input.
**Use Maximum for**: High-stakes, novel claims, production code, strategic decisions.

### Question 4: Are credible sources accessible?
- Can we find authoritative sources via web search?
- Is the domain covered by official documentation?
- Are there academic or industry research publications?

**Kill if**: No credible sources exist (purely speculative topic).
**Proceed with caveat if**: Limited sources exist — flag evidence quality as Low.

## Kill Gate 2: Mid-Research Assessment

After initial searching, reassess:

### Is the finding novel?
- Are we just confirming what every other source says?
- If yes, the research has low value — summarize the consensus briefly.

### Is the evidence adequate?
- Can we meet minimum triangulation requirements (2+ sources per major claim)?
- If not, flag as low-evidence and consider reducing scope.

### Are we falling into a rabbit hole?
- Is the research expanding beyond useful scope?
- Apply ADaPT framework: only decompose further when current granularity fails.

## Kill Gate 3: Pre-Publication Assessment

Before delivering output:

### Does this pass the "so what?" test?
- Would a decision-maker change their actions based on this?
- If not, the research may be intellectually interesting but not actionable.

### Would we be embarrassed by this in 6 months?
- Run the pre-mortem: are there obvious failure modes?
- Are claims adequately caveated?

## Topic Redirection Patterns

When killing a topic, don't just say "no." Redirect constructively:

- "This topic is well-established. The consensus is [X]. Would you like me
  to research [more specific angle] instead?"
- "This question is too broad. Here are 3 specific sub-questions that would
  produce more actionable findings: [list]"
- "There aren't enough credible sources for deep research on this. I can
  provide a Standard-tier summary of what's available."
