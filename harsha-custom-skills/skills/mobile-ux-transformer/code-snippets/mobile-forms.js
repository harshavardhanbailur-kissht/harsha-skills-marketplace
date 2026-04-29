/**
 * Mobile Forms Utilities
 * Input handling, validation, and keyboard management
 */

// ==========================================================================
// Input Type Configuration
// ==========================================================================

const INPUT_CONFIG = {
  email: {
    type: 'email',
    inputmode: 'email',
    autocomplete: 'email',
    pattern: '[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$'
  },
  phone: {
    type: 'tel',
    inputmode: 'tel',
    autocomplete: 'tel'
  },
  postalCode: {
    type: 'text',
    inputmode: 'numeric',
    autocomplete: 'postal-code',
    pattern: '[0-9]*'
  },
  creditCard: {
    type: 'text',
    inputmode: 'numeric',
    autocomplete: 'cc-number',
    pattern: '[0-9 ]*',
    maxlength: 19
  },
  cvv: {
    type: 'text',
    inputmode: 'numeric',
    autocomplete: 'cc-csc',
    pattern: '[0-9]*',
    maxlength: 4
  },
  expiry: {
    type: 'text',
    inputmode: 'numeric',
    autocomplete: 'cc-exp',
    placeholder: 'MM/YY',
    maxlength: 5
  },
  otp: {
    type: 'text',
    inputmode: 'numeric',
    autocomplete: 'one-time-code',
    pattern: '[0-9]*',
    maxlength: 6
  },
  name: {
    type: 'text',
    autocomplete: 'name'
  },
  address: {
    type: 'text',
    autocomplete: 'street-address'
  },
  city: {
    type: 'text',
    autocomplete: 'address-level2'
  },
  url: {
    type: 'url',
    inputmode: 'url',
    autocomplete: 'url'
  },
  search: {
    type: 'search',
    inputmode: 'search'
  },
  number: {
    type: 'text',
    inputmode: 'numeric',
    pattern: '[0-9]*'
  },
  decimal: {
    type: 'text',
    inputmode: 'decimal',
    pattern: '[0-9.]*'
  },
  password: {
    type: 'password',
    autocomplete: 'current-password'
  },
  newPassword: {
    type: 'password',
    autocomplete: 'new-password'
  }
};

/**
 * Apply optimal input configuration
 */
function configureInput(input, type) {
  const config = INPUT_CONFIG[type];
  if (!config) return;
  
  Object.keys(config).forEach(attr => {
    input.setAttribute(attr, config[attr]);
  });
}

// ==========================================================================
// Input Formatters
// ==========================================================================

const Formatters = {
  /**
   * Format phone number as (XXX) XXX-XXXX
   */
  phone(value) {
    const digits = value.replace(/\D/g, '').slice(0, 10);
    if (digits.length < 4) return digits;
    if (digits.length < 7) return `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
  },
  
  /**
   * Format credit card with spaces
   */
  creditCard(value) {
    const digits = value.replace(/\D/g, '').slice(0, 16);
    return digits.replace(/(\d{4})(?=\d)/g, '$1 ').trim();
  },
  
  /**
   * Format expiry date as MM/YY
   */
  expiry(value) {
    const digits = value.replace(/\D/g, '').slice(0, 4);
    if (digits.length < 3) return digits;
    return `${digits.slice(0, 2)}/${digits.slice(2)}`;
  },
  
  /**
   * Format currency
   */
  currency(value, locale = 'en-US', currency = 'USD') {
    const number = parseFloat(value.replace(/[^\d.]/g, ''));
    if (isNaN(number)) return '';
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency
    }).format(number);
  }
};

/**
 * Create auto-formatter for input
 */
function createFormatter(input, formatter) {
  input.addEventListener('input', (e) => {
    const cursorPos = input.selectionStart;
    const oldLength = input.value.length;
    
    input.value = formatter(input.value);
    
    // Adjust cursor position
    const newLength = input.value.length;
    const newCursorPos = cursorPos + (newLength - oldLength);
    input.setSelectionRange(newCursorPos, newCursorPos);
  });
}

// ==========================================================================
// Validation
// ==========================================================================

const Validators = {
  required(value) {
    return value.trim().length > 0;
  },
  
  email(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  },
  
  phone(value) {
    const digits = value.replace(/\D/g, '');
    return digits.length >= 10;
  },
  
  creditCard(value) {
    const digits = value.replace(/\D/g, '');
    if (digits.length < 13 || digits.length > 19) return false;
    
    // Luhn algorithm
    let sum = 0;
    let isEven = false;
    
    for (let i = digits.length - 1; i >= 0; i--) {
      let digit = parseInt(digits[i], 10);
      
      if (isEven) {
        digit *= 2;
        if (digit > 9) digit -= 9;
      }
      
      sum += digit;
      isEven = !isEven;
    }
    
    return sum % 10 === 0;
  },
  
  expiry(value) {
    const [month, year] = value.split('/').map(v => parseInt(v, 10));
    if (!month || !year) return false;
    if (month < 1 || month > 12) return false;
    
    const now = new Date();
    const currentYear = now.getFullYear() % 100;
    const currentMonth = now.getMonth() + 1;
    
    if (year < currentYear) return false;
    if (year === currentYear && month < currentMonth) return false;
    
    return true;
  },
  
  cvv(value) {
    const digits = value.replace(/\D/g, '');
    return digits.length >= 3 && digits.length <= 4;
  },
  
  minLength(min) {
    return (value) => value.length >= min;
  },
  
  maxLength(max) {
    return (value) => value.length <= max;
  },
  
  pattern(regex) {
    return (value) => regex.test(value);
  }
};

/**
 * Validate field with debouncing
 */
function createValidator(input, validators, options = {}) {
  const { debounce: debounceMs = 300, showError = true } = options;
  let timeout;
  
  const validate = () => {
    const value = input.value;
    const errors = [];
    
    for (const [name, validator] of Object.entries(validators)) {
      const isValid = typeof validator === 'function' 
        ? validator(value) 
        : Validators[validator]?.(value);
      
      if (!isValid) {
        errors.push(name);
      }
    }
    
    if (showError) {
      updateFieldState(input, errors.length === 0, errors);
    }
    
    return errors.length === 0;
  };
  
  input.addEventListener('input', () => {
    clearTimeout(timeout);
    timeout = setTimeout(validate, debounceMs);
  });
  
  input.addEventListener('blur', validate);
  
  return validate;
}

function updateFieldState(input, isValid, errors = []) {
  const wrapper = input.closest('.form-field') || input.parentElement;
  const errorEl = wrapper.querySelector('.field-error') || 
                  document.getElementById(`${input.id}-error`);
  
  input.setAttribute('aria-invalid', !isValid);
  
  if (errorEl) {
    errorEl.textContent = isValid ? '' : getErrorMessage(errors[0]);
    errorEl.hidden = isValid;
  }
  
  wrapper.classList.toggle('has-error', !isValid);
}

function getErrorMessage(errorType) {
  const messages = {
    required: 'This field is required',
    email: 'Please enter a valid email address',
    phone: 'Please enter a valid phone number',
    creditCard: 'Please enter a valid card number',
    expiry: 'Please enter a valid expiry date',
    cvv: 'Please enter a valid CVV',
    minLength: 'Input is too short',
    maxLength: 'Input is too long',
    pattern: 'Invalid format'
  };
  return messages[errorType] || 'Invalid input';
}

// ==========================================================================
// Keyboard Management
// ==========================================================================

/**
 * Handle keyboard appearance on iOS
 */
function setupKeyboardHandler() {
  if (!('visualViewport' in window)) return;
  
  let initialHeight = window.visualViewport.height;
  
  window.visualViewport.addEventListener('resize', () => {
    const currentHeight = window.visualViewport.height;
    const keyboardHeight = initialHeight - currentHeight;
    
    if (keyboardHeight > 100) {
      // Keyboard is visible
      document.body.style.setProperty('--keyboard-height', `${keyboardHeight}px`);
      document.body.classList.add('keyboard-visible');
      
      // Scroll focused element into view
      const focused = document.activeElement;
      if (focused && focused.tagName === 'INPUT') {
        setTimeout(() => {
          focused.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
      }
    } else {
      // Keyboard is hidden
      document.body.style.removeProperty('--keyboard-height');
      document.body.classList.remove('keyboard-visible');
    }
  });
}

/**
 * Move focus to next input on Enter
 */
function setupFormNavigation(form) {
  const inputs = Array.from(form.querySelectorAll('input, select, textarea'));
  
  inputs.forEach((input, index) => {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && input.tagName !== 'TEXTAREA') {
        e.preventDefault();
        
        const nextInput = inputs[index + 1];
        if (nextInput) {
          nextInput.focus();
        } else {
          // Submit form or blur
          input.blur();
        }
      }
    });
  });
}

// ==========================================================================
// Export
// ==========================================================================

export {
  INPUT_CONFIG,
  configureInput,
  Formatters,
  createFormatter,
  Validators,
  createValidator,
  setupKeyboardHandler,
  setupFormNavigation
};
