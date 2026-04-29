# Collaborative & Real-Time UX Psychology Research

## Executive Summary

This report synthesizes research on real-time collaboration interfaces, drawing from CSCW literature, industry research from Figma, Google, Microsoft, and academic studies on multiplayer experiences.

---

## 1. Presence Indicators

### Avatar/Cursor Presence Psychology

**Key Findings:**
- Increased avatar realism fosters social presence but may create discomfort in intimate interactions (CHI 2025, N=157)
- Webcam-driven avatars improve meeting satisfaction over audio-driven or static avatars
- More humanlike avatars create greater sense of social, hypothetical, and spatial closeness

### Online Status Indicator Research (CHI 2020, N=200)

| Finding | Percentage |
|---------|------------|
| Correctly identified OSI presence | 90% |
| Answered "not sure" about OSI | 62.5% |
| Incorrectly answered "no" | 35.5% |

**Key Finding:** Users often misunderstand OSIs and carefully curate self-presentation via them.

### Workspace Awareness Framework (Gutwin & Greenberg)

Answers **"who, what, where, when, and how"**:

| Category | Element | Question |
|----------|---------|----------|
| **Who** | Presence | Who is in the workspace? |
| **Who** | Identity | Who is that? |
| **Who** | Authorship | Who did that? |
| **What** | Action | What are they doing? |
| **What** | Intention | What will they do next? |
| **Where** | Location | Where are they working? |
| **Where** | Gaze | Where are they looking? |

**Three Sources:**
1. Consequential communication (body language)
2. Feedthrough (artifact changes)
3. Intentional communication (gestures/speech)

---

## 2. Real-Time Collaboration Patterns

### Simultaneous Editing Psychology

**Meta-analysis (Chen et al. 2018):**
- Knowledge achievement: **g = +0.42**
- Skill acquisition: **g = +0.64**
- Student perceptions: **g = +0.38**

**Cognitive Load:** Online collaboration requires higher cognitive load than face-to-face due to lack of nonverbal cues.

### Conflict Resolution Approaches

| Approach | Mechanism | UX Characteristics |
|----------|-----------|-------------------|
| **OT** | Server-based | Optimistic updates, conflicts resolved on backend |
| **CRDTs** | Mathematically commutative | Eventual consistency guaranteed |

**Visual Patterns:**
- Color-coding conflicting sections
- Side-by-side comparison
- Pop-up notifications
- Cell-level access control
- Parallel workspaces

### Figma's Approach

- Built custom multiplayer system simpler than traditional OT
- Uses CRDTs for eventual consistency
- Introducing multiplayer **reduced overall UX complexity**

---

## 3. Cursor & Selection Sharing

### Multi-Cursor Evolution

1. Blinking text carets (Google Docs)
2. Flying mouse cursors (Mural)
3. Design canvas cursors (Figma)
4. Floating avatars and "video-cursors"

### Color Coding Accessibility (WCAG)

**Critical Rule:** Color alone should not be the only means of conveying information.

| Requirement | Value |
|-------------|-------|
| Text contrast minimum | 4.5:1 |
| Interactive elements contrast | 3:1 |
| People with CVD | >300 million |

**ColorADD System:** Universal code using shapes (square=blue, circle=red, diamond=yellow, triangle=green).

### Annotation and Commenting UX (CHI 2023)

- Practitioners use comments and virtual sticky notes for async collaboration
- Developers can forget to view files on "comment mode"
- **Key Challenge:** Extraneous information can confuse non-UX collaborators
- Practitioners often prefer verbal methods over text-based strategies

---

## 4. Social Presence Theory

### Core Dimensions (Short, Williams & Christie, 1976)

1. **Copresence:** Feelings of isolation/inclusion, mutual awareness
2. **Psychological Involvement:** Mutual attention, empathy, understanding
3. **Behavioral Engagement:** Behavioral interaction, mutual assistance

### Validated Measurement Scales

| Scale | Items | Reliability |
|-------|-------|-------------|
| Gunawardena & Zittle (1997) | 17 items | .52-.87 correlation |
| Kreijns et al. Dutch Scale | 5 items | α=.81 |
| Robot Social Presence (2023) | 17 items, 5 dimensions | Expert validated |

### Awareness vs. Distraction Balance

**Mixed-Presence Collaboration Study:**
- High awareness enhances workspace awareness, UX, coordination
- Leads to more correct decisions
- **Critical Challenge:** Balancing information with cognitive overload

**Knowledge Worker Statistics:**
- Average **~3 minutes** on any single task before switching/interruption
- Returning to interrupted task requires substantial time

### Synchronous vs. Asynchronous Trade-offs

| Mode | Best For | Evidence |
|------|----------|----------|
| **Synchronous** | Convergence, relationship building | Longer, better documents |
| **Asynchronous** | Deep thought, flexibility, writing | 40% meeting reduction = 52% satisfaction increase |

---

## 5. Communication Integration

### @Mention and Notification Psychology

**Research Findings:**
- Notifications alone significantly disrupted attention-demanding tasks
- Error rate **>3x greater** for those receiving notifications
- Notifications prompt mind-wandering
- Fewer interruptions lead to higher end-of-day performance

### Thread vs. Flat Discussion

| Format | Advantages | Challenges |
|--------|------------|------------|
| **Threaded** | Subtopics, hierarchical, clearer context | Long-distance relations difficult |
| **Flat** | Simpler, chronological | Chaotic with high volume |

---

## 6. Permission & Access UX

### Share Dialog Complexity

**Android Permissions Research (Berkeley, N=361):**
- Only **3%** correctly answered all permission questions
- Users misunderstand closely related data permissions
- Users overestimate scope and risk of present permissions

**Permission Request Effectiveness:**
- **12% more likely** to grant when given a reason
- "Priming" before actual request improves acceptance

### Link Sharing Psychology

- Individuals often share unimportant information while keeping important private
- Barriers: Fear of being scooped, fear of data misuse

### Collaborative Ownership Models

- Collective ownership promotes creation of shared mental model
- Essential for moving forward cohesively

---

## 7. Performance & Latency

### Collaboration Lag Perception

| Task Type | Perception Threshold |
|-----------|---------------------|
| General visual | ~13ms response capability |
| Mouse-based | 60ms (simple tasks) |
| Touchpad/stylus | 50ms detection |
| Dragging tasks JND | 33ms |
| Tapping tasks JND | 82ms |
| Multi-user VR | 75ms |

**Guidelines:**
- Acceptable latency: **100-300ms** (varies by task)
- Collaborative target: **<200ms**
- **500+ms delays** make collaboration frustrating

### Optimistic Concurrency UX

- Changes reflected in UI immediately, even before syncing
- Creates perception of speed and reliability
- **Last-Write-Wins:** Common but can lose important updates

### Sync State Indication

- Users perceive sites with **skeleton screens as 30% faster**
- For always-synced content, loading feedback should be minimal
- Users more tolerant when receiving feedback (progress bars)

---

## Essential Design Principles

1. **Answer core questions:** "Who is here?", "Where are they?", "What are they doing?"
2. **Keep collaborative features subtle**
3. **Use multiple identification methods** (not just color)
4. **Target latency <200ms**
5. **Use skeleton screens over spinners** (30% faster perceived)
6. **Provide context for permissions** (12% higher grant rate)
7. **Balance awareness and distraction** (3 min average focus time)
8. **Design for both sync and async**

---

## Key Metrics to Monitor

- Social presence scale scores (5-17 item questionnaires)
- Task completion time with/without collaborative features
- Error rates during collaborative sessions
- Notification-to-action latency
- Perceived latency (JND measurements)
- Cognitive load (standardized instruments)

---

## Sources

- CSCW 2025 Program
- Gutwin & Greenberg (2002) - Workspace Awareness Framework
- Short, Williams & Christie (1976) - Social Presence Theory
- Figma Blog - How Multiplayer Technology Works
- Microsoft Research - Mixed-Presence Collaboration
- CHI 2020 - Online Status Indicators
- W3C - WCAG Color Guidelines
- Chen et al. (2018) - Collaborative Learning Meta-analysis
