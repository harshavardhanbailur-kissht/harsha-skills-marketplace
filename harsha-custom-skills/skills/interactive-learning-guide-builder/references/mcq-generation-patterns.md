# MCQ Generation Patterns Reference

## MCQ Quality Framework

### The Anatomy of a Great MCQ

```json
{
  "question": "Clear, unambiguous question testing ONE concept",
  "options": [
    "Correct answer (placed randomly, not always A)",
    "Plausible distractor targeting common misconception #1",
    "Plausible distractor targeting common misconception #2", 
    "Plausible distractor that's close but subtly wrong"
  ],
  "correctAnswer": 0,
  "explanation": "Why the correct answer is right, with context",
  "wrongExplanations": {
    "1": "Why this specific wrong answer is wrong — teaches the misconception",
    "2": "Why this specific wrong answer is wrong — teaches the misconception",
    "3": "Why this specific wrong answer is wrong — teaches the misconception"
  },
  "difficulty": "basic|intermediate|advanced",
  "referencesLessons": ["lesson-1-1", "lesson-2-3"]
}
```

### Rules for Good Questions

1. **Test understanding, not memorization** — "Which scenario would require X?" not "What is the definition of X?"
2. **One correct answer only** — avoid "all of the above" or "none of the above"
3. **Distractors should be plausible** — each wrong answer should target a specific misconception
4. **Avoid negatives** — "Which is NOT..." questions are confusing; rephrase positively
5. **Be specific** — vague questions lead to arguments about interpretation
6. **Randomize correct answer position** — don't always put correct answer as option A

### Difficulty Levels

**Basic (Knowledge/Recall)**
- Tests: Can you remember the definition/fact?
- Format: "What is X?" / "Which of the following is X?"
- Use: First MCQ in a lesson, early modules
- Example: "What does LAP stand for? A) Loan Against Property B) Loan Application Process..."

**Intermediate (Application/Analysis)**
- Tests: Can you apply the concept to a scenario?
- Format: "Given [scenario], what would happen?" / "Which approach is correct for [situation]?"
- Use: Middle MCQs, mid-course modules
- Example: "A Sales Manager receives an applicant with CIBIL score 777. Which program track would this applicant be eligible for?"

**Advanced (Synthesis/Evaluation)**
- Tests: Can you combine knowledge from multiple areas?
- Format: "Considering [context from Module A] and [context from Module B], which conclusion is correct?"
- Use: Checkpoint MCQs, cross-module assessments, final assessment
- Example: "An applicant has been processed through LeadGen Stage 3 in the Normal program. The BCM discovers the CIBIL score was 790. Considering the program eligibility rules and the current stage, what should happen next?"

### Cross-Module MCQ Design

Cross-module MCQs test connections between different topics. They should:

1. **Reference specific prior modules** — "Based on Module 2 (LeadGen) and Module 4 (Credit Processing)..."
2. **Require synthesis** — can't be answered with knowledge from just one module
3. **Be clearly harder** — these are checkpoint/milestone questions
4. **Include richer explanations** — explain the connection between the two concepts

### MCQ Anti-Patterns (DO NOT DO)

- ❌ "Which of the following is TRUE?" with vague options
- ❌ Testing obscure trivia that doesn't aid understanding
- ❌ Making the correct answer obviously longer/more detailed than wrong ones
- ❌ Using "All of the above" / "None of the above"
- ❌ Testing exact numbers when the concept matters more
- ❌ Wrong answer explanations that just say "This is incorrect" — EXPLAIN WHY

### Progressive Hint Design

Each lesson's hints should follow this progression:

1. **Hint 1 (Subtle nudge)**: "Think about the role responsibilities discussed in Lesson 2.1"
2. **Hint 2 (Directional clue)**: "The key difference between Normal and Saral programs relates to credit score thresholds"
3. **Hint 3 (Near-answer)**: "CIBIL 777 is the exact threshold — scores at or above go to Normal program, below go to Saral"

### Generating MCQs from Source Material

**From Glossary/Definitions**:
- Basic: Test term recognition
- Intermediate: Test term application in context

**From Process Flows**:
- Basic: "What comes after Stage X?"
- Intermediate: "If [condition], which stage do you skip to?"
- Advanced: "Compare the Normal and Saral flows at Stage Y"

**From Transcriptions/Walkthroughs**:
- Basic: "Which form does the SM fill at this step?"
- Intermediate: "Why does the system require [field] at this point?"
- Advanced: "What would happen if [field] was incorrect at this stage?"

**From Architecture/Technical Content**:
- Basic: "Which technology handles [function]?"
- Intermediate: "Why was [approach A] chosen over [approach B]?"
- Advanced: "Design a solution for [new scenario] using the patterns discussed"

### Retest Mode Patterns

When a user retests a module:
1. **Shuffle question order** — don't present in same sequence
2. **Shuffle option order** — correct answer at different position
3. **Include 1-2 new questions** if available (from question bank)
4. **Track improvement** — show "You got 3/5 → 5/5 this time"
5. **Highlight previously-wrong answers** — "You missed this last time"

### Knowledge Reinforcement Checkpoints

Place checkpoint assessments at these intervals:
- After every 3 lessons within a module
- At the end of each module (module-level assessment)
- After every 2-3 modules (cross-module checkpoint)
- Final assessment at course end (comprehensive)

Checkpoint MCQs should:
- Pull 60% from current module, 40% from prior modules
- Increase difficulty slightly from lesson-level MCQs
- Include at least 1 cross-module question per checkpoint
