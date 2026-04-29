# Cognitive Architecture Reference

## Working Memory

### Capacity Limits

**Modern Understanding**: 4±1 chunks (Cowan, 2001)
- NOT Miller's 7±2 (1956) - that included chunking strategies
- Pure capacity without chunking: 3-5 items
- Chunks can be hierarchical (letters → words → phrases)

**Interface Implications**:
| Element | Maximum | Source |
|---------|---------|--------|
| Navigation items (ungrouped) | 4-5 | Working memory |
| Visible options | 5-7 | With grouping |
| Form fields per section | 3-4 | Chunk boundary |
| Wizard steps visible | 4-5 | Progress tracking |

### Chunking Strategies

**Effective Chunking**:
```
// Bad: 12 ungrouped items
Phone: 1234567890

// Good: Chunked into 3 groups
Phone: (123) 456-7890
```

**Code Detection**:
- Form sections with clear headings
- Visual grouping with whitespace
- Progressive disclosure patterns

### Memory Decay

**Without Rehearsal**:
- 50% loss within 20 seconds
- Near-complete loss by 30 seconds

**Design Implications**:
- Don't require users to remember information across screens
- Show reference information in context
- Persist important data visually

---

## Attention

### Attention Residue

**Core Finding** (Leroy, 2009):
- Part of attention stays with prior tasks
- Especially strong with unfinished tasks (Zeigarnik effect)
- Takes ~23 minutes to fully refocus after interruption

**Design Implications**:
- Auto-save with visible state indicators
- Clear task completion signals
- Minimize required context switches
- Support "pick up where you left off"

### Attention Span

**Modern Measurement** (Gloria Mark):
- Average screen attention: 47 seconds (2021)
- Down from 75 seconds (2012)
- Frequent self-interruption

**Implications**:
- Front-load critical information
- Enable quick scanning
- Support interrupted workflows

### Selective Attention

**Inattentional Blindness**:
- Users miss unexpected elements even when looking directly at them
- 50% miss gorilla in attention experiments (Simons & Chabris)

**Change Blindness**:
- Difficulty detecting changes across visual disruptions
- Modal dialogs can cause users to miss underlying changes

**Design Countermeasures**:
```css
/* Draw attention through motion */
@keyframes attention-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(255, 0, 0, 0); }
}

.requires-attention {
  animation: attention-pulse 2s ease-in-out 3;
}
```

### Interruption Cost

**Cognitive Disruption** (Altmann & Trafton):
- ~7 seconds transient slowdown after any interruption
- Error rate increases during recovery
- Complex tasks: Much longer recovery

**Notification Impact**:
- Each notification: 30% attention drop
- Phone visible (even silent): Cognitive capacity reduction

---

## Cognitive Load Theory

### Three Types of Load

**1. Intrinsic Load**
- Inherent difficulty of material
- Cannot be reduced by design
- Example: Tax forms are complex because taxes are complex

**2. Extraneous Load**
- Caused by poor design
- CAN and SHOULD be minimized
- Example: Confusing navigation, unclear labels

**3. Germane Load**
- Productive learning effort
- Supports schema formation
- Example: Worked examples, meaningful practice

### Load Reduction Strategies

**Split Attention Effect**:
- Don't separate related information
- Bad: Error message at top, field at bottom
- Good: Inline error adjacent to field

**Redundancy Effect**:
- Don't repeat information unnecessarily
- Bad: Audio narration reading on-screen text
- Good: Audio describes, visual shows

**Modality Effect**:
- Use multiple channels for complex information
- Audio + visual more effective than visual + visual
- Working memory has separate audio/visual stores

### Measuring Cognitive Load

**Behavioral Indicators**:
- Task completion time
- Error rate
- Number of attempts
- Time to first interaction

**Self-Report** (NASA-TLX):
- Mental demand
- Temporal demand
- Performance
- Effort
- Frustration

---

## Decision Making

### Hick's Law

**Formula**: RT = a + b × log₂(n+1)
- RT: Reaction time
- n: Number of choices
- Each doubling of choices adds constant time

**Practical Application**:
| Choices | Relative Time |
|---------|---------------|
| 2 | 1.0x (baseline) |
| 4 | 1.5x |
| 8 | 2.0x |
| 16 | 2.5x |

**Caveat**: Only applies to equally probable choices
- Frequently used options should be more prominent
- Familiarity reduces effect

### Choice Overload

**Jam Study** (Iyengar & Lepper, 2000):
- 24 jam options: 3% purchase rate
- 6 jam options: 30% purchase rate

**But Effect is Contested**:
- Meta-analyses show inconsistent replication
- Depends on: expertise, preference certainty, display format

**Safe Guidance**:
- Default/recommended options reduce paralysis
- Filtering and sorting essential for large catalogs
- Progressive disclosure for complex choices

### Decision Fatigue

**Ego Depletion** (contested but design-relevant):
- Decision quality degrades with many decisions
- Defaults become more likely late in sequences

**Design Countermeasures**:
- Smart defaults
- Save progress frequently
- Most important decisions early in flow
- Reduce trivial choices

---

## Learning & Skill Acquisition

### Power Law of Practice

**Formula**: T = a × N^(-b)
- Performance improves as power function of practice
- Rapid early gains, diminishing returns

**Implications**:
- First-time user experience is critical
- Expert shortcuts can be hidden initially
- Progressive disclosure of advanced features

### Stages of Skill Acquisition (Fitts & Posner)

**1. Cognitive Stage**
- Conscious attention required
- High error rate
- Needs explicit guidance

**2. Associative Stage**
- Patterns forming
- Errors decreasing
- Still requires some attention

**3. Autonomous Stage**
- Automatic execution
- Low error rate
- Parallel task capability

### Gesture Learning Curves

**Empirical Findings**:
- Trials to plateau: 10-15
- Weeks to automaticity: 3-5
- Maximum gestures for older users: 6 pairs

**Teaching Gestures**:
- Dynamic guides reduce errors: 27% vs 43% without
- Repetition required for muscle memory
- Consistent gesture-action mapping critical

---

## Mental Models

### Model Formation

**Users build internal representations**:
- Based on prior experience
- Influenced by visual affordances
- Resistant to change once formed

**Design Alignment**:
- Match common mental models (folder = container)
- Provide clear conceptual models
- Avoid novel metaphors without education

### Model Violations

**When interface doesn't match expectations**:
- Confusion, errors, frustration
- Users blame themselves initially
- Eventually blame product, abandon

**Detection Questions**:
- Does navigation match expected hierarchy?
- Do button positions match conventions?
- Are destructive actions appropriately weighted?

---

## Flow State

### Conditions for Flow (Csikszentmihalyi)

1. **Clear goals**: Know what to do next
2. **Immediate feedback**: Know how you're doing
3. **Challenge-skill balance**: Not too easy, not too hard

### Channel Model

```
High Challenge ─────────────────────────
        │         ANXIETY    │
        │                    │
        │    ┌───────────┐   │
        │    │   FLOW    │   │
        │    └───────────┘   │
        │                    │
        │         BOREDOM    │
Low Challenge ──────────────────────────
        Low Skill        High Skill
```

### Supporting Flow in Interfaces

**Clear Goals**:
```html
<!-- Good: Clear next action -->
<h2>Step 2 of 4: Add shipping address</h2>

<!-- Bad: Unclear expectations -->
<h2>Information</h2>
```

**Immediate Feedback**:
```javascript
// Good: Instant validation
input.addEventListener('input', validate);

// Bad: Only on submit
form.addEventListener('submit', validateAll);
```

**Challenge Balance**:
- Adaptive difficulty
- Progressive complexity
- Skip options for experts

---

## Error Psychology

### Slip vs Mistake

**Slips**: Right intention, wrong action
- Typos
- Wrong button clicked
- Execution errors

**Mistakes**: Wrong intention
- Misunderstanding system
- Wrong mental model
- Planning errors

### Error Prevention Strategies

**For Slips**:
- Confirmation dialogs for destructive actions
- Undo functionality
- Target size appropriate for action risk

**For Mistakes**:
- Clear system feedback
- Educational scaffolding
- Prevent impossible states

### Error Rate by Hierarchy Depth

| Depth | Error Rate | Implication |
|-------|------------|-------------|
| 1 level | 4% | Minimal nesting |
| 3 levels | 20% | Acceptable |
| 6 levels | 34% | Redesign needed |

---

## Memory Systems

### Types Relevant to Interface Design

**Procedural Memory**:
- "How to" knowledge
- Keyboard shortcuts
- Gesture patterns
- Resistant to decay

**Episodic Memory**:
- Personal experiences
- "Where did I see that?"
- Context-dependent recall

**Semantic Memory**:
- Facts and concepts
- Icon meanings
- Interface conventions

### Recognition vs Recall

**Recognition is easier**:
- Seeing options: Recognition
- Remembering commands: Recall
- GUI menus leverage recognition
- CLI requires recall

**Design Preference**:
```
// Prefer recognition (dropdown)
<select>
  <option>Option 1</option>
  <option>Option 2</option>
</select>

// Over recall (text input)
<input placeholder="Enter command...">
```

---

## The Debunked: Learning Styles

### THOROUGHLY DEBUNKED

**No Evidence for Matching**:
- Pashler et al. (2009): "Lack of credible evidence for utility is striking and disturbing"
- Hattie meta-analysis: Effect size essentially ZERO
- Yet 93-97% of teachers still believe

**What DOES Matter**:
- Multiple modalities benefit ALL learners (Mayer, 2003)
- Prior knowledge
- Working memory capacity
- Metacognition
- Motivation

**Design Guidance**:
- DON'T ask users for "learning style"
- DO provide multiple formats (text, video, interactive)
- DO allow user control over presentation

---

## Quick Detection Signals

### Working Memory Honored
- Groups of ≤5 items
- Progressive disclosure
- Information visible in context
- No cross-screen memorization required

### Attention Honored
- Auto-save indicators
- Interruption recovery support
- Front-loaded critical info
- Minimal notifications

### Cognitive Load Minimized
- Inline validation/errors
- Related info co-located
- No redundant information
- Appropriate modality use

### Decision Support
- Smart defaults
- Filtered/sorted large lists
- Progressive disclosure
- Important decisions early

### Flow Supported
- Clear next steps
- Immediate feedback
- Appropriate challenge level
- Uninterrupted task completion

### Mental Models Respected
- Conventional patterns
- Familiar metaphors
- Predictable behavior
- Consistent affordances

---

## Code Patterns to Detect

### Good Patterns
```javascript
// Working memory: Chunked display
const groups = chunkArray(items, 4);

// Attention: Auto-save
useEffect(() => {
  const timer = setTimeout(() => saveDraft(), 1000);
  return () => clearTimeout(timer);
}, [content]);

// Cognitive load: Inline validation
<input onChange={validateField} />
<span className="error">{error}</span>

// Flow: Clear progress
<ProgressBar current={2} total={4} />
```

### Warning Patterns
```javascript
// Too many choices without filtering
{items.map(item => <Option key={item.id} {...item} />)}

// Information spread across screens
navigate('/step2'); // User must remember step1 data

// Delayed feedback
onSubmit: () => setTimeout(validate, 5000)

// Deep nesting
<Menu>
  <SubMenu>
    <SubSubMenu>
      <SubSubSubMenu>
        {/* Error rate: ~34% */}
      </SubSubSubMenu>
    </SubSubMenu>
  </SubMenu>
</Menu>
```
