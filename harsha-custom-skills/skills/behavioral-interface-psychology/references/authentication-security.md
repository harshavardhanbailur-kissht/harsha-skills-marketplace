# Authentication & Security Reference

## Password Psychology

### User Behavior Reality

**Password Reuse**: 78% admit reusing passwords (Bitwarden 2024)
**Password Manager Usage**: Only 36% (Security.org 2024)
**Recovery Flow Abandonment**: 75% (Stytch)

### NIST SP 800-63B Guidelines (2025)

**Mandatory**:
- Minimum 15 characters
- Check against breach databases
- No composition rules (special chars, etc.)
- No periodic expiration
- No password hints
- Implement rate limiting

**Prohibited**:
- Truncating passwords
- Disallowing paste
- Complex composition requirements (counterproductive)

### Why Composition Rules Fail

**Research Finding**: Complex rules produce:
- Predictable patterns (Password1!, P@ssw0rd)
- Written-down passwords
- Higher reset rates
- Same entropy as length-only requirements

### Password Meter Effectiveness

**Key Study** (Ur et al., USENIX 2012, N=2,931):

| Meter Type | Security Outcome |
|------------|------------------|
| No meter | Baseline |
| Generic meter | No improvement |
| **Data-driven feedback** | Significant improvement |

**Requirements for Effective Meters**:
1. Stringently calibrated
2. Specific feedback ("avoid keyboard patterns")
3. Consistent with actual attack models

**User Perception**: 68.2% felt strength bar accurate

---

## Two-Factor Authentication

### Adoption Rates

**Overall 2FA Usage**: 79% (2021, up from 28% in 2017)

| Method | Usage | Security |
|--------|-------|----------|
| SMS | 85% | Vulnerable to SIM swap |
| Email | 74% | Depends on email security |
| Authenticator apps | 36% | Strong |
| Hardware keys | 4-5% | Strongest |

### Effectiveness

**Google Auto-Enrollment Study**:
- 50% reduction in compromised accounts
- Just by adding SMS 2FA

**Microsoft MFA**:
- Blocks 99.9% of account compromise attacks

### 2FA UX Best Practices

**Reduce Friction**:
- "Remember this device" option
- Risk-based prompting (new device/location)
- Multiple backup methods
- Clear recovery process

**Implementation**:
```
1. Primary: Authenticator app
2. Backup: SMS (acknowledged security trade-off)
3. Recovery: Pre-generated codes (stored securely)
```

---

## Passkeys

### Current State (2024-2025)

**Consumer Awareness**: 57% (up from 39% in 2022)
**Google Accounts Using Passkeys**: 800M

### Performance Benefits

| Metric | Passkeys vs. Passwords |
|--------|------------------------|
| Sign-in success | +30% higher |
| Authentication speed | 20% faster |
| Phishing resistance | ~100% |

### Implementation Considerations

**User Experience**:
- Platform authenticator (Face ID, Windows Hello)
- Cross-device sync (iCloud, Google)
- No memorization required

**Technical**:
```javascript
// WebAuthn registration
const credential = await navigator.credentials.create({
  publicKey: {
    challenge: serverChallenge,
    rp: { name: "Example Corp" },
    user: { id: userId, name: email, displayName: name },
    pubKeyCredParams: [
      { type: "public-key", alg: -7 },  // ES256
      { type: "public-key", alg: -257 } // RS256
    ],
    authenticatorSelection: {
      residentKey: "preferred",
      userVerification: "preferred"
    }
  }
});
```

### Migration Strategy

1. Offer passkeys alongside passwords
2. Promote on successful password login
3. Default to passkey when available
4. Maintain password fallback (for now)

---

## Security Questions: AVOID

### Fundamental Problems

**Google Study** (Bonneau et al., N=millions):
- **40%** of English-speaking US users unable to recall answers

**Fake Answer Paradox**:
- 37% who provided fake answers did so to "make harder to guess"
- Actually made accounts LESS secure (inconsistent, forgotten)

### Better Alternatives

| Instead of Security Questions | Use |
|-------------------------------|-----|
| Mother's maiden name | TOTP code |
| First pet | Backup email |
| Childhood street | Recovery phone |
| Favorite teacher | Pre-generated codes |

---

## Password Recovery

### Flow Abandonment

**75% abandon** password recovery flows

### Effective Recovery

**SMS Reset Success**: >80%

**Best Practice Flow**:
```
1. Email/phone entry
2. Verification code sent
3. Code entry (with retry option)
4. New password creation
5. Session management (logout others?)
```

**Avoid**:
- Security questions
- Complex identity verification for low-risk accounts
- Long timeouts on verification codes

---

## Security Warnings

### Warning Fatigue

**Healthcare Alert Statistics**:
- Median: 63 alerts/day
- 86.9% report excessive alerts
- Override rate: 90% for medication alerts

**Security Alert False Alarm Rates**:
- Healthcare systems: 72-99%
- Security monitoring: 52%

### Effective Warning Design

**Research-Based Principles**:

1. **Specificity**: Explain the actual risk
2. **Actionability**: Clear steps to address
3. **Appropriate severity**: Don't cry wolf
4. **Timing**: Interrupt at decision point

**Example**:
```html
<!-- Bad: Generic -->
<div class="warning">Warning: This action may be dangerous.</div>

<!-- Good: Specific + Actionable -->
<div class="warning">
  <strong>This file was downloaded from an untrusted source</strong>
  <p>Files from unknown sources can contain malware.</p>
  <button>Scan with antivirus</button>
  <button>Delete file</button>
</div>
```

### Habituation Prevention

**Strategies**:
- Vary warning appearance for genuine threats
- Reduce false positives aggressively
- Use polymorphic dialogs (changing layout)
- Require genuine engagement (not just click-through)

**Google Chrome Study**:
- Polymorphic warnings: +30% attention
- Consistent placement reduces noticing over time

---

## SSL/Security Indicators

### Chrome UI Evolution

| Era | Indicator | Current Status |
|-----|-----------|----------------|
| Early | Green address bar | Removed |
| 2018 | "Secure" label | Removed |
| Current | Lock icon | Removed (2023) |
| Now | No positive indicator | HTTPS is default |

### User Understanding

**Most Users**: Don't check for security indicators
**Effective**: Warnings for insecure (HTTP) pages
**Ineffective**: Positive indicators for secure pages

---

## Digital Wellbeing

### "One Sec" App Study

**Research** (Grüning et al., PNAS 2023, N=280):

| Metric | Result |
|--------|--------|
| Reduction in unwanted app usage | **57%** after 6 weeks |
| Attempts dismissed after breathing | 36% |
| Overall opening attempts | -37% week 1→6 |

### Screen Time Tracking

**Key Finding**: Tracking increases awareness but does NOT reduce usage

**What Works**:
- Friction interventions (delays, confirmations)
- Grayscale modes
- App removal/limiting
- Physical device separation

### Dark Pattern Implications

**Attention-Hijacking Patterns**:
- Infinite scroll
- Autoplay
- Variable reward (pull-to-refresh)
- Notification urgency

**Ethical Design Alternative**:
```javascript
// Good: Natural stopping points
<Feed 
  pageSize={20}
  showEndMessage={true}
  requireLoadMore={true}
/>

// Bad: Infinite scroll
<Feed infiniteScroll={true} />
```

---

## Account Security UX

### Session Management

**Best Practices**:
- Show active sessions with device/location
- One-click "log out everywhere"
- Automatic session expiration
- High-risk action re-authentication

### Breach Response

**User Communication**:
1. Clear explanation of what happened
2. Specific data affected
3. Required actions (password reset)
4. Timeline of events
5. Resources for protection

**Technical Response**:
- Force password reset
- Invalidate all sessions
- Enable additional verification
- Monitor for suspicious activity

---

## Biometric Authentication

### Acceptance Rates

| Biometric | User Acceptance |
|-----------|-----------------|
| Fingerprint | ~90% |
| Face recognition | ~85% |
| Iris scan | ~70% |
| Voice recognition | ~60% |

### Design Considerations

**Fallback Required**:
- Biometrics can fail (wet fingers, masks)
- Always provide alternative (PIN, password)
- Don't lock users out

**Privacy Communication**:
- Explain data stays on device
- Clarify not sent to servers
- Address surveillance concerns

---

## Quick Detection Signals

### Authentication Designed Well
- Length-focused requirements (15+ chars)
- No composition rules
- Paste allowed
- Effective password meter
- Passkey support

### 2FA Implemented Well
- "Remember device" option
- Multiple backup methods
- Clear recovery process
- Risk-based prompting

### Security Warnings Effective
- Specific risk explanation
- Clear actions provided
- Appropriate severity
- Minimal false positives

### Recovery User-Friendly
- SMS/email verification
- No security questions
- Clear process
- Reasonable timeouts

---

## Code Patterns to Detect

### Good Patterns
```javascript
// Length-focused validation
const validatePassword = (password) => {
  if (password.length < 15) {
    return 'Password must be at least 15 characters';
  }
  if (isBreached(password)) {
    return 'This password has been found in data breaches';
  }
  return null;
};

// Allow paste
<input 
  type="password" 
  onPaste={() => {}} // Do nothing, allowing paste
/>

// Passkey with fallback
const authenticate = async () => {
  if (await supportsPasskey()) {
    return await authenticateWithPasskey();
  }
  return await showPasswordForm();
};

// Risk-based 2FA
if (isNewDevice || isUnusualLocation) {
  require2FA();
} else {
  allowRememberedSession();
}
```

### Warning Patterns
```javascript
// Composition rules (BAD)
const validatePassword = (p) => {
  return /[A-Z]/.test(p) && 
         /[a-z]/.test(p) && 
         /[0-9]/.test(p) && 
         /[!@#$%]/.test(p);
};

// Blocking paste (BAD - WCAG violation)
<input 
  type="password" 
  onPaste={(e) => e.preventDefault()}
/>

// Security questions (BAD)
<select name="security-question">
  <option>Mother's maiden name</option>
  <option>First pet's name</option>
</select>

// Generic warning
<Alert>Are you sure?</Alert>

// Forced frequent rotation
if (passwordAge > 90) {
  forcePasswordChange();
}
```

### Security Checklist
```javascript
// Configuration audit
const securityConfig = {
  passwordMinLength: 15,        // ✓ NIST compliant
  allowPaste: true,             // ✓ Accessible
  noCompositionRules: true,     // ✓ NIST compliant
  breachCheck: true,            // ✓ Best practice
  passkeySupport: true,         // ✓ Modern
  securityQuestions: false,     // ✓ Avoided
  forceRotation: false,         // ✓ NIST compliant
  mfaOptions: ['totp', 'sms'],  // ✓ Backup available
  rememberedDevices: true,      // ✓ UX friendly
};
```

---

## Regulatory Considerations

### NIST 800-63B Compliance

| Requirement | Status |
|-------------|--------|
| 15+ character minimum | Required |
| Breach database check | Required |
| No composition rules | Required |
| No rotation | Required |
| No hints | Required |
| Allow paste | Required |

### GDPR Implications

- Consent for biometric data
- Right to delete authentication data
- Breach notification requirements
- Data minimization in auth logs
