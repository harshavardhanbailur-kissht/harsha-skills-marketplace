# LAP — Top 10 best-written tickets (uniform-pattern study)

Pool scouted: 75 candidates across Story / Task / Epic (3 typed JQL passes, 25 each); 30-ticket shortlist deep-scored.

| Key | Type | Summary (short) | Score | Why it scored well | Direct link |
| --- | --- | --- | --- | --- | --- |
| LAP-1812 | Story | E-Sign LAP documents Phase 2 | 95 | User-story header + actors + preconditions + 8-step functional flow + explicit AC block + working prototype + 10 child bugs | https://kissht.atlassian.net/browse/LAP-1812 |
| LAP-2251 | Task | LOS Issue Tracker dropdown values + cascade rules | 90 | TL;DR, worked examples, full taxonomy tables, Python pseudocode for cascade + server-side validation, AC checklist, source-of-truth refs | https://kissht.atlassian.net/browse/LAP-2251 |
| LAP-2046 | Story | Pan Re-Verification for ETB Users | 80 | Numbered Problem → Solution → Applicability → Exception → Summary table; 6 links + 11 attachments | https://kissht.atlassian.net/browse/LAP-2046 |
| LAP-2206 | Epic | LeadSquared Operational Intelligence — Discovery | 75 | Definition box + objective + 9 numbered scope areas each with sub-bullets, designed to spawn child tickets | https://kissht.atlassian.net/browse/LAP-2206 |
| LAP-2284 | Task | Google Chat bot DM notifications | 75 | Goal/Concepts/Rules/Cross-cutting/Out-of-scope/Engineering principles/Config/AC/Open questions — best-organized free-form Task | https://kissht.atlassian.net/browse/LAP-2284 |
| LAP-1923 | Story | Sales attendance module | 75 | Phased scope tags, exhaustive disposition flow, 7 follow-up bugs, 10 attachments incl. screen recordings | https://kissht.atlassian.net/browse/LAP-1923 |
| LAP-1724 | Story | LSQ ↔ Internal Top-Up | 75 | Main vs Co-Applicant sections with explicit if/else branches and edge cases; 7 child bugs | https://kissht.atlassian.net/browse/LAP-1724 |
| LAP-903  | Story | AA for Co-Applicant | 65 | Tight functional spec + heavy QA evidence (videos + bank-statement xlsx + screenshots) + 6 child bugs | https://kissht.atlassian.net/browse/LAP-903 |
| LAP-2237 | Story | Setting Reapply Date for rejections | 65 | 8-rule logic + 20-row reason→cooling-off table + worked example + manual-review carve-out | https://kissht.atlassian.net/browse/LAP-2237 |
| LAP-2048 | Epic | LAP ↔ LSQ Video KYC | 55 | 3-act epic (Pre-init → Digital Journey → VCIP/Auditor) with bypass + soft/hard reject branches | https://kissht.atlassian.net/browse/LAP-2048 |

**Diversity check:** 5 Stories, 3 Tasks, 2 Epics — meets "at least 2 each" rule.

**Almost-picked, dropped (ranked 11–15):**
- LAP-2080 (Task, score 55) — clean Problem/What/Why/AC structure, but kept slot for higher-scoring Story.
- LAP-2258 (Task, 55) — has AC block, but no links and references a missing inline screenshot.
- LAP-2200 (Task, 50) — well-structured API spec but no AC.
- LAP-1743 (Story, 55) — companion to LAP-1724, very similar shape.
- LAP-1330 (Story, 30) — concise current-vs-needed format, but too short to serve as exemplar.

**Caveats:**
- Most LAP tickets have empty `components` and `fixVersions`. The `fix` and `components` columns of the rubric scored ~zero across the entire pool — those signals don't differentiate this project.
- `comments` field was excluded from fetches because expanding comments + attachments together repeatedly overflowed the tool-result token budget. Comment depth was inferred from issuelinks (bug fan-out) instead.
- Attachment counts skew the rubric heavily (a Story with 15 screenshots like LAP-1812 jumps 10 points), but is genuinely correlated with quality in this project — well-spec'd tickets attract QA evidence.
- Description-length signal was capped at 4,000 chars. LAP-2251 (~9,500 chars) is much richer than the score reflects.
- Several Epics in the LAP project are essentially containers (one-line description). Picking 2 strong Epics required dipping below the median Epic score.
