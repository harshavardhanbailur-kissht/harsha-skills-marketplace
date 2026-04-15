# Industry-Specific Decomposition Patterns

## Why Industry Matters

Different industries have different mandatory epics, features, and acceptance criteria. A payment processing PRD in fintech must include compliance epics that a consumer app PRD never touches. A healthcare PRD must satisfy FDA and HIPAA requirements. A mobile game has completely different concerns than a B2B SaaS platform.

Using industry-specific patterns when decomposing ensures you don't miss critical requirements that are "obvious" to domain experts but invisible to outsiders.

## How to Use This Guide

1. **Identify industry:** Is this PRD for fintech, healthcare, SaaS, mobile, etc.?
2. **Check mandatory epics:** Are all industry-specific epics present in the PRD?
3. **Flag missing epics:** If not, ask the user whether they should be added
4. **Apply feature patterns:** Use industry patterns for common feature categories
5. **Apply task patterns:** Check that task acceptance criteria include domain-specific requirements

---

## FINTECH Decomposition Pattern

### Why It's Different
Fintech handles money and regulatory requirements. A mistake in authentication can mean fraud. A missing audit trail can mean regulatory violation. Every feature touches security, compliance, or both.

### Mandatory Epics

**1. Compliance Epic** (P0-Critical)
- KYC (Know Your Customer) verification
- AML (Anti-Money Laundering) screening
- PCI-DSS compliance (if handling cards)
- Regulatory reporting (FinCEN, etc.)

**2. Security Epic** (P0-Critical)
- Encryption (in transit and at rest)
- Audit trails (every financial action logged)
- Multi-factor authentication
- Rate limiting & fraud detection
- Secure key management

**3. Financial Operations Epic**
- Transaction processing
- Reconciliation & settlement
- Fee calculation & billing
- Chargebacks & disputes

**4. Regulatory Reporting Epic**
- Generate compliance reports
- Maintain audit trails
- Data retention policies
- Customer reporting (statements)

### Common Features

| Feature | Notes |
|---------|-------|
| Payment Processing | Support multiple payment methods (card, ACH, wire). Every transaction must be auditable. |
| Account Management | Users must verify identity (KYC). Account status tracked (new, verified, suspended). |
| Transaction Monitoring | Real-time fraud detection. Suspicious activity flagged and blocked. |
| Compliance Dashboard | Show regulatory status, violations, audit trail. Admin-only. |
| User Verification | Multi-step KYC with identity documents. AML screening before account approval. |

### Task Patterns

Every task in fintech should answer:
- **Who performed this action?** (audit trail requirement)
- **How can we prove it was authorized?** (compliance requirement)
- **Can it be reversed/corrected?** (dispute handling requirement)

**Example task breakdown for "Process Payment":**
```
T-2.1.1: Design payment data model
Acceptance Criteria:
- [ ] Transaction ID (unique, immutable)
- [ ] Timestamp (UTC, immutable)
- [ ] Amount, currency, source, destination
- [ ] Status enum (pending, processing, completed, failed, disputed)
- [ ] User ID & authorization method (linked to KYC)
- [ ] Audit fields: created_by, created_at, updated_at, updated_by
- [ ] Soft delete only (never purge transaction records)

T-2.1.2: Implement payment processing
Acceptance Criteria:
- [ ] Verify user is KYC-approved before processing
- [ ] Check amount against limits (user daily limit, AML threshold)
- [ ] Log every state transition (pending → processing → completed)
- [ ] Implement idempotency (same request always safe to retry)
- [ ] PCI-DSS compliance (no full card numbers in logs)
- [ ] Reconcile with payment processor within 24 hours
- [ ] Detect and flag suspicious patterns

T-2.1.3: Build payment audit UI
Acceptance Criteria:
- [ ] Show immutable transaction history
- [ ] Display regulatory flags (high-risk, frozen, etc.)
- [ ] Admin can review and approve disputed transactions
- [ ] Export audit trail (for regulatory inspection)
```

### Extra Acceptance Criteria

Every fintech feature should have:
- **Regulatory requirement mapping:** Which regulation does this satisfy?
- **Audit trail completeness:** All user actions logged with timestamp, user ID, authorization
- **Data retention:** How long is data kept? (Often 7 years for financial records)
- **Soft delete only:** Financial records are never purged, only soft-deleted
- **PCI-DSS compliance:** If handling cards, prove no full card numbers stored/logged

### Clarification Questions to Ask

When reviewing fintech PRD, ask:
```
1. "Which payment methods are in scope for MVP?
   - Card only
   - Card + ACH (bank transfer)
   - Card + ACH + Wire
   - Other: [specify]"

2. "What's the KYC process?
   - Just email verification (risky)
   - Identity document upload
   - Video verification
   - Third-party service (Jumio, etc.)"

3. "Which regulations apply?
   - US money transmitter (FinCEN)
   - GDPR (EU users)
   - PCI-DSS (card handling)
   - Other: [specify]"

4. "What's the dispute handling process?
   - Users can dispute transactions (self-service)
   - Admin reviews all disputes (slower but safer)
   - Automated ML-based approval"
```

---

## HEALTHCARE Decomposition Pattern

### Why It's Different
Healthcare handles sensitive patient data (PHI: Protected Health Information). Regulatory requirements (HIPAA, GDPR, FDA) are non-negotiable. An audit failure can result in massive fines or service shutdown. Features interact with clinical workflows and may affect patient safety.

### Mandatory Epics

**1. HIPAA Compliance Epic** (P0-Critical)
- Encryption of PHI (in transit and at rest)
- Access controls (role-based, audit logged)
- Patient data rights (access, correction, deletion)
- Breach notification procedures
- Business Associate Agreements (BAAs)

**2. Clinical Workflow Epic**
- Integration with clinical decision-making
- Workflows for different user roles (doctors, nurses, admins)
- Order management (tests, medications)
- Results reporting and notification

**3. FDA Requirements Epic** (if building device software)
- Software lifecycle per IEC 62304
- Change control process
- Risk management
- Verification & validation testing
- Post-market surveillance

**4. Audit & Compliance Logging Epic**
- Every PHI access logged (who, what, when, why)
- Immutable audit trail
- Compliance reports for regulators
- Breach detection & response

**5. Data Governance Epic**
- Data classification (public, confidential, sensitive)
- Retention policies (when to purge)
- De-identification for research
- Data lineage tracking

### Common Features

| Feature | Notes |
|---------|-------|
| Patient Records | Complete medical history. HIPAA-protected. Every access logged. |
| Order Management | Doctors order tests/medications. System enforces clinical guidelines. |
| Results Reporting | Lab/imaging results with clinical decision support. Notification to providers. |
| Patient Portal | Patients access their own data (HIPAA right of access). |
| Consent Management | Track patient consent for data sharing, research participation. |
| Audit Dashboard | Admins review access logs, detect breaches. |

### Task Patterns

Every healthcare task should include:

**PHI Handling Task:**
```
T-3.2.1: Implement patient record encryption
Acceptance Criteria:
- [ ] All PHI encrypted at rest (AES-256)
- [ ] Encryption keys in KMS (not in application)
- [ ] Every database query logs who accessed what PHI
- [ ] Access log is immutable (append-only)
- [ ] HIPAA audit trail shows: user ID, timestamp, action, PHI ID, reason
- [ ] Automatic alerts for unusual access patterns
- [ ] Encrypt backups with separate keys
- [ ] Key rotation every 90 days documented
- [ ] Disaster recovery tested (can restore encrypted data)
```

**Clinical Workflow Task:**
```
T-3.2.2: Build medication order interface
Acceptance Criteria:
- [ ] Check drug interactions before order
- [ ] Warn if dosage is outside normal range
- [ ] Require prescriber's digital signature (PKI)
- [ ] Prevent unsigned orders from reaching pharmacy
- [ ] Log reason for order creation
- [ ] Log any modifications or cancellations
- [ ] Provide audit trail for quality improvement (not individual doctor reporting)
- [ ] Integrate with pharmacy system (EDI or HL7)
```

**FDA Validation Task** (if device software):
```
T-3.2.3: Implement FDA-required change control
Acceptance Criteria:
- [ ] Every code change has associated requirement (traceability)
- [ ] Every change triggers automated test suite
- [ ] Every change documented with clinical impact assessment
- [ ] Changes to clinical algorithms require FDA notified body review
- [ ] Post-market update tracking (version history immutable)
- [ ] IEC 62304 evidence package generated automatically
- [ ] Vendor assessment completed (BAA in place)
- [ ] Risk management per ISO 14971 (failure modes, mitigations)
```

### Extra Acceptance Criteria

Every healthcare feature should have:
- **HIPAA Assessment:** Which HIPAA rules does this satisfy/implicate?
- **FDA Classification** (if applicable): Class I/II/III device? Software critical for diagnosis?
- **IEC 62304 Alignment:** Where in the software lifecycle does this fit?
- **Audit Trail:** Every access to PHI logged immutably
- **Encryption:** All PHI encrypted in transit and at rest
- **Access Control:** Role-based, with audit trail
- **Clinical Validation:** Has clinician verified this is correct/safe?

### Clarification Questions to Ask

```
1. "Is this software a medical device (FDA regulated)?
   - No, it's just an administrative tool (lower scrutiny)
   - Yes, it's used for clinical decision-making (Class II minimum)
   - Yes, and critical for patient safety (Class III, highest scrutiny)"

2. "Which regulations apply?
   - HIPAA (US healthcare)
   - GDPR (EU healthcare)
   - FDA 21 CFR Part 11 (electronic records)
   - PIPEDA (Canada)
   - Multiple: [specify]"

3. "What's the data retention policy?
   - Keep forever (defensive, most common)
   - Delete after X years (data minimization)
   - Patient request (GDPR right to deletion)"

4. "Who are the users?
   - Clinicians (doctors, nurses, therapists)
   - Administrative staff
   - Patients (patient portal access)
   - Researchers (de-identified access)
   - Multiple roles with different permissions: [specify]"
```

---

## SaaS/B2B Decomposition Pattern

### Why It's Different
SaaS platforms serve multiple customers (tenants). Each tenant's data must be isolated from others. Users have roles and permissions. Billing is tied to feature usage. Integrations with external systems (payment processors, data warehouses, etc.) are common.

### Mandatory Epics

**1. Multi-Tenancy Epic**
- Tenant isolation (data cannot leak between tenants)
- Tenant configuration (custom settings, branding)
- Per-tenant billing & metering
- Tenant administration (user management, audit trails)

**2. Authentication & Authorization Epic**
- User login (SSO, SAML, OAuth)
- Role-based access control (RBAC)
- Permission enforcement (API and UI level)
- Audit trail of access

**3. Billing Integration Epic**
- Metering (track feature usage: API calls, storage, etc.)
- Billing (charge based on usage or plan tier)
- Payment processing (Stripe, PayPal, etc.)
- Invoice generation & delivery

**4. API & Webhooks Epic**
- RESTful API for programmatic access
- Webhook support (notify customer of events)
- API authentication (API keys, OAuth)
- Rate limiting & quotas

**5. Observability Epic**
- Logging (what happened)
- Monitoring (system health)
- Alerting (when things break)
- Audit trails (compliance & debugging)

### Common Features

| Feature | Notes |
|---------|-------|
| Tenant Onboarding | New customer signs up, workspace created, isolated from others. |
| User Management | Admin manages team members, roles, permissions. Per-tenant. |
| RBAC System | Enforce permissions: "can user X access resource Y?" |
| API Authentication | Customers authenticate with API keys or OAuth. |
| Usage Metering | Track API calls, storage, compute, charge accordingly. |
| Billing Dashboard | Show usage, costs, invoices, payment method. |
| Webhook Delivery | Notify customer when events happen (order placed, payment failed). |
| Data Export | Customers can export their data (GDPR compliance). |

### Task Patterns

**Tenant Isolation Task:**
```
T-4.1.1: Implement tenant isolation in database
Acceptance Criteria:
- [ ] Every table has tenant_id column
- [ ] Every query filters by tenant_id (prevent cross-tenant data leak)
- [ ] RLS (Row-Level Security) enforced at database level
- [ ] Audit logs show which queries accessed which tenant data
- [ ] Test: Can user from Tenant A ever see Tenant B data? (No)
- [ ] Backup/restore: Can admin accidentally expose Tenant B data when restoring Tenant A? (No)
- [ ] Analytics queries: Can't leak aggregate stats across tenants
```

**RBAC Task:**
```
T-4.2.1: Build permission checking system
Acceptance Criteria:
- [ ] Define role hierarchy (Admin > Manager > User)
- [ ] Define permissions (create_report, delete_report, view_settings, etc.)
- [ ] Enforce at API level (every endpoint checks permission)
- [ ] Enforce at UI level (hide buttons user can't use)
- [ ] Cache permissions (not querying DB for every request)
- [ ] Audit every permission check (for debugging)
- [ ] Support custom roles (tenants can define own role types)
- [ ] Detect privilege escalation (admin alerts if user gets suddenly elevated)
```

**Usage Metering Task:**
```
T-4.3.1: Implement API call metering
Acceptance Criteria:
- [ ] Count API calls per tenant, per day/month
- [ ] Report to billing system (tenant used 10k calls this month)
- [ ] Enforce quota (reject calls after limit reached)
- [ ] Quota is soft (customer can exceed, will be charged overage)
- [ ] Query latency not affected by metering (use async tracking)
- [ ] Meter is accurate (no off-by-one errors, retry-safe)
- [ ] Customer sees usage in real-time (UI shows "1,245 / 10,000 calls used")
- [ ] Billing can query meter data (for invoice generation)
```

**Webhook Task:**
```
T-4.5.1: Build webhook delivery system
Acceptance Criteria:
- [ ] Tenant configures webhook URLs (where to send events)
- [ ] System sends HTTP POST when event happens
- [ ] Retry on failure (exponential backoff, 24-hour window)
- [ ] Webhook signature (tenant can verify message authenticity)
- [ ] Webhook logs (tenant can see delivery status, response)
- [ ] Signature algorithm documented (HMAC-SHA256)
- [ ] No sensitive data in webhook (customer must query API for full details)
- [ ] Performance: <100ms webhook queue latency (don't block main request)
```

### Extra Acceptance Criteria

Every SaaS feature should have:
- **Tenant Isolation:** Can user A see user B's data? (Must be no)
- **Permission Enforcement:** Is permission checked at API level AND UI level?
- **Metering:** If usage-based billing, is this feature metered?
- **Audit Trail:** Is important action logged for compliance?
- **Rate Limiting:** Is this feature protected from abuse?
- **Multi-Tenancy:** Are there any hard-coded tenant assumptions?

### Clarification Questions to Ask

```
1. "What's the authentication method?
   - Username/password (self-hosted)
   - SSO (SAML, OAuth) for enterprise customers
   - Both (different tiers)"

2. "What's the permission model?
   - Simple (admin vs user)
   - Complex (custom roles per tenant)
   - Attribute-based (permissions based on user attributes)"

3. "How is billing handled?
   - Fixed monthly fee (easier)
   - Usage-based (need metering)
   - Hybrid (fixed + overage charges)"

4. "Do you need webhooks or just REST API?
   - REST API only (customer pulls data)
   - Webhooks (we push events to customer)
   - Both"
```

---

## MOBILE APP Decomposition Pattern

### Why It's Different
Mobile apps run on diverse devices with varying network conditions. Users expect instant load times and smooth animations. Mobile-specific concerns (offline support, battery usage, push notifications, app store guidelines) are non-negotiable. Platform differences (iOS vs Android) multiply development effort.

### Mandatory Epics

**1. Platform Strategy Epic**
- Decision: native iOS/Android, cross-platform (React Native, Flutter), or hybrid?
- If multi-platform: shared business logic vs platform-specific UI?
- App store compliance (guidelines for iOS, Google Play)

**2. Offline Support Epic**
- Work without internet connection
- Sync when connection restored
- Conflict resolution (offline change + server change)

**3. Push Notifications Epic**
- FCM (Firebase Cloud Messaging) for Android
- APNs (Apple Push Notification service) for iOS
- User permission management
- Notification display (badge, sound, vibration)

**4. Performance & Optimization Epic**
- App size (binary bloat kills download rates)
- Battery usage (excessive background work kills user retention)
- Network efficiency (minimize data transfer)
- Animation smoothness (60 FPS on older devices)

**5. App Store Compliance Epic**
- iOS App Store review (Apple has strict guidelines)
- Google Play store review (slightly more lenient)
- Privacy policy (GDPR, CCPA compliance)
- In-app purchases (if monetized)

### Common Features

| Feature | Notes |
|---------|-------|
| Offline Mode | Core features work without internet. Sync on reconnect. |
| Push Notifications | Server sends notifications. App displays them. |
| Local Storage | Cache data locally (SQLite, Realm, NSUserDefaults). |
| Authentication | Store token securely (Keychain/Keystore, not SharedPreferences). |
| Deep Linking | Handle: myapp://product/123 URLs (from notifications, social sharing). |
| Crash Reporting | Send crash logs to server (Sentry, Firebase). |
| Analytics | Track user behavior (events, sessions, funnels). |
| Background Sync | Sync data with server even when app is closed. |

### Task Patterns

**Platform-Specific Implementation Task:**
```
T-5.1.1: Implement iOS login screen
Acceptance Criteria:
- [ ] Design follows iOS HIG (Human Interface Guidelines)
- [ ] Face ID / Touch ID support (not just password)
- [ ] Keyboard type correct (email keyboard for email field)
- [ ] Auto-fill compatible (password managers work)
- [ ] Safe Area respected (notch on newer phones)
- [ ] Accessibility: VoiceOver compatible, text sizes respected
- [ ] Performance: <500ms to display screen
- [ ] Memory: <20MB (app size limit for cellular download)
```

**Offline Sync Task:**
```
T-5.2.1: Build offline-first data sync engine
Acceptance Criteria:
- [ ] App works offline (database local, no API required)
- [ ] When online: sync changes to server
- [ ] Conflict handling: last-write-wins (or custom logic)
- [ ] Offline queue: track queued changes, retry on network return
- [ ] Battery efficient: batch syncs, don't sync constantly
- [ ] Data consistency: never show stale data or latest server data depending on context
- [ ] Test: Simulate offline, make changes, go online, verify sync
- [ ] Test: Offline change + simultaneous server change (conflict resolution)
```

**Push Notification Task:**
```
T-5.3.1: Integrate Firebase Cloud Messaging (FCM)
Acceptance Criteria:
- [ ] Register device token with server when app launches
- [ ] Server sends push notifications via FCM
- [ ] Notification triggers local alert (banner, sound, vibration)
- [ ] User can tap notification (deep link to relevant screen)
- [ ] User can disable notifications (system settings respected)
- [ ] Notification doesn't wake device if user has Do Not Disturb on
- [ ] Payload encrypted (sensitive data not visible in system logs)
- [ ] Test: Uninstall/reinstall app, old tokens are cleaned up on server
```

**Battery Optimization Task:**
```
T-5.4.1: Optimize background sync for battery
Acceptance Criteria:
- [ ] Background sync only triggers on WiFi (not cellular)
- [ ] Sync bundled (don't sync every 5 minutes, batch it)
- [ ] Use system background fetch (not custom wake-ups)
- [ ] Stop sync if battery <20% (user's battery matters more)
- [ ] No location tracking while app is backgrounded
- [ ] Test battery impact: measure mAh before/after (should be <1% overhead)
- [ ] Document: "If you enable background sync, battery will decrease by X%"
```

### Extra Acceptance Criteria

Every mobile feature should have:
- **Platform Compliance:** Follows iOS HIG or Material Design
- **Offline Capability:** What works offline? What requires internet?
- **Performance:** <500ms load time, 60 FPS animations, <50MB app size
- **Battery Impact:** Does this drain battery? Can we optimize?
- **Accessibility:** VoiceOver/TalkBack support, text size scaling
- **Security:** Sensitive data stored securely (Keychain, not SharedPreferences)
- **Network Efficiency:** Minimize data transfer, use compression

### Clarification Questions to Ask

```
1. "What's the platform strategy?
   - iOS only
   - Android only
   - Both iOS + Android (native for each)
   - Both (cross-platform like React Native)"

2. "What's your offline strategy?
   - Online only (no offline support)
   - Read-only offline (cache data, read it offline)
   - Offline-first (full functionality offline, sync when online)"

3. "What's your monetization?
   - Free (supported by ads? subscriptions? none?)
   - Paid upfront
   - In-app purchases
   - Subscription"

4. "What are your size constraints?
   - <50MB (fits in smaller storage)
   - <100MB (standard, fits on older devices)
   - No constraint (bigger is OK)"
```

---

## AI/ML PRODUCT Decomposition Pattern

### Why It's Different
ML products have unique concerns: data quality matters more than code quality. Model drift (performance degrades over time) requires monitoring. Privacy and bias are critical. Training pipelines are separate from serving pipelines. A/B testing is essential for validating improvements.

### Mandatory Epics

**1. Data Pipeline Epic**
- Data ingestion (collect raw data)
- Data cleaning & preprocessing
- Feature engineering (transform data for model)
- Data validation (ensure quality)

**2. Model Training Epic**
- Training pipeline (how to train models)
- Hyperparameter tuning (find best settings)
- Version control (track model versions)
- Experiment tracking (which model config gave best results?)

**3. Model Serving Epic**
- Inference API (serve predictions at scale)
- Model deployment (get model into production)
- Canary deployment (roll out gradually, detect issues)
- Model serving latency (inference <100ms)

**4. Monitoring & Bias Detection Epic**
- Model monitoring (is accuracy degrading?)
- Bias monitoring (is model fair across demographics?)
- Data drift detection (is production data different from training data?)
- Retraining triggers (automatically retrain when accuracy drops)

**5. Feedback Loop Epic**
- Collect predictions & ground truth (did model predict right?)
- Label new data (humans verify predictions)
- Retrain with new data (model improves over time)

### Common Features

| Feature | Notes |
|---------|-------|
| Feature Store | Centralized storage of features (reusable across models). |
| Model Registry | Version control for models (track all trained models). |
| Experiment Tracking | Log model performance, hyperparameters, data version. |
| Inference API | REST endpoint: POST prediction_request → model_output |
| A/B Testing | Serve Model A to 50% users, Model B to 50%, compare results. |
| Model Monitoring | Alert if accuracy <threshold or latency >SLA. |
| Bias Testing | Test fairness: does model perform equally across groups? |
| Data Validation | Detect when new data violates schema or distribution. |

### Task Patterns

**Data Pipeline Task:**
```
T-6.1.1: Build data ingestion pipeline
Acceptance Criteria:
- [ ] Ingest from sources: databases, APIs, files
- [ ] Validate schema (expected columns, types present)
- [ ] Detect outliers (flag suspicious data)
- [ ] Store raw data in data lake (immutable)
- [ ] Lineage: track which data went into which model version
- [ ] Idempotent: re-running ingestion doesn't duplicate data
- [ ] Error handling: skip corrupted records, log for review
- [ ] Monitoring: alerts if data pipeline fails
```

**Feature Engineering Task:**
```
T-6.1.2: Implement feature engineering
Acceptance Criteria:
- [ ] Transform raw data into features (e.g., normalize, one-hot encode)
- [ ] Store features in feature store (reusable)
- [ ] Version features (feature_v1, feature_v2, etc.)
- [ ] Document features: what each feature means
- [ ] Test: verify feature distribution matches training data
- [ ] Performance: feature computation <1 second for inference
- [ ] Offline: can compute features for batch predictions
- [ ] Online: can compute features in real-time for API predictions
```

**Model Training Task:**
```
T-6.2.1: Build model training pipeline
Acceptance Criteria:
- [ ] Load training data, features, labels
- [ ] Train model (could be days for large datasets)
- [ ] Track hyperparameters (learning rate, epochs, etc.)
- [ ] Log metrics (accuracy, F1, AUC on test set)
- [ ] Version model (save as model_v123)
- [ ] Reproducibility: same input data/seeds = same model
- [ ] Validation: split data (train 70%, val 15%, test 15%)
- [ ] Experiment tracking: log to MLflow or similar
```

**Model Serving Task:**
```
T-6.3.1: Build inference API
Acceptance Criteria:
- [ ] REST endpoint: POST /predict with features
- [ ] Model loaded in memory (not loaded from disk per request)
- [ ] Batch prediction: POST /predict_batch with multiple records
- [ ] Response: prediction + confidence + latency <100ms
- [ ] Versioning: can serve multiple model versions (A/B testing)
- [ ] Monitoring: log every prediction (for bias/drift monitoring)
- [ ] Error handling: model not ready, invalid input, server error
- [ ] Scalability: serve 1000 requests/second (scale based on requirements)
```

**Model Monitoring Task:**
```
T-6.4.1: Implement model monitoring
Acceptance Criteria:
- [ ] Track prediction accuracy (ground truth from user feedback)
- [ ] Alert if accuracy <80% (detect model degradation)
- [ ] Track model drift (compare training vs production data)
- [ ] Detect data drift: production data differs from training data
- [ ] Bias monitoring: model fairness across demographics (gender, age, etc.)
- [ ] Latency monitoring: alert if inference >200ms
- [ ] Automatic retraining: if accuracy <80%, trigger retraining pipeline
- [ ] Dashboard: show model health, accuracy trends, alerts
```

**A/B Testing Task:**
```
T-6.5.1: Build A/B testing framework
Acceptance Criteria:
- [ ] Route users: 50% get Model A, 50% get Model B
- [ ] Randomization: same user always gets same model (reproducible)
- [ ] Metrics tracking: track accuracy/conversion per model
- [ ] Statistical testing: confidence intervals for improvement
- [ ] Duration: minimum 1 week (account for weekly seasonality)
- [ ] Winner declaration: automatically pick best model when significant
- [ ] Revert capability: can revert to previous model if issues
- [ ] Logging: every prediction tagged with experiment ID
```

### Extra Acceptance Criteria

Every ML feature should have:
- **Data Quality:** Training data validated, no corruption
- **Monitoring:** Accuracy, latency, bias, data drift tracked
- **Reproducibility:** Same input = same output (for debugging)
- **A/B Testing:** New models tested before production rollout
- **Bias Testing:** Performance fair across demographic groups
- **Latency:** Inference <100ms (production SLA)
- **Versioning:** All models, data, code versions tracked

### Clarification Questions to Ask

```
1. "What's the prediction target?
   - Classification (predict category)
   - Regression (predict number)
   - Ranking (rank candidates by relevance)
   - Clustering (group similar items)"

2. "What's your accuracy/latency tradeoff?
   - High accuracy is critical, latency can be 1-2 seconds
   - Both critical: <95% accuracy, <100ms latency"

3. "How will you collect ground truth?
   - User feedback (user tells us if prediction was right)
   - Manual labeling (humans verify)
   - Implicit feedback (user behavior indicates correctness)"

4. "What's your bias testing strategy?
   - No bias testing (risky)
   - Test fairness across gender/age/geography
   - Custom fairness metrics: [specify]"
```

---

## GAMING Decomposition Pattern

### Why It's Different
Gaming is about engagement and experience. Technical excellence is required, but it serves gameplay. Performance is critical (60 FPS expected). User behavior is different (compete, cooperate, spend money). Monetization (ads, in-app purchases) shapes design.

### Mandatory Epics

**1. Game Loop/Core Mechanics Epic**
- Game loop (physics, input, rendering per frame)
- Core gameplay (what does the player do?)
- Progression system (levels, XP, unlocks)
- Difficulty balancing

**2. Asset Pipeline Epic**
- 3D models, sprites, audio
- Performance optimization (LOD, texture compression)
- Animation system
- UI/UX design

**3. Multiplayer/Networking Epic** (if applicable)
- Network protocol (real-time vs turn-based)
- Lag compensation (make game feel responsive despite network)
- Player matching (find opponents)
- Chat & social

**4. Monetization Epic** (if applicable)
- In-app purchases (cosmetics, power-ups, season pass)
- Ad integration (rewarded ads for in-game currency)
- Pricing strategy (how much stuff costs)
- Anti-cheat (prevent players from cheating to avoid spending)

**5. Analytics & Engagement Epic**
- Funnel analysis (how many players reach level 10?)
- Monetization tracking (ARPU, LTV, conversion rate)
- A/B testing (new mechanic increases engagement?)
- Retention metrics (are players coming back?)

### Common Features

| Feature | Notes |
|---------|-------|
| Physics System | Gravity, collision, movement simulation. |
| Input Handling | Keyboard, controller, touch input. |
| Rendering | Graphics engine, lighting, post-processing. |
| Audio System | Background music, SFX, voice acting. |
| Save System | Save/load game state (local storage). |
| Shop System | Buy cosmetics, power-ups with in-game or real currency. |
| Leaderboards | Track top players globally or by friends. |
| Social | Friend lists, guild/clan system, chat. |

### Task Patterns

**Performance Task:**
```
T-7.1.1: Optimize rendering for 60 FPS
Acceptance Criteria:
- [ ] Target: 60 FPS on mid-range devices (60fps, not 30fps)
- [ ] Measure: frame time <16.6ms per frame
- [ ] Profiling: identify bottlenecks (CPU, GPU, memory)
- [ ] Optimization: reduce draw calls, use LOD, reduce resolution if needed
- [ ] Memory: <200MB on low-end devices
- [ ] Battery: doesn't drain excessively (monitor mAh)
- [ ] Test: verify 60 FPS on target devices (iPhone 10, Galaxy S10, etc.)
- [ ] Regression: new feature doesn't drop FPS below 55
```

**Gameplay Balance Task:**
```
T-7.2.1: Balance difficulty progression
Acceptance Criteria:
- [ ] Design difficulty curve (easy early, hard late)
- [ ] Play-test with target audience (measure fun, challenge, frustration)
- [ ] Adjust: difficulty based on feedback
- [ ] Metrics: measure player completion rate (want >70% of players beat final level)
- [ ] Spike detection: identify difficulty spikes where players quit
- [ ] Pacing: levels ~5-15 minutes each (right length)
- [ ] Reward: progression feels rewarding (frequent unlocks, not too sparse)
- [ ] A/B test: test difficulty variations on subsets of players
```

**Monetization Task:**
```
T-7.4.1: Implement in-app purchases
Acceptance Criteria:
- [ ] Shop UI: display items, prices, buy button
- [ ] Purchase flow: verify payment, give item, update inventory
- [ ] Pricing: cosmetics cheap ($1), season pass mid ($10), battle pass seasonal
- [ ] Never pay-to-win: players can't buy power for real money (or cosmetics only)
- [ ] Progression: free players can reach same end-game as paying players
- [ ] Monetization check: ARPU >$1 per user (adjust prices if not hitting target)
- [ ] Regional pricing: adjust for purchasing power (cheaper in India)
- [ ] Anti-fraud: detect and prevent fraudulent purchases
```

**Multiplayer Networking Task:**
```
T-7.3.1: Implement lag compensation
Acceptance Criteria:
- [ ] Network latency typical: 50-150ms (RTT)
- [ ] Input prediction: predict player action, execute locally immediately
- [ ] Server reconciliation: correct if server says different
- [ ] Feels responsive: even on high-latency connections (<500ms)
- [ ] Fairness: both players have similar latency experience
- [ ] Bandwidth: <100KB per second per player (mobile-friendly)
- [ ] Test: simulate high latency (200ms), verify playable
- [ ] Attack resistance: prevent players from cheating by spoofing packets
```

### Extra Acceptance Criteria

Every game feature should have:
- **Performance:** FPS target (usually 60), memory budget (<200MB), battery impact
- **Game Feel:** Responsive controls, satisfying feedback (sound, visual)
- **Balancing:** Difficulty appropriate, progression rewarding
- **Monetization:** If paid, ensure fair pricing and no pay-to-win
- **Multiplayer Fairness:** If competitive, lag compensation and anti-cheat
- **Engagement:** Metrics show feature increases retention

### Clarification Questions to Ask

```
1. "What's the target platform?
   - Console (PS5, Xbox)
   - PC (Steam)
   - Mobile (iOS, Android)
   - Multiple: [specify]"

2. "What's the monetization model?
   - Free-to-play (ads + cosmetics)
   - Premium upfront ($20-60)
   - Subscription (battle pass)
   - Hybrid: [specify]"

3. "Is this competitive multiplayer?
   - Single-player only
   - Co-op (play together)
   - PvP (play against each other, need anti-cheat)
   - MMO (massive multiplayer)"

4. "What's your target ARPU (average revenue per user)?
   - Not monetized (free)
   - Casual games: $0.50 - $2
   - Mobile games: $5 - $20
   - Console games: $10 - $50"
```

---

## E-COMMERCE Decomposition Pattern

### Why It's Different
E-commerce is about converting browsers into buyers. Every feature should support the conversion funnel. Performance matters (slow pages lose customers). Inventory management is critical (can't sell what you don't have). Payments and shipping are complex. Reviews/recommendations affect purchasing decisions.

### Mandatory Epics

**1. Product Catalog Epic**
- Product data (name, description, images, SKU)
- Inventory management (stock levels, warnings)
- Search & filtering (help customers find products)
- Product reviews & ratings

**2. Cart & Checkout Epic**
- Shopping cart (add/remove items)
- Checkout flow (billing, shipping address)
- Payment processing (safe, PCI-compliant)
- Order confirmation

**3. Order Management Epic**
- Order tracking (where's my package?)
- Order history (past purchases)
- Returns/refunds
- Customer service integration

**4. Personalization Epic**
- Recommendations (show relevant products)
- Search ranking (show best-selling items first)
- Email marketing (cart abandonment, product recommendations)

**5. Performance & SEO Epic**
- Page load time (<3 seconds target)
- Mobile optimization
- SEO for discoverability
- Analytics (understand user behavior)

### Common Features

| Feature | Notes |
|---------|-------|
| Product Pages | High-quality images, detailed descriptions, customer reviews. |
| Search | Full-text search, faceted filtering (brand, price, rating). |
| Recommendations | "Customers also bought..." suggestions. |
| Cart | Add items, change quantities, remove items. |
| Checkout | Guest or registered checkout, payment methods. |
| Order Tracking | Real-time status, shipping carrier integration (FedEx, UPS). |
| Customer Reviews | Ratings, written reviews, verification (bought it). |
| Wishlist | Save items for later. |

### Task Patterns

**Product Page Task:**
```
T-8.1.1: Build product detail page
Acceptance Criteria:
- [ ] Display product images (gallery, zoom)
- [ ] Product information (name, SKU, price, description)
- [ ] Stock status (In Stock, Low Stock, Out of Stock)
- [ ] Customer reviews (ratings, written reviews)
- [ ] Recommendations: "Customers also bought" section
- [ ] Related products: similar items
- [ ] Add to cart button (large, prominent)
- [ ] Performance: page loads <2 seconds
- [ ] SEO: product name in title, description in meta
- [ ] Mobile: responsive design, touch-friendly buttons
```

**Search & Filtering Task:**
```
T-8.2.1: Implement product search
Acceptance Criteria:
- [ ] Search box: find products by name/SKU
- [ ] Results: show best-selling first (not random)
- [ ] Facets: filter by price, brand, rating, etc.
- [ ] Performance: search results <500ms (use index)
- [ ] Typo tolerance: "teh product" matches "the product"
- [ ] Ranking: boost bestsellers, discount items
- [ ] No results: "We don't have this. Try [suggestions]"
- [ ] Analytics: log searches (find gaps in catalog)
```

**Checkout Flow Task:**
```
T-8.3.1: Build checkout page
Acceptance Criteria:
- [ ] Shipping address: collect/validate address
- [ ] Billing address: same as shipping or different?
- [ ] Shipping method: Standard (5-7 days), Express (2-3 days), Overnight
- [ ] Shipping cost: calculate based on weight, distance
- [ ] Tax: calculate based on shipping address
- [ ] Payment method: credit card, PayPal, Apple Pay, Google Pay
- [ ] Order review: show items, prices, total before final confirmation
- [ ] Guest checkout: don't require account
- [ ] Mobile: mobile-optimized checkout (high cart abandonment on mobile)
- [ ] Security: PCI-DSS compliance, no full card numbers stored
```

**Product Recommendations Task:**
```
T-8.4.1: Build recommendation engine
Acceptance Criteria:
- [ ] Collaborative filtering: "Users who bought X also bought Y"
- [ ] Content-based: "Similar products" (same category, price range)
- [ ] Ranking: show highest-margin items first (business priority)
- [ ] Personalization: different recommendations per user
- [ ] A/B testing: test recommendation algorithm variants
- [ ] Performance: recommendation API <100ms (don't block page load)
- [ ] Coverage: if user is new (no history), show bestsellers
- [ ] Monitoring: track CTR (click-through rate) on recommendations
```

### Extra Acceptance Criteria

Every e-commerce feature should have:
- **Conversion Impact:** Does this feature increase sales? (measure)
- **Performance:** Page load <3 seconds, checkout mobile-optimized
- **Payment Security:** PCI-DSS compliant, no full card data stored
- **Mobile Friendly:** Optimized for mobile (60% of traffic)
- **SEO:** Product pages discoverable, structured data (schema.org)
- **Analytics:** Track user behavior, conversion funnel

### Clarification Questions to Ask

```
1. "What's your inventory strategy?
   - Drop-shipping (supplier handles inventory)
   - Warehoused (you hold inventory)
   - Hybrid: [specify]"

2. "What payment methods are required?
   - Credit card only
   - Credit card + PayPal
   - Credit card + digital wallets (Apple Pay, Google Pay)
   - Multiple currencies/payment methods: [specify]"

3. "What's your shipping strategy?
   - Flat-rate shipping
   - Real-time rates (based on weight, address)
   - Free shipping over $X
   - Multiple carriers: [specify]"

4. "Do you need recommendations?
   - No recommendations
   - Basic (bestsellers, related products)
   - Advanced ML-based recommendations"
```

---

## Cross-Industry Common Epics

Most PRDs, regardless of industry, need these epics:

### Authentication & Authorization Epic
- User accounts (sign up, login)
- Roles & permissions (who can do what?)
- Password management (reset, strength requirements)
- Session management (logout, timeout)

**Why it matters:** Every app has users. Every user needs credentials.

### Observability Epic
- Logging (what happened in the system?)
- Monitoring (is the system healthy?)
- Alerting (notify ops when something breaks)
- Audit trails (compliance, debugging)

**Why it matters:** You can't fix what you can't see.

### CI/CD & Deployment Epic
- Automated tests (unit, integration, E2E)
- Build pipeline (compile, package, test)
- Deployment pipeline (stage, production)
- Rollback capability (revert to previous version)

**Why it matters:** Manual deployment is error-prone and slow.

### Testing Strategy Epic
- Unit tests (test individual functions)
- Integration tests (test components working together)
- End-to-end tests (test full user workflows)
- Performance tests (measure latency, throughput)
- Security tests (penetration testing, vulnerability scans)

**Why it matters:** Shipping bugs is expensive. Testing prevents them.

### Performance Optimization Epic
- Caching (in-memory, CDN, browser)
- Database optimization (indexes, query optimization)
- Asset optimization (image compression, minification)
- Load testing (find breaking point)

**Why it matters:** Slow apps lose users to competitors.

### Security Epic
- Authentication (verify users are who they claim)
- Authorization (verify users can do what they're trying)
- Encryption (data in transit and at rest)
- Input validation (prevent injection attacks)
- Dependency scanning (find vulnerable libraries)

**Why it matters:** Breaches are expensive. Prevention is cheaper.

---

## When Industry Patterns Don't Apply

Not every PRD fits neatly into an industry pattern. Use patterns as inspiration, not dogma.

**Questions to ask:**
- Is this PRD in a regulated industry?
- Are there mandatory compliance requirements?
- Are there unusual technical constraints (offline, battery, real-time)?
- Are there multi-user/multi-tenant requirements?
- Are there monetization concerns?

If the answer to any is "yes," check the relevant industry pattern. Otherwise, focus on the core requirements and don't add unnecessary epics.

## Summary

Industry-specific patterns ensure you decompose PRDs without missing critical requirements that are obvious to domain experts but invisible to outsiders. Use this guide to:

1. Identify the industry
2. Check that mandatory epics are present (or explicitly excluded)
3. Apply common feature and task patterns
4. Ask clarification questions specific to the industry
5. Add cross-industry epics that every product needs

A 20-minute investment in this guide now saves weeks of rework later.
