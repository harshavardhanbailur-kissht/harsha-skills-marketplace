# Code Output Patterns by Framework

## Design Tokens (Framework-Agnostic)

Always generate design tokens first, then adapt to target framework.

### JSON Token Format

```json
{
  "colors": {
    "primary": {
      "50": "#eff6ff",
      "100": "#dbeafe",
      "200": "#bfdbfe",
      "300": "#93c5fd",
      "400": "#60a5fa",
      "500": "#3b82f6",
      "600": "#2563eb",
      "700": "#1d4ed8",
      "800": "#1e40af",
      "900": "#1e3a8a"
    },
    "neutral": {
      "50": "#f9fafb",
      "100": "#f3f4f6",
      "200": "#e5e7eb",
      "300": "#d1d5db",
      "400": "#9ca3af",
      "500": "#6b7280",
      "600": "#4b5563",
      "700": "#374151",
      "800": "#1f2937",
      "900": "#111827"
    },
    "semantic": {
      "success": "#10b981",
      "error": "#ef4444",
      "warning": "#f59e0b",
      "info": "#3b82f6"
    }
  },
  "typography": {
    "fontFamily": {
      "sans": "'Inter', system-ui, -apple-system, sans-serif",
      "serif": "'Georgia', serif",
      "mono": "'Fira Code', monospace"
    },
    "fontSize": {
      "xs": "0.75rem",
      "sm": "0.875rem",
      "base": "1rem",
      "lg": "1.125rem",
      "xl": "1.25rem",
      "2xl": "1.5rem",
      "3xl": "1.875rem",
      "4xl": "2.25rem",
      "5xl": "3rem"
    },
    "fontWeight": {
      "normal": "400",
      "medium": "500",
      "semibold": "600",
      "bold": "700"
    },
    "lineHeight": {
      "tight": "1.25",
      "normal": "1.5",
      "relaxed": "1.625"
    }
  },
  "spacing": {
    "0": "0",
    "1": "0.25rem",
    "2": "0.5rem",
    "3": "0.75rem",
    "4": "1rem",
    "5": "1.25rem",
    "6": "1.5rem",
    "8": "2rem",
    "10": "2.5rem",
    "12": "3rem",
    "16": "4rem",
    "20": "5rem",
    "24": "6rem"
  },
  "borderRadius": {
    "none": "0",
    "sm": "0.25rem",
    "md": "0.5rem",
    "lg": "0.75rem",
    "xl": "1rem",
    "2xl": "1.5rem",
    "full": "9999px"
  },
  "shadow": {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
  },
  "transition": {
    "duration": {
      "fast": "150ms",
      "normal": "300ms",
      "slow": "500ms"
    },
    "easing": {
      "default": "cubic-bezier(0.4, 0, 0.2, 1)",
      "in": "cubic-bezier(0.4, 0, 1, 1)",
      "out": "cubic-bezier(0, 0, 0.2, 1)"
    }
  }
}
```

---

## CSS Custom Properties (Plain CSS)

### Variables File

```css
/* tokens.css */
:root {
  /* Colors - Primary */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-200: #bfdbfe;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1e40af;
  --color-primary-900: #1e3a8a;
  
  /* Colors - Neutral */
  --color-neutral-50: #f9fafb;
  --color-neutral-100: #f3f4f6;
  --color-neutral-200: #e5e7eb;
  --color-neutral-300: #d1d5db;
  --color-neutral-400: #9ca3af;
  --color-neutral-500: #6b7280;
  --color-neutral-600: #4b5563;
  --color-neutral-700: #374151;
  --color-neutral-800: #1f2937;
  --color-neutral-900: #111827;
  
  /* Colors - Semantic */
  --color-success: #10b981;
  --color-success-light: #d1fae5;
  --color-error: #ef4444;
  --color-error-light: #fee2e2;
  --color-warning: #f59e0b;
  --color-warning-light: #fef3c7;
  --color-info: #3b82f6;
  --color-info-light: #dbeafe;
  
  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-serif: 'Georgia', serif;
  --font-mono: 'Fira Code', monospace;
  
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  
  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  
  /* Transitions */
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
}
```

### Component Examples (Plain CSS)

```css
/* components.css */

/* Button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2) var(--space-4);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--leading-normal);
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-primary-200);
}

.btn--primary {
  background: var(--color-primary-500);
  color: white;
}

.btn--primary:hover {
  background: var(--color-primary-600);
}

.btn--primary:active {
  background: var(--color-primary-700);
}

.btn--secondary {
  background: transparent;
  border: 2px solid var(--color-primary-500);
  color: var(--color-primary-500);
}

.btn--secondary:hover {
  background: var(--color-primary-50);
}

/* Input */
.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-neutral-900);
  background: white;
  border: 1px solid var(--color-neutral-300);
  border-radius: var(--radius-md);
  transition: all var(--duration-fast) var(--ease-default);
}

.input:hover {
  border-color: var(--color-neutral-400);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.input--error {
  border-color: var(--color-error);
}

.input--error:focus {
  box-shadow: 0 0 0 3px var(--color-error-light);
}

/* Card */
.card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--space-6);
}

.card--interactive {
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.card--interactive:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}
```

---

## React + Tailwind CSS

### Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

### React Components

```jsx
// components/Button.jsx
import React from 'react';

const variants = {
  primary: 'bg-primary-500 text-white hover:bg-primary-600 active:bg-primary-700 focus:ring-primary-200',
  secondary: 'bg-transparent border-2 border-primary-500 text-primary-500 hover:bg-primary-50 focus:ring-primary-200',
  ghost: 'bg-transparent text-primary-500 hover:bg-primary-50 focus:ring-primary-200',
  destructive: 'bg-red-500 text-white hover:bg-red-600 active:bg-red-700 focus:ring-red-200',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false,
  loading = false,
  className = '',
  ...props 
}) => {
  return (
    <button
      className={`
        inline-flex items-center justify-center
        font-medium rounded-lg
        transition-all duration-150 ease-out
        focus:outline-none focus:ring-2 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : null}
      {children}
    </button>
  );
};
```

```jsx
// components/Input.jsx
import React from 'react';

export const Input = ({
  label,
  error,
  helperText,
  required = false,
  className = '',
  ...props
}) => {
  const inputId = props.id || props.name;
  
  return (
    <div className={className}>
      {label && (
        <label 
          htmlFor={inputId}
          className="block text-sm font-medium text-neutral-700 mb-1"
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        id={inputId}
        className={`
          w-full px-3 py-2
          text-base text-neutral-900
          bg-white border rounded-lg
          transition-all duration-150 ease-out
          focus:outline-none focus:ring-2 focus:ring-offset-0
          ${error 
            ? 'border-red-500 focus:border-red-500 focus:ring-red-200' 
            : 'border-neutral-300 hover:border-neutral-400 focus:border-primary-500 focus:ring-primary-200'
          }
        `}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
        {...props}
      />
      {error && (
        <p id={`${inputId}-error`} className="mt-1 text-sm text-red-500 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
      {helperText && !error && (
        <p id={`${inputId}-helper`} className="mt-1 text-sm text-neutral-500">
          {helperText}
        </p>
      )}
    </div>
  );
};
```

```jsx
// components/Card.jsx
import React from 'react';

export const Card = ({
  children,
  interactive = false,
  className = '',
  onClick,
  ...props
}) => {
  const Component = onClick ? 'button' : 'div';
  
  return (
    <Component
      className={`
        bg-white rounded-xl shadow-md p-6
        ${interactive || onClick ? 'cursor-pointer transition-all duration-150 ease-out hover:shadow-lg hover:-translate-y-0.5' : ''}
        ${className}
      `}
      onClick={onClick}
      {...props}
    >
      {children}
    </Component>
  );
};

export const CardHeader = ({ children, className = '' }) => (
  <div className={`mb-4 ${className}`}>{children}</div>
);

export const CardTitle = ({ children, className = '' }) => (
  <h3 className={`text-xl font-semibold text-neutral-900 ${className}`}>{children}</h3>
);

export const CardDescription = ({ children, className = '' }) => (
  <p className={`text-sm text-neutral-500 mt-1 ${className}`}>{children}</p>
);

export const CardContent = ({ children, className = '' }) => (
  <div className={className}>{children}</div>
);

export const CardFooter = ({ children, className = '' }) => (
  <div className={`mt-4 pt-4 border-t border-neutral-200 flex gap-2 ${className}`}>
    {children}
  </div>
);
```

---

## Vue 3 + Composition API

### Component with CSS Variables

```vue
<!-- components/Button.vue -->
<template>
  <button 
    :class="['btn', `btn--${variant}`, `btn--${size}`]"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <svg 
      v-if="loading" 
      class="btn__spinner" 
      fill="none" 
      viewBox="0 0 24 24"
    >
      <circle 
        class="opacity-25" 
        cx="12" cy="12" r="10" 
        stroke="currentColor" 
        stroke-width="4" 
      />
      <path 
        class="opacity-75" 
        fill="currentColor" 
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" 
      />
    </svg>
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'ghost', 'destructive'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  disabled: Boolean,
  loading: Boolean
});
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-medium, 500);
  border-radius: var(--radius-md, 0.5rem);
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast, 150ms) var(--ease-default);
}

.btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-primary-200);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Variants */
.btn--primary {
  background: var(--color-primary-500);
  color: white;
}
.btn--primary:hover:not(:disabled) { background: var(--color-primary-600); }
.btn--primary:active:not(:disabled) { background: var(--color-primary-700); }

.btn--secondary {
  background: transparent;
  border: 2px solid var(--color-primary-500);
  color: var(--color-primary-500);
}
.btn--secondary:hover:not(:disabled) { background: var(--color-primary-50); }

.btn--ghost {
  background: transparent;
  color: var(--color-primary-500);
}
.btn--ghost:hover:not(:disabled) { background: var(--color-primary-50); }

.btn--destructive {
  background: var(--color-error);
  color: white;
}
.btn--destructive:hover:not(:disabled) { background: #dc2626; }

/* Sizes */
.btn--sm { padding: 0.375rem 0.75rem; font-size: 0.875rem; }
.btn--md { padding: 0.5rem 1rem; font-size: 1rem; }
.btn--lg { padding: 0.75rem 1.5rem; font-size: 1.125rem; }

/* Loading spinner */
.btn__spinner {
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
  width: 1rem;
  height: 1rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
```

---

## Svelte

```svelte
<!-- Button.svelte -->
<script>
  export let variant = 'primary';
  export let size = 'md';
  export let disabled = false;
  export let loading = false;
</script>

<button
  class="btn btn--{variant} btn--{size}"
  {disabled}
  class:btn--loading={loading}
  on:click
  {...$$restProps}
>
  {#if loading}
    <svg class="spinner" fill="none" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
    </svg>
  {/if}
  <slot />
</button>

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    border-radius: 0.5rem;
    border: none;
    cursor: pointer;
    transition: all 150ms ease-out;
  }
  
  .btn:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px #bfdbfe;
  }
  
  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .btn--primary { background: #3b82f6; color: white; }
  .btn--primary:hover:not(:disabled) { background: #2563eb; }
  
  .btn--secondary {
    background: transparent;
    border: 2px solid #3b82f6;
    color: #3b82f6;
  }
  .btn--secondary:hover:not(:disabled) { background: #eff6ff; }
  
  .btn--sm { padding: 0.375rem 0.75rem; font-size: 0.875rem; }
  .btn--md { padding: 0.5rem 1rem; font-size: 1rem; }
  .btn--lg { padding: 0.75rem 1.5rem; font-size: 1.125rem; }
  
  .spinner {
    animation: spin 1s linear infinite;
    margin-right: 0.5rem;
    width: 1rem;
    height: 1rem;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
```
