# Accessibility & Internationalization Requirements

Complete reference for accessibility (a11y) and internationalization (i18n) PRD requirements.

---

## Accessibility Standards Overview

### WCAG 2.2 (Current Standard)

Published October 2023, updated December 2024.

**Conformance Levels:**
- **Level A**: Minimum accessibility
- **Level AA**: Standard compliance target (most regulations)
- **Level AAA**: Enhanced accessibility

### WCAG 2.2 New Success Criteria

| Criterion | Level | Requirement |
|-----------|-------|-------------|
| 2.4.11 Focus Not Obscured (Minimum) | AA | Focused component at least partially visible |
| 2.4.12 Focus Not Obscured (Enhanced) | AAA | Focused component fully visible |
| 2.4.13 Focus Appearance | AAA | Focus indicator meets size/contrast |
| 2.5.7 Dragging Movements | AA | Provide single-pointer alternative |
| 2.5.8 Target Size (Minimum) | AA | 24×24 CSS pixels minimum |
| 3.2.6 Consistent Help | A | Help mechanism in consistent location |
| 3.3.7 Redundant Entry | A | Don't require re-entry of same info |
| 3.3.8 Accessible Authentication (Minimum) | AA | No cognitive function tests for login |
| 3.3.9 Accessible Authentication (Enhanced) | AAA | No object/content recognition for login |

---

## Color Contrast Requirements

### Text Contrast Ratios

| Text Type | Level AA | Level AAA |
|-----------|----------|-----------|
| Normal text (<18pt or <14pt bold) | 4.5:1 | 7:1 |
| Large text (≥18pt or ≥14pt bold) | 3:1 | 4.5:1 |
| UI components & graphics | 3:1 | 3:1 |

### PRD Specification Format
```markdown
## Color Contrast Requirements
- Body text: Minimum 4.5:1 contrast ratio against background
- Headings (18pt+): Minimum 3:1 contrast ratio
- Interactive elements: Minimum 3:1 contrast ratio
- Focus indicators: Minimum 3:1 contrast against adjacent colors
- Error states: Must not rely on color alone
```

---

## Target Size Requirements

### WCAG 2.5.8 (Level AA)
- Minimum 24×24 CSS pixels
- Exceptions: inline links, user-agent controlled, essential presentation

### WCAG 2.5.5 (Level AAA)
- Minimum 44×44 CSS pixels

### PRD Specification Format
```markdown
## Touch Target Requirements
- Primary actions: Minimum 44×44px touch target
- Secondary actions: Minimum 24×24px touch target
- Spacing between targets: Minimum 8px gap
- Mobile: Follow platform guidelines (iOS: 44pt, Android: 48dp)
```

---

## Keyboard Navigation

### Requirements
```markdown
## Keyboard Accessibility
- All interactive elements focusable via Tab key
- Logical focus order matching visual layout
- Visible focus indicators on all focusable elements
- No keyboard traps (user can always navigate away)
- Skip links for repetitive navigation
- Custom widgets follow ARIA patterns

## Focus Indicator Specifications
- Visible outline: minimum 2px solid
- Contrast: 3:1 against adjacent colors
- Must not be suppressed (no outline:none without alternative)

## Keyboard Shortcuts
- Document all keyboard shortcuts
- Provide method to remap or disable shortcuts
- Single-key shortcuts must be remappable (WCAG 2.1.4)
```

---

## Screen Reader Compatibility

### Requirements
```markdown
## Screen Reader Support
- Test with: NVDA (Windows), VoiceOver (macOS/iOS), TalkBack (Android)
- All images have meaningful alt text or marked decorative
- Form fields have associated labels
- Error messages announced to assistive technology
- Dynamic content updates announced via ARIA live regions
- Tables have proper headers and scope attributes

## ARIA Implementation
- Use native HTML elements when possible
- ARIA roles, states, and properties for custom widgets
- Follow ARIA Authoring Practices patterns
- Test ARIA implementation with actual screen readers
```

---

## Regulatory Requirements

### United States

**Section 508 (Federal)**
- Applies to federal agencies and contractors
- Incorporates WCAG 2.0 Level AA
- Requires Voluntary Product Accessibility Template (VPAT)

**ADA (Americans with Disabilities Act)**
- Applies to places of public accommodation
- Increasingly applied to websites/apps
- No specific technical standard (courts often reference WCAG)

### European Union

**European Accessibility Act (EAA)**
- Effective: June 28, 2025
- Applies to: Computers, ATMs, e-commerce, banking, transportation, e-books
- References: EN 301 549 (which references WCAG 2.1 Level AA)

**Penalties by Country:**
| Country | Maximum Penalty |
|---------|-----------------|
| France | €300,000 |
| Spain | €1,000,000 |
| Hungary | €1,260,000 |
| Some countries | 5% of annual turnover |

### Canada
**Accessible Canada Act**: Federal accessibility requirements

### UK
**Equality Act 2010**: Requires reasonable adjustments for disabled users

---

## Accessibility PRD Section Template

```markdown
## Accessibility Requirements

### Conformance Target
- WCAG 2.2 Level AA compliance required
- Target additional Level AAA criteria: [list specific criteria]

### Applicable Regulations
- [ ] Section 508 (US Federal)
- [ ] ADA (US)
- [ ] European Accessibility Act
- [ ] EN 301 549
- [ ] Other: [specify]

### Testing Requirements
- Automated testing: axe-core, WAVE, Lighthouse
- Manual testing: Keyboard navigation, screen reader testing
- User testing: Include users with disabilities

### Screen Reader Testing Matrix
| Screen Reader | Browser | Platform | Tested |
|---------------|---------|----------|--------|
| NVDA | Firefox | Windows | [ ] |
| NVDA | Chrome | Windows | [ ] |
| VoiceOver | Safari | macOS | [ ] |
| VoiceOver | Safari | iOS | [ ] |
| TalkBack | Chrome | Android | [ ] |

### Specific Requirements
#### Perceivable
- [ ] Text alternatives for non-text content
- [ ] Captions for video content
- [ ] Color contrast meets requirements
- [ ] Text resizable to 200% without loss

#### Operable
- [ ] All functionality keyboard accessible
- [ ] No keyboard traps
- [ ] Skip navigation links
- [ ] Focus indicators visible
- [ ] Target sizes meet minimum

#### Understandable
- [ ] Language of page identified
- [ ] Consistent navigation
- [ ] Error identification and suggestions
- [ ] Labels and instructions for input

#### Robust
- [ ] Valid HTML
- [ ] Name, role, value for custom components
- [ ] Status messages programmatically determined

### Documentation Requirements
- Accessibility statement/conformance report
- VPAT (if applicable)
- Known issues and remediation timeline
```

---

## Internationalization (i18n) Requirements

### Language Support

```markdown
## Supported Languages
| Language | Code | Direction | Script |
|----------|------|-----------|--------|
| English | en | LTR | Latin |
| Spanish | es | LTR | Latin |
| Arabic | ar | RTL | Arabic |
| Chinese (Simplified) | zh-CN | LTR | Han |
| Japanese | ja | LTR | Mixed |
| Hebrew | he | RTL | Hebrew |

## Language Detection
- Primary: User account preference
- Fallback: Browser Accept-Language header
- Override: Language selector in UI
```

### RTL (Right-to-Left) Support

**12 RTL Scripts covering ~215 languages:**
- Arabic, Hebrew, Persian, Urdu, etc.

```markdown
## RTL Requirements
### Must Mirror
- Navigation placement
- Form layouts
- Progress indicators
- List markers
- Breadcrumbs

### Must NOT Mirror
- Video playback controls
- Real-world directional content
- Numbers (Arabic numerals read LTR)
- Graphs and charts (typically)
- Phone numbers
- Credit card numbers

### Technical Implementation
- Use CSS logical properties (margin-inline-start vs margin-left)
- dir="rtl" attribute on html element
- Bidirectional text handling for mixed content
- Test with actual RTL content (not mirrored LTR)
```

### Date, Time, and Number Formatting

```markdown
## Localization Requirements

### Date Formats
| Locale | Format | Example |
|--------|--------|---------|
| en-US | MM/DD/YYYY | 12/25/2024 |
| en-GB | DD/MM/YYYY | 25/12/2024 |
| de-DE | DD.MM.YYYY | 25.12.2024 |
| ja-JP | YYYY年MM月DD日 | 2024年12月25日 |

### Time Formats
- 12-hour vs 24-hour based on locale
- Timezone handling: Store UTC, display local
- Relative time: "2 hours ago" localized

### Number Formats
| Locale | Thousands | Decimal | Currency |
|--------|-----------|---------|----------|
| en-US | , | . | $1,234.56 |
| de-DE | . | , | 1.234,56 € |
| fr-FR | (space) | , | 1 234,56 € |

### Currency
- Use ISO 4217 codes (USD, EUR, GBP)
- Display currency symbol per locale
- Handle currency-specific decimal places
```

### Character Encoding

```markdown
## Character Encoding
- UTF-8 encoding required throughout
- Database: UTF-8 or UTF-8MB4 (for full emoji support)
- API responses: UTF-8 with Content-Type header
- Form submissions: Accept-Charset: UTF-8
```

### Text Expansion

```markdown
## Text Expansion Allowances
| English Length | Typical Expansion |
|----------------|-------------------|
| 1-10 chars | 200-300% |
| 11-20 chars | 180-200% |
| 21-30 chars | 160-180% |
| 31-50 chars | 140-160% |
| 51-70 chars | 130-140% |
| 70+ chars | 130% |

## UI Design Requirements
- Avoid fixed-width containers for text
- Allow text wrapping
- Test with longest translations (German, Finnish often expand most)
- Consider vertical expansion for some Asian languages
```

### Translation Workflow

```markdown
## Translation Requirements
### String Externalization
- All user-facing strings in resource files
- No hardcoded strings in code
- Placeholder syntax: {variable} or %s

### Context for Translators
- Provide context comments for ambiguous strings
- Include screenshots where helpful
- Indicate character limits

### Translation Management
- Tool: [Crowdin | Lokalise | Phrase | Transifex]
- Review workflow: Machine → Human → QA
- Pseudolocalization testing

### Quality Assurance
- [ ] All strings translated
- [ ] Placeholders preserved
- [ ] Character limits respected
- [ ] Context-appropriate translations
- [ ] Tested in actual UI
```

---

## i18n PRD Section Template

```markdown
## Internationalization Requirements

### Supported Locales (Initial)
- [List locales with ISO codes]

### Future Locales (Planned)
- [List planned locales with timeline]

### Locale-Specific Features
| Feature | Locale-Specific Behavior |
|---------|--------------------------|
| Date format | Per-locale formatting |
| Currency | Per-locale display |
| Sort order | Locale-aware collation |

### RTL Support
- [ ] Required for initial launch
- [ ] Planned for future release
- [ ] Not applicable

### Content Localization
- UI strings: [Translation approach]
- Help content: [Translation approach]
- Marketing content: [Translation approach]
- Legal content: [Translation approach]

### Technical Requirements
- All dates stored in UTC
- All strings externalized
- Locale passed in API requests
- Database supports Unicode

### Testing Requirements
- Pseudolocalization testing
- Native speaker review
- Locale-specific functional testing
```
