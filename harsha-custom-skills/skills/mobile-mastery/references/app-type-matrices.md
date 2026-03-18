# Mobile App Type Priority Matrices

Domain-specific weighted priority matrices for mobile app development, modeled after ui-ux-mastery domain matrices. Each app type includes critical patterns, metrics, pitfalls, and architecture recommendations.

---

## Table of Contents

- [Domain Detection Function](#domain-detection-function)
- [Universal Conflict Resolution Hierarchy](#universal-conflict-resolution-hierarchy)
- [1. Social/Community App](#1-socialcommunity-app)
- [2. Fintech/Banking App](#2-fintechbanking-app)
- [3. Healthcare/Medical App](#3-healthcaremedical-app)
- [4. E-Commerce/Marketplace App](#4-e-commercemarketplace-app)
- [5. Media/Streaming App](#5-mediastreaming-app)
- [6. Enterprise/B2B App](#6-enterpriseb2b-app)
- [7. Education/EdTech App](#7-educationedtech-app)
- [8. Gaming (Casual) App](#8-gaming-casual-app)
- [9. IoT/Smart Home App](#9-iotsmart-home-app)
- [10. Super App / Multi-Service](#10-super-app--multi-service)
- [Cross-Domain Patterns (Apply to ALL App Types)](#cross-domain-patterns-apply-to-all-app-types)
- [Implementation Checklist](#implementation-checklist)
- [References & Further Reading](#references--further-reading)

## Domain Detection Function

```python
def detect_app_domain(user_description: str) -> str:
    """
    Identify app type from user description using keyword matching and heuristics.
    Returns primary domain classification.
    """
    description = user_description.lower()

    # Domain keyword mappings with weights
    domains = {
        'social_community': {
            'keywords': ['feed', 'timeline', 'social', 'community', 'friends',
                        'followers', 'posts', 'likes', 'comments', 'engagement'],
            'weight': 0.0
        },
        'fintech_banking': {
            'keywords': ['bank', 'payment', 'transfer', 'wallet', 'crypto',
                        'investment', 'stock', 'security', 'compliance', 'fraud'],
            'weight': 0.0
        },
        'healthcare_medical': {
            'keywords': ['health', 'medical', 'doctor', 'patient', 'diagnosis',
                        'prescription', 'clinical', 'hipaa', 'wellness', 'therapy'],
            'weight': 0.0
        },
        'ecommerce_marketplace': {
            'keywords': ['shop', 'buy', 'sell', 'cart', 'checkout', 'payment',
                        'product', 'seller', 'marketplace', 'vendor', 'listing'],
            'weight': 0.0
        },
        'media_streaming': {
            'keywords': ['video', 'stream', 'music', 'podcast', 'playback',
                        'download', 'media', 'drm', 'bitrate', 'buffer'],
            'weight': 0.0
        },
        'enterprise_b2b': {
            'keywords': ['enterprise', 'sso', 'ldap', 'audit', 'compliance',
                        'workflow', 'approval', 'sync', 'offline', 'crm'],
            'weight': 0.0
        },
        'education_edtech': {
            'keywords': ['learning', 'course', 'education', 'student', 'teacher',
                        'quiz', 'progress', 'certification', 'lesson', 'engagement'],
            'weight': 0.0
        },
        'gaming_casual': {
            'keywords': ['game', 'play', 'score', 'level', 'challenge', 'reward',
                        'monetization', 'multiplayer', 'retention', 'loop'],
            'weight': 0.0
        },
        'iot_smarthome': {
            'keywords': ['iot', 'device', 'bluetooth', 'ble', 'control', 'sensor',
                        'pairing', 'real-time', 'smart', 'connected'],
            'weight': 0.0
        },
        'super_app': {
            'keywords': ['super app', 'mini program', 'modular', 'multi-service',
                        'unified', 'all-in-one', 'ecosystem', 'plugin'],
            'weight': 0.0
        }
    }

    # Score each domain
    for domain, data in domains.items():
        score = sum(description.count(keyword) for keyword in data['keywords'])
        domains[domain]['weight'] = score

    # Return highest scoring domain
    highest = max(domains.items(), key=lambda x: x[1]['weight'])
    return highest[0] if highest[1]['weight'] > 0 else 'general_mobile'
```

---

## Universal Conflict Resolution Hierarchy

Apply this priority order when trade-offs occur across ALL app types:

```
MOBILE PRIORITY HIERARCHY (descending):
1. SAFETY              (99%)  → Data protection, compliance, error prevention
2. ACCESSIBILITY       (97%)  → WCAG 2.1 AA, motor/visual/hearing/cognitive
3. CORE FUNCTION       (95%)  → Primary use case, critical path
4. PLATFORM CONVENTION (88%)  → OS-specific patterns (iOS/Android)
5. PERFORMANCE         (78%)  → Load time, responsiveness, battery
6. AESTHETICS          (65%)  → Visual design, polish, branding

Example: If safety conflicts with aesthetics → implement safety measure (99% > 65%)
Example: If performance conflicts with accessibility → optimize for both,
         but never sacrifice accessibility (97% > 78%)
```

---

## 1. Social/Community App

**Primary Concern**: Real-time engagement, feed performance, media delivery

### Priority Matrix

```python
SOCIAL_APP_PRIORITIES = {
    'feed_performance': 0.35,      # Feed speed, infinite scroll, pagination
    'real_time_sync': 0.20,        # Live notifications, message sync, presence
    'media_handling': 0.18,        # Image/video compression, lazy loading
    'engagement_loops': 0.15,      # Likes, comments, shares, notifications
    'content_moderation': 0.07,    # Spam, abuse, safety
    'network_efficiency': 0.05     # Bandwidth, offline support
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Feed load time (cold) | <1500ms | >3000ms = churn risk |
| Initial render | <500ms | >1000ms unacceptable |
| Feed scroll FPS | 60 FPS | <30 FPS = visible stutter |
| Push notification latency | <5s | >30s = unreliable perception |
| Media upload time | <2s | >10s = user abandonment |
| Offline draft retention | 100% | <90% = data loss |
| Engagement CTR target | 8-12% | <2% = algorithm failure |

### Critical Patterns (Must-Have)

```python
SOCIAL_CRITICAL_PATTERNS = [
    'Virtual_List_View',           # FlatList/LazyColumn for infinite scroll
    'Image_Compression_Pipeline',  # JPEG for feeds, WEBP for web
    'Pagination_with_Cursor',      # Cursor-based, not offset pagination
    'Real_Time_Update_Channel',    # WebSocket/Firebase for live updates
    'Optimistic_UI_Updates',       # Show action immediately, sync async
    'Offline_Queue',               # Local cache for offline composition
    'Notification_Priority_Queue', # Don't spam with every event
    'Media_Preload_Strategy',      # Cache next 3-5 items, preload headers
    'Connection_State_Aware_UI',   # Show offline indicator, queue status
    'Mention_Autocomplete_Cache'   # Local prefix tree for suggestions
]
```

### Common Pitfalls

```
❌ Loading full-size images for feed thumbnails (100-300KB each)
❌ Infinite scroll without pagination (memory leak on old devices)
❌ Synchronous database queries blocking UI thread
❌ No optimistic updates (feels laggy even at 200ms latency)
❌ Broadcasting all real-time changes to all clients
❌ No image compression (>50% of data usage)
❌ Storing all historical notifications in memory
❌ Blocking feed until profile/follower data loads
❌ No connection state detection (stale data shown as fresh)
❌ Real-time sync conflicts without resolution strategy
```

### Recommended Architecture

```
┌─────────────────────────────────────────┐
│         Presentation (Feed UI)          │  SwiftUI/Jetpack Compose
├─────────────────────────────────────────┤
│  State Manager (Redux/Bloc/MVVM)        │  Unidirectional data flow
├─────────────────────────────────────────┤
│  Real-Time Channel (WebSocket/Firebase) │  Event streaming
├─────────────────────────────────────────┤
│  Repository (Network + Cache + Offline) │  Cursor pagination
├─────────────────────────────────────────┤
│  Local DB (SQLite/Realm + In-Memory)    │  Dual-layer storage
└─────────────────────────────────────────┘

Key Patterns:
- Use virtual lists (FlatList/LazyColumn) NOT ScrollView
- Compress media immediately on capture (device CPU, not server)
- Cache feed with cursor pagination (SQLite for persistence)
- WebSocket for real-time, not polling
- Separate cache for drafts and sent items
```

### Reference Files to Load

| File | When |
|------|------|
| `../media-social.md` | Building feed, media handling |
| `../push-notifications.md` | Notification strategy |
| `../state-management.md` | Redux/Bloc patterns |
| `../networking.md` | Real-time sync, connection handling |
| `../performance.md` | FPS, memory profiling |

---

## 2. Fintech/Banking App

**Primary Concern**: Security, compliance, trust, accuracy

### Priority Matrix

```python
FINTECH_PRIORITIES = {
    'security_encryption': 0.30,   # TLS, data encryption, key management
    'compliance_audit': 0.25,      # PCI-DSS, SOC2, regulatory logging
    'transaction_accuracy': 0.20,  # Atomic operations, consistency checks
    'biometric_auth': 0.12,        # Face ID, Touch ID, fraud detection
    'error_recovery': 0.08,        # Network failure handling, retries
    'ui_clarity': 0.05             # Clear amounts, confirmations, warnings
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Transaction confirmation latency | <2s | >5s user loses trust |
| Authentication success rate | 99.9% | <99% = user frustration |
| Biometric spoofing false positive | <0.001% | >0.01% = liability |
| PCI-DSS compliance audit | 100% | Any failure = cannot operate |
| Encryption algorithm | TLS 1.3+ | TLS 1.0-1.1 = violation |
| Session timeout | 15min (inactivity) | >30min = security risk |
| Fraud detection latency | <1s | >10s = fraud already completed |
| Error recovery time | <5min | >30min = customer support call |

### Critical Patterns (Must-Have)

```python
FINTECH_CRITICAL_PATTERNS = [
    'End_To_End_Encryption',       # All data in transit encrypted
    'Certificate_Pinning',          # Prevent MITM attacks
    'Biometric_with_Fallback',     # Touch ID + passcode backup
    'Transaction_Atomic_Operations', # All-or-nothing, no partial states
    'Idempotency_Keys',            # Prevent duplicate transactions
    'Audit_Logging_Immutable',     # Append-only audit trail
    'Rate_Limiting',               # Brute force, DDoS protection
    'Session_Management',          # Expiry, reauthentication on sensitive ops
    'Amount_Confirmation_UI',      # Always show amount x2 before confirming
    'Transaction_History_Reconciliation', # Verify local vs remote
    'Jailbreak_Root_Detection',    # Refuse to run on compromised device
    'Network_Traffic_Analysis'     # Detect man-in-middle attempts
]
```

### Common Pitfalls

```
❌ Storing PII (SSN, account numbers) in app logs or crash reports
❌ Unencrypted local data storage (use Keychain/Encrypted Shared Preferences)
❌ No certificate pinning (vulnerable to MITM on public WiFi)
❌ Fingerprint auth without fallback option (broken sensor = locked out)
❌ Reversing transactions without immediate user notification
❌ No rate limiting on login/PIN attempts
❌ Showing full account numbers in UI (mask all but last 4 digits)
❌ Background data refresh without encryption
❌ No timestamp on transactions (can't prove when transfer happened)
❌ Caching sensitive data in memory longer than necessary
❌ Biometric unlock for app but not for transactions (2-factor needed)
❌ No fraud detection - catching fraud weeks later
```

### Recommended Architecture

```
┌──────────────────────────────────────────┐
│    Sensitive UI (Secure Enclave)         │  View controller lifecycle
├──────────────────────────────────────────┤
│    Transaction Validation Logic          │  Amount, recipient, limits
├──────────────────────────────────────────┤
│    Biometric + Passcode Auth             │  With fallback chain
├──────────────────────────────────────────┤
│    Encrypted Request Signing (PKI)       │  Asymmetric + HMAC
├──────────────────────────────────────────┤
│    TLS 1.3 + Certificate Pinning         │  With fallback
├──────────────────────────────────────────┤
│    Keychain/Encrypted Storage (device)   │  Never unencrypted at rest
├──────────────────────────────────────────┤
│    Audit Log (append-only, signed)       │  Immutable record
└──────────────────────────────────────────┘

Key Decisions:
- Biometric: Require additional verification for transfers >$1000
- Store only encrypted refresh tokens locally, never access tokens
- Timestamp all transactions client-side + server-side for dispute resolution
- Implement exponential backoff retry (1s, 2s, 4s) with max 5 attempts
```

### Reference Files to Load

| File | When |
|------|------|
| `../security.md` | Encryption, authentication |
| `../authentication.md` | Biometric, session management |
| `../data-storage.md` | Secure storage, Keychain |
| `../networking.md` | Certificate pinning, TLS |

---

## 3. Healthcare/Medical App

**Primary Concern**: Safety, HIPAA compliance, accessibility, error prevention

### Priority Matrix

```python
HEALTHCARE_PRIORITIES = {
    'hipaa_compliance': 0.28,      # PHI protection, audit logs
    'safety_ui': 0.25,            # Error prevention, confirmations, warnings
    'accessibility_wcag': 0.22,    # 2.1 AA minimum, seniors/disabled users
    'clinical_workflow': 0.15,     # Reduce physician time, EHR integration
    'data_accuracy': 0.07,         # Medication doses, test results
    'offline_critical_data': 0.03  # Critical data accessible offline
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| HIPAA audit trail | 100% of PHI access | Any gap = violation |
| Medication dose error detection | 99.9% | 1 in 1000 = patient harm |
| WCAG 2.1 AA compliance | 100% | <95% = excludes disabled |
| Clinical decision support latency | <1s | >5s = workflow disruption |
| Data sync accuracy | 100% | Any mismatch = diagnostic error |
| Session timeout | 5min (inactivity) | >30min = security risk |
| Accessibility color contrast | 4.5:1 ratio | <3:1 = unreadable |
| PHI encryption strength | AES-256 | <256-bit = inadequate |

### Critical Patterns (Must-Have)

```python
HEALTHCARE_CRITICAL_PATTERNS = [
    'HIPAA_Access_Audit_Logs',     # Who accessed what PHI, when
    'Medication_Name_Validation',  # Prevent sound-alike errors
    'Drug_Allergy_Checking',       # Contraindication detection
    'Confirmation_Dialogs',        # High-risk actions require y/n
    'Color_Blind_Testing',         # Not red/green only for vital status
    'Font_Scalability',            # Support 200% text enlargement
    'VoiceOver_Screen_Reader',     # iOS VoiceOver support
    'High_Contrast_Mode',          # Support high contrast system setting
    'Undo_Functionality',          # Undo recent actions (except publish)
    'Timestamp_Immutable_Records', # Dates cannot be changed retroactively
    'Two_Factor_Auth_PHI',         # 2FA for PHI access
    'Automatic_Logout_PHI'         # Auto-logout on PHI screen after 5min
]
```

### Common Pitfalls

```
❌ Using red/green only to indicate normal/abnormal vital signs
❌ Font too small for elderly users (needs 200% scalability)
❌ No medication dose checking (user manually enters 10x dose)
❌ Deleting historical records without immutable archive
❌ PHI visible in unencrypted backups or crash reports
❌ No allergy/drug interaction checking
❌ Confirmation dialogs don't show what's being confirmed
❌ No timestamps on medical records
❌ Background location tracking without explicit consent
❌ Sharing PHI with third-party analytics without consent
❌ No offline access to critical medications/allergies
❌ Color contrast <4.5:1 (fails WCAG AA)
❌ No undo for data entry (can't fix mistype)
```

### Recommended Architecture

```
┌──────────────────────────────────────────┐
│    Physician/Patient Secure UI           │  Double-confirm on edits
├──────────────────────────────────────────┤
│    Clinical Decision Support Engine      │  Medication checks, alerts
├──────────────────────────────────────────┤
│    PHI Validation Layer                  │  Dose, allergy, contraindications
├──────────────────────────────────────────┤
│    Audit Log (append-only, signed)       │  All PHI access logged
├──────────────────────────────────────────┤
│    EHR Integration (HL7 FHIR)            │  Sync with hospital system
├──────────────────────────────────────────┤
│    Offline SQLite + AES-256 Encryption   │  Critical data cached locally
├──────────────────────────────────────────┤
│    Accessibility Layer (a11y)            │  VoiceOver, high contrast
└──────────────────────────────────────────┘

Key Decisions:
- All PHI encrypted at rest (AES-256) and in transit (TLS 1.3)
- Immutable clinical notes - no retroactive editing
- Medication doses presented in multiple formats (mg, mL, mcg)
- Offline access to allergy/medication list (critical for emergencies)
- Automatic logout after 5min inactivity on any screen with PHI
```

### Reference Files to Load

| File | When |
|------|------|
| `../accessibility.md` | WCAG, VoiceOver, high contrast |
| `../security.md` | PHI encryption, audit trails |
| `../data-storage.md` | Encrypted local storage |
| `../offline-first.md` | Critical data offline access |

---

## 4. E-Commerce/Marketplace App

**Primary Concern**: Conversion rate, checkout friction, trust, payment reliability

### Priority Matrix

```python
ECOMMERCE_PRIORITIES = {
    'conversion_optimization': 0.30, # Checkout flow, reducing friction
    'trust_signals': 0.22,          # Reviews, ratings, security badges
    'product_discoverability': 0.18, # Search, filtering, recommendations
    'payment_reliability': 0.15,    # Payment processing, error handling
    'inventory_accuracy': 0.10,     # Stock levels, real-time updates
    'checkout_performance': 0.05    # Form speed, validation feedback
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Cart abandonment | <60% | >75% = massive revenue loss |
| Checkout completion time | <3min | >10min = abandonment spike |
| One-click purchase time | <10s | >20s = user goes elsewhere |
| Product load time | <2s | >4s = 40% abandonment |
| Search results relevance | >80% | <50% frustration |
| Payment success rate | 99.5% | <95% = fraud filter too strict |
| Review load time | <1s | >3s perceived as slow |
| Trust badge visibility | 100% of checkout | Not visible = conversion loss |

### Critical Patterns (Must-Have)

```python
ECOMMERCE_CRITICAL_PATTERNS = [
    'Guest_Checkout_Prominent',    # No forced signup before purchase
    'Costs_Visible_Early',         # Show shipping/tax on cart page
    'Express_Payment_Options',     # Apple Pay, Google Pay, PayPal
    'Real_Time_Stock_Updates',     # Show "Only 2 left" or "Out of stock"
    'Product_Image_Gallery',       # Multiple angles, zoom capability
    'Product_Reviews_Aggregated',  # Min 5 reviews for credibility
    'One_Page_Checkout',           # Not multi-step (increases abandonment)
    'Payment_Error_Recovery',      # Save form, explain failure, retry
    'Return_Policy_Accessible',    # Linked near checkout, clear terms
    'Address_Validation',          # Autocomplete, real-time validation
    'Order_Confirmation_Immediate', # Show confirmation + send email
    'Wishlist_Sharing',            # Add to wishlist, share with friends
    'Recommendation_Engine',       # "Frequently bought together"
    'Secure_Payment_Indicators'    # Lock icon, SSL info visible
]
```

### Common Pitfalls

```
❌ Requiring account creation before checkout (24% abandonment)
❌ Hiding shipping cost until final step (48% abandonment)
❌ No guest checkout option
❌ Checkout form with >12 fields (each field = 2% loss)
❌ No product images showing scale/context
❌ Out-of-stock items shown without clear indication
❌ No reviews or ratings on product cards
❌ Slow search results (>2s)
❌ No express payment options (Apple Pay, Google Pay)
❌ Poor error messages on payment failure
❌ Address autocomplete missing (user types "123 Main" vs zipcode search)
❌ Broken back button in checkout (users restart)
❌ No confirmation dialog before charging
❌ Wishlists not shareable
```

### Recommended Architecture

```
┌──────────────────────────────────────────┐
│    Product Discovery (Search/Browse)     │  Elasticsearch/Algolia
├──────────────────────────────────────────┤
│    Product Detail + Reviews              │  Lazy-load reviews
├──────────────────────────────────────────┤
│    Cart Management (local + remote)      │  Sync on login
├──────────────────────────────────────────┤
│    One-Page Checkout Flow                │  Progressive disclosure
├──────────────────────────────────────────┤
│    Express Payment Integration           │  Apple Pay, Google Pay
├──────────────────────────────────────────┤
│    Payment Processor (Stripe/Square)     │  With retry logic
├──────────────────────────────────────────┤
│    Order Confirmation + Tracking         │  Real-time shipment updates
└──────────────────────────────────────────┘

Key Decisions:
- Cart persisted locally (SQLite) + synced remotely
- Guest checkout with optional account creation post-purchase
- Search powered by external service (Algolia, Elasticsearch)
- Implement address autocomplete (Google Places API)
- Payment processor handles PCI compliance, not app
- Retry payment up to 3x with exponential backoff
```

### Reference Files to Load

| File | When |
|------|------|
| `../networking.md` | Payment processing, retry logic |
| `../state-management.md` | Cart state, checkout flow |
| `../security.md` | PCI-DSS compliance |
| `../performance.md` | Search latency, image optimization |

---

## 5. Media/Streaming App

**Primary Concern**: Playback reliability, DRM, download management, adaptive bitrate

### Priority Matrix

```python
MEDIA_STREAMING_PRIORITIES = {
    'playback_reliability': 0.30,  # No buffering, smooth playback
    'drm_content_protection': 0.20, # Copy protection, license enforcement
    'adaptive_bitrate': 0.18,      # Adjust quality to network conditions
    'download_management': 0.15,   # Offline viewing, storage management
    'user_experience': 0.10,       # Scrubbing, skip, quality controls
    'analytics_engagement': 0.07   # Track watch time, completion
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Time to first frame (TTFF) | <2s | >5s = user closes app |
| Buffering occurrence | <2% | >10% = unacceptable |
| Rebuffering duration | <2s | >10s = frustration |
| Playback quality switches | <3 per session | >5 = jarring experience |
| Download reliability | 99.9% | <95% = user loses trust |
| DRM license validation | <200ms | >1000ms = startup delay |
| Bitrate adaptation latency | <500ms | >2s = visible quality jump |
| Subtitle sync accuracy | ±200ms | >500ms = noticeably off |

### Critical Patterns (Must-Have)

```python
MEDIA_STREAMING_CRITICAL_PATTERNS = [
    'Adaptive_Bitrate_Streaming',  # HLS/DASH with network detection
    'DRM_License_Caching',         # Offline license, device binding
    'Download_Resume_Capability',  # Pause/resume, not restart
    'Download_Expiry_Enforcement', # License expires after 30 days
    'Network_Conditions_Detection', # Detect WiFi vs cellular
    'Video_Buffer_Management',     # Pre-buffer next 10-30s
    'Subtitle_Sync',               # Accurate timing (<200ms)
    'Playback_Position_Persistence', # Resume from last position
    'Quality_Settings_Menu',       # Manual override of automatic selection
    'Video_Codec_Compatibility',   # H.264, H.265, VP9 support
    'Audio_Format_Selection',      # Stereo, 5.1, Dolby Atmos options
    'Picture_In_Picture_Support',  # Android/iOS 15+
    'Seek_Prediction',             # Pre-buffer around seek point
    'Playback_Speed_Control'       # 0.75x, 1x, 1.25x, 1.5x, 2x
]
```

### Common Pitfalls

```
❌ No adaptive bitrate (fixed quality = buffering on 3G)
❌ No DRM enforcement (content can be screen-captured)
❌ Download without resume (user loses 500MB download, must restart)
❌ No download expiry enforcement (piracy risk)
❌ Buffering without visual indicator (user thinks it froze)
❌ Not detecting network type (using streaming quality on cellular)
❌ Subtitles out of sync (>500ms = unwatchable)
❌ No playback position persistence (user loses place in episode)
❌ Fixed playback speed (some users need to watch faster/slower)
❌ Not supporting offline viewing
❌ High DRM license renewal latency (>1s startup delay)
❌ Not detecting device orientation change smoothly
❌ Audio/video sync drift on long videos (>1min)
❌ Download storage not showing user how much space used
```

### Recommended Architecture

```
┌──────────────────────────────────────────┐
│    Playback UI (AVPlayer/MediaPlayer)    │  Controls, scrubbing, quality
├──────────────────────────────────────────┤
│    DRM License Manager                   │  Fetch, cache, validate
├──────────────────────────────────────────┤
│    Network Condition Detector            │  WiFi vs cellular vs weak
├──────────────────────────────────────────┤
│    Adaptive Bitrate Engine (HLS/DASH)    │  ABR algorithm
├──────────────────────────────────────────┤
│    Download Manager + Storage            │  Pause/resume, expiry
├──────────────────────────────────────────┤
│    Subtitle/Caption Sync                 │  WebVTT parsing, timing
├──────────────────────────────────────────┤
│    Analytics (watch time, completion)    │  Engagement tracking
└──────────────────────────────────────────┘

Key Decisions:
- Use platform native players (AVPlayer on iOS, ExoPlayer on Android)
- Implement ABR with network detection (drop to 480p on LTE)
- DRM licenses cached locally but device-bound
- Download expiry enforced per license terms (often 30 days)
- Pre-buffer 30s ahead, have 10s behind for smooth seek
- Subtitle sync: WebVTT with adjustment for device clock skew
```

### Reference Files to Load

| File | When |
|------|------|
| `../media-social.md` | Video handling, formats |
| `../performance.md` | Buffering, memory management |
| `../offline-first.md` | Download management |
| `../networking.md` | Bitrate detection, retries |

---

## 6. Enterprise/B2B App

**Primary Concern**: Compliance, SSO integration, offline sync, role-based access

### Priority Matrix

```python
ENTERPRISE_PRIORITIES = {
    'sso_integration': 0.25,       # LDAP, Active Directory, OAuth2
    'offline_data_sync': 0.22,     # Critical data available offline
    'role_based_access': 0.20,     # Permissions, data filtering per role
    'compliance_audit': 0.15,      # Audit logs, data residency
    'performance_at_scale': 0.12,  # Handle 10k+ records, slow network
    'ui_customization': 0.06       # White-label, theming per company
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| SSO authentication latency | <2s | >5s = business user frustration |
| Offline data sync conflict resolution | 99% | >1% = data corruption risk |
| Role-based access enforcement | 100% | Any gap = compliance violation |
| Large dataset pagination | <1s per page | >3s = unusable |
| Audit log completeness | 100% | Any gap = cannot prove compliance |
| Network reconnection latency | <5s | >30s = lost productivity |
| Sync conflict resolution time | <100ms | >1s = visible delay |

### Critical Patterns (Must-Have)

```python
ENTERPRISE_CRITICAL_PATTERNS = [
    'SSO_Integration_OIDC',        # OAuth2 + OpenID Connect
    'Offline_First_Architecture',  # Local DB, sync on reconnect
    'Role_Based_Access_Control',   # Data filtering per user role
    'Audit_Logging_Comprehensive', # All user actions logged
    'Conflict_Resolution_CRDT',    # Operational transformation or CRDT
    'Device_Management_MDM',       # Remote wipe, compliance enforcement
    'Data_Residency_Compliance',   # Geo-specific storage
    'Large_Dataset_Pagination',    # Cursor-based, lazy load
    'Session_Management_SSO',      # Shared SSO session across apps
    'Offline_Indication_Clear',    # Show offline status, queue state
    'Batch_Operations',            # Bulk edit, bulk export
    'Export_Functionality',        # CSV/PDF export with role-based filtering
    'Biometric_Device_Lock',       # Face ID/Touch ID for device access
    'VPN_Enforcement',             # Require VPN for sensitive data access
    'Certificate_Pinning'          # Prevent MITM on corporate network
]
```

### Common Pitfalls

```
❌ No offline support (app unusable on flight, bad WiFi)
❌ Not enforcing role-based access (junior user sees CEO data)
❌ Sync conflicts without resolution strategy (which version wins?)
❌ No audit trail (regulatory audit fails)
❌ Slow pagination (loading 10k records = lag)
❌ SSO not working if company uses non-standard LDAP
❌ Device not removable from MDM (lost phone = security risk)
❌ No geolocation enforcement (data in wrong jurisdiction)
❌ Export includes data user shouldn't see
❌ Sync fails without notifying user (user thinks data saved)
❌ No VPN requirement for sensitive operations
❌ Unencrypted device storage (phone stolen = data exposed)
❌ Session doesn't survive app restart
❌ No audit log for who deleted what, when
```

### Recommended Architecture

```
┌──────────────────────────────────────────┐
│    Enterprise Sign-In (SSO/OAuth2)       │  OIDC provider integration
├──────────────────────────────────────────┤
│    Role-Based Access Control Layer       │  Filter data per role
├──────────────────────────────────────────┤
│    Offline-First Sync Engine             │  CRDT or OT for conflicts
├──────────────────────────────────────────┤
│    Local SQLite + Device Encryption      │  AES-256, key in Keychain
├──────────────────────────────────────────┤
│    Audit Logging (immutable, signed)     │  All user actions
├──────────────────────────────────────────┤
│    MDM Integration                       │  Device compliance checks
├──────────────────────────────────────────┤
│    VPN/Network Security Detection        │  Enforce VPN for sensitive ops
└──────────────────────────────────────────┘

Key Decisions:
- Offline-first: All data syncs bidirectionally, conflicts resolved via CRDT
- SSO: Use OAuth2 + OpenID Connect, fallback to local auth if necessary
- Role-based filtering at repository layer (prevent exposing data in UI)
- Audit trail: Append-only, digitally signed, cannot be edited
- Device wipe: MDM integration to remotely wipe on company demand
```

### Reference Files to Load

| File | When |
|------|------|
| `../authentication.md` | SSO, OIDC, session management |
| `../offline-first.md` | Sync, CRDT, conflict resolution |
| `../security.md` | Device encryption, MDM |
| `../data-storage.md` | Encrypted local storage |

---

## 7. Education/EdTech App

**Primary Concern**: Engagement, progress tracking, accessibility, offline content

### Priority Matrix

```python
EDUCATION_PRIORITIES = {
    'engagement_loops': 0.28,      # Streaks, rewards, progress visualization
    'progress_tracking': 0.22,     # Detailed metrics, skill trees
    'accessibility_wcag': 0.18,    # 2.1 AA, closed captions, transcripts
    'offline_content': 0.15,       # Lessons available offline
    'personalization': 0.10,       # Adaptive difficulty, recommendations
    'social_learning': 0.07        # Leaderboards, peer feedback
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Daily active user engagement | >40% | <20% = retention failure |
| Lesson completion rate | 60-70% | <30% = content too hard |
| Quiz performance | 70-80% | <50% = content not understood |
| Video watchtime (% completed) | 80% | <50% = too long/boring |
| Offline content availability | 90% | <50% = unreliable |
| Accessibility score (WCAG) | 100% | <95% = excludes students |
| Progress visualization load time | <500ms | >2s = disengaging |
| Streak persistence | 100% | Any loss = user frustration |

### Critical Patterns (Must-Have)

```python
EDUCATION_CRITICAL_PATTERNS = [
    'Engagement_Streak_System',    # Daily login rewards, streak count
    'Progress_Visualization',      # XP, level, skill tree display
    'Quiz_with_Immediate_Feedback', # Show answer immediately
    'Adaptive_Difficulty',         # Adjust based on performance
    'Offline_Lesson_Content',      # Lessons downloadable
    'Closed_Captions_Transcripts', # Video accessibility
    'Accessibility_VoiceOver',     # Full VoiceOver support
    'Skill_Tree_Progression',      # Visual skill unlocking
    'Leaderboard_Optional',        # Opt-in competition
    'Parent_Dashboard',            # Parent monitoring without surveillance
    'Push_Notification_Reminders', # "You broke your streak" nudges
    'Achievement_Badges',          # Unlockable milestones
    'Spaced_Repetition_Algorithm', # SRS for retention
    'Detailed_Performance_Analytics', # Per-skill, per-student data
    'Content_Recommendation_Engine' # Suggest next lesson
]
```

### Common Pitfalls

```
❌ No offline access (student on train can't study)
❌ No closed captions on videos (deaf/hard-of-hearing excluded)
❌ Font too small (<14pt, fails accessibility)
❌ Color alone to indicate status (red/green unreadable for colorblind)
❌ Streaks lost on missed day without warning
❌ No adaptive difficulty (too easy = boring, too hard = frustration)
❌ No progress visualization (students lose motivation)
❌ Quiz without immediate feedback (students don't learn why wrong)
❌ Punishing mistakes (should encourage learning from errors)
❌ No dark mode for evening study
❌ Push notifications too frequent (disruptive)
❌ No pause for long learning sessions (burnout risk)
❌ Leaderboards mandatory (anxiety for struggling students)
❌ No teacher/parent oversight tools
❌ Spaced repetition not implemented (students forget)
```

### Recommended Architecture

```
┌──────────────────────────────────────────┐
│    Lesson Content (Downloadable)         │  Audio, video, text
├──────────────────────────────────────────┤
│    Quiz Engine (SRS Algorithm)           │  Spaced repetition, adaptive
├──────────────────────────────────────────┤
│    Progress Tracking + Analytics         │  Per-skill, per-student
├──────────────────────────────────────────┤
│    Engagement System                     │  Streaks, badges, XP
├──────────────────────────────────────────┤
│    Offline SQLite + Sync                 │  Content cached locally
├──────────────────────────────────────────┤
│    Accessibility Layer (a11y)            │  Captions, VoiceOver, contrast
├──────────────────────────────────────────┤
│    Parent/Teacher Dashboard              │  Progress reports
└──────────────────────────────────────────┘

Key Decisions:
- All video content has closed captions and transcripts
- Spaced repetition algorithm: Show again after 1d, 3d, 7d, 21d
- Streak rewards: Login daily for streak multiplier, not reset on miss
- Dark mode: Support system dark mode preference
- Offline: Cache lessons locally, sync progress on reconnect
- Adaptive: Adjust difficulty based on quiz performance
```

### Reference Files to Load

| File | When |
|------|------|
| `../accessibility.md` | WCAG, captions, VoiceOver |
| `../offline-first.md` | Content caching |
| `../push-notifications.md` | Engagement nudges |
| `../state-management.md` | Progress persistence |

---

## 8. Gaming (Casual) App

**Primary Concern**: Performance, engagement loops, monetization, retention

### Priority Matrix

```python
GAMING_PRIORITIES = {
    'frame_rate_stability': 0.28,  # 60 FPS minimum, no frame drops
    'engagement_loops': 0.25,      # Session length, retention mechanics
    'monetization_balance': 0.18,  # Ad frequency, IAP upsell, not pay-to-win
    'social_features': 0.12,       # Multiplayer, leaderboards, invites
    'battery_efficiency': 0.10,    # GPU/CPU optimization
    'smooth_animations': 0.07      # Transitions, particle effects
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Frame rate (FPS) | 60 FPS | <30 FPS = unplayable |
| Frame drops per minute | 0 | >2 = visible stuttering |
| Session length (casual) | 5-15 min | <2 min = weak engagement |
| Daily active user retention | 30% D30 | <15% D30 = game failing |
| Ad revenue per session | $0.01-0.05 | >$0.10 = too aggressive |
| Monetization rate (IAP) | 2-5% | >10% = pay-to-win perception |
| Battery drain per hour | <5% | >15% = user deletes app |
| Load time (from launch to playable) | <2s | >5s = user closes |

### Critical Patterns (Must-Have)

```python
GAMING_CRITICAL_PATTERNS = [
    'Frame_Rate_Stability_60_FPS', # Consistent 60 FPS, not 55-60
    'GPU_Optimization',            # Reduce draw calls, batch rendering
    'Memory_Management',           # No memory leaks, GC tuning
    'Level_Progression_System',    # Tutorial → Easy → Medium → Hard
    'In_Game_Monetization',        # Rewarded ads, IAP, battle pass
    'Session_Save_State',          # Resume from any point
    'Audio_Management',            # Music loops, SFX volume balance
    'Touch_Input_Responsiveness',  # <100ms input latency
    'Multiplayer_Matchmaking',     # Fair skill-based matching
    'Leaderboards_Anti_Cheat',     # Detect/prevent scoring hacks
    'Push_Notifications_Engagement', # Daily quests, friend invites
    'Progression_Visibility',      # XP, level, next unlock shown
    'Error_Recovery',              # Reconnect on network loss
    'Tutorial_Optional',           # Skipable for returning players
    'Performance_Profiling_Tools'  # Built-in FPS counter, memory viewer
]
```

### Common Pitfalls

```
❌ Frame rate drops below 30 FPS (unplayable)
❌ No level progression (impossible learning curve)
❌ Ads interrupt every 30 seconds (user quits)
❌ Pay-to-win (skill irrelevant if not spending money)
❌ No save state (user loses 1 hour of progress)
❌ No offline play (needs internet for single-player)
❌ Drains battery in <1 hour (user uninstalls)
❌ Long load times (>5s, user closes)
❌ Unfair matchmaking (skill gap too large)
❌ No anti-cheat (leaderboards meaningless)
❌ Inadequate tutorial (new players quit in 2 minutes)
❌ Audio unbalanced (music too loud, SFX too quiet)
❌ No pause functionality (can't stop mid-game)
❌ Disconnection = lost game (no reconnect)
❌ No progression visualization
```

### Recommended Architecture

```
┌──────────────────────────────────────────┐
│    Game Engine (Unity/Unreal/Native)     │  Core gameplay loop
├──────────────────────────────────────────┤
│    Physics + Collision System            │  Deterministic results
├──────────────────────────────────────────┤
│    Input Handler (<100ms latency)        │  Touch/accelerometer
├──────────────────────────────────────────┤
│    Audio Manager (Music + SFX)           │  Layered, ducked
├──────────────────────────────────────────┤
│    Monetization (Ads + IAP)              │  Rewarded ads, fair pricing
├──────────────────────────────────────────┤
│    Multiplayer/Matchmaking               │  Skill-based, anti-cheat
├──────────────────────────────────────────┤
│    Analytics + Telemetry                 │  Session length, churn
├──────────────────────────────────────────┤
│    Save State Persistence                │  CloudKit/Play Games
└──────────────────────────────────────────┘

Key Decisions:
- Target 60 FPS with frame limiter (not unlimited)
- Monetization: Optional ads for rewards, cosmetic-only IAPs
- Session length: 5-15 minutes for casual games
- Progression: Unlock new mechanics every 2-3 levels (not boring)
- Audio: Music -10dB when SFX plays, full volume at menus
- Save state: Auto-save every 10 seconds or on completion
```

### Reference Files to Load

| File | When |
|------|------|
| `../performance.md` | FPS optimization, memory profiling |
| `../monetization.md` | IAP, ads, battle pass mechanics |
| `../push-notifications.md` | Engagement mechanics |
| `../state-management.md` | Game state persistence |

---

## 9. IoT/Smart Home App

**Primary Concern**: BLE connectivity, real-time control, device pairing, reliability

### Priority Matrix

```python
IOT_PRIORITIES = {
    'ble_connectivity': 0.28,      # BLE range, stability, reconnection
    'real_time_control': 0.22,     # Command latency, status sync
    'device_pairing': 0.18,        # Secure pairing, ease of setup
    'offline_fallback': 0.15,      # Local control without cloud
    'reliability_robustness': 0.12, # Handle disconnections gracefully
    'battery_efficiency': 0.05     # Don't drain device battery
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| BLE connection latency | <500ms | >2s = feels unresponsive |
| Command execution latency | <1s | >5s = user thinks broken |
| Device discovery time | <5s | >15s = bad UX |
| Pairing process time | <2min | >5min = user frustration |
| Reconnection latency (after disconnect) | <3s | >10s = unreliable perception |
| Battery impact on device | <2% per 8hr | >5% = user disables |
| Cloud fallback latency | <2s | >10s = unreliable |
| Status update frequency | 1x/second | >5s stale = confusing |

### Critical Patterns (Must-Have)

```python
IOT_CRITICAL_PATTERNS = [
    'BLE_Central_Manager',         # Handle multiple device connections
    'Device_Pairing_Secure',       # Secure pairing, not hardcoded
    'Offline_Local_Control',       # Control device without cloud
    'Connection_State_Awareness',  # Show connected/disconnected clearly
    'Automatic_Reconnection',      # Retry with exponential backoff
    'Command_Queuing',             # Queue commands, execute in order
    'Real_Time_Status_Updates',    # Live status via BLE notifications
    'Device_Discovery',            # Scan, list nearby devices
    'Signal_Strength_Display',     # RSSI indicator for pairing
    'Firmware_Update_OTA',         # Over-the-air device updates
    'Scene_Automation',            # Schedule, rules, automation
    'Multi_Device_Control',        # Control multiple devices in sequence
    'Local_Network_Fallback',      # WiFi for cloud sync if BLE fails
    'Error_Recovery_UI',           # Clear error messages, recovery steps
    'Battery_Status_Monitor'       # Show device battery level
]
```

### Common Pitfalls

```
❌ No local control (must use cloud every time)
❌ BLE connection not persistent (reconnects every command)
❌ Pairing process too complex (users give up)
❌ No signal strength display (user doesn't know why pairing fails)
❌ Command latency >2s (feels broken even if working)
❌ Not showing connection status clearly
❌ Cloud dependency for simple local operations
❌ No command queuing (commands sent out of order)
❌ Battery drain on controlled device (user disables)
❌ Firmware updates slow or impossible
❌ No automation/scheduling (manual only)
❌ Error messages unclear (what went wrong?)
❌ Range limited (device within 10m only)
❌ No multi-device control
❌ Crashing on BLE disconnect
```

### Recommended Architecture

```
┌──────────────────────────────────────────┐
│    BLE Central Manager                   │  Multiple device connections
├──────────────────────────────────────────┤
│    Device Pairing + Security             │  Secure pairing protocol
├──────────────────────────────────────────┤
│    Local Control Engine                  │  Commands without cloud
├──────────────────────────────────────────┤
│    Real-Time Status Listener             │  BLE notifications
├──────────────────────────────────────────┤
│    Cloud Sync (async)                    │  Background sync if available
├──────────────────────────────────────────┤
│    Command Queue + Retry Logic           │  Automatic retry
├──────────────────────────────────────────┤
│    Device Discovery + Scanning           │  Find devices in range
├──────────────────────────────────────────┤
│    Automation/Scheduling Engine          │  Rules, scenes, automations
└──────────────────────────────────────────┘

Key Decisions:
- Local-first: Always use BLE for control if in range
- Cloud for: Remote access (away from home), sync, backups
- Pairing: Use secure pairing (not hardcoded PIN)
- Reconnection: Exponential backoff (1s, 2s, 4s, 8s) up to 5min
- Status updates: Subscribe to BLE notifications, not polling
- Automation: Local execution if device in range, cloud if remote
```

### Reference Files to Load

| File | When |
|------|------|
| `../wearables-iot.md` | BLE, device communication |
| `../networking.md` | Connection handling, retries |
| `../offline-first.md` | Local control, sync |
| `../security.md` | Secure pairing, encryption |

---

## 10. Super App / Multi-Service

**Primary Concern**: Modular architecture, unified auth, performance at scale

### Priority Matrix

```python
SUPER_APP_PRIORITIES = {
    'modular_architecture': 0.28,  # Independent modules, mini-programs
    'unified_authentication': 0.22, # Single sign-on across services
    'performance_at_scale': 0.20,  # Handle 100+ screens, 50+ modules
    'mini_program_isolation': 0.15, # Modules don't crash main app
    'shared_data_sync': 0.10,      # Data consistency across modules
    'feature_discovery': 0.05      # Help users find features
}
```

### Key Metrics & Thresholds

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| App cold start time | <2s | >5s = user abandonment |
| Mini-program load time | <500ms | >2s = feels broken |
| Module isolation failure rate | 0% | >0.1% = crash propagation |
| Unified auth latency | <1s | >3s = frustration |
| Inter-module data sync latency | <1s | >5s = inconsistent state |
| App size | <200MB | >400MB = too large |
| Memory usage | <300MB | >600MB = low-end device crash |

### Critical Patterns (Must-Have)

```python
SUPER_APP_CRITICAL_PATTERNS = [
    'Modular_Plugin_Architecture', # Dynamic module loading
    'Mini_Program_Isolation',      # Module crash doesn't crash app
    'Unified_Auth_Single_Sign_On', # Share session across modules
    'Shared_Service_Layer',        # Network, storage, analytics
    'Dynamic_Module_Loading',      # Load modules on demand
    'Module_Communication_Bridge', # Safe inter-module messaging
    'Shared_Data_Sync',            # Data consistency across modules
    'Feature_Flag_System',         # Enable/disable features per user
    'Module_Permission_System',    # Control what modules can access
    'App_Shell_Architecture',      # Core nav + dynamic modules
    'Bottom_Tab_Navigation',       # Easy access to main services
    'Search_Cross_Module',         # Search across all modules
    'Notification_Aggregation',    # Unified notification center
    'Analytics_Aggregate',         # Track usage across modules
    'Gradual_Module_Loading'       # Don't load all at startup
]
```

### Common Pitfalls

```
❌ One module crash crashes entire app
❌ Modules loading at startup (slow cold start)
❌ No module isolation (one module hogs memory)
❌ Auth not shared (sign in to each module separately)
❌ Module dependencies tangled (refactoring nightmare)
❌ App size >400MB (won't install in some regions)
❌ No feature flags (can't disable problematic modules)
❌ Duplicate code across modules (storage, networking)
❌ No module communication pattern (hacky, tight coupling)
❌ Modules can't be updated independently
❌ No way to uninstall unused modules
❌ Feature discovery missing (users don't know what's available)
❌ Data inconsistency between modules (user sees different values)
❌ Module loading stalls main UI thread
❌ No lifecycle management for modules
```

### Recommended Architecture

```
┌──────────────────────────────────────────┐
│    App Shell (Navigation, Core UI)       │  Tab bar, main navigation
├──────────────────────────────────────────┤
│    Module Registry + Loader              │  Dynamic loading
├──────────────────────────────────────────┤
│    Unified Auth + Session                │  Single sign-on
├──────────────────────────────────────────┤
│    Shared Service Layer                  │  Network, storage, analytics
├──────────────────────────────────────────┤
│    Module Isolation Boundary             │  Crash boundaries
├──────────────────────────────────────────┤
│    Inter-Module Communication Bridge     │  Safe messaging
├──────────────────────────────────────────┤
│    Feature Flag + Permission System      │  Control access
├──────────────────────────────────────────┤
│    Mini-Program Runtime                  │  Execute isolated modules
└──────────────────────────────────────────┘

Key Decisions:
- Modular: Each feature is independent module with own nav stack
- Loading: Load on first tap, cache for session, unload on app quit
- Auth: Share auth tokens/session across all modules
- Isolation: Each module has try-catch at entry point
- Communication: Use event bus/bridge for inter-module messaging
- Size: Core app + 3 main modules at install, download others on demand
```

### Reference Files to Load

| File | When |
|------|------|
| `../architecture.md` | Modular patterns, VIPER, Redux |
| `../authentication.md` | Unified SSO |
| `../state-management.md` | Shared state across modules |
| `../performance.md` | App startup, memory profiling |

---

## Cross-Domain Patterns (Apply to ALL App Types)

These patterns apply universally and should be implemented first:

```python
UNIVERSAL_MOBILE_PATTERNS = [
    'Error_Handling_Graceful',     # Try-catch, user-friendly messages
    'Network_Resilience',          # Detect connection, retry logic
    'Performance_Monitoring',      # Crash reporting, analytics
    'Accessibility_WCAG_2.1_AA',   # Color, contrast, text size
    'Localization_i18n',           # Multiple language support
    'Platform_Guidelines',         # Follow iOS HIG, Material Design
    'Deep_Linking',                # Link to specific screens
    'Onboarding_Tutorial',         # First-time user guidance
    'Permission_Requests_Justified', # Ask when needed, explain why
    'Battery_Efficiency',          # Minimize background processes
    'Responsive_Design',           # Adapt to screen sizes
    'Touch_Input_Affordances',     # Min 44x44pt tap targets
    'Keyboard_Handling',           # Dismiss keyboard appropriately
    'Light_Dark_Mode',             # Support system theme
    'Testing_Unit_UI_E2E',         # Multi-layer testing coverage
    'Crash_Analytics_Telemetry',   # Monitor app health
    'Code_Review_Quality_Gates',   # Static analysis before merge
    'Dependency_Management',       # Update dependencies regularly
    'Secrets_Management',          # Never hardcode API keys
    'Documentation_Runbooks'       # How to debug, deploy, monitor
]
```

---

## Implementation Checklist

Use this checklist for any mobile app project:

```python
def validate_app_architecture(app_type: str) -> Dict[str, bool]:
    """Check app meets domain-specific critical requirements."""

    critical_checks = {
        # Universal checks
        'error_handling_present': check_error_handlers(),
        'network_resilience': check_retry_logic(),
        'analytics_integrated': check_telemetry(),
        'accessibility_wcag_aa': check_accessibility(),

        # Domain-specific checks
        app_type.lower(): {
            'social_community': {
                'virtual_list_implemented': True,
                'image_compression_pipeline': True,
                'real_time_sync_channel': True,
                'optimistic_updates': True,
            },
            'fintech_banking': {
                'tls_1_3_or_higher': True,
                'certificate_pinning': True,
                'biometric_with_fallback': True,
                'audit_logging': True,
            },
            'healthcare_medical': {
                'hipaa_compliance': True,
                'clinical_workflow_efficient': True,
                'accessibility_wcag_aa_plus': True,
                'offline_critical_data': True,
            },
            # ... etc for each domain
        }
    }

    return critical_checks
```

---

## References & Further Reading

- **Social/Real-Time**: Firebase Realtime Database, Socket.io, List virtualization patterns
- **Fintech Security**: OWASP Mobile Security Testing Guide, PCI-DSS v3.2.1
- **Healthcare**: HIPAA Security Rule, HL7 FHIR standards, FDA Software Validation
- **E-Commerce**: Baymard Institute research, CRO best practices
- **Streaming**: MPEG-DASH spec, HLS spec, DRM implementation guides
- **Enterprise**: OAuth2/OIDC specs, Conflict-free Replicated Data Types (CRDT)
- **Education**: Spaced Repetition research (Ebbinghaus curve), WCAG for education
- **Gaming**: Unity/Unreal optimization guides, Game feel principles (Swink)
- **IoT**: CoreBluetooth/Bluetooth Low Energy specifications
- **Super Apps**: Micro-frontends architecture, Module federation patterns

---

*Last updated: March 2026*
*Domain matrices modeled after ui-ux-mastery skill patterns*
*Weights sum to 1.0 for each domain; apply to prioritization decisions*
