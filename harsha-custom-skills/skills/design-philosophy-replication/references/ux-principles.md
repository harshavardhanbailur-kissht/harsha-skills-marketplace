# UX Principles & Laws Reference

## Nielsen's 10 Usability Heuristics

These heuristics, developed by Jakob Nielsen and unchanged since 1994, remain the gold standard for interface evaluation.

### 1. Visibility of System Status
Always communicate what's happening through immediate feedback, progress indicators, and "you are here" markers. Users should never wonder "did that work?" or "what's happening now?"

**Implementation:**
- Show loading states for any action >100ms
- Provide progress bars for multi-step processes
- Highlight current location in navigation
- Confirm successful actions with visual feedback
- Show real-time validation in forms

### 2. Match Between System and Real World
Use familiar language, follow real-world conventions, leverage natural mapping between controls and outcomes. Speak the user's language, not technical jargon.

**Implementation:**
- Use terms users already know (not internal company terms)
- Order information logically (dates chronologically, names alphabetically)
- Use familiar icons (trash can for delete, magnifying glass for search)
- Map controls to expected outcomes (slider right = increase)

### 3. User Control and Freedom
Provide clear emergency exits, support undo/redo, show cancel buttons for all operations. Users often choose functions by mistake and need a clear way out.

**Implementation:**
- Always provide "Cancel" alongside "Confirm"
- Support Ctrl+Z / Cmd+Z for undo
- Allow users to go back in multi-step flows
- Provide "Edit" options for submitted content
- Don't trap users in modals without escape routes

### 4. Consistency and Standards
Follow platform conventions. Jakob's Law states: users spend most of their time on OTHER sites, so they expect yours to work the same way.

**Implementation:**
- Use standard icons and their expected meanings
- Place navigation where users expect it
- Follow OS conventions (close button position, scrolling behavior)
- Maintain internal consistency across your product
- Use consistent terminology throughout

### 5. Error Prevention
Better than good error messages is preventing errors through helpful constraints and confirmations. Design to make errors impossible or catch them before submission.

**Implementation:**
- Use appropriate input types (email, tel, number)
- Provide format hints and examples
- Confirm destructive actions ("Delete 3 items?")
- Disable invalid options rather than showing errors after selection
- Auto-save work to prevent data loss

### 6. Recognition Rather Than Recall
Keep options visible, provide help in context, never force users to remember information across screens. Minimize cognitive load by making information visible.

**Implementation:**
- Show recently used items
- Display previous search queries
- Keep form labels visible (not just placeholders)
- Provide autocomplete suggestions
- Show related options in context

### 7. Flexibility and Efficiency of Use
Offer keyboard shortcuts for experts while maintaining accessibility for novices. Accelerators can speed up interaction for experienced users without hindering new users.

**Implementation:**
- Provide keyboard shortcuts for common actions
- Support power-user features (bulk actions, advanced search)
- Allow customization of frequently used features
- Provide multiple ways to accomplish tasks
- Remember user preferences

### 8. Aesthetic and Minimalist Design
Every element competes for attention; prioritize content supporting primary goals. Dialogues should not contain irrelevant or rarely needed information.

**Implementation:**
- Remove decorative elements that don't serve function
- Use progressive disclosure for advanced options
- Prioritize primary actions visually
- Reduce visual noise and clutter
- White space is not wasted space

### 9. Help Users Recognize, Diagnose, and Recover from Errors
Plain language (no error codes), precise indication of the problem, constructive solutions. Error messages should help users fix problems, not just identify them.

**Implementation:**
- Explain what went wrong in plain language
- Show exactly which field has the error
- Suggest how to fix it
- Don't blame the user
- Provide a clear path forward

### 10. Help and Documentation
Searchable, contextual, task-focused, concise. Even though it's better if the system can be used without documentation, it may be necessary to provide help.

**Implementation:**
- Provide contextual help (tooltips, inline hints)
- Make help searchable
- Focus on user tasks, not features
- Keep help content concise
- Provide examples and tutorials

---

## Core UX Laws

### Fitts's Law
**Time to acquire a target = f(distance, size)**

The time required to move to a target depends on the distance to it and its size. Larger targets that are closer are faster to click.

**Practical Applications:**
- Make primary actions **large** (minimum 44×44px touch targets, recommended 48×48px)
- Place primary CTAs **close** to where user's attention already is
- Put related actions near each other
- Place primary CTAs where thumbs naturally rest on mobile (bottom of screen)
- Make destructive actions smaller and further from primary actions
- Use infinite edges (screen edges are infinitely tall targets)

### Hick's Law
**Decision time = log₂(n + 1)**

The time to make a decision increases logarithmically with the number of choices. More options = slower decisions = lower conversions.

**Practical Applications:**
- Limit navigation items (5-7 max for primary nav)
- Break complex choices into progressive steps
- Highlight recommended options
- Use smart defaults to reduce decisions
- Remove unnecessary options
- Group related choices together

### Miller's Law
**Working memory holds 7±2 items**

The average person can hold about 7 (±2) items in working memory at once.

**Practical Applications:**
- Use **chunking** to group related information
- Phone numbers: (555) 123-4567 not 5551234567
- Credit cards: 4532 1234 5678 9012
- Limit navigation categories
- Break long forms into sections
- Don't require users to remember across screens

### Jakob's Law
**Users spend most time on OTHER sites**

Users develop expectations based on their cumulative experience with other websites. They prefer sites that work like all the others they already know.

**Practical Applications:**
- Use standard UI patterns (shopping cart icon, hamburger menu)
- Place navigation where expected (top or left)
- Follow e-commerce conventions (product pages, checkout flows)
- Innovate in **expression** (visual style, micro-animations)
- Don't innovate in **structure** (navigation, core workflows)
- When in doubt, follow established patterns

### Law of Proximity
**Elements near each other appear related**

Objects that are close together are perceived as belonging to a group. Proximity overrides similarity in grouping.

**Practical Applications:**
- Group related form fields together
- Separate unrelated content with whitespace
- Place labels close to their inputs
- Keep action buttons near their associated content
- Use consistent spacing to indicate relationships

### Law of Similarity
**Similar elements are perceived as related**

Elements that share visual characteristics (color, shape, size) are perceived as belonging together.

**Practical Applications:**
- Style all primary buttons the same
- Use consistent colors for similar functions
- Differentiate distinct elements visually
- Create visual patterns for related content

### Law of Common Region
**Elements within a boundary are perceived as grouped**

Items within an enclosed area (card, border, background color) are seen as belonging together.

**Practical Applications:**
- Use cards to group related content
- Add backgrounds to section related form fields
- Use borders to define distinct areas
- Create clear visual containers

---

## Cognitive Load Reduction

Cognitive load is the mental effort required to process information. Reducing it makes interfaces easier to use.

### Types of Cognitive Load

**Intrinsic Load**: Complexity inherent to the task itself (can't eliminate, can chunk)
**Extraneous Load**: Complexity added by poor design (eliminate this)
**Germane Load**: Effort spent learning and building schemas (encourage this)

### Reduction Techniques

**Progressive Disclosure**
Show only what's needed at each stage. Reveal complexity gradually as users need it.
- Multi-step forms perform better than single overwhelming forms
- "Show more" links for detailed content
- Advanced options hidden by default
- Contextual help that appears when needed

**Chunking**
Break information into logical groups.
- Limit to ~15 content points per page
- Use clear section headers as cognitive landmarks
- Group related form fields
- Separate distinct processes into steps

**Recognition Over Recall**
Keep options visible rather than requiring memory.
- Display previously entered information
- Use familiar icons and patterns
- Show recent searches and selections
- Provide autocomplete suggestions

**Smart Defaults**
Pre-fill fields with likely values.
- Use shipping address as billing address by default
- Pre-select most common options
- Remember user preferences across sessions
- Suggest based on user history

**Reduce Decisions**
Limit choices where possible.
- Pricing tables: 3 options convert better than 5
- Guide users toward recommended choices
- Use progressive disclosure for advanced options
- Eliminate unnecessary choices

**External Memory Aids**
Don't require users to remember across screens.
- Persist shopping cart contents
- Show order summary throughout checkout
- Keep context visible during multi-step processes
- Provide clear breadcrumbs

---

## Form UX Research Findings

### Structure
- **Single-column layouts outperform multi-column** — Users don't know whether to read across or down
- Group related fields together
- Start with easy fields (name, email) to build commitment (foot-in-the-door technique)
- Progress bars increase completion rates on long forms

### Labels
- **Top-aligned labels work best** — Fastest completion time, works for all field widths
- Always keep labels visible; never replace entirely with placeholders
- Use clear, concise labels (not clever ones)
- Mark required vs optional fields clearly

### Validation
- **Inline validation shows 22% higher success rates** than submit-only validation
- Validate after user leaves field (onBlur), not during typing
- Show specific, actionable error messages
- Include icons with error messages (not color alone for accessibility)
- Don't clear the form on error

### Input Fields
- Minimum **44px height** for touch targets
- Match field width to expected input length (zip code smaller than address)
- Auto-format where helpful (phone numbers, credit cards)
- Show password requirements upfront, not after failure
- Use appropriate input types (email, tel, number) for mobile keyboards

### Buttons
- Primary submit button should be clearly distinguished
- Place submit button close to last form field
- "Cancel" should not look like primary action
- Disable submit during processing (prevent double-submission)
- Show clear success state after submission
