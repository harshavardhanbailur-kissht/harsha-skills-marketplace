# Notification & Performance Psychology Reference

## Notification Psychology

### Volume & Frequency Research

**Daily notification volume:**
- Average: 46 notifications/day (2023 data)
- Power users: 80-100+ notifications/day
- Optimal frequency for marketing: ≤3/week
- Each additional notification beyond threshold: diminishing engagement

**Attention Economics:**
- Average time on single screen: 47 seconds
- Refocus time after interruption: ~23 minutes (Mark et al.)
- Transient cognitive disruption: ~7 seconds slowdown
- Each reminder beyond optimal: 30% attention drop

### Timing & Context Research

**Intelligent Timing (Yahoo! Japan Study):**
- Context-aware delivery: 49.7% response improvement
- Breakout phone usage detection improves delivery
- Machine learning timing outperforms fixed schedules

**Opt-in Rates by Platform:**
- iOS (requires explicit permission): 51%
- Android 13+ (explicit permission): 67%
- Pre-permission prompts: 65% opt-in vs 25-35% baseline
- Explanation of value before permission: significant improvement

**Timing Factors:**
- Time of day matters: work hours vs personal time
- Day of week effects: weekday vs weekend patterns
- User state detection: active vs idle
- Location context: home, work, commute

### Alert Fatigue Research

**Healthcare Alert Fatigue (Clinical Decision Support):**
- Median alerts/day: 63
- Clinicians reporting excessive alerts: 86.9%
- Override rates for medication alerts: 90%
- False alarm rates: 72-99%

**Security Alert Fatigue:**
- False positive rates: 52% (typical security systems)
- Alert volume leading to dismissal without review
- Cry wolf effect: ignoring legitimate alerts

**Mitigation Strategies:**
- Tiered alert severity (only critical interrupt)
- Aggregation and batching
- Personalized thresholds
- Smart suppression during focus time

### Notification Design Patterns

**Effective Notification Anatomy:**
- Clear source identification
- Actionable content
- Appropriate urgency signaling
- Easy dismissal/management

**Anti-Patterns:**
- Fake urgency (crying wolf)
- Manipulative timing (re-engagement dark pattern)
- Permission nagging
- Notification spam

---

## Performance Perception Psychology

### Response Time Thresholds (Miller, Card, Nielsen)

**Perceptual boundaries:**
| Threshold | Perception | Design Implication |
|-----------|------------|-------------------|
| 100ms | Instantaneous | Direct manipulation feels connected |
| 200ms | Slight delay | Noticeable but acceptable |
| 1 second | Flow maintained | System working, attention held |
| 10 seconds | Attention limit | Need feedback or user leaves |

**Business Impact Research:**

**Vodafone Study:**
- LCP improvement: 31% faster
- Result: 8% sales increase

**Lazada (Alibaba) Study:**
- LCP improvement: 3× faster
- Result: 16.9% mobile conversion increase

**Akamai/SOASTA Study (N=10 billion visits):**
- 100ms delay = 7% conversion reduction
- Peak conversion at 1.8s load time
- Mobile abandonment: 53% at >3s load

**Amazon Internal Research:**
- 100ms added latency = 1% revenue loss
- At Amazon's scale: billions in impact

### Progress Indication Psychology

**Progress Bar Perception (Harrison et al., CHI 2010):**

**Backwards-moving ribbing effect:**
- Reduces perceived duration: 11%
- Creates illusion of faster completion
- Works through motion perception mechanisms

**Pulsation effects:**
- Accelerating pulsation: perceived faster
- Decelerating pulsation: perceived slower

**Progress Rate Perception:**
- Fast-to-slow progress: 11.3% breakoff (best)
- Slow-to-fast progress: 21.8% breakoff (worst)
- Constant progress: middle performance
- Statistical significance: χ²(3)=31.57, p<0.001

**Design Implications:**
- Front-load apparent progress
- Use non-linear progress mapping
- Show task breakdown for long operations

### Loading State Techniques

**Skeleton Screens Research (Mejtoft et al., 2018):**
- Higher perceived speed (subjective)
- BUT: users actually slower at task completion
- Cognitive load of parsing skeleton structure
- Best for: familiar layouts, repeated visits

**Optimistic UI Pattern:**
- Immediate state update before server confirmation
- Appropriate for: >99% success rate operations
- Requires: graceful rollback mechanism
- Risk: user confusion if operation fails

**Spinner vs Progress Bar:**
- Indeterminate spinner: acceptable <4 seconds
- Progress bar: required >4 seconds
- Percentage indicator: helpful for long operations

### Frame Rate Perception

**Motion Perception Thresholds:**
| Frame Rate | Perception |
|------------|------------|
| 14fps | Continuous motion threshold |
| 24fps | Cinema standard (motion blur compensates) |
| 30fps | Acceptable for most UI |
| 60fps | Gold standard, smooth |
| 90fps | Diminishing returns begin |
| 120fps+ | Minimal perceptible improvement |

**Critical Insight:**
- Consistency matters MORE than absolute rate
- 55fps consistent > 60fps with drops to 45fps
- Frame drops cause perception of "jank"

**Animation Duration Guidelines:**
- Enter animations: 200-300ms
- Exit animations: 150-200ms (faster feels responsive)
- State changes: 100-200ms
- Page transitions: 300-500ms

### Core Web Vitals Impact

**Largest Contentful Paint (LCP):**
- Good: ≤2.5s
- Needs improvement: 2.5-4.0s
- Poor: >4.0s

**First Input Delay (FID) / Interaction to Next Paint (INP):**
- Good: ≤100ms / ≤200ms
- Needs improvement: 100-300ms / 200-500ms
- Poor: >300ms / >500ms

**Cumulative Layout Shift (CLS):**
- Good: ≤0.1
- Needs improvement: 0.1-0.25
- Poor: >0.25

**Business Correlation:**
- Sites meeting all Core Web Vitals: 24% less abandonment
- CLS improvements: significant conversion impact
- LCP most correlated with user satisfaction

---

## Interruption & Focus Psychology

### Context Switching Costs

**Attention Residue (Leroy, 2009):**
- Part of attention remains on previous task
- Reduces performance on current task
- Auto-save with state indicators helps

**Task Switching Research:**
- Heavy media multitaskers: 0.5s longer to refocus (Ophir et al., 2009)
- Cost increases with task complexity
- Cost increases with interruption duration

### Focus Protection Patterns

**Do Not Disturb Intelligence:**
- Activity detection (meetings, focused work)
- Time-based scheduling
- Priority breakthrough for emergencies
- Cross-device coordination

**Notification Batching:**
- Aggregate low-priority notifications
- Deliver at natural breakpoints
- User-controllable batch frequency

**Focus Mode Design:**
- Clear entry/exit
- Visible status indicator
- Automated (contextual) activation option
- Appropriate exception handling

---

## Code Detection Patterns

### Notification Implementation Signals

**Permission Request Timing:**
```javascript
// POOR: Immediate on page load
window.onload = () => Notification.requestPermission();

// BETTER: After user action showing value
subscribeButton.onclick = async () => {
  const permission = await Notification.requestPermission();
  // Contextual request after demonstrated intent
};
```

**Notification Frequency Control:**
```javascript
// Look for rate limiting
const NOTIFICATION_COOLDOWN = 4 * 60 * 60 * 1000; // 4 hours
const lastNotification = localStorage.get('lastNotification');
if (Date.now() - lastNotification > NOTIFICATION_COOLDOWN) {
  // Send notification
}

// Look for batching
const pendingNotifications = [];
const batchAndSend = debounce(() => {
  // Aggregate and send
}, 30000);
```

### Loading State Signals

**Skeleton Screen Implementation:**
```jsx
// Check for skeleton components
<div className="skeleton-loader">
  <div className="skeleton-text" />
  <div className="skeleton-image" />
</div>

// CSS pulse animation for skeletons
.skeleton {
  animation: pulse 1.5s ease-in-out infinite;
}
```

**Progress Indication:**
```javascript
// Check progress calculation method
// LINEAR (less optimal):
const progress = completed / total * 100;

// NON-LINEAR (better perceived speed):
const progress = Math.sqrt(completed / total) * 100;
// Or: easeOutQuad for front-loaded progress
```

**Optimistic Updates:**
```javascript
// React Query / TanStack optimistic update pattern
useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries(['todos']);
    // Snapshot previous value
    const previous = queryClient.getQueryData(['todos']);
    // Optimistically update
    queryClient.setQueryData(['todos'], (old) => [...old, newTodo]);
    return { previous };
  },
  onError: (err, newTodo, context) => {
    // Rollback on error
    queryClient.setQueryData(['todos'], context.previous);
  },
});
```

### Performance Monitoring Signals

**Core Web Vitals Tracking:**
```javascript
// web-vitals library usage
import { getLCP, getFID, getCLS, getINP } from 'web-vitals';

getLCP(console.log);
getFID(console.log);
getCLS(console.log);
getINP(console.log);
```

**Resource Loading Optimization:**
```html
<!-- Preload critical resources -->
<link rel="preload" href="critical.css" as="style">
<link rel="preconnect" href="https://api.example.com">

<!-- Lazy load non-critical -->
<img loading="lazy" src="below-fold.jpg">
```

---

## Research Gaps & Future Directions

**Under-researched areas:**
1. Notification fatigue recovery time
2. Cross-device notification coordination effects
3. AI-personalized notification timing optimization
4. Long-term effects of skeleton screens on user expectations
5. Cultural differences in interruption tolerance

**Emerging considerations:**
- Always-on displays and ambient notifications
- Wearable notification optimization
- Voice-first notification delivery
- Attention-aware adaptive interfaces

---

## Key Takeaways for Code Analysis

1. **Check notification permission timing** - should be contextual, not immediate
2. **Look for rate limiting/batching** - absent = potential fatigue generator
3. **Verify loading state implementations** - skeleton screens need familiar layouts
4. **Check progress bar calculations** - non-linear perceived as faster
5. **Look for Core Web Vitals monitoring** - absence suggests performance blind spot
6. **Verify animation durations** - outside 100-500ms range needs justification
7. **Check for optimistic UI patterns** - high-success operations should use them
