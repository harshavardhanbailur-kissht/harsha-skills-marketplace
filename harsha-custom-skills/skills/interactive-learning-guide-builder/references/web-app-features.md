# Web App Features Specification

## Architecture: Single-File React App

The learning guide is delivered as a single HTML file with embedded React, Tailwind CSS, and all course data. No backend required. All state is managed in-memory via React useState/useReducer.

## Feature Specification

### 1. Sidebar Navigation
- **Module tree**: Collapsible modules with lessons listed underneath
- **Completion indicators**: Checkmark icon for completed lessons, circle for pending
- **Current lesson highlight**: Active lesson visually distinct (blue/accent background)
- **Progress count**: "3/8 lessons completed" per module
- **Click to jump**: Any lesson accessible at any time (no locking)
- **Responsive**: Collapses to hamburger menu on mobile

### 2. Progress Tracking
- **Global progress bar**: Top of page, shows overall % complete
- **Module progress**: Per-module completion percentage
- **Lesson status**: Not started / In progress / Completed
- **MCQ score tracking**: Track correct/wrong per lesson (in-memory)
- **Completion criteria**: Lesson is "complete" when all MCQs attempted (not necessarily all correct)

### 3. Lesson View
- **Title**: Lesson title with module breadcrumb
- **Content area**: Rendered markdown with:
  - Headers (h2, h3)
  - Bold/italic for emphasis
  - Code blocks for technical content
  - Ordered/unordered lists
- **Key Terms**: Highlighted with tooltip definitions on hover
- **Tips boxes**: Styled callout boxes (yellow/amber background, lightbulb icon)
  - "💡 Pro Tip: [practical advice]"
  - "⚠️ Common Mistake: [what to avoid]"
  - "📌 Remember: [key takeaway]"
- **Section dividers**: Clean visual separation between content sections

### 4. MCQ Interaction
- **Question display**: Clear question text with numbered options
- **Selection**: Click an option to select it (radio button style)
- **Submit button**: "Check Answer" button to confirm selection
- **Correct feedback**: Green highlight + "✓ Correct!" + explanation
- **Wrong feedback**: Red highlight on selected + Green highlight on correct + "✗ Incorrect" + wrong explanation + correct explanation
- **Next question**: Button to proceed to next MCQ
- **Score display**: "You got 4/5 correct" at end of lesson MCQs
- **Retry option**: "Try again" button to re-attempt wrong questions

### 5. Hints System
- **"Need a hint?" button**: Appears below each MCQ
- **Progressive reveal**: 
  - Click 1: Shows Hint 1 (subtle nudge)
  - Click 2: Shows Hint 2 (bigger clue)
  - Click 3: Shows Hint 3 (near-answer)
- **Styling**: Indented, lighter text, hint icon
- **No penalty**: Using hints doesn't affect completion

### 6. Show Answer
- **"Show Answer" button**: Below hints
- **Full reveal**: Shows correct answer + comprehensive explanation
- **Marked**: Lesson tracks that answer was shown (displayed in retest mode)
- **Styling**: Distinct from hint styling (blue info box)

### 7. Notes Sandbox
- **Textarea per lesson**: "Your Notes" expandable section at bottom
- **Auto-save**: Notes saved to in-memory state (persist during session)
- **Placeholder text**: "Write your notes, questions, or key takeaways here..."
- **Expand/collapse**: Starts collapsed, toggle to expand

### 8. Checkpoint Assessments
- **Placement**: After every 3 lessons + end of each module
- **Mixed questions**: 60% current module + 40% prior modules
- **Cross-module MCQs**: Compound questions spanning multiple topics
- **Score summary**: Shows performance breakdown by module
- **Weaknesses identified**: "You might want to revisit Module 2, Lesson 3"

### 9. Retest Mode
- **"Retake Quiz" button**: Available on any completed module
- **Shuffled questions**: Different order from first attempt
- **Shuffled options**: Correct answer at different position
- **Comparison**: Shows "Previous: 3/5 → Current: 5/5"
- **Focus on mistakes**: Previously-wrong questions marked with indicator

### 10. Keyboard Shortcuts
- **←/→**: Previous/Next lesson
- **1/2/3/4**: Select MCQ option
- **Enter**: Submit answer / Next question
- **H**: Toggle hint
- **S**: Show answer
- **N**: Toggle notes panel
- **Esc**: Close any open panel

### 11. Search (Nice to Have)
- **Cmd+K / Ctrl+K**: Open search overlay
- **Search across**: Lesson titles, content, glossary terms
- **Jump to result**: Click to navigate to matching lesson

## UI Design Tokens

### Color Palette (Dark Mode Default)
```css
--bg-primary: #0f172a;       /* Slate 900 */
--bg-secondary: #1e293b;     /* Slate 800 */
--bg-card: #334155;          /* Slate 700 */
--text-primary: #f8fafc;     /* Slate 50 */
--text-secondary: #94a3b8;   /* Slate 400 */
--accent: #3b82f6;           /* Blue 500 */
--success: #22c55e;          /* Green 500 */
--error: #ef4444;            /* Red 500 */
--warning: #f59e0b;          /* Amber 500 */
--info: #06b6d4;             /* Cyan 500 */
--hint: #8b5cf6;             /* Violet 500 */
```

### Light Mode Alternative
```css
--bg-primary: #ffffff;
--bg-secondary: #f8fafc;
--bg-card: #f1f5f9;
--text-primary: #0f172a;
--text-secondary: #64748b;
/* Accent colors same */
```

### Typography
```css
--font-body: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
--text-body: 1rem / 1.7;     /* 16px, generous line height */
--text-h1: 1.875rem / 1.3;   /* 30px */
--text-h2: 1.5rem / 1.35;    /* 24px */
--text-h3: 1.25rem / 1.4;    /* 20px */
--text-small: 0.875rem / 1.5; /* 14px */
```

### Spacing
```css
--content-max-width: 48rem;  /* 768px - comfortable reading width */
--sidebar-width: 16rem;      /* 256px */
--spacing-section: 2rem;     /* Between major sections */
--spacing-element: 1rem;     /* Between elements */
```

## Component Hierarchy

```
App
├── Header (course title, global progress bar, theme toggle)
├── Sidebar
│   ├── ModuleList
│   │   ├── ModuleItem (collapsible)
│   │   │   └── LessonItem (clickable, completion indicator)
│   │   └── CheckpointItem
│   └── CourseProgress (overall stats)
├── MainContent
│   ├── LessonBreadcrumb
│   ├── LessonContent
│   │   ├── ContentSection (rendered markdown)
│   │   ├── KeyTermHighlight (tooltip on hover)
│   │   ├── TipBox (styled callout)
│   │   └── ContentDivider
│   ├── MCQSection
│   │   ├── MCQQuestion
│   │   ├── MCQOptions (selectable)
│   │   ├── MCQFeedback (correct/wrong + explanations)
│   │   ├── HintRevealer (progressive)
│   │   └── ShowAnswer
│   ├── LessonScore (after all MCQs)
│   ├── NotesSandbox (collapsible textarea)
│   └── LessonNavigation (prev/next buttons)
└── Footer (keyboard shortcuts reference)
```

## Data Flow

```
course-content.json → React State (useReducer)
                          ↓
                    Component Tree renders from state
                          ↓
                    User interactions (click MCQ, navigate)
                          ↓
                    Dispatch actions to reducer
                          ↓
                    State updates → Re-render
```

### State Shape
```javascript
{
  currentModuleId: "module-1",
  currentLessonId: "lesson-1-1",
  completedLessons: Set(["lesson-1-1", "lesson-1-2"]),
  mcqAnswers: {
    "lesson-1-1": { "mcq-0": { selected: 2, correct: true, hintsUsed: 0, shownAnswer: false } }
  },
  notes: { "lesson-1-1": "My notes for this lesson..." },
  retestHistory: { "module-1": [{ date: "...", score: 3, total: 5 }] },
  theme: "dark",
  sidebarOpen: true
}
```
