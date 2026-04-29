# Mobile Form Design

> Optimization patterns for high-conversion mobile forms

## Form Statistics That Matter

| Metric | Value | Implication |
|--------|-------|-------------|
| Mobile form abandonment | 81% | Massive opportunity to improve |
| Ideal field count | 3-5 fields | More fields = more abandonment |
| Required account creation impact | -23% completion | Offer guest checkout |
| Single-column vs multi-column | 15.4s faster | Always use single column |
| Expedia "Company" field removal | +$12M/year | Every field has cost |

---

## Core Form Principles

### 1. Single Column Layout Only

Multi-column forms cause confusion and slower completion on mobile.

```css
/* Single column form layout */
.mobile-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 100%;
  padding: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Never use multi-column on mobile */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
  }
  
  .form-row .form-field {
    width: 100%;
  }
}
```

### 2. Minimum 16px Font Size

**Critical:** Font sizes below 16px trigger iOS zoom on input focus.

```css
/* Prevent iOS zoom */
input, select, textarea {
  font-size: 16px;
  font-size: max(16px, 1rem);
}

/* Touch-friendly input sizing */
input, select, textarea {
  min-height: 48px;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
}
```

### 3. Top-Aligned or Floating Labels

```html
<!-- Top-aligned label (clearest) -->
<div class="form-field">
  <label for="email">Email address</label>
  <input type="email" id="email" autocomplete="email">
</div>

<!-- Floating label (space-efficient) -->
<div class="form-field floating">
  <input type="email" id="email" placeholder=" " autocomplete="email">
  <label for="email">Email address</label>
</div>
```

```css
/* Floating label implementation */
.form-field.floating {
  position: relative;
}

.form-field.floating input {
  padding-top: 24px;
  padding-bottom: 8px;
}

.form-field.floating label {
  position: absolute;
  top: 50%;
  left: 16px;
  transform: translateY(-50%);
  transition: all 0.2s;
  pointer-events: none;
  color: var(--text-secondary);
}

.form-field.floating input:focus + label,
.form-field.floating input:not(:placeholder-shown) + label {
  top: 8px;
  transform: translateY(0);
  font-size: 12px;
  color: var(--primary);
}
```

---

## HTML5 Input Types

Using correct input types shows appropriate mobile keyboards.

### Keyboard Types by Input

| Input Type | Keyboard | Use For |
|------------|----------|---------|
| `type="text"` | Standard QWERTY | Names, general text |
| `type="email"` | @ and . visible | Email addresses |
| `type="tel"` | Phone pad | Phone numbers |
| `type="number"` | Numeric | Quantities (has +/-) |
| `inputmode="numeric"` | Numeric only | Credit cards, PINs |
| `type="url"` | / and .com visible | Website URLs |
| `type="search"` | Search button | Search fields |
| `type="password"` | Standard + secure | Passwords |

### Complete Input Examples

```html
<!-- Name -->
<input 
  type="text" 
  autocomplete="name" 
  autocapitalize="words"
  spellcheck="false"
  placeholder="John Doe">

<!-- Email -->
<input 
  type="email" 
  autocomplete="email" 
  autocapitalize="none"
  autocorrect="off"
  spellcheck="false"
  placeholder="john@example.com">

<!-- Phone -->
<input 
  type="tel" 
  autocomplete="tel" 
  placeholder="+1 (555) 000-0000">

<!-- Credit Card Number -->
<input 
  type="text" 
  inputmode="numeric" 
  autocomplete="cc-number"
  pattern="[0-9\s]{13,19}"
  maxlength="19"
  placeholder="1234 5678 9012 3456">

<!-- Credit Card Expiry -->
<input 
  type="text" 
  inputmode="numeric" 
  autocomplete="cc-exp"
  pattern="[0-9]{2}/[0-9]{2}"
  maxlength="5"
  placeholder="MM/YY">

<!-- CVV -->
<input 
  type="text" 
  inputmode="numeric" 
  autocomplete="cc-csc"
  pattern="[0-9]{3,4}"
  maxlength="4"
  placeholder="123">

<!-- One-Time Code (OTP) -->
<input 
  type="text" 
  inputmode="numeric" 
  autocomplete="one-time-code"
  pattern="[0-9]{6}"
  maxlength="6"
  placeholder="000000">

<!-- New Password -->
<input 
  type="password" 
  autocomplete="new-password"
  minlength="8">

<!-- Street Address -->
<input 
  type="text" 
  autocomplete="street-address"
  placeholder="123 Main St">

<!-- Postal Code -->
<input 
  type="text" 
  inputmode="text" 
  autocomplete="postal-code"
  placeholder="12345">
```

---

## Autocomplete Attributes

Enable browser/password manager autofill with proper autocomplete values.

### Personal Information

| Field | Autocomplete Value |
|-------|-------------------|
| Full name | `name` |
| Given name | `given-name` |
| Family name | `family-name` |
| Email | `email` |
| Phone | `tel` |
| Birthday | `bday` |
| Gender | `sex` |
| URL | `url` |
| Photo | `photo` |

### Address Fields

| Field | Autocomplete Value |
|-------|-------------------|
| Street address | `street-address` |
| Address line 1 | `address-line1` |
| Address line 2 | `address-line2` |
| City | `address-level2` |
| State/Province | `address-level1` |
| ZIP/Postal code | `postal-code` |
| Country | `country-name` |
| Country code | `country` |

### Payment Fields

| Field | Autocomplete Value |
|-------|-------------------|
| Card holder name | `cc-name` |
| Card number | `cc-number` |
| Expiry date | `cc-exp` |
| Expiry month | `cc-exp-month` |
| Expiry year | `cc-exp-year` |
| CVV/CVC | `cc-csc` |
| Card type | `cc-type` |

### Authentication

| Field | Autocomplete Value |
|-------|-------------------|
| Username | `username` |
| Current password | `current-password` |
| New password | `new-password` |
| One-time code | `one-time-code` |

### Shipping vs Billing

```html
<!-- Shipping address -->
<input autocomplete="shipping street-address">
<input autocomplete="shipping address-level2">
<input autocomplete="shipping postal-code">

<!-- Billing address -->
<input autocomplete="billing street-address">
<input autocomplete="billing address-level2">
<input autocomplete="billing postal-code">
```

---

## Form Validation

### Inline Validation Pattern

Validate as user types (with debouncing) rather than on submit.

```javascript
class FormValidator {
  constructor(form) {
    this.form = form;
    this.debounceTimers = {};
    this.setupValidation();
  }
  
  setupValidation() {
    this.form.querySelectorAll('input, select, textarea').forEach(field => {
      // Validate on blur
      field.addEventListener('blur', () => this.validateField(field));
      
      // Validate on input (debounced)
      field.addEventListener('input', () => {
        clearTimeout(this.debounceTimers[field.name]);
        this.debounceTimers[field.name] = setTimeout(() => {
          this.validateField(field);
        }, 500);
      });
    });
  }
  
  validateField(field) {
    const value = field.value.trim();
    const wrapper = field.closest('.form-field');
    let error = null;
    
    // Required check
    if (field.required && !value) {
      error = 'This field is required';
    }
    
    // Type-specific validation
    else if (value) {
      switch (field.type) {
        case 'email':
          if (!this.isValidEmail(value)) {
            error = 'Please enter a valid email';
          }
          break;
        case 'tel':
          if (!this.isValidPhone(value)) {
            error = 'Please enter a valid phone number';
          }
          break;
      }
      
      // Pattern validation
      if (field.pattern && !new RegExp(field.pattern).test(value)) {
        error = field.dataset.patternError || 'Invalid format';
      }
      
      // Custom validators
      const customValidator = this.customValidators[field.name];
      if (customValidator) {
        error = customValidator(value);
      }
    }
    
    // Update UI
    this.showFieldState(wrapper, field, error);
    return !error;
  }
  
  showFieldState(wrapper, field, error) {
    const errorEl = wrapper.querySelector('.field-error');
    
    wrapper.classList.remove('valid', 'invalid');
    field.setAttribute('aria-invalid', error ? 'true' : 'false');
    
    if (error) {
      wrapper.classList.add('invalid');
      if (errorEl) {
        errorEl.textContent = error;
        errorEl.hidden = false;
      }
    } else if (field.value.trim()) {
      wrapper.classList.add('valid');
      if (errorEl) errorEl.hidden = true;
    }
  }
  
  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }
  
  isValidPhone(phone) {
    return /^[\d\s\-\+\(\)]{10,}$/.test(phone);
  }
}
```

### Validation Styling

```css
.form-field.invalid input {
  border-color: var(--error);
  background-color: var(--error-bg);
}

.form-field.valid input {
  border-color: var(--success);
}

.field-error {
  color: var(--error);
  font-size: 14px;
  margin-top: 4px;
}

/* Accessibility: Error icon */
.form-field.invalid::after {
  content: '!';
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background: var(--error);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}
```

---

## Input Masks

Format input as user types for better readability.

```javascript
// Phone number formatting
function formatPhone(input) {
  input.addEventListener('input', (e) => {
    let value = e.target.value.replace(/\D/g, '');
    
    if (value.length > 0) {
      if (value.length <= 3) {
        value = `(${value}`;
      } else if (value.length <= 6) {
        value = `(${value.slice(0,3)}) ${value.slice(3)}`;
      } else {
        value = `(${value.slice(0,3)}) ${value.slice(3,6)}-${value.slice(6,10)}`;
      }
    }
    
    e.target.value = value;
  });
}

// Credit card formatting
function formatCreditCard(input) {
  input.addEventListener('input', (e) => {
    let value = e.target.value.replace(/\D/g, '');
    value = value.match(/.{1,4}/g)?.join(' ') || value;
    e.target.value = value.slice(0, 19);
  });
}

// Expiry date formatting
function formatExpiry(input) {
  input.addEventListener('input', (e) => {
    let value = e.target.value.replace(/\D/g, '');
    
    if (value.length >= 2) {
      value = value.slice(0, 2) + '/' + value.slice(2, 4);
    }
    
    e.target.value = value;
  });
}
```

---

## Submit Button Best Practices

### Positioning

```css
/* Fixed submit button for long forms */
.form-submit-container {
  position: sticky;
  bottom: 0;
  background: var(--surface);
  padding: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
  border-top: 1px solid var(--border);
  margin: 0 -16px;
}

.submit-button {
  width: 100%;
  min-height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: var(--primary);
  color: white;
  border: none;
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Loading State

```html
<button type="submit" class="submit-button" id="submit">
  <span class="button-text">Continue</span>
  <span class="button-loading" hidden>
    <svg class="spinner">...</svg>
    Processing...
  </span>
</button>
```

```javascript
// Handle form submission with loading state
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const button = form.querySelector('.submit-button');
  const textEl = button.querySelector('.button-text');
  const loadingEl = button.querySelector('.button-loading');
  
  // Disable and show loading
  button.disabled = true;
  textEl.hidden = true;
  loadingEl.hidden = false;
  
  try {
    await submitForm(new FormData(form));
    // Success handling
  } catch (error) {
    // Error handling
    button.disabled = false;
    textEl.hidden = false;
    loadingEl.hidden = true;
  }
});
```

---

## Checkout Optimization

### Guest Checkout

**Critical:** Required account creation causes 26% abandonment.

```html
<div class="checkout-options">
  <button class="checkout-option active" data-option="guest">
    <span class="option-icon">⚡</span>
    <span class="option-label">Guest Checkout</span>
    <span class="option-desc">Quick and easy</span>
  </button>
  <button class="checkout-option" data-option="account">
    <span class="option-icon">👤</span>
    <span class="option-label">Create Account</span>
    <span class="option-desc">Save for next time</span>
  </button>
</div>
```

### Mobile Payment Integration

```html
<!-- Apple Pay / Google Pay buttons -->
<div class="express-checkout">
  <p class="express-label">Express checkout</p>
  <div class="express-buttons">
    <button id="apple-pay" class="express-button">
      <img src="apple-pay-mark.svg" alt="Apple Pay">
    </button>
    <button id="google-pay" class="express-button">
      <img src="google-pay-mark.svg" alt="Google Pay">
    </button>
  </div>
  <div class="divider">
    <span>or pay with card</span>
  </div>
</div>
```

### Progress Indicator

```html
<nav class="checkout-progress" aria-label="Checkout progress">
  <ol>
    <li class="completed" aria-current="false">
      <span class="step-number">1</span>
      <span class="step-label">Cart</span>
    </li>
    <li class="current" aria-current="step">
      <span class="step-number">2</span>
      <span class="step-label">Shipping</span>
    </li>
    <li aria-current="false">
      <span class="step-number">3</span>
      <span class="step-label">Payment</span>
    </li>
  </ol>
</nav>
```

---

## Accessibility Requirements

### Proper Labeling

```html
<!-- Every input needs a label -->
<div class="form-field">
  <label for="email">Email address</label>
  <input type="email" id="email" required aria-describedby="email-hint email-error">
  <p id="email-hint" class="field-hint">We'll send your receipt here</p>
  <p id="email-error" class="field-error" role="alert" hidden></p>
</div>
```

### Error Announcements

```javascript
// Announce errors to screen readers
function announceError(message) {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'alert');
  announcement.setAttribute('aria-live', 'assertive');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  document.body.appendChild(announcement);
  
  setTimeout(() => announcement.remove(), 1000);
}
```

### Focus Management

```javascript
// Focus first error on failed submission
function focusFirstError(form) {
  const firstInvalid = form.querySelector('[aria-invalid="true"]');
  if (firstInvalid) {
    firstInvalid.focus();
    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}
```

---

## Key Takeaways

1. **Single column only** — Never multi-column on mobile
2. **16px minimum** — Prevents iOS zoom
3. **Correct input types** — Shows right keyboard
4. **Autocomplete attributes** — Enables autofill
5. **Inline validation** — Validate as user types
6. **Guest checkout** — Don't require accounts
7. **Fixed submit button** — Always accessible
8. **Express payments** — Apple/Google Pay convert higher
