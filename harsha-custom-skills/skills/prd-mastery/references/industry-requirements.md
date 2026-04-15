# Industry-Specific PRD Requirements

Complete reference for regulated and specialized industry PRD requirements.

---

## Healthcare & Medical Devices

### FDA Design Controls (21 CFR 820.30)

Required documentation:

**Design Input**
```
- Intended use/indications for use
- User needs derived from clinical requirements
- Risk-based requirements (safety, performance)
- Applicable regulatory requirements
```

**Design Output**
```
- Device specifications
- Manufacturing specifications
- Quality acceptance criteria
- Essential safety/performance characteristics
```

**Design History File (DHF)**
```
- Complete design and development records
- Design reviews documentation
- Verification and validation records
- All design changes with rationale
```

### IEC 62304 Software Safety Classification

| Class | Severity | Documentation Required |
|-------|----------|------------------------|
| A | No injury possible | Basic documentation |
| B | Non-serious injury | Moderate documentation |
| C | Death or serious injury | Full compliance, all processes |

**PRD Requirements by Class:**

Class A:
- Software requirements specification
- Traceability to system requirements

Class B:
- All Class A requirements
- Architecture documentation
- Risk management file

Class C:
- All Class B requirements
- Detailed design documentation
- Complete unit testing evidence
- Code coverage metrics

### HIPAA Compliance Sections

```markdown
## PHI Handling Requirements
- Data classification (PHI vs non-PHI)
- Encryption requirements (at rest: AES-256, in transit: TLS 1.2+)
- Access controls and audit logging
- Minimum necessary principle application
- BAA requirements for third parties

## Technical Safeguards
- Unique user identification
- Emergency access procedures
- Automatic logoff specifications
- Encryption and decryption requirements
- Audit controls
- Integrity controls
- Authentication requirements
```

### Medical Device PRD Template Sections

```markdown
## Regulatory Pathway
- [ ] 510(k) Substantial Equivalence
- [ ] De Novo Classification
- [ ] PMA (Premarket Approval)

## Device Classification
- Class: [I | II | III]
- Product Code: [FDA code]
- Regulation Number: [21 CFR reference]

## Clinical Requirements
- Intended use statement
- Indications for use
- Contraindications
- Warnings and precautions

## Risk Analysis (Design FMEA)
| Hazard | Cause | Effect | Severity | Probability | Risk Level | Mitigation |

## Biocompatibility (if applicable)
- Patient contact type
- Contact duration
- ISO 10993 testing requirements
```

---

## Fintech & Financial Services

### PCI-DSS Compliance Levels

| Level | Annual Transactions | Requirements |
|-------|---------------------|--------------|
| 1 | >6 million | External QSA audit, quarterly scans |
| 2 | 1-6 million | Annual SAQ, quarterly scans |
| 3 | 20K-1 million | Annual SAQ, quarterly scans |
| 4 | <20K | Annual SAQ recommended |

### Financial PRD Requirements

```markdown
## Payment Processing Requirements
- Card data handling (tokenization required)
- PCI-DSS scope and CDE boundaries
- Point-to-point encryption (P2PE)
- Key management procedures

## KYC/AML Requirements
- Customer identification program (CIP)
- Customer due diligence (CDD)
- Enhanced due diligence triggers
- Suspicious activity monitoring
- Reporting requirements (SARs, CTRs)

## Data Handling
- Financial calculation precision (decimal handling)
- Rounding rules (banker's rounding)
- Currency handling (ISO 4217 codes)
- Timezone considerations for transactions

## Audit Trail Requirements
- All financial transactions logged
- Immutable audit records
- Retention period: [7+ years typical]
- Tamper-evident logging

## Fraud Prevention
- Velocity checks
- Device fingerprinting
- Behavioral analysis
- 3D Secure authentication
- Transaction limits
```

### SOC 2 Trust Services Criteria

```markdown
## Security
- Logical and physical access controls
- System operations monitoring
- Change management

## Availability
- System availability commitments
- Disaster recovery
- Backup and restore

## Processing Integrity
- Data processing accuracy
- Error handling
- Quality assurance

## Confidentiality
- Data classification
- Encryption requirements
- Secure disposal

## Privacy
- Notice and consent
- Collection limitation
- Use, retention, and disposal
```

---

## Automotive Software

### ISO 26262 Functional Safety

**ASIL (Automotive Safety Integrity Level)**

| ASIL | Severity | Exposure | Controllability | Example |
|------|----------|----------|-----------------|---------|
| D | Life-threatening | High | Difficult | Steering, brakes |
| C | Life-threatening | High | Controllable | Airbags |
| B | Severe injury | Medium | Controllable | Lights |
| A | Light injury | Low | Easy | Infotainment |
| QM | No safety impact | - | - | Non-safety features |

### ASPICE (Automotive SPICE)

**Process Capability Levels:**
- Level 0: Incomplete
- Level 1: Performed
- Level 2: Managed (minimum OEM requirement)
- Level 3: Established (Daimler-Benz requirement)
- Level 4: Predictable
- Level 5: Optimizing

### Automotive PRD Requirements

```markdown
## Safety Classification
- ASIL Level: [A | B | C | D | QM]
- Safety goals derived from hazard analysis
- Safety requirements with ASIL inheritance

## Cybersecurity (ISO/SAE 21434)
- Threat analysis and risk assessment (TARA)
- Cybersecurity goals
- Cybersecurity requirements

## OTA Update Requirements (UN R156)
- Software identification
- Update validation
- Rollback capability
- Secure boot chain
- Update integrity verification

## V-Model Documentation
| Phase | Document |
|-------|----------|
| Requirements | SRS (Software Requirements Specification) |
| Architecture | SAD (Software Architecture Description) |
| Design | SDD (Software Detailed Design) |
| Implementation | Code + Unit Tests |
| Integration | Integration Test Report |
| Verification | Verification Report |
| Validation | Validation Report |
```

---

## Aviation Software (DO-178C)

### Development Assurance Levels (DAL)

| Level | Failure Condition | Probability | Objectives |
|-------|-------------------|-------------|------------|
| A | Catastrophic | ≤1×10⁻⁹ | 71 |
| B | Hazardous | ≤1×10⁻⁷ | 69 |
| C | Major | ≤1×10⁻⁵ | 62 |
| D | Minor | ≤1×10⁻³ | 26 |
| E | No Effect | - | 0 |

### DO-178C Requirements Hierarchy

```
System Requirements
    ↓
High-Level Requirements (HLR)
    ↓
Low-Level Requirements (LLR)
    ↓
Source Code
```

### Aviation PRD Requirements

```markdown
## Requirements Standards
- Requirements must be requirements-based (not code-based)
- Each requirement traceable to system requirement
- Derived requirements identified and justified

## High-Level Requirements (HLR)
- Functional behavior
- Performance criteria
- Timing constraints
- Memory constraints

## Low-Level Requirements (LLR)
- Data structures
- Algorithm specifications
- Interface definitions
- Error handling

## Verification Requirements
- Requirements-based test cases
- Structural coverage analysis (MC/DC for Level A)
- Independence requirements (by DAL)

## Configuration Management
- Problem reporting
- Change control
- Configuration identification
- Baseline management
```

### MIL-STD-498 (Defense)

**22 Data Item Descriptions including:**
- System/Subsystem Specification (SSS)
- Software Requirements Specification (SRS)
- Interface Requirements Specification (IRS)
- Software Design Description (SDD)
- Software Test Plan (STP)
- Software Test Description (STD)
- Software Test Report (STR)

---

## Gaming Industry

### Game Design Document (GDD) Structure

```markdown
# [Game Title] Design Document

## Executive Summary
- Genre
- Platform(s)
- Target audience
- Unique selling proposition

## Core Game Loop
[What players do repeatedly]
- Primary loop (moment-to-moment)
- Secondary loop (session-level)
- Tertiary loop (long-term progression)

## Design Pillars
[3-5 core principles guiding all decisions]
1. [Pillar 1]
2. [Pillar 2]
3. [Pillar 3]

## Player Properties & Mechanics
- Character abilities
- Progression systems
- Economy design
- Social features

## Level/World Design
- Environment themes
- Difficulty progression
- Content volume

## Monetization Strategy
- [ ] Premium (one-time purchase)
- [ ] Free-to-play with IAP
- [ ] Subscription
- [ ] Battle pass
- [ ] Cosmetic microtransactions

## Technical Requirements
- Target frame rate
- Minimum/recommended specs
- Network requirements (if multiplayer)

## Audio/Visual Direction
- Art style reference
- Audio design notes
- Music direction

## Development Milestones
| Milestone | Deliverables |
|-----------|--------------|
| Prototype | Core loop playable |
| Vertical Slice | Full quality segment |
| Alpha | Feature complete |
| Beta | Content complete |
| Gold | Release candidate |
```

---

## AI/ML Products

See `references/ai-era.md` for complete AI product PRD requirements.

### AI-Specific Sections Summary

```markdown
## Model Requirements
- Input/output specifications
- Accuracy/precision targets
- Latency constraints
- Cost per inference limits

## Training Data
- Data sources
- Labeling methodology
- Data quality standards
- Bias assessment

## Evaluation
- Benchmark datasets
- Evaluation metrics
- A/B testing methodology
- Continuous monitoring

## Safety & Ethics
- Bias testing requirements
- Explainability needs
- Hallucination handling
- Adversarial robustness
- Human oversight requirements
```

---

## Consumer Hardware/IoT

### Certification Requirements

| Certification | Region | Purpose | Cost Range |
|---------------|--------|---------|------------|
| FCC | USA | RF emissions | $3K-15K+ |
| CE | EU | Safety/EMC | $5K-20K |
| RoHS | EU | Hazardous substances | Part of CE |
| UL | USA | Safety | $5K-50K+ |

### Hardware PRD Requirements

```markdown
## Industrial Design
- Form factor specifications
- Material requirements
- Color/finish requirements
- Weight/size constraints

## Electrical Requirements
- Power consumption (active/standby/sleep)
- Battery specifications (if applicable)
- Voltage/current requirements
- Thermal limits

## Mechanical Requirements
- Environmental ratings (IP code)
- Drop test specifications
- Operating temperature range
- Humidity tolerance

## Connectivity
- Wireless protocols (Wi-Fi, BLE, Thread, Zigbee)
- Matter certification (if applicable)
- Antenna requirements
- Range specifications

## Manufacturing
- BOM cost target
- Target volumes
- Supply chain considerations
- DFM (Design for Manufacturing) notes

## Development Stages
| Stage | Purpose | Exit Criteria |
|-------|---------|---------------|
| POC | Feasibility | Core function works |
| EVT | Engineering Validation | Functional prototype |
| DVT | Design Validation | Pre-production units |
| PVT | Production Validation | Production-ready |
| MP | Mass Production | Ship to customers |
```

---

## E-commerce/Marketplace

### Three-Sided Marketplace PRD

```markdown
## Customer-Facing Requirements
- Discovery and search
- Product detail pages
- Cart and checkout
- Order tracking
- Returns/refunds

## Merchant-Facing Requirements
- Inventory management
- Order management
- Analytics dashboard
- Payout management
- Customer communication

## Fulfillment/Delivery Requirements
- Route optimization
- Status tracking
- Proof of delivery
- Exception handling

## Platform Requirements
- Search and ranking algorithms
- Pricing and fee structure
- Dispute resolution
- Fraud prevention
- Trust and safety
```

---

## Blockchain/Web3

### Smart Contract PRD Requirements

```markdown
## Contract Specifications
- Immutability considerations
- Upgrade patterns (if applicable)
- Gas optimization requirements

## Security Requirements
- Audit requirements
- Known vulnerability checks
- Reentrancy protection
- Access control

## Transparency
- Publicly auditable code
- Event logging requirements
- State visibility

## Execution Conditions
- Trigger conditions
- Failure handling
- Timeout behaviors

## Testing Requirements
- Mainnet fork testing
- Formal verification (if applicable)
- Economic attack simulation
```
