# Design Tokens

> Cross-platform design system implementation

## What Are Design Tokens?

Design tokens are named entities that store visual design attributes. They provide a single source of truth for design decisions that can be transformed into any platform format.

```
Raw Value → Token → Platform Output
#007AFF → color.primary → CSS, iOS, Android, etc.
```

---

## Token Hierarchy

### Three-Tier System

```
┌─────────────────────────────────────────┐
│  COMPONENT TOKENS (Specific)            │
│  button.primary.background              │
│  card.border.radius                     │
└───────────────┬─────────────────────────┘
                │ references
┌───────────────▼─────────────────────────┐
│  SEMANTIC TOKENS (Meaningful)           │
│  color.interactive.primary              │
│  radius.medium                          │
└───────────────┬─────────────────────────┘
                │ references
┌───────────────▼─────────────────────────┐
│  PRIMITIVE TOKENS (Raw Values)          │
│  color.blue.500: #007AFF                │
│  radius.4: 4px                          │
└─────────────────────────────────────────┘
```

---

## Token Structure (JSON)

### Primitive Tokens

```json
{
  "color": {
    "blue": {
      "50": { "value": "#EFF6FF" },
      "100": { "value": "#DBEAFE" },
      "200": { "value": "#BFDBFE" },
      "300": { "value": "#93C5FD" },
      "400": { "value": "#60A5FA" },
      "500": { "value": "#3B82F6" },
      "600": { "value": "#2563EB" },
      "700": { "value": "#1D4ED8" },
      "800": { "value": "#1E40AF" },
      "900": { "value": "#1E3A8A" }
    },
    "gray": {
      "50": { "value": "#F9FAFB" },
      "100": { "value": "#F3F4F6" },
      "200": { "value": "#E5E7EB" },
      "300": { "value": "#D1D5DB" },
      "400": { "value": "#9CA3AF" },
      "500": { "value": "#6B7280" },
      "600": { "value": "#4B5563" },
      "700": { "value": "#374151" },
      "800": { "value": "#1F2937" },
      "900": { "value": "#111827" }
    }
  },
  "spacing": {
    "0": { "value": "0" },
    "1": { "value": "4px" },
    "2": { "value": "8px" },
    "3": { "value": "12px" },
    "4": { "value": "16px" },
    "5": { "value": "20px" },
    "6": { "value": "24px" },
    "8": { "value": "32px" },
    "10": { "value": "40px" },
    "12": { "value": "48px" },
    "16": { "value": "64px" }
  },
  "radius": {
    "none": { "value": "0" },
    "sm": { "value": "4px" },
    "md": { "value": "8px" },
    "lg": { "value": "12px" },
    "xl": { "value": "16px" },
    "2xl": { "value": "24px" },
    "full": { "value": "9999px" }
  },
  "fontSize": {
    "xs": { "value": "12px" },
    "sm": { "value": "14px" },
    "base": { "value": "16px" },
    "lg": { "value": "18px" },
    "xl": { "value": "20px" },
    "2xl": { "value": "24px" },
    "3xl": { "value": "30px" },
    "4xl": { "value": "36px" }
  },
  "fontWeight": {
    "normal": { "value": "400" },
    "medium": { "value": "500" },
    "semibold": { "value": "600" },
    "bold": { "value": "700" }
  },
  "lineHeight": {
    "tight": { "value": "1.25" },
    "normal": { "value": "1.5" },
    "relaxed": { "value": "1.75" }
  }
}
```

### Semantic Tokens

```json
{
  "color": {
    "text": {
      "primary": { "value": "{color.gray.900}" },
      "secondary": { "value": "{color.gray.600}" },
      "disabled": { "value": "{color.gray.400}" },
      "inverse": { "value": "#FFFFFF" }
    },
    "background": {
      "primary": { "value": "#FFFFFF" },
      "secondary": { "value": "{color.gray.50}" },
      "tertiary": { "value": "{color.gray.100}" }
    },
    "border": {
      "default": { "value": "{color.gray.200}" },
      "strong": { "value": "{color.gray.300}" }
    },
    "interactive": {
      "primary": { "value": "{color.blue.600}" },
      "primaryHover": { "value": "{color.blue.700}" },
      "primaryActive": { "value": "{color.blue.800}" }
    },
    "status": {
      "success": { "value": "#10B981" },
      "warning": { "value": "#F59E0B" },
      "error": { "value": "#EF4444" },
      "info": { "value": "{color.blue.500}" }
    }
  },
  "spacing": {
    "page": {
      "x": { "value": "{spacing.4}" },
      "y": { "value": "{spacing.6}" }
    },
    "card": {
      "padding": { "value": "{spacing.4}" },
      "gap": { "value": "{spacing.3}" }
    },
    "stack": {
      "sm": { "value": "{spacing.2}" },
      "md": { "value": "{spacing.4}" },
      "lg": { "value": "{spacing.6}" }
    }
  }
}
```

### Component Tokens

```json
{
  "button": {
    "primary": {
      "background": { "value": "{color.interactive.primary}" },
      "backgroundHover": { "value": "{color.interactive.primaryHover}" },
      "backgroundActive": { "value": "{color.interactive.primaryActive}" },
      "text": { "value": "{color.text.inverse}" },
      "borderRadius": { "value": "{radius.lg}" },
      "paddingX": { "value": "{spacing.4}" },
      "paddingY": { "value": "{spacing.3}" },
      "fontSize": { "value": "{fontSize.base}" },
      "fontWeight": { "value": "{fontWeight.semibold}" },
      "minHeight": { "value": "48px" }
    },
    "secondary": {
      "background": { "value": "transparent" },
      "border": { "value": "{color.border.default}" },
      "text": { "value": "{color.interactive.primary}" }
    }
  },
  "input": {
    "background": { "value": "{color.background.primary}" },
    "border": { "value": "{color.border.default}" },
    "borderFocus": { "value": "{color.interactive.primary}" },
    "borderError": { "value": "{color.status.error}" },
    "borderRadius": { "value": "{radius.md}" },
    "padding": { "value": "{spacing.3}" },
    "fontSize": { "value": "{fontSize.base}" },
    "minHeight": { "value": "48px" }
  },
  "card": {
    "background": { "value": "{color.background.primary}" },
    "border": { "value": "{color.border.default}" },
    "borderRadius": { "value": "{radius.xl}" },
    "padding": { "value": "{spacing.4}" },
    "shadow": { "value": "0 1px 3px rgba(0,0,0,0.1)" }
  }
}
```

---

## Dark Mode Tokens

```json
{
  "color": {
    "text": {
      "primary": {
        "value": "{color.gray.900}",
        "$extensions": {
          "dark": { "value": "#FFFFFF" }
        }
      },
      "secondary": {
        "value": "{color.gray.600}",
        "$extensions": {
          "dark": { "value": "{color.gray.400}" }
        }
      }
    },
    "background": {
      "primary": {
        "value": "#FFFFFF",
        "$extensions": {
          "dark": { "value": "{color.gray.900}" }
        }
      },
      "secondary": {
        "value": "{color.gray.50}",
        "$extensions": {
          "dark": { "value": "{color.gray.800}" }
        }
      }
    }
  }
}
```

---

## Style Dictionary Configuration

### config.json

```json
{
  "source": ["tokens/**/*.json"],
  "platforms": {
    "css": {
      "transformGroup": "css",
      "buildPath": "build/css/",
      "files": [{
        "destination": "tokens.css",
        "format": "css/variables"
      }]
    },
    "scss": {
      "transformGroup": "scss",
      "buildPath": "build/scss/",
      "files": [{
        "destination": "_tokens.scss",
        "format": "scss/variables"
      }]
    },
    "ios": {
      "transformGroup": "ios",
      "buildPath": "build/ios/",
      "files": [{
        "destination": "Tokens.swift",
        "format": "ios/swift/class"
      }]
    },
    "android": {
      "transformGroup": "android",
      "buildPath": "build/android/",
      "files": [{
        "destination": "tokens.xml",
        "format": "android/resources"
      }]
    },
    "js": {
      "transformGroup": "js",
      "buildPath": "build/js/",
      "files": [{
        "destination": "tokens.js",
        "format": "javascript/es6"
      }]
    }
  }
}
```

### Output Examples

**CSS Variables:**
```css
:root {
  --color-text-primary: #111827;
  --color-text-secondary: #4B5563;
  --color-background-primary: #FFFFFF;
  --color-interactive-primary: #2563EB;
  --spacing-4: 16px;
  --radius-lg: 12px;
  --button-primary-min-height: 48px;
}

[data-theme="dark"] {
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #9CA3AF;
  --color-background-primary: #111827;
}
```

**iOS Swift:**
```swift
public enum Tokens {
    public enum Color {
        public static let textPrimary = UIColor(hex: "#111827")
        public static let textSecondary = UIColor(hex: "#4B5563")
        public static let interactivePrimary = UIColor(hex: "#2563EB")
    }
    
    public enum Spacing {
        public static let s4: CGFloat = 16
        public static let s6: CGFloat = 24
    }
    
    public enum Radius {
        public static let lg: CGFloat = 12
    }
}
```

**Android XML:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="color_text_primary">#111827</color>
    <color name="color_text_secondary">#4B5563</color>
    <color name="color_interactive_primary">#2563EB</color>
    <dimen name="spacing_4">16dp</dimen>
    <dimen name="radius_lg">12dp</dimen>
</resources>
```

---

## Naming Conventions

### Recommended Pattern

```
[category].[element].[variant].[state].[scale]

Examples:
color.text.primary
color.button.primary.hover
spacing.stack.md
font.size.lg
```

### Naming Rules

1. **Use camelCase or kebab-case** — Be consistent
2. **Avoid abbreviations** — `backgroundColor` not `bgColor`
3. **Group by category** — Color, spacing, typography
4. **Include variants** — Primary, secondary, tertiary
5. **Include states** — Default, hover, active, disabled

---

## Token Tools

| Tool | Purpose | Platform |
|------|---------|----------|
| **Style Dictionary** | Token transformation | Multi-platform |
| **Tokens Studio** | Figma plugin | Design |
| **Token Transformer** | GitHub Action | CI/CD |
| **Theme UI** | React theming | Web |
| **Stitches** | CSS-in-JS | Web |

---

## Key Takeaways

1. **Three-tier hierarchy** — Primitive → Semantic → Component
2. **Single source of truth** — One JSON/YAML file for all platforms
3. **Reference tokens** — Never use raw values in semantic/component layers
4. **Theme support** — Build dark mode into token structure
5. **Automate builds** — Use Style Dictionary or similar
6. **Sync with design** — Keep tokens aligned with Figma
7. **Document tokens** — Generate documentation from token files
