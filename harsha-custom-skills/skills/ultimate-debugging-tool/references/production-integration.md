# Production Integration and Monitoring

Connecting development debugging with production monitoring to identify, prioritize, and fix issues before users report them.

## 1. Error Tracking Setup

### Sentry for React/Next.js

Install and configure error tracking with source maps:

```bash
npm install @sentry/react @sentry/nextjs @sentry/tracing
```

**Next.js Configuration** (sentry.client.config.ts):
```typescript
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,

  beforeSend(event, hint) {
    // Filter out noisy errors
    if (event.exception) {
      const error = hint.originalException;

      if (error instanceof Error) {
        // Ignore chunk load errors (already handled by chunk retry)
        if (error.message.includes('Failed to import')) return null;

        // Ignore network timeouts (out of our control)
        if (error.message.includes('timeout')) return null;

        // Ignore user cancellations
        if (error.name === 'AbortError') return null;
      }
    }

    return event;
  },

  integrations: [
    new Sentry.Replay({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],

  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

export default Sentry;
```

**Error Boundary with Context**:
```typescript
import * as Sentry from '@sentry/react';
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/context/auth';

export const ErrorBoundaryFallback = ({ error, resetError }) => {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Capture error context in Sentry
    Sentry.withScope((scope) => {
      scope.setContext('error_boundary', {
        route: router.pathname,
        userId: user?.id,
        timestamp: new Date().toISOString(),
      });

      scope.setTag('error_type', 'error_boundary');
      Sentry.captureException(error);
    });
  }, [error, user?.id, router.pathname]);

  return (
    <div className="error-container">
      <h1>Something went wrong</h1>
      <p>We've been notified and are working on a fix.</p>
      <button onClick={resetError}>Try again</button>
      <details>
        <summary>Error details</summary>
        <pre>{error?.message}</pre>
      </details>
    </div>
  );
};

export const withErrorBoundary = (Component) => {
  const Wrapped = Sentry.withErrorBoundary(Component, {
    fallback: ErrorBoundaryFallback,
    showDialog: false,
  });

  return Wrapped;
};
```

**Sentry in App Router** (app/layout.tsx):
```typescript
import { ReactNode } from 'react';
import * as Sentry from '@sentry/nextjs';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        {/* Source map upload metadata */}
        <meta property="sentry:dsn" content={process.env.NEXT_PUBLIC_SENTRY_DSN} />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
```

### Custom Error Context

```typescript
// hooks/useErrorContext.ts
import * as Sentry from '@sentry/react';
import { useCallback } from 'react';

export const useErrorContext = () => {
  const captureError = useCallback((error: Error, context: Record<string, any>) => {
    Sentry.withScope((scope) => {
      Object.entries(context).forEach(([key, value]) => {
        scope.setContext(key, value);
      });

      Sentry.captureException(error);
    });
  }, []);

  return { captureError };
};

// Usage in component:
const { captureError } = useErrorContext();

try {
  await saveFormData(data);
} catch (error) {
  captureError(error as Error, {
    form: {
      name: 'user-settings',
      fields: Object.keys(data),
      data: JSON.stringify(data),
    },
    user: {
      id: user.id,
      email: user.email,
    },
    timing: {
      duration: Date.now() - startTime,
    },
  });
}
```

## 2. Performance Monitoring

### Web Vitals Library

Install and track Core Web Vitals:

```bash
npm install web-vitals
```

**Next.js Integration** (pages/_app.tsx or app/layout.tsx):
```typescript
import { useEffect } from 'react';
import { getCLS, getCWV, getFCP, getLCP, getTTFB, getINP } from 'web-vitals';
import * as Sentry from '@sentry/react';

function reportWebVital(metric) {
  console.log(metric);

  // Send to Sentry
  Sentry.captureMessage(`Web Vital: ${metric.name}`, {
    level: 'info',
    contexts: {
      trace: {
        op: 'web_vital',
        description: `${metric.name}: ${metric.value.toFixed(2)}`,
      },
    },
    measurements: {
      [metric.name.toLowerCase()]: {
        value: metric.value,
        unit: metric.unit,
      },
    },
  });

  // Send to analytics endpoint
  sendToAnalytics(metric);
}

export function WebVitalsProvider() {
  useEffect(() => {
    getCLS(reportWebVital);
    getFCP(reportWebVital);
    getLCP(reportWebVital);
    getTTFB(reportWebVital);
    getINP(reportWebVital);
  }, []);

  return null;
}
```

### Custom Performance Marks

```typescript
// hooks/usePerformanceMark.ts
import { useEffect } from 'react';

export const usePerformanceMark = (name: string, options?: PerformanceMarkOptions) => {
  useEffect(() => {
    const markName = `${name}-start`;
    performance.mark(markName, options);

    return () => {
      const endMarkName = `${name}-end`;
      performance.mark(endMarkName);

      try {
        performance.measure(name, markName, endMarkName);

        const measure = performance.getEntriesByName(name)[0] as PerformanceMeasure;
        console.log(`${name}: ${measure.duration.toFixed(2)}ms`);

        // Send to analytics
        sendMetric(name, measure.duration);
      } catch (error) {
        console.error(`Failed to measure ${name}:`, error);
      }
    };
  }, [name]);
};

// Usage:
export const ProductListing = () => {
  usePerformanceMark('product-listing-render');

  return <div>{/* content */}</div>;
};
```

### Analytics Integration

```typescript
// services/analytics.ts
export const sendMetric = (name: string, value: number, tags?: Record<string, string>) => {
  // Google Analytics 4
  if (window.gtag) {
    window.gtag('event', 'performance_metric', {
      metric_name: name,
      metric_value: value,
      ...tags,
    });
  }

  // Custom analytics endpoint
  navigator.sendBeacon('/api/metrics', JSON.stringify({
    metric: name,
    value,
    timestamp: Date.now(),
    url: window.location.href,
    userAgent: navigator.userAgent,
    tags,
  }));
};

export const sendToAnalytics = (metric) => {
  const body = JSON.stringify({
    name: metric.name,
    delta: metric.delta,
    value: metric.value,
    id: metric.id,
    navigationType: metric.navigationType,
    rating: metric.rating,
  });

  // Use sendBeacon to ensure delivery even on page unload
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/web-vitals', body);
  } else {
    fetch('/api/web-vitals', { body, method: 'POST', keepalive: true });
  }
};
```

## 3. CI/CD Performance Gates

### Lighthouse CI Configuration

**GitHub Actions Workflow** (.github/workflows/lighthouse.yml):
```yaml
name: Lighthouse CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - run: npm ci
      - run: npm run build
      - run: npm run start &
      - run: npx wait-on http://localhost:3000

      - uses: treosh/lighthouse-ci-action@v9
        with:
          configPath: './lighthouserc.json'
          uploadArtifacts: true
          temporaryPublicStorage: true
```

**Lighthouse Config** (lighthouserc.json):
```json
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:3000/",
        "http://localhost:3000/products",
        "http://localhost:3000/checkout"
      ],
      "numberOfRuns": 3,
      "settings": {
        "configPath": "./lighthouse-config.js",
        "chromeFlags": "--disable-gpu"
      }
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.85 }],
        "categories:best-practices": ["error", { "minScore": 0.85 }],
        "categories:seo": ["error", { "minScore": 0.9 }],
        "first-contentful-paint": ["error", { "maxNumericValue": 2000 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 3000 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "interaction-to-next-paint": ["error", { "maxNumericValue": 200 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

### Bundle Size Checks

**size-limit Configuration** (.size-limit.json):
```json
[
  {
    "path": "dist/index.js",
    "limit": "50 KB",
    "gzip": true
  },
  {
    "path": "dist/vendor.js",
    "limit": "200 KB",
    "gzip": true
  },
  {
    "path": "node_modules/react/index.js",
    "limit": "50 KB",
    "import": "{ useState, useEffect }"
  }
]
```

**GitHub Actions** (.github/workflows/size.yml):
```yaml
name: Bundle Size Check

on: [pull_request]

jobs:
  size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: andresz1/size-limit-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

### TypeScript and ESLint as CI Requirements

**package.json scripts**:
```json
{
  "scripts": {
    "type-check": "tsc --noEmit",
    "lint": "eslint . --max-warnings=0",
    "ci:check": "npm run type-check && npm run lint && npm run test -- --coverage"
  }
}
```

**GitHub Actions** (.github/workflows/quality.yml):
```yaml
name: Code Quality

on: [pull_request, push]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - run: npm ci

      - name: Type Check
        run: npm run type-check

      - name: Lint
        run: npm run lint

      - name: Tests
        run: npm run test -- --coverage

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

## 4. Debugging Production Issues

### Source Map Upload

**Sentry Release Management**:
```bash
# Install Sentry CLI
npm install -D @sentry/cli

# Create release
SENTRY_AUTH_TOKEN=<token> npx sentry-cli releases create -p <project> <version>

# Upload source maps
SENTRY_AUTH_TOKEN=<token> npx sentry-cli releases files <version> upload-sourcemaps dist

# Finalize release
SENTRY_AUTH_TOKEN=<token> npx sentry-cli releases finalize <version>
```

**Automated in Build** (package.json):
```json
{
  "scripts": {
    "build": "next build",
    "upload-sourcemaps": "sentry-cli releases files $npm_package_version upload-sourcemaps dist",
    "release": "npm run build && npm run upload-sourcemaps"
  }
}
```

### Session Replay Configuration

```typescript
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  // ... other config

  integrations: [
    new Sentry.Replay({
      maskAllText: true,
      blockAllMedia: true,
      maskAllInputs: true,
    }),
  ],

  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

### Feature Flags for Safe Deployment

**LaunchDarkly Integration**:
```bash
npm install launchdarkly-js-client-sdk
```

```typescript
// lib/featureFlags.ts
import * as LaunchDarkly from 'launchdarkly-js-client-sdk';

const client = LaunchDarkly.initialize(
  process.env.NEXT_PUBLIC_LD_CLIENT_ID,
  {
    key: user.id,
    email: user.email,
    custom: {
      organization: user.orgId,
    },
  }
);

export const useFeatureFlag = (flagKey: string, defaultValue: boolean = false) => {
  const [value, setValue] = useState(defaultValue);

  useEffect(() => {
    client.on('ready', () => {
      setValue(client.variation(flagKey, defaultValue));
    });

    client.on(`change:${flagKey}`, (current) => {
      setValue(current);
    });
  }, [flagKey]);

  return value;
};

// Usage:
export const CheckoutFlow = () => {
  const useNewPaymentProcessor = useFeatureFlag('new-payment-processor', false);

  return (
    <div>
      {useNewPaymentProcessor ? <NewPaymentUI /> : <LegacyPaymentUI />}
    </div>
  );
};
```

### Canary Releases

**Deployment Strategy** (.github/workflows/deploy.yml):
```yaml
name: Canary Deploy

on:
  workflow_dispatch:
    inputs:
      percentage:
        description: 'Percentage of traffic to canary'
        required: true
        default: '5'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build
        run: npm run build

      - name: Deploy to Staging
        run: vercel deploy --prod

      - name: Route Canary Traffic
        run: |
          kubectl patch service app -p '{"spec":{"selector":{"version":"canary"}}}'
          kubectl set replicas deployment/app-canary=1

      - name: Monitor Metrics
        run: |
          npm run monitor-canary -- --duration=10m --threshold=5

      - name: Approve and Deploy
        if: success()
        run: |
          kubectl set replicas deployment/app-canary=10
          kubectl set replicas deployment/app=0
```

## 5. Feedback Loop

### Production Issues → Debugging Priorities

```typescript
// Example: Alert on error spike
const monitorErrorRate = async () => {
  const errors = await Sentry.captureException({
    query: {
      statsPeriod: '24h',
      query: 'is:unresolved',
    },
  });

  const errorRate = errors.length / totalRequests;

  if (errorRate > 0.05) { // 5% threshold
    // Trigger alert
    await notifyTeam({
      level: 'critical',
      message: `Error rate spiked to ${(errorRate * 100).toFixed(2)}%`,
      errors: errors.slice(0, 10),
    });
  }
};
```

### Performance Metrics → Optimization Priorities

```typescript
// Example: Alert on performance regression
const checkPerformanceRegression = async () => {
  const metrics = await fetch('/api/metrics/historical').then(r => r.json());

  const today = metrics[metrics.length - 1];
  const average = metrics.slice(-7).reduce((sum, m) => sum + m.lcp, 0) / 7;

  if (today.lcp > average * 1.2) { // 20% regression
    notifyTeam({
      level: 'warning',
      message: `LCP regression detected: ${today.lcp}ms (avg: ${average}ms)`,
      metrics: today,
    });
  }
};
```

### User Reports → Reproduction Steps

```typescript
// Store user context for bug reports
export const captureUserReport = async (message: string) => {
  const session = await Sentry.captureMessage(message, 'error');

  Sentry.withScope((scope) => {
    scope.setContext('user_report', {
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      memory: performance.memory,
      navigation: performance.getEntriesByType('navigation')[0],
    });

    scope.setTag('source', 'user_report');
    Sentry.captureException(new Error(message));
  });

  return session.id;
};
```

### Postmortem → Prevention Rules

```typescript
// Example: Auto-alert on patterns discovered in postmortem
const addPreventionRule = (pattern: string, response: string) => {
  // Add to error filter
  Sentry.init({
    beforeSend(event) {
      if (event.exception?.values[0]?.value?.includes(pattern)) {
        notifyTeam({
          level: 'critical',
          pattern,
          resolution: response,
        });
      }
    },
  });
};

// Usage
addPreventionRule(
  'ChunkLoadError',
  'User should see "page unresponsive" notice with reload button'
);
```

## Summary

A complete production monitoring setup includes:
1. Error tracking with context (Sentry)
2. Performance monitoring (Web Vitals)
3. CI/CD gates (Lighthouse, bundle size, quality checks)
4. Safe deployments (feature flags, canary releases)
5. Feedback loops (errors → priorities → prevention)

This creates a virtuous cycle where production issues inform development, and quality gates prevent regressions before they reach users.
