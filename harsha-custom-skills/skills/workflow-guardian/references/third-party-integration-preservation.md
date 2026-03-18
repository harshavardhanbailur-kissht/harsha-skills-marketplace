# Third-Party Integration Preservation Patterns

## Overview

This reference guide provides comprehensive patterns for safely integrating with and preserving existing third-party services when developing new features. The core principle is: **detect the existing service pattern, extend using that pattern, never add competing alternatives**.

When Claude adds features involving third-party integrations, the most common source of breakage is introducing incompatible services or modifying integration patterns without preserving the original configuration.

---

## 1. Payment Gateway Preservation

### 1.1 Detection Patterns

#### Stripe Detection
```javascript
// Check for Stripe library
- window.Stripe or require('stripe')
- <script src="https://js.stripe.com/v3/"></script>
- stripe_key in environment variables
- .env: REACT_APP_STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY
- stripe/ folder in API routes
- stripe.Charge, stripe.PaymentIntent, stripe.Subscription classes
- Webhook listener at /api/webhooks/stripe
```

#### Razorpay Detection
```javascript
// Check for Razorpay library
- window.Razorpay or require('razorpay')
- <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
- razorpay_key in environment variables
- .env: REACT_APP_RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
- razorpay/ folder in API routes
- Razorpay.Order, Razorpay.Payment classes
- Webhook listener at /api/webhooks/razorpay
```

#### PayPal Detection
```javascript
// Check for PayPal SDK
- window.paypal or require('@paypal/checkout-server-sdk')
- <script src="https://www.paypal.com/sdk/js?client-id=..."></script>
- paypal_client_id, paypal_secret in environment variables
- .env: REACT_APP_PAYPAL_CLIENT_ID, PAYPAL_SECRET
- paypal/ folder in API routes
- paypal.orders, paypal.payments classes
- Webhook listener at /api/webhooks/paypal
```

### 1.2 Safe Extension Patterns

#### Adding New Payment Feature to Existing Stripe Integration
```javascript
// EXISTING PAYMENT FLOW (already using Stripe)
const existingCheckoutFlow = async (amount) => {
  const response = await fetch('/api/create-payment-intent', {
    method: 'POST',
    body: JSON.stringify({ amount })
  });
  const { clientSecret } = await response.json();
  return stripe.confirmCardPayment(clientSecret);
};

// NEW FEATURE: Subscription Management (EXTENDS existing Stripe pattern)
// SAFE: Uses the same Stripe instance and webhook handler
const addSubscription = async (productId, customerId) => {
  // Uses existing Stripe integration
  const response = await fetch('/api/create-subscription', {
    method: 'POST',
    body: JSON.stringify({ productId, customerId })
  });
  const { subscriptionId } = await response.json();
  // Webhook handler at /api/webhooks/stripe already exists
  // Just add new event type: customer.subscription.updated
  return subscriptionId;
};

// NEVER DO THIS:
// const addPayPalAlternative = async () => {
//   // This breaks existing Stripe integration by introducing competing gateway
//   const paypalResponse = await fetch('/api/create-paypal-payment');
// };
```

#### Adding New Payment Feature to Existing Razorpay Integration
```javascript
// EXISTING PAYMENT FLOW
const existingCheckoutFlow = async (amount) => {
  const response = await fetch('/api/razorpay/create-order', {
    method: 'POST',
    body: JSON.stringify({ amount })
  });
  const { orderId } = await response.json();
  return Razorpay.openCheckout({ key_id, order_id: orderId });
};

// NEW FEATURE: Recurring Payments (EXTENDS existing Razorpay pattern)
// SAFE: Uses same Razorpay instance and webhook structure
const addRecurringPayment = async (amount, interval) => {
  const response = await fetch('/api/razorpay/create-subscription', {
    method: 'POST',
    body: JSON.stringify({ amount, interval })
  });
  const { subscriptionId } = await response.json();
  // Existing webhook handler continues to work
  return subscriptionId;
};

// Key insight: Both features use /api/razorpay/* pattern
// Both trigger /api/webhooks/razorpay validation
```

### 1.3 Webhook Handling Preservation

#### Safe Webhook Extension
```javascript
// EXISTING webhook handler for Stripe
app.post('/api/webhooks/stripe', (req, res) => {
  const sig = req.headers['stripe-signature'];
  const event = stripe.webhooks.constructEvent(
    req.rawBody,
    sig,
    process.env.STRIPE_WEBHOOK_SECRET
  );

  // Existing handlers
  switch (event.type) {
    case 'payment_intent.succeeded':
      handlePaymentSuccess(event);
      break;
    case 'payment_intent.payment_failed':
      handlePaymentFailure(event);
      break;
    // ADD NEW HANDLER here (don't create new webhook endpoint)
    case 'customer.subscription.updated':
      handleSubscriptionUpdate(event);
      break;
  }

  res.json({ received: true });
});

// SAFE: Extends existing webhook
// DANGEROUS: Creating /api/webhooks/stripe-subscriptions endpoint
```

### 1.4 Payment Form Security Preservation

#### PCI Compliance Considerations
```javascript
// EXISTING Stripe card element form
const StripeCheckout = () => {
  const [cardElement, setCardElement] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Stripe handles card data - app never touches raw card numbers
    const result = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: cardElement,
        billing_details: { name: customerName }
      }
    });
  };

  // SAFE: Stripe tokenizes card data
  // DANGEROUS: Accepting raw card numbers in form
  //   const cardNumber = document.getElementById('card-number').value;
  //   // This violates PCI DSS and creates liability
};

// When adding new payment features:
// 1. Never accept raw card/payment data
// 2. Always tokenize through existing gateway
// 3. Pass only tokens to backend API
// 4. Keep card verification within existing element
```

### 1.5 Breakage Prevention Checklist

```
[ ] Identified existing payment gateway (Stripe/Razorpay/PayPal)
[ ] Located API route pattern (/api/stripe/* or /api/razorpay/*)
[ ] Found webhook endpoint and secret in environment
[ ] Identified event types already being handled
[ ] Confirmed no competing payment gateway exists
[ ] Extending feature uses same gateway instance
[ ] New webhook event types added to existing handler
[ ] No new environment variables for alternative gateway
[ ] Form/payment flow uses existing tokenization pattern
[ ] Backend API continues using existing gateway SDK
[ ] No changes to webhook signature verification
```

---

## 2. Email Service Preservation

### 2.1 Detection Patterns

#### SendGrid Detection
```javascript
// Check for SendGrid library
- require('@sendgrid/mail') or require('@sendgrid/client')
- .env: SENDGRID_API_KEY
- sendgrid/ folder in API routes
- sg.send() or sgMail.send() calls
- Email verification/unsubscribe in sendgrid domain
- sendgrid/email-templates folder (template IDs stored)
- SENDGRID_TEMPLATE_ID_* pattern in environment
- Webhook listener at /api/webhooks/sendgrid
- Inbound parse webhook configured
```

#### Mailgun Detection
```javascript
// Check for Mailgun library
- require('mailgun.js') or require('mailgun-js')
- .env: MAILGUN_API_KEY, MAILGUN_DOMAIN
- mailgun/ folder in API routes
- mg.messages.create() calls
- Email sending from mailgun domain (mg.example.com)
- mailgun/email-templates folder
- MAILGUN_TEMPLATE_ID_* pattern in environment
- Webhook listener at /api/webhooks/mailgun
- Route webhook configured for events
```

#### AWS SES Detection
```javascript
// Check for AWS SES
- require('@aws-sdk/client-sesv2') or aws-sdk SES client
- .env: AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
- ses/ folder in API routes
- new SESClient().sendEmail() or sendRawEmail() calls
- Verified sender email address configured
- .env: SES_FROM_EMAIL, SES_REGION
- SNS webhook listener at /api/webhooks/ses
- Bounce/complaint handlers configured
```

#### Resend Detection
```javascript
// Check for Resend library
- require('resend') or from 'resend'
- .env: RESEND_API_KEY
- resend/ folder in API routes
- resend.emails.send() calls
- React email components in emails/ folder
- Webhook listener at /api/webhooks/resend
- Email domain verified in Resend dashboard
```

### 2.2 Safe Extension Patterns

#### Adding New Email Type to Existing SendGrid Integration
```javascript
// EXISTING SendGrid setup
const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

// Existing email templates already in environment
const TEMPLATES = {
  welcome: process.env.SENDGRID_TEMPLATE_WELCOME,
  passwordReset: process.env.SENDGRID_TEMPLATE_PASSWORD_RESET,
  orderConfirm: process.env.SENDGRID_TEMPLATE_ORDER_CONFIRM
};

// EXISTING function using template system
const sendWelcomeEmail = async (email, firstName) => {
  await sgMail.send({
    to: email,
    from: 'noreply@company.com',
    templateId: TEMPLATES.welcome,
    dynamicTemplateData: { firstName }
  });
};

// NEW FEATURE: Add invoice email (SAFE extension)
const sendInvoiceEmail = async (email, invoiceId, amount) => {
  // Uses same SendGrid instance
  // Follows same template pattern
  // Requires adding SENDGRID_TEMPLATE_INVOICE to .env

  // First, create template in SendGrid dashboard
  // Add to environment: SENDGRID_TEMPLATE_INVOICE=d-template-id

  await sgMail.send({
    to: email,
    from: 'noreply@company.com',
    templateId: process.env.SENDGRID_TEMPLATE_INVOICE,
    dynamicTemplateData: { invoiceId, amount }
  });
};

// NEVER DO THIS:
// const sendInvoiceViaMailgun = async (email, invoiceId) => {
//   // This breaks SendGrid integration by introducing competing service
//   const mg = mailgun({ apiKey: process.env.MAILGUN_API_KEY });
//   await mg.messages.create(...);
// };
```

#### Transactional vs Marketing Email Separation
```javascript
// EXISTING SendGrid integration with separation
const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

// Transactional emails (critical, time-sensitive, user-triggered)
const transactionalEmails = {
  passwordReset: process.env.SENDGRID_TEMPLATE_PASSWORD_RESET,
  orderConfirm: process.env.SENDGRID_TEMPLATE_ORDER_CONFIRM,
  accountVerification: process.env.SENDGRID_TEMPLATE_VERIFY_ACCOUNT
};

// Marketing emails (promotional, scheduled, bulk)
const marketingEmails = {
  weeklyNewsletter: process.env.SENDGRID_TEMPLATE_NEWSLETTER,
  productPromotion: process.env.SENDGRID_TEMPLATE_PROMO,
  abandonedCart: process.env.SENDGRID_TEMPLATE_ABANDONED_CART
};

// NEW FEATURE: Add promotional email (respects existing separation)
const sendPromotionalEmail = async (email, productData) => {
  // This is marketing, so:
  // 1. Check unsubscribe status from SendGrid
  // 2. Include unsubscribe link
  // 3. Use marketing template ID

  const contact = await checkSendGridContact(email);
  if (contact.unsubscribed_marketing) {
    return; // Respect existing preferences
  }

  await sgMail.send({
    to: email,
    from: 'marketing@company.com',
    templateId: process.env.SENDGRID_TEMPLATE_PROMO,
    dynamicTemplateData: productData,
    asm: {
      groupId: 123 // Existing unsubscribe group ID
    }
  });
};

// Key distinction:
// - Transactional: no unsubscribe check, critical
// - Marketing: check preferences, include unsubscribe
```

### 2.3 Email Configuration Preservation

#### Environment Variable Pattern
```bash
# EXISTING SendGrid configuration
SENDGRID_API_KEY=SG.xxxxx
SENDGRID_FROM_EMAIL=noreply@company.com
SENDGRID_FROM_NAME=Company Support
SENDGRID_TEMPLATE_WELCOME=d-xxxxx
SENDGRID_TEMPLATE_PASSWORD_RESET=d-xxxxx
SENDGRID_TEMPLATE_ORDER_CONFIRM=d-xxxxx

# NEW FEATURE: Add invoice email
# SAFE: Add template ID following existing pattern
SENDGRID_TEMPLATE_INVOICE=d-xxxxx

# NEVER DO:
# MAILGUN_API_KEY=key-xxxxx  # This conflicts with SendGrid
# AWS_SES_FROM_EMAIL=noreply@aws.com  # This introduces competing service
```

### 2.4 Webhook Event Handling Preservation

#### Extending Existing Email Webhooks
```javascript
// EXISTING SendGrid webhook handler
app.post('/api/webhooks/sendgrid', (req, res) => {
  const events = req.body;

  events.forEach(event => {
    switch (event.event) {
      case 'delivered':
        markEmailAsDelivered(event.email);
        break;
      case 'bounce':
        handleBounce(event.email, event.reason);
        break;
      case 'unsubscribe':
        markUnsubscribed(event.email);
        break;
      // NEW: Handle new email event types here
      case 'complaint':
        handleComplaint(event.email);
        break;
    }
  });

  res.status(200).json({ success: true });
});

// SAFE: Extend existing webhook
// DANGEROUS: Creating /api/webhooks/sendgrid-events endpoint
```

### 2.5 Breakage Prevention Checklist

```
[ ] Identified existing email service (SendGrid/Mailgun/SES/Resend)
[ ] Located API key and configuration in environment
[ ] Found template ID pattern in environment
[ ] Identified existing email event handlers
[ ] Confirmed no competing email service exists
[ ] New emails use same sgMail/mg/ses instance
[ ] New email templates follow existing naming pattern
[ ] Template IDs added to environment (not hardcoded)
[ ] Webhook handler extended with new event types
[ ] Transactional/marketing separation maintained
[ ] Unsubscribe preferences respected
[ ] No changes to webhook endpoint or verification
[ ] From email address consistent with existing
```

---

## 3. Analytics/Tracking Preservation

### 3.1 Detection Patterns

#### Google Analytics Detection
```javascript
// Check for Google Analytics
- window.gtag or window.dataLayer
- <script async src="https://www.googletagmanager.com/gtag/js?id=GA-..."></script>
- gtag('config', 'GA-XXXXXXX')
- .env: REACT_APP_GA_ID or NEXT_PUBLIC_GA_ID
- gtag('event', ...) calls throughout codebase
- analytics/ folder in utils
- Google Analytics event tracking pattern
- Custom events like 'purchase', 'sign_up'
- User ID tracking with gtag('set', {'user_id': userId})
```

#### Mixpanel Detection
```javascript
// Check for Mixpanel library
- window.mixpanel or require('mixpanel-browser')
- <script src="https://cdn.mxpnl.com/libs/mixpanel-latest.min.js"></script>
- mixpanel.init('project-token')
- .env: REACT_APP_MIXPANEL_TOKEN
- mixpanel.track('event_name') calls
- mixpanel.identify(userId) in auth flows
- mixpanel.people.set() for user properties
- Event tracking files in tracking/ folder
```

#### Amplitude Detection
```javascript
// Check for Amplitude library
- window.amplitude or require('@amplitude/analytics-browser')
- <script src="https://cdn.amplitude.com/libs/amplitude-...min.js"></script>
- amplitude.init('api-key')
- .env: REACT_APP_AMPLITUDE_KEY or NEXT_PUBLIC_AMPLITUDE_KEY
- amplitude.track('event_name') calls
- amplitude.setUserId(userId) in auth flows
- amplitude.setUserProperties() calls
- Event tracking files in tracking/ folder
```

### 3.2 Safe Extension Patterns

#### Adding New Event Tracking to Existing Google Analytics
```javascript
// EXISTING Google Analytics setup
import { initializeApp } from 'next/script';

export const pageview = (url) => {
  window.gtag('config', process.env.NEXT_PUBLIC_GA_ID, {
    page_path: url,
  });
};

export const event = ({ action, category, label, value }) => {
  window.gtag('event', action, {
    event_category: category,
    event_label: label,
    value: value,
  });
};

// EXISTING events being tracked
// - 'sign_up', 'login', 'logout'
// - 'page_view'
// - 'purchase'

// NEW FEATURE: Add feature usage tracking (SAFE extension)
export const trackFeatureUsage = (featureName) => {
  // Uses same gtag instance
  // Follows same event pattern
  window.gtag('event', 'feature_used', {
    event_category: 'feature',
    event_label: featureName,
  });
};

// NEW FEATURE: Add A/B test tracking (SAFE extension)
export const trackABTestVariant = (testName, variant) => {
  // Uses same tracking infrastructure
  window.gtag('event', 'experiment_viewed', {
    event_category: 'experiment',
    event_label: testName,
    experiment_variant: variant,
  });
};

// NEVER DO THIS:
// export const initMixpanel = () => {
//   // This breaks Google Analytics by introducing competing analytics
//   mixpanel.init(process.env.REACT_APP_MIXPANEL_TOKEN);
// };
```

#### Adding Event Tracking to Existing Mixpanel
```javascript
// EXISTING Mixpanel setup
import mixpanel from 'mixpanel-browser';

mixpanel.init(process.env.REACT_APP_MIXPANEL_TOKEN);

// Existing event tracking
export const trackSignUp = (email, referralSource) => {
  mixpanel.track('sign_up', {
    email,
    referral_source: referralSource,
  });

  // User identification after signup
  mixpanel.identify(userId);
};

// NEW FEATURE: Track premium feature access (SAFE extension)
export const trackPremiumFeatureAccess = (featureName, userId) => {
  // Uses same mixpanel instance
  mixpanel.track('premium_feature_accessed', {
    feature_name: featureName,
    user_id: userId,
    timestamp: new Date().toISOString(),
  });
};

// NEW FEATURE: Update user properties for segmentation (SAFE extension)
export const updateUserPlan = (userId, planType) => {
  // Uses same mixpanel instance
  mixpanel.identify(userId);
  mixpanel.people.set({
    plan_type: planType,
    plan_updated_at: new Date().toISOString(),
  });
};

// Key insight: All tracking uses single mixpanel instance
// All events flow through Mixpanel dashboard
```

### 3.3 Privacy and GDPR Consent Preservation

#### GDPR Consent Pattern
```javascript
// EXISTING GDPR consent management
const consentManager = {
  hasAnalyticsConsent: () => {
    return localStorage.getItem('analytics_consent') === 'true';
  },

  hasMarketingConsent: () => {
    return localStorage.getItem('marketing_consent') === 'true';
  },

  setConsent: (type, value) => {
    localStorage.setItem(`${type}_consent`, value);

    // Update analytics based on consent
    if (type === 'analytics') {
      updateAnalyticsTracking(value);
    }
  }
};

// EXISTING event tracking respects consent
export const trackEvent = (eventName, data) => {
  if (!consentManager.hasAnalyticsConsent()) {
    return; // Don't track if consent not given
  }

  window.gtag('event', eventName, data);
};

// NEW FEATURE: Add consent-aware tracking (respects existing pattern)
export const trackUserProperty = (property, value) => {
  // Follows existing consent check pattern
  if (!consentManager.hasAnalyticsConsent()) {
    return;
  }

  window.gtag('event', 'user_property_set', {
    property_name: property,
    property_value: value,
  });
};

// Key principle: All new tracking respects existing consent checks
```

### 3.4 Tracking Configuration Preservation

```javascript
// EXISTING tracking configuration
const trackingConfig = {
  provider: 'google_analytics', // Never change this
  apiKey: process.env.NEXT_PUBLIC_GA_ID,

  enabledEvents: {
    pageView: true,
    click: true,
    signup: true,
    purchase: true,
  },

  excludedRoutes: ['/admin', '/api/'], // Existing config

  customDimensions: {
    userId: 'dimension1',
    userPlan: 'dimension2',
    referralSource: 'dimension3',
  }
};

// SAFE: Add new event to enabledEvents
trackingConfig.enabledEvents.featureUsage = true;

// SAFE: Add new custom dimension
trackingConfig.customDimensions.cohortId = 'dimension4';

// DANGEROUS: Adding competing analytics provider
// trackingConfig.mixpanelToken = process.env.REACT_APP_MIXPANEL_TOKEN;

// DANGEROUS: Changing provider
// trackingConfig.provider = 'amplitude';
```

### 3.5 Breakage Prevention Checklist

```
[ ] Identified existing analytics provider (GA/Mixpanel/Amplitude)
[ ] Located API key in environment variables
[ ] Found existing event tracking calls
[ ] Identified custom dimensions/properties being tracked
[ ] Confirmed no competing analytics service exists
[ ] New events use same tracking library instance
[ ] New events follow existing naming/structure pattern
[ ] GDPR consent checks apply to new tracking
[ ] User ID tracking consistent with existing pattern
[ ] No changes to analytics library initialization
[ ] No competing analytics library imported
[ ] Dashboard events will appear in same location
```

---

## 4. Error Monitoring Preservation

### 4.1 Detection Patterns

#### Sentry Detection
```javascript
// Check for Sentry library
- require('@sentry/react') or require('@sentry/node')
- import * as Sentry from '@sentry/react'
- Sentry.init() in app initialization
- .env: REACT_APP_SENTRY_DSN or SENTRY_DSN
- Sentry.captureException() calls
- Sentry.captureMessage() calls
- Sentry.withProfiler() HOC for React components
- Sentry provider wrapping app
- sentry.server.config.ts or sentry.edge.config.ts
- Sentry context setting: Sentry.setUser(), Sentry.setTag()
```

#### LogRocket Detection
```javascript
// Check for LogRocket library
- require('logrocket') or from 'logrocket'
- import LogRocket from 'logrocket'
- LogRocket.init('app-id')
- .env: REACT_APP_LOGROCKET_ID or NEXT_PUBLIC_LOGROCKET_ID
- LogRocket.captureException() calls
- LogRocket.getSessionURL() in error reports
- Redux integration with LogRocket
- Error stream subscribers
- Session recording setup
```

#### Bugsnag Detection
```javascript
// Check for Bugsnag library
- require('@bugsnag/js') or require('@bugsnag/plugin-react')
- Bugsnag.start() initialization
- .env: BUGSNAG_API_KEY
- Bugsnag.notify() calls
- Bugsnag.addFeatureFlag() for tracking
- ErrorBoundary from @bugsnag/plugin-react
- Breadcrumb tracking setup
- Release tracking with Bugsnag.setReleaseStage()
```

### 4.2 Safe Extension Patterns

#### Adding Error Context to Existing Sentry Integration
```javascript
// EXISTING Sentry setup
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
});

// EXISTING error boundary
const ErrorBoundary = Sentry.withErrorBoundary(App, {
  fallback: <ErrorPage />,
  showDialog: true,
});

// EXISTING exception capture
export const handleError = (error, context) => {
  Sentry.captureException(error, {
    tags: {
      section: context.section,
      userId: context.userId,
    },
  });
};

// NEW FEATURE: Add payment error tracking (SAFE extension)
export const handlePaymentError = (error, paymentData) => {
  // Uses same Sentry instance
  Sentry.captureException(error, {
    tags: {
      section: 'payments',
      paymentMethod: paymentData.method,
      amount: paymentData.amount,
    },
    level: 'error',
  });
};

// NEW FEATURE: Add breadcrumb for user actions (SAFE extension)
export const trackUserAction = (action, metadata) => {
  // Uses same Sentry breadcrumb system
  Sentry.captureMessage(`User action: ${action}`, 'info');
  Sentry.addBreadcrumb({
    category: 'user-action',
    message: action,
    level: 'info',
    data: metadata,
  });
};

// NEVER DO THIS:
// export const setupBugsnag = () => {
//   // This breaks Sentry by introducing competing error monitor
//   Bugsnag.start({ apiKey: process.env.BUGSNAG_API_KEY });
// };
```

#### Adding Error Monitoring to Existing LogRocket Integration
```javascript
// EXISTING LogRocket setup
import LogRocket from 'logrocket';

LogRocket.init(process.env.REACT_APP_LOGROCKET_ID);

// Existing Redux integration
import createReduxMiddleware from 'logrocket-redux';
store.dispatch = createReduxMiddleware(store)(store.dispatch);

// EXISTING error capture with session URL
export const reportError = (error, context) => {
  const sessionURL = LogRocket.getSessionURL();
  LogRocket.captureException(error, {
    tags: context,
    extra: { sessionURL },
  });
};

// NEW FEATURE: Add API error tracking (SAFE extension)
export const trackAPIError = (endpoint, statusCode, errorData) => {
  // Uses same LogRocket instance
  LogRocket.captureMessage('API Error', 'error');
  LogRocket.getSessionURL(); // Include in error report

  // The error will be visible in session replay
};

// NEW FEATURE: Add user identification (SAFE extension)
export const identifyUser = (userId, email) => {
  // Uses same LogRocket instance
  LogRocket.identify(userId, {
    email,
    subscriptionType: 'premium',
  });
};

// Key insight: LogRocket session recordings automatically
// capture console errors, network activity, user clicks
```

### 4.3 Breadcrumb and Context Patterns

#### Preserving Breadcrumb Structure
```javascript
// EXISTING breadcrumb patterns
class ErrorTracker {
  addBreadcrumb(message, category, level = 'info') {
    const breadcrumb = {
      timestamp: new Date().toISOString(),
      message,
      category,
      level,
    };

    // Send to Sentry
    Sentry.addBreadcrumb(breadcrumb);
  }
}

const tracker = new ErrorTracker();

// EXISTING usage
tracker.addBreadcrumb('User login attempt', 'auth');
tracker.addBreadcrumb('Payment initiated', 'payment');

// NEW FEATURE: Add feature breadcrumbs (respects existing pattern)
tracker.addBreadcrumb('Feature X enabled', 'feature');

// Breadcrumbs appear in Sentry in chronological order
// All breadcrumbs flow to same error monitor
```

### 4.4 Middleware Order Preservation

#### Error Monitoring Middleware
```javascript
// EXISTING middleware setup - ORDER MATTERS
app.use(
  express.json(),
  logger,
  authenticateUser,
  // Error monitoring must be before error handling
  Sentry.Handlers.requestHandler(),
  // Application routes here
  apiRoutes,
  // Error monitoring handler must be after routes
  Sentry.Handlers.errorHandler(),
  // Final error handler
  globalErrorHandler
);

// SAFE: Add new middleware before error monitoring
app.use(validateInputs); // Works correctly

// DANGEROUS: Add middleware after error monitoring
// app.use(apiRoutes);  // This breaks error context

// Key principle: Don't reorder middleware that affects error monitoring
```

### 4.5 Breakage Prevention Checklist

```
[ ] Identified existing error monitor (Sentry/LogRocket/Bugsnag)
[ ] Located DSN or API key in environment
[ ] Found error boundary components
[ ] Identified existing error capture calls
[ ] Confirmed no competing error monitor exists
[ ] New errors use same captureException pattern
[ ] New breadcrumbs follow existing category naming
[ ] Error context (tags, metadata) uses existing structure
[ ] No changes to error middleware initialization order
[ ] No competing error monitor library imported
[ ] Session recording (LogRocket) not disabled
[ ] Error reporting dashboard unchanged
```

---

## 5. Cloud Storage Integration Preservation

### 5.1 Detection Patterns

#### Firebase Storage Detection
```javascript
// Check for Firebase Storage
- require('firebase-admin').storage() or getStorage()
- import { getStorage } from 'firebase/storage'
- firebase.initializeApp(firebaseConfig)
- .env: REACT_APP_FIREBASE_PROJECT_ID, REACT_APP_FIREBASE_STORAGE_BUCKET
- firebase.storage().ref() calls
- uploadBytes(), downloadURL() patterns
- Storage bucket reference: gs://bucket-name
- Firebase Cloud Functions with storage.on('finalize')
```

#### Supabase Storage Detection
```javascript
// Check for Supabase Storage
- require('@supabase/supabase-js') with storage
- import { createClient } from '@supabase/supabase-js'
- supabase.storage.from('bucket-name')
- .env: REACT_APP_SUPABASE_URL, REACT_APP_SUPABASE_ANON_KEY
- supabase.storage.from().upload() calls
- getPublicUrl(), getSignedUrl() patterns
- Bucket configuration in Supabase dashboard
```

#### AWS S3 Detection
```javascript
// Check for AWS S3
- require('@aws-sdk/client-s3') or require('aws-sdk')
- new S3Client() initialization
- .env: AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
- AWS_S3_BUCKET, AWS_S3_REGION in environment
- PutObjectCommand, GetObjectCommand patterns
- s3.upload() calls
- S3 URL signing with getSignedUrl()
```

#### Cloudinary Detection
```javascript
// Check for Cloudinary
- require('cloudinary').v2 or from 'next-cloudinary'
- cloudinary.config({ cloud_name, api_key })
- .env: NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY
- cloudinary.uploader.upload() calls
- cloudinary.url() for CDN URLs
- Image optimization with cloudinary transformations
- Upload widget from cloudinary/next
```

### 5.2 Safe Extension Patterns

#### Adding File Handling to Existing Firebase Storage
```javascript
// EXISTING Firebase Storage setup
import { ref, uploadBytes, getBytes, deleteObject } from 'firebase/storage';
import { storage } from './firebaseConfig';

// EXISTING upload pattern
export const uploadUserAvatar = async (userId, file) => {
  const avatarRef = ref(storage, `avatars/${userId}`);
  const result = await uploadBytes(avatarRef, file);
  return result.ref.fullPath;
};

// EXISTING download pattern
export const getUserAvatar = async (userId) => {
  const avatarRef = ref(storage, `avatars/${userId}`);
  try {
    const url = await getDownloadURL(avatarRef);
    return url;
  } catch {
    return null;
  }
};

// NEW FEATURE: Add document upload (SAFE extension)
export const uploadDocument = async (userId, documentFile) => {
  // Uses same Firebase Storage instance
  // Follows same ref() and uploadBytes() pattern
  const docRef = ref(storage, `documents/${userId}/${Date.now()}`);
  const result = await uploadBytes(docRef, documentFile);
  return result.ref.fullPath;
};

// NEW FEATURE: Add image optimization (respects existing storage)
export const uploadImage = async (userId, imageFile) => {
  // Still uses Firebase Storage
  // Image optimization happens in download, not storage
  const imageRef = ref(storage, `images/${userId}/${Date.now()}`);
  await uploadBytes(imageRef, imageFile);
  return getDownloadURL(imageRef);
};

// NEVER DO THIS:
// export const uploadToCloudinary = async (userId, file) => {
//   // This breaks Firebase Storage integration
//   const result = await cloudinary.uploader.upload(file);
// };
```

#### Adding to Existing Supabase Storage
```javascript
// EXISTING Supabase Storage setup
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.REACT_APP_SUPABASE_URL,
  process.env.REACT_APP_SUPABASE_ANON_KEY
);

// EXISTING upload pattern
export const uploadProfileImage = async (userId, file) => {
  const { data, error } = await supabase.storage
    .from('profiles')
    .upload(`${userId}/avatar.jpg`, file, { upsert: true });

  if (error) throw error;
  return data.path;
};

// EXISTING public URL pattern
export const getProfileImageUrl = (userId) => {
  const { data } = supabase.storage
    .from('profiles')
    .getPublicUrl(`${userId}/avatar.jpg`);
  return data.publicUrl;
};

// NEW FEATURE: Add document storage (SAFE extension)
export const uploadDocument = async (userId, documentFile, documentName) => {
  // Uses same Supabase instance
  // Follows same bucket and path pattern
  const { data, error } = await supabase.storage
    .from('documents')
    .upload(`${userId}/${documentName}`, documentFile);

  if (error) throw error;
  return data.path;
};

// NEW FEATURE: Add signed URLs for temporary access (SAFE extension)
export const getDocumentSignedUrl = async (userId, documentName) => {
  // Uses same Supabase storage with signed URL feature
  const { data, error } = await supabase.storage
    .from('documents')
    .createSignedUrl(`${userId}/${documentName}`, 3600); // 1 hour

  if (error) throw error;
  return data.signedUrl;
};

// Key insight: All storage operations use same supabase instance
// All buckets ('profiles', 'documents') in same storage service
```

### 5.3 URL Generation Pattern Preservation

#### Signed vs Public URLs
```javascript
// EXISTING S3 URL generation
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';

const s3Client = new S3Client({ region: process.env.AWS_REGION });

// PUBLIC URLs (permanent access)
export const getPublicFileUrl = (key) => {
  return `https://${process.env.AWS_S3_BUCKET}.s3.${process.env.AWS_S3_REGION}.amazonaws.com/${key}`;
};

// SIGNED URLs (temporary access)
export const getSignedDownloadUrl = async (key, expiresIn = 3600) => {
  const command = new GetObjectCommand({
    Bucket: process.env.AWS_S3_BUCKET,
    Key: key,
  });

  const url = await getSignedUrl(s3Client, command, { expiresIn });
  return url;
};

// EXISTING usage
// Public URLs for profile images, product photos
// Signed URLs for private documents, reports

// NEW FEATURE: Add invoice download (SAFE extension)
export const getInvoiceSignedUrl = async (userId, invoiceId) => {
  // Uses same signed URL pattern
  const key = `invoices/${userId}/${invoiceId}.pdf`;
  return getSignedDownloadUrl(key, 7200); // 2 hours
};

// Key principle: Don't mix public/signed logic
// Keep pattern consistent across new features
```

### 5.4 Image Optimization and CDN Preservation

#### Cloudinary Image Optimization Pattern
```javascript
// EXISTING Cloudinary setup
const cloudinary = require('cloudinary').v2;
cloudinary.config({
  cloud_name: process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
});

// EXISTING image optimization
export const getOptimizedImageUrl = (publicId, { width, height, quality }) => {
  // All images go through Cloudinary CDN
  return cloudinary.url(publicId, {
    width,
    height,
    crop: 'fill',
    quality: quality || 'auto',
  });
};

// EXISTING usage
// Product images: width 300, height 300
// Hero images: width 1200, height 400
// Thumbnails: width 150, height 150

// NEW FEATURE: Add user profile image optimization (SAFE extension)
export const getProfileImageOptimized = (userId, size = 'medium') => {
  // Uses same Cloudinary instance
  const sizes = {
    small: { width: 50, height: 50 },
    medium: { width: 150, height: 150 },
    large: { width: 300, height: 300 },
  };

  const { width, height } = sizes[size];
  return cloudinary.url(`user-${userId}`, {
    width,
    height,
    crop: 'thumb',
    gravity: 'face',
    quality: 'auto',
  });
};

// NEW FEATURE: Add responsive image variants (SAFE extension)
export const getResponsiveImageUrl = (publicId, breakpoint) => {
  // Uses same Cloudinary instance
  const breakpoints = {
    mobile: { width: 320, dpr: 'auto' },
    tablet: { width: 768, dpr: 'auto' },
    desktop: { width: 1200, dpr: 'auto' },
  };

  const config = breakpoints[breakpoint];
  return cloudinary.url(publicId, {
    width: config.width,
    dpr: config.dpr,
    quality: 'auto',
  });
};

// Key insight: All images use Cloudinary transforms
// Consistent quality settings across all features
```

### 5.5 Breakage Prevention Checklist

```
[ ] Identified existing cloud storage (Firebase/Supabase/S3/Cloudinary)
[ ] Located storage credentials in environment
[ ] Found existing upload/download patterns
[ ] Identified bucket/collection naming convention
[ ] Confirmed no competing storage service exists
[ ] New uploads use same storage instance
[ ] New file paths follow existing directory structure
[ ] URL generation follows existing public/signed pattern
[ ] Image optimization uses existing service
[ ] No changes to storage initialization
[ ] No competing storage library imported
[ ] File access patterns (CORS, permissions) unchanged
```

---

## 6. Authentication Provider Integration Preservation

### 6.1 Detection Patterns

#### Firebase Auth Detection
```javascript
// Check for Firebase Authentication
- require('firebase-admin').auth() or getAuth()
- import { getAuth } from 'firebase/auth'
- firebase.initializeApp(firebaseConfig)
- .env: REACT_APP_FIREBASE_API_KEY, REACT_APP_FIREBASE_PROJECT_ID
- onAuthStateChanged() listeners
- signInWithPopup(), signInWithEmail() patterns
- createUserWithEmailAndPassword()
- Firebase Auth Rules in firestore.rules
- Custom claims handling: auth.token.admin
```

#### Supabase Auth Detection
```javascript
// Check for Supabase Authentication
- require('@supabase/supabase-js') with auth
- import { createClient } from '@supabase/supabase-js'
- supabase.auth.onAuthStateChange()
- .env: REACT_APP_SUPABASE_URL, REACT_APP_SUPABASE_ANON_KEY
- supabase.auth.signInWithPassword()
- supabase.auth.signUp()
- supabase.auth.signInWithOAuth()
- Session management in localStorage
- JWT token handling
```

#### Auth0 Detection
```javascript
// Check for Auth0
- require('@auth0/auth0-react') or require('auth0')
- import { Auth0Provider } from '@auth0/auth0-react'
- useAuth0() hooks
- .env: REACT_APP_AUTH0_DOMAIN, REACT_APP_AUTH0_CLIENT_ID
- Auth0Provider wrapping application
- loginWithRedirect(), logout() patterns
- useUser() for current user
- getAccessTokenSilently() for API calls
```

#### Clerk Detection
```javascript
// Check for Clerk
- require('@clerk/nextjs') or require('@clerk/react')
- import { ClerkProvider } from '@clerk/nextjs'
- useAuth(), useUser() from Clerk
- .env: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY
- SignIn, SignUp components from @clerk/nextjs
- Middleware for authentication in Next.js
- Session tokens and JWTs
```

### 6.2 Safe Extension Patterns

#### Adding OAuth to Existing Firebase Auth
```javascript
// EXISTING Firebase Auth setup
import { getAuth, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';

const auth = getAuth();
const googleProvider = new GoogleAuthProvider();

// EXISTING Google OAuth
export const signInWithGoogle = async () => {
  const result = await signInWithPopup(auth, googleProvider);
  return result.user;
};

// EXISTING session management
export const onAuthStateChanged = (callback) => {
  return auth.onAuthStateChanged((user) => {
    callback(user);
  });
};

// NEW FEATURE: Add GitHub OAuth (SAFE extension)
// Uses same Firebase Auth instance
const githubProvider = new GithubAuthProvider();

export const signInWithGitHub = async () => {
  // Same pattern as existing Google OAuth
  const result = await signInWithPopup(auth, githubProvider);
  return result.user;
};

// NEW FEATURE: Add custom token auth (SAFE extension)
// Uses same Firebase Auth instance
export const signInWithCustomToken = async (customToken) => {
  // Server generates custom token using Firebase admin SDK
  const result = await signInWithCustomClaim(auth, customToken);
  return result.user;
};

// NEVER DO THIS:
// import { Auth0Provider } from '@auth0/auth0-react';
// export const setupAuth0 = () => {
//   // This breaks Firebase Auth integration
//   // User sessions managed by two different providers
// };
```

#### Adding to Existing Supabase Auth
```javascript
// EXISTING Supabase Auth setup
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.REACT_APP_SUPABASE_URL,
  process.env.REACT_APP_SUPABASE_ANON_KEY
);

// EXISTING session management
export const onAuthStateChange = (callback) => {
  return supabase.auth.onAuthStateChange((event, session) => {
    callback(session?.user);
  });
};

// EXISTING password-based auth
export const signUpWithEmail = async (email, password) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  });
  return data.user;
};

// NEW FEATURE: Add Magic Link auth (SAFE extension)
// Uses same Supabase Auth instance
export const signInWithMagicLink = async (email) => {
  const { data, error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: `${window.location.origin}/auth/callback`,
    },
  });
  return data;
};

// NEW FEATURE: Add GitHub OAuth (SAFE extension)
// Uses same Supabase Auth, OAuth configuration
export const signInWithGitHub = async () => {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'github',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
    },
  });
  return data;
};

// Key insight: All auth flows maintain Supabase session
// Token refresh handled transparently by Supabase
```

### 6.3 Session Management Preservation

#### Token Refresh Pattern
```javascript
// EXISTING Auth0 token management
import { useAuth0 } from '@auth0/auth0-react';

export const useAuthToken = () => {
  const { getAccessTokenSilently } = useAuth0();

  const getToken = async () => {
    try {
      // Auth0 handles token refresh automatically
      const token = await getAccessTokenSilently();
      return token;
    } catch (error) {
      // User must re-authenticate
      return null;
    }
  };

  return { getToken };
};

// EXISTING API call pattern with token
export const apiCall = async (endpoint, options = {}) => {
  const token = await getToken();

  const response = await fetch(endpoint, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  return response.json();
};

// NEW FEATURE: Add API request interceptor (SAFE extension)
// Maintains existing token refresh logic
export const setupApiInterceptor = () => {
  const { getAccessTokenSilently } = useAuth0();

  // Intercepts all fetch calls to add Auth0 token
  const originalFetch = window.fetch;

  window.fetch = async (...args) => {
    const [resource, config] = args;

    if (resource.includes('/api/')) {
      const token = await getAccessTokenSilently();
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }

    return originalFetch(resource, config);
  };
};

// Key principle: Token refresh logic unchanged
// All API calls use same authentication pattern
```

### 6.4 OAuth Flow Preservation

#### Protected Routes Pattern
```javascript
// EXISTING Clerk session-based routing
import { useAuth } from '@clerk/react';
import { useRouter } from 'next/router';

export const ProtectedRoute = ({ children }) => {
  const { isSignedIn, isLoaded } = useAuth();
  const router = useRouter();

  if (!isLoaded) return <Loading />;

  if (!isSignedIn) {
    router.push('/sign-in');
    return null;
  }

  return children;
};

// EXISTING OAuth provider configuration
// OAuth providers configured in Clerk dashboard
// Refresh tokens handled by Clerk automatically

// NEW FEATURE: Add role-based access control (SAFE extension)
// Uses same Clerk session, adds authorization layer
export const RoleProtectedRoute = ({ children, requiredRole }) => {
  const { isSignedIn, isLoaded } = useAuth();
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    if (isSignedIn) {
      // Fetch user role from database
      fetchUserRole().then(setUserRole);
    }
  }, [isSignedIn]);

  if (!isLoaded) return <Loading />;
  if (!isSignedIn) return router.push('/sign-in');
  if (userRole !== requiredRole) return <Unauthorized />;

  return children;
};

// NEW FEATURE: Add session timeout (SAFE extension)
// Works with Clerk's existing session management
export const useSessionTimeout = (timeoutMinutes = 30) => {
  const { signOut } = useAuth();
  const timeoutRef = useRef(null);

  const resetTimeout = useCallback(() => {
    clearTimeout(timeoutRef.current);

    timeoutRef.current = setTimeout(() => {
      signOut();
    }, timeoutMinutes * 60 * 1000);
  }, [signOut, timeoutMinutes]);

  useEffect(() => {
    // Existing Clerk session remains valid
    resetTimeout();

    window.addEventListener('mousemove', resetTimeout);
    return () => window.removeEventListener('mousemove', resetTimeout);
  }, [resetTimeout]);
};

// Key insight: Authorization layer on top of existing auth
// Token refresh continues to work transparently
```

### 6.5 Custom Claims and User Properties

#### Preserving Custom Claims
```javascript
// EXISTING Firebase custom claims
import { getAuth } from 'firebase/auth';
import { initializeApp } from 'firebase/app';

const auth = getAuth();

// EXISTING pattern: Custom claims set via admin SDK
// Only server can set custom claims
// Claims persist across sessions

export const useUserRole = () => {
  const [role, setRole] = useState(null);

  useEffect(() => {
    auth.onAuthStateChanged(async (user) => {
      if (user) {
        const idTokenResult = await user.getIdTokenResult();
        // Admin claim set server-side
        setRole(idTokenResult.claims.admin ? 'admin' : 'user');
      }
    });
  }, []);

  return role;
};

// NEW FEATURE: Add additional custom property (SAFE extension)
export const useUserOrganization = () => {
  const [organization, setOrganization] = useState(null);

  useEffect(() => {
    auth.onAuthStateChanged(async (user) => {
      if (user) {
        const idTokenResult = await user.getIdTokenResult();
        // Server adds organization claim same way as admin claim
        setOrganization(idTokenResult.claims.organization);
      }
    });
  }, []);

  return organization;
};

// NEW FEATURE: Add user profile data (SAFE extension)
// Separate from auth claims, stored in Firestore
export const useUserProfile = () => {
  const [profile, setProfile] = useState(null);
  const user = auth.currentUser;

  useEffect(() => {
    if (user) {
      // Query Firestore using same auth context
      const docRef = doc(firestore, 'users', user.uid);
      onSnapshot(docRef, (doc) => {
        setProfile(doc.data());
      });
    }
  }, [user]);

  return profile;
};

// Key principle: Custom claims immutable per session
// Additional data stored in database, not auth claims
```

### 6.6 Breakage Prevention Checklist

```
[ ] Identified existing auth provider (Firebase/Supabase/Auth0/Clerk)
[ ] Located auth credentials/keys in environment
[ ] Found existing session management pattern
[ ] Identified OAuth providers configured
[ ] Confirmed no competing auth provider exists
[ ] New auth flows use same provider instance
[ ] New OAuth providers added to existing configuration
[ ] Token refresh logic unchanged
[ ] Session state synchronized across features
[ ] Custom claims/metadata pattern maintained
[ ] No changes to authentication middleware
[ ] Protected routes use existing auth hook/pattern
[ ] CORS configuration unchanged for auth endpoints
```

---

## 7. Common Third-Party Integration Breakages

### 7.1 Multiple Analytics Providers

#### The Problem
```javascript
// DANGEROUS: Competing analytics providers
// App initializes both Google Analytics and Mixpanel

// In initialization.js
window.gtag = gtag;
mixpanel.init('token');

// Problem: Both track user behavior, but to different dashboards
// Team uses Google Analytics for reporting
// Mixpanel events go nowhere
// Revenue tracking splits between systems
// User identification inconsistent between systems
```

#### The Fix
```javascript
// SAFE: Single analytics provider with unified tracking
import { initializeAnalytics, trackEvent } from './analytics';

// Single configuration
const analyticsConfig = {
  provider: 'google_analytics',
  trackingId: process.env.REACT_APP_GA_ID,
};

// All events flow through single provider
export const trackPurchase = (amount) => {
  trackEvent('purchase', { value: amount });
  // Event appears in Google Analytics dashboard
};

export const trackSignup = (source) => {
  trackEvent('signup', { source });
  // Event appears in Google Analytics dashboard
};

// No competing Mixpanel.track() calls
```

### 7.2 Webhook Signature Verification Breaking

#### The Problem
```javascript
// EXISTING Stripe webhook verification
app.post('/api/webhooks/stripe', (req, res) => {
  const sig = req.headers['stripe-signature'];

  try {
    const event = stripe.webhooks.constructEvent(
      req.rawBody,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Process event
});

// DANGEROUS: Adding webhook without verification
app.post('/api/webhooks/custom-processor', (req, res) => {
  // Some payment processor sends webhook
  const event = req.body; // No signature verification!

  // This can accept forged events
  // Anyone can trigger fake payments
});
```

#### The Fix
```javascript
// SAFE: Extend existing verification pattern
app.post('/api/webhooks/stripe', (req, res) => {
  const sig = req.headers['stripe-signature'];

  // Existing verification
  const event = stripe.webhooks.constructEvent(
    req.rawBody,
    sig,
    process.env.STRIPE_WEBHOOK_SECRET
  );

  // Existing handlers
  switch (event.type) {
    case 'payment_intent.succeeded':
      handlePaymentSuccess(event);
      break;
    // NEW: Add handler without changing verification
    case 'customer.subscription.updated':
      handleSubscriptionUpdate(event);
      break;
  }

  res.json({ received: true });
});

// If adding new payment processor (use existing verification pattern)
app.post('/api/webhooks/payment-provider', (req, res) => {
  const sig = req.headers['x-payment-provider-signature'];

  // Verify signature from THIS provider
  if (!verifyPaymentProviderSignature(req.rawBody, sig)) {
    return res.status(400).send('Invalid signature');
  }

  const event = req.body;
  // Process event securely
});
```

### 7.3 Auth Flow Session State Loss

#### The Problem
```javascript
// EXISTING Auth0 setup
const auth0Config = {
  domain: process.env.REACT_APP_AUTH0_DOMAIN,
  clientId: process.env.REACT_APP_AUTH0_CLIENT_ID,
  redirectUri: window.location.origin + '/callback',
};

// EXISTING callback handler
const handleAuthCallback = async () => {
  const { appState } = await auth0.handleRedirectCallback();
  router.push(appState?.returnTo || '/');
};

// DANGEROUS: Changing auth flow without preserving state
// DEVELOPER ADDS: Different redirect URI
const loginWithAuth0 = () => {
  auth0.loginWithPopup({
    redirectUri: window.location.origin + '/auth/complete', // Changed!
  });
  // Callback expects /callback, but redirects to /auth/complete
  // Session state not recovered
  // appState lost
  // returnTo parameter forgotten
};
```

#### The Fix
```javascript
// SAFE: Preserve existing auth flow
const loginWithAuth0 = () => {
  // Uses existing config, callback location
  auth0.loginWithPopup();
};

// NEW FEATURE: Add social login (respects existing flow)
const loginWithGoogle = () => {
  // Same auth0 instance, same callback
  auth0.loginWithPopup({
    connection: 'google-oauth2',
  });
  // Callback at /callback still works
  // appState preserved
};

// NEW FEATURE: Add passwordless (respects existing flow)
const loginWithEmail = (email) => {
  // Same auth0 instance, same callback
  auth0.passwordlessStart({
    connection: 'email',
    email,
    send: 'link',
  });
  // Callback at /callback still works
};

// Key: Callback location, redirect URI, state preservation ALL unchanged
```

### 7.4 API Key Environment Variable Renames

#### The Problem
```javascript
// EXISTING configuration
const stripeKey = process.env.STRIPE_PUBLISHABLE_KEY;

// DANGEROUS: Renaming without updating everywhere
// Developer changes to:
const stripeKey = process.env.REACT_APP_STRIPE_PUBLIC_KEY;

// Problems:
// 1. Old environment variable no longer exists
// 2. Deployment still has STRIPE_PUBLISHABLE_KEY set
// 3. App cannot initialize Stripe
// 4. Payment forms fail
// 5. New environment variable never configured
```

#### The Fix
```javascript
// SAFE: Keep existing variable names
const stripeKey = process.env.STRIPE_PUBLISHABLE_KEY;

// If renaming is necessary:
// 1. Set BOTH old and new environment variables
// 2. Read from both, prefer new
const stripeKey = process.env.REACT_APP_STRIPE_PUBLIC_KEY ||
                  process.env.STRIPE_PUBLISHABLE_KEY;

// 3. Deploy with both variables set
// 4. After verifying new var works, deprecate old one

// BETTER: Use existing variable names
// Keep environment configuration stable
```

### 7.5 CORS Configuration Breaking

#### The Problem
```javascript
// EXISTING CORS configuration
app.use(cors({
  origin: ['https://app.example.com', 'https://admin.example.com'],
  credentials: true,
}));

// EXISTING payment service makes cross-origin API calls
// https://api.stripe.com/v1/payment_intents - ALLOWED

// DANGEROUS: Adding new feature with different API domain
// NEW FEATURE: Integrate Shopify for inventory
// https://api.shopify.com/graphql.json - NOT in CORS allowlist

// Problem:
// Browser blocks Shopify API calls
// Inventory feature fails silently
// CORS policy error in console
```

#### The Fix
```javascript
// SAFE: Extend CORS allowlist
app.use(cors({
  origin: [
    'https://app.example.com',
    'https://admin.example.com',
    'https://api.shopify.com', // NEW: Add new API domain
  ],
  credentials: true,
}));

// OR BETTER: Use backend API proxy
// Frontend calls /api/shopify/* endpoints
// Backend makes request to Shopify
// No frontend CORS issues

app.get('/api/shopify/inventory', async (req, res) => {
  // Backend handles CORS with Shopify API
  const inventory = await shopifyClient.request(...);
  res.json(inventory);
});

// Key: Either extend allowlist or use backend proxy
// Don't break existing CORS configuration
```

### 7.6 Middleware Order Affecting Integrations

#### The Problem
```javascript
// EXISTING middleware order (CORRECT)
app.use(express.json());
app.use(requestLogger);
app.use(authenticateUser);
app.use(Sentry.Handlers.requestHandler()); // Error monitor BEFORE routes
app.use('/api', apiRoutes);
app.use(errorHandler);
app.use(Sentry.Handlers.errorHandler()); // Error monitor AFTER routes

// This order is important:
// 1. Sentry can capture errors from all routes
// 2. Error handler cleans up
// 3. Sentry logs final errors

// DANGEROUS: Adding middleware in wrong place
app.use(express.json());
app.use(requestLogger);
app.use(authenticateUser);
app.use('/api', apiRoutes);
app.use(Sentry.Handlers.requestHandler()); // WRONG POSITION!
app.use(errorHandler);

// Problems:
// 1. Sentry doesn't wrap routes
// 2. Errors in routes not captured by Sentry
// 3. Error context missing
```

#### The Fix
```javascript
// SAFE: Middleware order preserved
app.use(express.json());
app.use(requestLogger);
app.use(authenticateUser);

// Error monitoring BEFORE routes
app.use(Sentry.Handlers.requestHandler());

// Application routes
app.use('/api', apiRoutes);

// Error monitoring AFTER routes
app.use(Sentry.Handlers.errorHandler());

// Global error handler
app.use(errorHandler);

// Key: Never change error monitoring middleware order
```

---

## 8. Detection and Prevention Workflow

### 8.1 Pre-Implementation Checklist

Before adding any third-party integration feature:

```
STEP 1: Identify Existing Services
[ ] Search codebase for known integration patterns
[ ] Check environment variables for API keys
[ ] Look in package.json for SDKs
[ ] Check for configuration files (.env, config.js)
[ ] Search for API endpoints and library imports

STEP 2: Map Current Integration
[ ] Document existing service (provider, version)
[ ] Find all places where service is used
[ ] Identify environment variables needed
[ ] Check webhook endpoints and handlers
[ ] Map user-facing features using this service

STEP 3: Plan Feature Extension
[ ] Determine if feature extends existing service
[ ] Check if new service would conflict
[ ] Plan using existing service instance
[ ] Identify necessary configuration additions
[ ] Plan webhook/event handler extensions

STEP 4: Validate No Competing Services
[ ] Search for alternative service libraries
[ ] Check for competing API keys in environment
[ ] Search for competing initialization code
[ ] Verify no duplicate webhook endpoints
[ ] Confirm single provider per concern

STEP 5: Implement With Existing Patterns
[ ] Use existing service instance
[ ] Follow existing code patterns
[ ] Extend existing handlers/webhooks
[ ] Add configuration following existing style
[ ] Test with existing authentication/environment
```

### 8.2 Code Review Questions

When reviewing code that touches third-party integrations:

```
INTEGRATION REVIEW CHECKLIST:

[ ] Is this feature using an existing third-party service?
[ ] If yes, did the code use the existing instance?
[ ] If adding new service, did it check for existing equivalent?
[ ] Are there multiple competing services in codebase?
[ ] Are environment variables following existing pattern?
[ ] Are webhook handlers extending existing endpoints?
[ ] Are authentication flows preserving session state?
[ ] Are middleware/configuration order changes justified?
[ ] Are CORS/security settings being modified?
[ ] Is this change isolated to intended feature?
[ ] Are existing integrations still functional?
[ ] Would a developer reading this know how the service is used?
```

### 8.3 Testing Third-Party Integration Safety

```javascript
// Test 1: Verify existing service still works
describe('Payment Integration', () => {
  it('should process payment with existing Stripe', async () => {
    const result = await processPayment(100, 'card_token');
    expect(result.status).toBe('succeeded');
  });

  it('should use same Stripe instance for subscriptions', () => {
    // Confirm subscription uses same instance as payments
    expect(getActiveStripeInstance()).toBe(stripeInstance);
  });
});

// Test 2: Verify no competing services initialized
describe('Analytics Integrity', () => {
  it('should only initialize Google Analytics', () => {
    expect(window.gtag).toBeDefined();
    expect(window.mixpanel).toBeUndefined();
    expect(window.amplitude).toBeUndefined();
  });

  it('should not have competing analytics API keys', () => {
    expect(process.env.REACT_APP_GA_ID).toBeDefined();
    expect(process.env.REACT_APP_MIXPANEL_TOKEN).toBeUndefined();
  });
});

// Test 3: Verify webhook signatures still validate
describe('Webhook Security', () => {
  it('should reject webhook without valid signature', async () => {
    const response = await fetch('/api/webhooks/stripe', {
      method: 'POST',
      body: JSON.stringify({ type: 'payment_intent.succeeded' }),
      headers: { 'stripe-signature': 'invalid' },
    });
    expect(response.status).toBe(400);
  });

  it('should accept webhook with valid signature', async () => {
    const sig = generateValidStripeSig(testEvent);
    const response = await fetch('/api/webhooks/stripe', {
      method: 'POST',
      body: JSON.stringify(testEvent),
      headers: { 'stripe-signature': sig },
    });
    expect(response.status).toBe(200);
  });
});

// Test 4: Verify authentication session preserved
describe('Auth Session Integrity', () => {
  it('should maintain session across new auth features', async () => {
    const session1 = await auth.getSession();
    // Add new OAuth provider
    const session2 = await auth.getSession();
    expect(session1.userId).toBe(session2.userId);
  });

  it('should not initialize competing auth provider', () => {
    expect(auth0 instanceof Auth0).toBe(true);
    expect(window.Clerk).toBeUndefined();
  });
});
```

---

## 9. Reference: Service Detection Quick Guide

### 9.1 File Patterns to Search

```bash
# Find payment integration
grep -r "stripe\|razorpay\|paypal" . --include="*.js" --include="*.ts"
grep -r "STRIPE\|RAZORPAY\|PAYPAL" .env* | head -20

# Find email service
grep -r "sendgrid\|mailgun\|ses\|resend" . --include="*.js" --include="*.ts"
grep -r "SENDGRID\|MAILGUN\|SES\|RESEND" .env* | head -20

# Find analytics
grep -r "gtag\|mixpanel\|amplitude" . --include="*.js" --include="*.ts"
grep -r "GA_ID\|MIXPANEL\|AMPLITUDE" .env* | head -20

# Find error monitoring
grep -r "sentry\|logrocket\|bugsnag" . --include="*.js" --include="*.ts"
grep -r "SENTRY\|LOGROCKET\|BUGSNAG" .env* | head -20

# Find storage
grep -r "firebase\|supabase\|s3\|cloudinary" . --include="*.js" --include="*.ts"
grep -r "FIREBASE\|SUPABASE\|S3\|CLOUDINARY" .env* | head -20

# Find auth
grep -r "firebase.*auth\|supabase.*auth\|auth0\|clerk" . --include="*.js" --include="*.ts"
grep -r "FIREBASE\|SUPABASE\|AUTH0\|CLERK" .env* | head -20
```

### 9.2 Environment File Patterns

```bash
# Search .env files for all API keys
grep -r "API_KEY\|SECRET\|DOMAIN\|ID" .env* | sort | uniq

# Identify API key providers by pattern
grep "_KEY\|_SECRET\|_ID" .env* | sed 's/=.*//' | sort

# Find webhook secrets
grep -r "WEBHOOK" .env* | head -20
```

### 9.3 Package.json Indicators

```bash
# Find integration libraries
npm list | grep -E "stripe|razorpay|sendgrid|mailgun|aws-sdk|firebase|auth0|clerk|sentry|mixpanel|amplitude"

# Search in package.json directly
cat package.json | grep -E '"(stripe|razorpay|sendgrid|mailgun|aws-sdk|firebase|auth0|clerk|sentry|mixpanel|amplitude)'
```

---

## 10. Conclusion and Key Principles

### The Golden Rule

**Detect the existing service pattern, extend using that pattern, never add competing alternatives.**

### Core Principles

1. **One Service Per Concern**: One payment gateway, one email service, one analytics platform
2. **Detect Before Building**: Always search for existing integrations first
3. **Extend, Don't Replace**: Use existing instances and patterns
4. **Preserve Configuration**: Keep environment variables, API keys, and settings stable
5. **Maintain Webhook Contracts**: Don't change webhook endpoints or signatures
6. **Respect Session State**: Authentication and authorization logic stays intact
7. **Document Integration Points**: Make it easy for next developer to find all uses

### Dangerous Patterns to Avoid

- Adding competing service (second payment gateway, analytics platform)
- Changing environment variable names
- Moving middleware that affects integrations
- Modifying webhook endpoints
- Breaking OAuth/session flow
- Changing CORS configuration without justification
- Renaming API routes used by integrations
- Removing integration endpoints

### Safe Patterns to Follow

- Extend existing service with new features
- Add new functionality using existing SDKs
- Follow existing code patterns and conventions
- Add configuration following existing style
- Extend existing handlers/webhooks
- Maintain backward compatibility
- Test existing functionality after changes
- Document why integration was chosen

---

**Last Updated**: February 2026
**For**: workflow-guardian skill
**Scope**: Third-party integration preservation patterns
