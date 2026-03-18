# Weighted Domain Detection System (v6) — Complete Catalog with Detection Methods

**Status**: Production | **Last Updated**: March 2026

Automatic domain mode activation based on codebase signal detection and confidence scoring. This system ensures handoff documentation speaks in the language of the domain—regulatory concepts, architectural patterns, compliance frameworks—rather than generic terms.

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Detection Framework](#detection-framework)
3. [Activation Thresholds](#activation-thresholds)
4. [Fintech Signal Catalog](#fintech-signal-catalog)
5. [Healthcare Signal Catalog](#healthcare-signal-catalog)
6. [Enterprise Signal Catalog](#enterprise-signal-catalog)
7. [Multi-Domain Stacking](#multi-domain-stacking)
8. [Edge Cases](#edge-cases)
9. [Scoring Worked Example](#scoring-worked-example)
10. [Implementation Notes](#implementation-notes)

---

## Quick Reference

**Point System** (from SKILL.md):
- **Tier 1 (Definitive)**: 10 points each — Unambiguous domain indicators
- **Tier 2 (Strong)**: 5 points each — Clear domain relevance
- **Tier 3 (Supporting)**: 2 points each — Corroborating signals
- **Tier 4 (Incidental)**: 1 point each — Weak but additive

**Activation Threshold**: ≥15 points for each domain (with ≥50% confidence floor)

**Multi-Domain Rule**: If both fintech AND enterprise score ≥15, both modes activate and stack.

---

## Detection Framework

The detector uses a three-tier weighted scoring system with explicit grep/glob patterns, code examples, and false positive warnings for each signal.

### Core Detection Rules

1. **Scan active code paths only** — exclude archived, disabled, or test-only modules (see Edge Cases)
2. **Require context for Tier 3+ signals** — a "payment" variable alone doesn't count
3. **Avoid false positives** — isolated occurrences in comments/filenames = 0 points
4. **Stack domains when multiple thresholds are exceeded** — fintech + enterprise = both documented
5. **Use grep/glob patterns provided** — precise detection, not approximation

### Confidence Scoring

Each domain receives a **domain confidence score** (0–100%) indicating detection certainty:

```
Confidence = (Total Signals Found / Possible Signals) × 100

High Confidence (≥ 80%): Strong domain signal presence
Medium Confidence (50–79%): Definite domain + supporting context
Low Confidence (< 50%): Single tier-1 signal without supporting context
```

**Documentation Impact:**
- High confidence (≥80%): Full domain mode, all sections expanded
- Medium confidence (50–79%): Core sections + note uncertainty in intro
- Low confidence (<50%): Minimal domain sections; recommend broader context from team

---

## Activation Thresholds

| Domain | Threshold | Behavior | Confidence Floor |
|--------|-----------|----------|------------------|
| Fintech | ≥ 15 | Activate fintech mode (APIs, payment flows, compliance) | ≥ 50% |
| Healthcare | ≥ 15 | Activate healthcare mode (HIPAA, PHI, clinical workflows) | ≥ 50% |
| Enterprise | ≥ 15 | Activate enterprise mode (multi-tenancy, SSO, audit) | ≥ 50% |
| Below threshold | < 15 | Use agnostic mode (generic best practices) | N/A |
| Multiple domains | 2+ ≥ 15 | Stack modes (all applicable modes activate together) | Each ≥ 50% |

When a codebase activates multiple domains, the documentation stacks them: agnostic foundation + fintech section + healthcare section, with explicit interaction zones (e.g., "Where fintech and healthcare meet: patient loans and credit bureau consent").

---

## Fintech Signal Catalog

Weighted toward **Indian fintech** signals because many codebases use Indian payment rails, RBI regulations, and Indian lenders.

### Tier 1: Definitive (10 points each)

Clear markers of fintech domain work, especially Indian-focused:

#### Signal: Indian Payment Gateway SDKs (Razorpay, Cashfree, PayTM, PhonePe)

**Rationale**: Control 80%+ of online payments in India; unmistakable fintech marker.

**Detection Pattern (grep):**
```bash
grep -r "razorpay\|cashfree\|paytm\|phonepe" requirements.txt package.json Gemfile
grep -r "import razorpay\|from razorpay\|require.*razorpay" --include="*.py" --include="*.js" --include="*.java"
```

**Code Examples (Positive Match):**
```python
# requirements.txt
razorpay==1.3.0
cashfree-pg==2.1.0

# payment.py
import razorpay
from cashfree_pg import Client
client = razorpay.Client(auth=("KEY_ID", "KEY_SECRET"))
```

**False Positive Warnings:**
- ✗ "razorpay" mentioned in comments only → Does NOT count
- ✗ Razorpay SDK in dev dependencies but never imported → Counts as Tier 1 (strong signal, even if unused)
- ✗ Old/archived version in requirements → Still counts (code may reference it)

**Points**: 10

---

#### Signal: Alternative Indian Payment Processors (JusPay, PayU, EaseBuzz, BillDesk)

**Rationale**: Established alternative Indian payment rails; definitive domain marker.

**Detection Pattern (grep):**
```bash
grep -r "juspay\|payu\|easebuzz\|billdesk" requirements.txt package.json Gemfile setup.py
grep -r "from juspay import\|import payu\|JusPayClient" --include="*.py" --include="*.js"
```

**Code Examples (Positive Match):**
```python
# payment_service.py
from juspay import JusPayClient
payu_gateway = PayU(merchant_id="MERCHANT123")

# requirements.txt
payu-sdk==2.0.1
billdesk-api==1.5.0
```

**False Positive Warnings:**
- ✗ JusPay mentioned in config file name only (e.g., `juspay_config.yml`) without actual SDK → Does NOT count as Tier 1; may count as Tier 3
- ✗ Test fixtures importing juspay for mock purposes → Still counts (indicates domain knowledge)

**Points**: 10

---

#### Signal: UPI Imports, NPCI References

**Rationale**: Unified Payments Interface (UPI) is India's real-time payment rail regulated by NPCI. Indicates payment infrastructure work at RBI level.

**Detection Pattern (grep):**
```bash
grep -r "upi\|npci\|upi_mandate\|vpa\|upi_id" --include="*.py" --include="*.js" src/ app/ lib/
grep -r "NPCITransaction\|UPIPayment\|UPIMandate" --include="*.py" --include="*.java"
```

**Code Examples (Positive Match):**
```python
# upi_handler.py
from npci_gateway import UPITransaction
class UPIPayment:
    def create_mandate(self, vpa, amount):
        transaction = NPCITransaction.create(vpa=vpa, type="UPI_MANDATE")
```

**False Positive Warnings:**
- ✗ "upi" as URL slug (e.g., `GET /api/upi-settings`) without payment logic → Does NOT count; context matters
- ✗ Variable named `upi_flag` in non-payment module → Needs context (is it payment-related?)

**Points**: 10

---

#### Signal: Aadhaar, PAN, GSTIN, IFSC Validation

**Rationale**: Indian identity and tax infrastructure. Unmistakable KYC/AML fintech marker.

**Detection Pattern (grep):**
```bash
grep -r "aadhaar\|pan_number\|gstin\|ifsc" --include="*.py" --include="*.js" src/ app/
grep -r "validate_aadhaar\|validate_pan\|pan_format\|ifsc_code" --include="*.py" --include="*.js"
grep -r "AadhaarValidator\|PanValidator" --include="*.java"
```

**Code Examples (Positive Match):**
```python
# kyc_validator.py
def validate_aadhaar(aadhaar_num):
    """Validates 12-digit Aadhaar number"""
    if len(aadhaar_num) != 12 or not aadhaar_num.isdigit():
        raise InvalidAadhaar()

class PANValidator:
    def validate(self, pan_code):
        # Pan format: AAAAA9999A
        pattern = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        return bool(re.match(pattern, pan_code))

# kyc.py
def process_kyc(aadhaar, pan, gstin, ifsc_code):
    # KYC flow using Indian identity docs
    aadhaar_verified = validate_aadhaar(aadhaar)
    ifsc_bank = validate_ifsc(ifsc_code)
```

**False Positive Warnings:**
- ✗ PAN mentioned in variable name but as abbreviation for something else (e.g., `pan=x, tilt=y` for 2D coordinates) → Does NOT count
- ✗ IFSC in config as a label (e.g., `IFSC_DB_HOST`) → Does NOT count without validation logic
- ✗ Test data containing fake Aadhaar numbers → Still counts (indicates domain work)

**Points**: 10

---

#### Signal: Credit Bureau Integration (CIBIL, Experian, CRIF)

**Rationale**: Credit score pull is core to lending decisioning in India. Unmistakable fintech domain work.

**Detection Pattern (grep):**
```bash
grep -r "cibil\|experian\|crif\|credit_score\|bureau" --include="*.py" --include="*.js" src/ app/
grep -r "CibilClient\|cibil_api\|ExperianAPI\|CrifScore" --include="*.py" --include="*.java"
grep -r "credit_pull\|bureau_integration\|score_fetch" --include="*.py" --include="*.js"
```

**Code Examples (Positive Match):**
```python
# credit_service.py
from cibil_api import CibilClient

class CreditScoreEngine:
    def __init__(self):
        self.cibil = CibilClient(api_key="KEY123")

    def fetch_score(self, pan):
        """Fetch credit score from CIBIL bureau"""
        response = self.cibil.get_score(pan=pan)
        return response.score

# models.py
class Applicant(db.Model):
    cibil_score = db.Column(db.Integer)
    experian_score = db.Column(db.Integer)
    bureau_check_date = db.Column(db.DateTime)
```

**False Positive Warnings:**
- ✗ "cibil" in config parameter name only (e.g., `CIBIL_ENABLED=true`) without actual API call → Tier 2, not Tier 1
- ✗ Comments referring to credit bureau without implementation → Does NOT count as Tier 1
- ✗ Test mocks of bureau API (for testing credit decisioning) → Still counts (indicates domain)

**Points**: 10

---

#### Signal: NBFC References, EMI Calculation, EMI Schedule, EMI Breakdown

**Rationale**: NBFC (Non-Banking Financial Company) and EMI (Equated Monthly Installment) calculations are core lending domain logic. Unmistakable fintech.

**Detection Pattern (grep):**
```bash
grep -r "nbfc\|emi\|equated_monthly\|repayment_schedule\|emi_breakdown" --include="*.py" --include="*.js" src/ app/
grep -r "class EMICalculator\|def calculate_emi\|emi_schedule" --include="*.py" --include="*.java"
grep -r "nbfc_compliance\|NBFC_DLG\|NBFCLender" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# emi_calculator.py
class EMICalculator:
    """Calculate equated monthly installment for loan products"""

    def calculate_emi(self, principal, rate_of_interest, tenure_months):
        """Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)"""
        r = rate_of_interest / (100 * 12)  # Monthly rate
        n = tenure_months
        emi = principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        return emi

    def generate_schedule(self, principal, emi, rate):
        """Generate full repayment schedule with breakdown"""
        schedule = []
        remaining = principal
        for month in range(1, n + 1):
            interest = remaining * (rate / 100 / 12)
            principal_part = emi - interest
            remaining -= principal_part
            schedule.append({
                'month': month,
                'emi': emi,
                'principal': principal_part,
                'interest': interest,
                'balance': max(0, remaining)
            })
        return schedule

# nbfc_lending.py
NBFC_DLG_COMPLIANCE = {
    'max_tenure': 60,  # RBI Digital Lending Guidelines
    'max_rate': 36,    # Legal max APR in India
}

class NBFCLender:
    def process_application(self, applicant):
        # NBFC compliance checks
        pass
```

**False Positive Warnings:**
- ✗ Variable named `emi` used in context unrelated to EMI (e.g., `emi=0.5` for some ratio) → Needs code context
- ✗ Comments mentioning EMI without actual calculation code → Does NOT count as Tier 1; may be Tier 3
- ✗ Test fixtures with fake EMI data → Still counts

**Points**: 10

---

### Tier 2: Strong (5 points each)

Patterns that strongly suggest fintech work without being definitive:

#### Signal: Razorpay Payment Flow Implementation (Payment IDs, Signatures, Webhooks)

**Rationale**: Indicates active Razorpay payment processing with webhook callback handling.

**Detection Pattern (grep):**
```bash
grep -r "razorpay_payment_id\|X-Razorpay-Signature\|razorpay.*webhook" --include="*.py" --include="*.js"
grep -r "webhook_signature_verify\|verify_razorpay_signature" --include="*.py" --include="*.java"
grep -rE "payment_id.*razorpay|razorpay.*payment_id" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# webhook_handler.py
from razorpay.constants import WEBHOOK_SECRET

@app.route('/webhook/razorpay', methods=['POST'])
def razorpay_webhook():
    data = request.json
    signature = request.headers.get('X-Razorpay-Signature')

    # Verify signature before processing
    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        json.dumps(data).encode(),
        hashlib.sha256
    ).hexdigest()

    if signature != expected_sig:
        return {'error': 'Invalid signature'}, 403

    payment_id = data['payload']['payment']['entity']['id']
    update_payment_status(payment_id, data)
    return {'status': 'received'}, 200
```

**False Positive Warnings:**
- ✗ Razorpay SDK imported but payment_id never used → Does NOT count
- ✗ Webhook handler that calls generic payment service (could work with any gateway) → May count as Tier 2, but verify Razorpay specificity
- ✗ Test webhook fixtures without real implementation → Still counts (strong signal of intent)

**Points**: 5

---

#### Signal: UPI Variable Naming (@okhdfcbank, VPA, UPI ID patterns)

**Rationale**: UPI-specific variable naming patterns (@bank_name format for Virtual Payment Address).

**Detection Pattern (grep):**
```bash
grep -r "@okhdfcbank\|@okaxis\|@okicici\|vpa\|upi_id" --include="*.py" --include="*.js" src/ app/
grep -r "borrower_vpa\|lender_vpa\|sender_vpa\|upi_beneficiary" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# upi_transfer.py
class UPITransfer:
    def initiate(self, sender_vpa, receiver_vpa, amount):
        """Send money via UPI using VPA (e.g., user@okhdfcbank)"""
        # sender_vpa = "john@okhdfcbank"
        # receiver_vpa = "merchant@okaxis"
        transaction = self.gateway.transfer(
            from_vpa=sender_vpa,
            to_vpa=receiver_vpa,
            amount=amount,
            txn_id=self.generate_txn_id()
        )
```

**False Positive Warnings:**
- ✗ VPA mentioned only in documentation or comments → Does NOT count
- ✗ Testing with hardcoded @okhdfcbank VPA without real implementation → Still counts
- ✗ Variable named `vpa` used for something other than UPI Virtual Payment Address → Needs code context

**Points**: 5

---

#### Signal: Fund Transfer Methods (IMPS, NEFT, RTGS, NACH, BBPS)

**Rationale**: Indian-specific fund transfer modes; indicates disbursement/payment logic.

**Detection Pattern (grep):**
```bash
grep -r "IMPS\|NEFT\|RTGS\|NACH\|BBPS" --include="*.py" --include="*.js" src/ app/
grep -rE "transfer_method.*NEFT|transfer_type.*IMPS|nach_mandate" --include="*.py"
grep -r "imps_account\|neft_settlement\|rtgs_transfer\|nach_debit" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# disbursement_service.py
from enum import Enum

class TransferMethod(Enum):
    IMPS = "IMPS"      # Immediate Payment Service (real-time, up to 2M)
    NEFT = "NEFT"      # National Electronic Funds Transfer (batch, next day)
    RTGS = "RTGS"      # Real Time Gross Settlement (>2M, real-time)
    NACH = "NACH"      # National Automated Clearing House (recurring)
    BBPS = "BBPS"      # Bharat Bill Payment System

class Disbursement:
    def initiate_transfer(self, recipient, amount, method=TransferMethod.IMPS):
        """Initiate fund transfer via specified method"""
        if method == TransferMethod.NACH:
            return self.setup_nach_mandate(recipient, amount)
        elif method == TransferMethod.IMPS:
            return self.imps_transfer(recipient, amount)
        # ... more methods

# models.py
class NAACHMandate(db.Model):
    mandate_id = db.Column(db.String(50), unique=True)
    borrower_account = db.Column(db.String(20))
    max_amount = db.Column(db.Integer)
    frequency = db.Column(db.String(20))  # Monthly, Quarterly
```

**False Positive Warnings:**
- ✗ NEFT mentioned in config name only (e.g., `NEFT_BATCH_TIME=2:30 AM`) without actual transfer logic → Does NOT count as Tier 1; may be Tier 3
- ✗ Constants defined but never used in transfer logic → Still counts (code structure indicates domain)
- ✗ Test data referencing NEFT → Still counts

**Points**: 5

---

#### Signal: Indian Address/Contact Data Structures (+91 Phone, 6-digit Pincode, MICR)

**Rationale**: Indian-specific data validation; appears in fintech KYC/account setup.

**Detection Pattern (grep):**
```bash
grep -r '"+91"' --include="*.py" --include="*.js" src/ app/
grep -r "validate_indian_phone\|pincode.*6\|pincode.*digit" --include="*.py"
grep -r "MICR\|ifsc_code" --include="*.py" --include="*.js"
```

**Code Examples (Positive Match):**
```python
# address_validator.py
import re

def validate_indian_phone(phone):
    """Validates Indian phone: +91 prefix + 10 digits"""
    pattern = r"^\+91[6-9]\d{9}$"
    return bool(re.match(pattern, phone))

def validate_pincode(pincode):
    """Validates Indian 6-digit pincode"""
    return len(pincode) == 6 and pincode.isdigit()

# kyc_data.py
class KYCData:
    phone = "+91-98765-43210"  # Indian phone format
    address_pincode = "560034"  # Bangalore
    bank_micr = "560090001"     # MICR for bank branch
```

**False Positive Warnings:**
- ✗ +91 phone prefix used in test fixtures only → Still counts
- ✗ Pincode validation for generic postal code (not specifically 6-digit Indian) → May NOT count
- ✗ MICR mentioned in comment without actual bank validation → Does NOT count as Tier 2

**Points**: 5

---

#### Signal: Lending State Machine (loan_disbursement, npa_status, dpd_tracking, recovery, moratorium)

**Rationale**: Loan state transitions and delinquency tracking; core lending domain logic.

**Detection Pattern (grep):**
```bash
grep -r "loan_status\|loan_disbursement\|npa_status\|dpd_tracking\|days_past_due" --include="*.py" --include="*.js" src/ app/
grep -r "LoanStatus\|class.*State.*Loan\|recovery_status\|moratorium" --include="*.py" --include="*.java"
grep -rE "Active|NPA|Closed|Recovery|Moratorium" --include="*.py" | grep -i loan
```

**Code Examples (Positive Match):**
```python
# loan_models.py
from enum import Enum

class LoanStatus(Enum):
    APPROVED = "APPROVED"
    DISBURSED = "DISBURSED"
    ACTIVE = "ACTIVE"
    NPA = "NPA"               # Non-Performing Asset
    UNDER_RECOVERY = "UNDER_RECOVERY"
    CLOSED = "CLOSED"
    MORATORIUM = "MORATORIUM"

class Loan(db.Model):
    status = db.Column(db.Enum(LoanStatus))
    disbursement_date = db.Column(db.DateTime)
    days_past_due = db.Column(db.Integer)
    npa_date = db.Column(db.DateTime)  # Marked as NPA if DPD > 180

    def mark_as_npa(self):
        """Mark loan as NPA if >180 DPD"""
        if self.days_past_due > 180:
            self.status = LoanStatus.NPA
            self.npa_date = datetime.now()

# recovery_service.py
class RecoveryService:
    def initiate_recovery(self, loan_id):
        """Start recovery process for defaulted loans"""
        loan = Loan.query.get(loan_id)
        loan.status = LoanStatus.UNDER_RECOVERY
```

**False Positive Warnings:**
- ✗ Generic task state machine with "status" field named "loan_status" without loan-specific logic → May NOT count
- ✗ Comments mentioning NPA without actual NPA marking code → Does NOT count as Tier 2
- ✗ Test fixtures with loan statuses → Still counts

**Points**: 5

---

#### Signal: Account Aggregator, FIU, FIP References (Open Banking)

**Rationale**: India's Account Aggregator Framework for open banking; indicates fintech integration.

**Detection Pattern (grep):**
```bash
grep -r "account_aggregator\|FIU\|FIP\|fiu_id\|fip_id\|aa_consent" --include="*.py" --include="*.js" src/ app/
grep -r "FIUConfig\|FIPIntegration\|AAConsent" --include="*.py" --include="*.java"
grep -r "consent_capture\|data_request\|account_link" --include="*.py" | grep -i aggregator
```

**Code Examples (Positive Match):**
```python
# account_aggregator.py
FIU_CONFIG = {
    'fiu_id': 'MYAPP_FIU',
    'api_endpoint': 'https://aa-gateway.rajabank.co.in',
}

class FIPIntegration:
    """Integration with Financial Information Provider (bank)"""

    def request_account_data(self, consent_handle, fip_id):
        """Request account data from FIP via AA framework"""
        pass

class AAConsent:
    """Account Aggregator Consent Management"""

    def capture_consent(self, customer_id, fips_requested):
        """Capture customer consent for data sharing"""
        consent = {
            'version': '1.0',
            'customer_id': customer_id,
            'fips': fips_requested,
            'purpose': 'LOAN_UNDERWRITING'
        }
        return self.aa_gateway.register_consent(consent)
```

**False Positive Warnings:**
- ✗ FIU/FIP mentioned only in config or comments → Does NOT count as Tier 2
- ✗ Test mocks of AA framework → Still counts
- ✗ AA reference in external library docs, not own code → Does NOT count

**Points**: 5

---

#### Signal: RBI References, GST Calculation, TDS/TCS, FLDG

**Rationale**: Indian regulatory framework references; indicates compliance awareness in fintech.

**Detection Pattern (grep):**
```bash
grep -r "RBI\|GST\|TDS\|TCS\|FLDG\|digital_lending" --include="*.py" --include="*.js" --include="*.md" src/ app/ docs/
grep -r "RBI_DLG\|DLG_2022\|gst_calculation\|tds_rate\|fldg_compliance" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# compliance_config.py
RBI_DLG_2022 = {
    'max_apr': 36,  # RBI Digital Lending Guidelines 2022
    'foreclosure_charges': 0,  # Not allowed
    'moratorium_required': True,
    'grievance_redressal_days': 30,
}

# tax_service.py
def calculate_gst(amount, gst_rate=18):
    """Calculate GST on amount"""
    return amount * (gst_rate / 100)

def calculate_tds(salary, rate=5):
    """Calculate Tax Deducted at Source"""
    return salary * (rate / 100)

def calculate_tcs(amount, rate=1):
    """Calculate Tax Collected at Source"""
    return amount * (rate / 100)

# compliance_audit.py
class ComplianceAudit:
    """Audit RBI DLG and GST compliance"""

    def check_apr_limit(self, loan):
        if loan.apr > RBI_DLG_2022['max_apr']:
            return False  # Non-compliant
```

**False Positive Warnings:**
- ✗ RBI mentioned in README or comments without actual code implementation → Does NOT count as Tier 2; may be Tier 3
- ✗ GST as generic tax calculation (not India-specific) → Needs Indian context
- ✗ Historical references to old RBI guidelines → Still counts (indicates domain)

**Points**: 5

---

### Tier 3: Supporting (2 points each)

Generic financial patterns common in fintech:

#### Signal: Payment, Transaction, Settlement (Core Fintech Concepts)

**Rationale**: Foundational fintech terms, but generic; require payment gateway or fintech context.

**Detection Pattern (grep):**
```bash
grep -r "def payment\|class Payment\|payment_id\|payment_status" --include="*.py" --include="*.js" src/ app/
grep -r "transaction\|settlement\|reconcile" --include="*.py" | head -20
```

**Code Examples (Positive Match):**
```python
# payment_service.py
def process_payment(amount, method):
    """Process payment transaction"""
    transaction = create_transaction(amount=amount, method=method)
    return transaction

class Settlement:
    def reconcile_daily(self):
        """Settle payments and reconcile"""
```

**False Positive Warnings:**
- ✗ Generic "payment" variable in non-fintech module (e.g., `payment=method` for display) → Does NOT count
- ✗ "transaction" as database transaction, not payment transaction → Does NOT count
- ✗ Must appear in payment gateway context (import razorpay, etc.) or webhook handler

**Points**: 2 (only when paired with Tier 1/2 signals)

---

#### Signal: Checkout, Cart, Order, Refund, Chargeback

**Rationale**: E-commerce/payment patterns; generic without payment infrastructure context.

**Detection Pattern (grep):**
```bash
grep -r "checkout\|shopping_cart\|order_status\|refund\|chargeback" --include="*.py" --include="*.js" src/ app/
grep -r "class Order\|def refund" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# order_service.py
class Order:
    status_choices = ['pending', 'paid', 'shipped', 'refunded']

    def refund(self):
        """Refund order amount"""
        self.status = 'refunded'
```

**False Positive Warnings:**
- ✗ Shopping cart in e-commerce app without payment integration → Does NOT count as fintech
- ✗ Generic order status without payment processing → May NOT count
- ✗ Must be in payment/fintech context

**Points**: 2 (only when paired with Tier 1/2 signals)

---

#### Signal: Webhook Handlers (Async Payment Confirmation)

**Rationale**: Async callback handling is common in payment systems.

**Detection Pattern (grep):**
```bash
grep -r "webhook\|callback\|@app.route.*webhook" --include="*.py" --include="*.js" src/ app/
grep -r "def.*webhook\|handle_webhook" --include="*.py"
```

**Code Examples (Positive Match):**
```python
@app.route('/webhook/payment', methods=['POST'])
def payment_webhook():
    """Handle async payment callback"""
    data = request.json
    update_payment_status(data['payment_id'], data['status'])
```

**False Positive Warnings:**
- ✗ Webhook handler for non-payment events (e.g., email notification webhook) → Does NOT count
- ✗ Must be associated with payment gateway or fintech context

**Points**: 2 (only when paired with payment gateway signals)

---

#### Signal: Interest, Principal, Tenure, Balance, Ledger (Financial Calculations)

**Rationale**: Core lending concepts; generic unless in lending module context.

**Detection Pattern (grep):**
```bash
grep -r "interest_rate\|principal_amount\|tenure\|ledger\|balance" --include="*.py" --include="*.js" src/ app/
grep -r "def.*interest\|calculate_balance" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# lending_calc.py
def calculate_interest(principal, rate, tenure):
    return principal * rate * tenure / 100

class Ledger:
    def record_transaction(self, txn_type, amount):
        pass
```

**False Positive Warnings:**
- ✗ "balance" in general account context (not financial) → Does NOT count
- ✗ "tenure" meaning employment tenure, not loan tenure → Does NOT count
- ✗ Must be in lending module context

**Points**: 2 (only in lending module context)

---

#### Signal: Invoice, Billing, Currency

**Rationale**: Financial documents; generic unless in payment context.

**Detection Pattern (grep):**
```bash
grep -r "invoice\|billing\|currency\|amount" --include="*.py" --include="*.js" src/ app/ | grep -i "class\|def"
```

**Code Examples (Positive Match):**
```python
class Invoice:
    def generate_pdf(self):
        pass

def format_currency(amount, currency='INR'):
    return f"{currency} {amount}"
```

**False Positive Warnings:**
- ✗ "Invoice" as generic document → Does NOT count without payment context
- ✗ Generic currency formatting → Does NOT count

**Points**: 2 (only in payment/billing context)

---

#### Signal: KYC, Compliance, Audit, Encryption, Hashing

**Rationale**: Finance-adjacent compliance; generic unless paired with domain context.

**Detection Pattern (grep):**
```bash
grep -r "kyc\|compliance\|audit\|encryption\|hashing" --include="*.py" --include="*.js" src/ app/
grep -r "KYCStatus\|verify_kyc\|audit_log" --include="*.py"
```

**Code Examples (Positive Match):**
```python
class KYCStatus(Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"

def audit_log(action, user_id):
    pass
```

**False Positive Warnings:**
- ✗ Generic "audit" logging in any app → Does NOT count
- ✗ KYC must be explicit (not just "verification")
- ✗ Must be in fintech context (Aadhaar, PAN, bureau pull, etc.)

**Points**: 2 (only when paired with Tier 1/2 fintech signals)

---

### Tier 4: Incidental (1 point each)

Global fintech terms requiring context; lower weight because less specific to fintech:

#### Signal: Global Payment Gateways (Stripe, PayPal, Braintree, Adyen)

**Rationale**: International payment platforms; lower weight because less domain-specific than Indian fintech.

**Detection Pattern (grep):**
```bash
grep -r "stripe\|paypal\|braintree\|adyen" --include="*.py" --include="*.js" requirements.txt package.json
```

**Code Examples (Positive Match):**
```python
import stripe
stripe.api_key = "sk_live_..."
```

**Points**: 1 each

---

#### Signal: Data Aggregators (Plaid)

**Rationale**: Open banking data aggregation; lower weight than core fintech.

**Detection Pattern (grep):**
```bash
grep -r "plaid" requirements.txt package.json --include="*.py" --include="*.js"
```

**Points**: 1

---

---

## Healthcare Signal Catalog

Healthcare domains demand strict HIPAA compliance (US), GDPR (EU), and have distinct PHI handling requirements.

### Tier 1: Definitive (10 points each)

Unmistakable healthcare infrastructure:

#### Signal: HIPAA Compliance Code

**Rationale**: US healthcare legal requirement; unmistakable healthcare domain.

**Detection Pattern (grep):**
```bash
grep -r "hipaa\|HIPAA" --include="*.py" --include="*.js" --include="*.md" src/ app/ docs/
grep -r "hipaa_config\|HIPAA_AUDIT_LOG\|hipaa_validation" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# hipaa_config.py
HIPAA_AUDIT_LOG_RETENTION = 6  # years

class HIPAACompliance:
    def log_phi_access(self, user_id, patient_id, action):
        """Log all PHI access for HIPAA audit"""
        pass
```

**Points**: 10

---

#### Signal: PHI Handler Functions, De-identification

**Rationale**: Protected Health Information handling; core HIPAA requirement.

**Detection Pattern (grep):**
```bash
grep -r "de_identify\|phi_encrypt\|deidentify\|phi_field\|sanitize_phi" --include="*.py" --include="*.js"
grep -r "Safe.Harbor\|k.anonymity" --include="*.py" --include="*.md"
```

**Code Examples (Positive Match):**
```python
# phi_handler.py
class PHIHandler:
    def de_identify_patient(self, patient_record):
        """Remove identifiers per HIPAA Safe Harbor method"""
        patient_record['name'] = None
        patient_record['ssn'] = None
        return patient_record

    def encrypt_phi_field(self, field_value):
        """Encrypt PHI at rest"""
        return encrypt(field_value, key=PHI_KEY)
```

**Points**: 10

---

#### Signal: HL7, FHIR Integration

**Rationale**: Healthcare data exchange standards; unmistakable healthcare interop.

**Detection Pattern (grep):**
```bash
grep -r "hl7\|fhir\|HL7\|FHIR" --include="*.py" --include="*.js" requirements.txt package.json
grep -r "import hl7\|FHIRServer\|Bundle\|Observation" --include="*.py" --include="*.java"
```

**Code Examples (Positive Match):**
```python
import hl7
from fhirpy import Client

class FHIRIntegration:
    def fetch_patient(self, patient_id):
        """Fetch patient from FHIR-compliant EHR"""
        return self.fhir_client.get(f"Patient/{patient_id}")
```

**Points**: 10

---

#### Signal: EHR System References (Epic, Cerner, Allscripts, SMART on FHIR)

**Rationale**: Electronic Health Record platform integrations; definitive healthcare.

**Detection Pattern (grep):**
```bash
grep -r "epic\|cerner\|allscripts\|smart_on_fhir\|ehr_system" --include="*.py" --include="*.js" --include="*.md"
grep -r "EpicIntegration\|CernerEHR\|SmartApp" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# ehr_integration.py
class EpicIntegration:
    def fetch_ehr_record(self, patient_mrn):
        """Fetch from Epic EHR system"""
        return self.epic_client.get_patient(mrn=patient_mrn)
```

**Points**: 10

---

### Tier 2: Strong (5 points each)

Patterns specific to clinical workflows:

#### Signal: Patient Record Management

**Rationale**: Core EHR concept; specific to healthcare.

**Detection Pattern (grep):**
```bash
grep -r "patient_record\|PatientModel\|patient_id" --include="*.py" --include="*.java" src/ app/ | grep "class\|def"
```

**Points**: 5

---

#### Signal: Diagnosis, Treatment, Prescription

**Rationale**: Clinical documentation; healthcare-specific.

**Detection Pattern (grep):**
```bash
grep -r "diagnosis\|treatment\|prescription\|PrescriptionOrder" --include="*.py" --include="*.java" src/ app/
```

**Points**: 5

---

#### Signal: ICD-10, CPT Medical Coding

**Rationale**: Billing and clinical classification; healthcare-specific.

**Detection Pattern (grep):**
```bash
grep -r "icd10\|ICD10\|cpt_code\|CPT" --include="*.py" --include="*.java" src/ app/
grep -r "validate_icd10\|cpt_mapping" --include="*.py"
```

**Points**: 5

---

#### Signal: Consent Management, Privacy Matrix

**Rationale**: Patient privacy enforcement; healthcare-specific.

**Detection Pattern (grep):**
```bash
grep -r "consent\|privacy_matrix\|consent_tracking" --include="*.py" --include="*.java" src/ app/
```

**Points**: 5

---

### Tier 3: Supporting (2 points each)

Generic health-domain patterns:

#### Signal: Appointment, Medication, Provider

**Rationale**: Clinical operations; generic unless in EHR context.

**Detection Pattern (grep):**
```bash
grep -r "appointment\|medication\|provider" --include="*.py" src/ app/ | grep "class\|def"
```

**Points**: 2 (only in EHR context)

---

#### Signal: Insurance Processing

**Rationale**: Coverage coordination; healthcare-specific.

**Detection Pattern (grep):**
```bash
grep -r "insurance\|coverage\|claim" --include="*.py" src/ app/ | grep "class\|def"
```

**Points**: 2

---

### Tier 4: Incidental (1 point)

Generic health mentions:

#### Signal: Health-Related Variable Names

**Rationale**: "patient", "health", "medical" in variable names alone; very generic.

**Detection Pattern (grep):**
```bash
grep -r "patient|health|medical" --include="*.py" src/ app/
```

**Points**: 1 each (requires Tier 2+ to count)

---

---

## Enterprise Signal Catalog

Enterprise codebases prioritize security, scalability, regulatory audit, and multi-customer isolation.

### Tier 1: Definitive (10 points each)

Enterprise infrastructure requirements:

#### Signal: SOC2 Audit Controls

**Rationale**: Enterprise security audit standard; unmistakable enterprise.

**Detection Pattern (grep):**
```bash
grep -r "soc2\|SOC2\|audit.*control\|CC6\|CC7\|CC9" --include="*.py" --include="*.js" --include="*.md" src/ docs/
grep -r "SOC2_CONTROLS\|audit_log_middleware" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# soc2_compliance.py
SOC2_CONTROLS = {
    'CC6': 'Logical access control',
    'CC7': 'User identity authentication',
    'CC9': 'Logical and physical access integrated'
}
```

**Points**: 10

---

#### Signal: SAML, SSO Implementation

**Rationale**: Single sign-on; enterprise authentication standard.

**Detection Pattern (grep):**
```bash
grep -r "saml\|SAML\|sso\|okta\|auth0" --include="*.py" --include="*.js" --include="*.xml" src/ app/ config/
grep -r "SSOClient\|SAMLRequest\|saml_config" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# sso_config.py
from flask_saml import FlaskSAML

saml_config = {
    'sp': {
        'entityID': 'https://myapp.com/metadata/',
    },
    'idp': {
        'entityID': 'https://idp.okta.com/',
    }
}

@app.route('/login/sso')
def sso_login():
    """Initiate SAML SSO"""
    return FlaskSAML().login()
```

**Points**: 10

---

#### Signal: Multi-Tenant Architecture

**Rationale**: Serving multiple customers from shared infrastructure; enterprise-defining.

**Detection Pattern (grep):**
```bash
grep -r "tenant_id\|tenant_isolation\|multi.tenant" --include="*.py" --include="*.java" src/ app/
grep -r "TenantRouter\|tenant_context\|schema.per.tenant" --include="*.py"
grep -r "WHERE tenant_id =" --include="*.py" --include="*.sql"
```

**Code Examples (Positive Match):**
```python
# tenant_router.py
class TenantRouter:
    def get_db_for_tenant(self, tenant_id):
        """Route to tenant-specific database"""
        return self.tenant_dbs[tenant_id]

# models.py
class BaseModel(db.Model):
    tenant_id = db.Column(db.Integer, nullable=False, index=True)

    def __init__(self, tenant_id, **kwargs):
        super().__init__(**kwargs)
        self.tenant_id = tenant_id

# queries
SELECT * FROM users WHERE tenant_id = ?
```

**Points**: 10

---

#### Signal: Service Mesh (Istio, Linkerd)

**Rationale**: Advanced network control; enterprise-scale microservices.

**Detection Pattern (grep):**
```bash
grep -r "istio\|linkerd\|mesh" --include="*.yaml" --include="*.yml" config/ k8s/
grep -r "VirtualService\|DestinationRule\|ServiceEntry" --include="*.yaml"
```

**Code Examples (Positive Match):**
```yaml
# istio_config.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: my-service
spec:
  hosts:
  - my-service
  http:
  - match:
    - uri:
        prefix: "/api"
    route:
    - destination:
        host: my-service-v1
```

**Points**: 10

---

### Tier 2: Strong (5 points each)

Enterprise governance and scale patterns:

#### Signal: RBAC, ABAC Implementation

**Rationale**: Role/attribute-based access control; enterprise authorization.

**Detection Pattern (grep):**
```bash
grep -r "rbac\|abac\|role_manager\|policy.*engine" --include="*.py" --include="*.java" src/ app/
grep -r "has_permission\|PolicyDecisionPoint\|RoleManager" --include="*.py"
```

**Code Examples (Positive Match):**
```python
# rbac.py
class RoleManager:
    def has_permission(self, user_id, resource, action):
        """Check if user has permission"""
        role = self.get_user_role(user_id)
        return self.policy_engine.can_access(role, resource, action)
```

**Points**: 5

---

#### Signal: Audit Trail Logging

**Rationale**: Regulatory audit trail; enterprise compliance.

**Detection Pattern (grep):**
```bash
grep -r "audit_log\|audit_trail\|immutable_log" --include="*.py" --include="*.java" src/ app/
```

**Points**: 5

---

#### Signal: LDAP, Active Directory Integration

**Rationale**: Enterprise identity management.

**Detection Pattern (grep):**
```bash
grep -r "ldap\|active_directory\|ad_sync" --include="*.py" --include="*.java" src/ app/
```

**Points**: 5

---

#### Signal: Kubernetes Configs, Orchestration

**Rationale**: Container scale patterns; enterprise deployment.

**Detection Pattern (grep):**
```bash
grep -r "deployment.yaml\|helm.*chart\|statefulset" --include="*.yaml" config/ k8s/ helm/
```

**Points**: 5

---

### Tier 3: Supporting (2 points each)

Architectural patterns common in enterprise:

#### Signal: Microservice Architecture

**Rationale**: Modularity pattern; enterprise scale.

**Detection Pattern (grep):**
```bash
ls -la services/ && [ $(find services/ -mindepth 1 -maxdepth 1 -type d | wc -l) -gt 3 ]
grep -r "service.to.service\|inter.service\|grpc\|http.*call" --include="*.py" | head -5
```

**Points**: 2

---

#### Signal: Circuit Breaker Patterns

**Rationale**: Resilience pattern; enterprise reliability.

**Detection Pattern (grep):**
```bash
grep -r "circuit_breaker\|CircuitBreaker\|resilience4j" --include="*.py" --include="*.java"
```

**Points**: 2

---

#### Signal: API Gateway

**Rationale**: Request routing/auth; enterprise API management.

**Detection Pattern (grep):**
```bash
grep -r "api_gateway\|gateway_routing\|nginx.*config" --include="*.py" --include="*.conf"
```

**Points**: 2

---

#### Signal: Event Streaming

**Rationale**: Async patterns at scale; enterprise event-driven.

**Detection Pattern (grep):**
```bash
grep -r "kafka\|rabbitmq\|event_bus\|pubsub" --include="*.py" requirements.txt package.json
```

**Points**: 2

---

### Tier 4: Incidental (1 point)

Generic governance mentions:

#### Signal: Generic Compliance/Logging Keywords

**Rationale**: "compliance", "logging", "security" in comments; very generic.

**Detection Pattern (grep):**
```bash
grep -r "compliance\|logging\|security" --include="*.py" | head -5
```

**Points**: 1 each (requires Tier 2+ to count)

---

---

## Multi-Domain Stacking

When two or more domains exceed their threshold (≥15 points, ≥50% confidence), modes stack rather than compete. This prevents forcing a fintech + healthcare system into a single lens.

### What Happens When Both Fintech AND Enterprise Score ≥15

Both domain-mode files activate and are **loaded in parallel**. The generated documentation will include:

1. **Agnostic Foundation** (common to all)
   - Architecture overview
   - Module structure
   - Data flow
   - Deployment

2. **Fintech Section** (if fintech ≥ 15)
   - PCI-DSS compliance mapping
   - RBI Digital Lending Guidelines
   - PII inventory (Aadhaar, PAN, CIBIL)
   - Payment flows

3. **Enterprise Section** (if enterprise ≥ 15)
   - SOC2 audit trail
   - RBAC/IAM matrix
   - Multi-tenant isolation
   - SLA commitments

4. **Interaction Zones** (NEW — when both activate)
   - "How fintech payment flows enforce SOC2 audit trail requirements"
   - "Multi-tenant isolation constraints on shared credit bureau API calls"
   - "RBAC applied to PII access during KYC processing"

### Example: Healthtech with Lending

A platform offering patient microloans might score:

```
Fintech: 35 points (razorpay, CIBIL, EMI)
Healthcare: 28 points (HIPAA, PHI, EHR integration)
Enterprise: 18 points (SAML, audit logs)

→ Activate FINTECH + HEALTHCARE + ENTERPRISE modes
→ Document three sections, with explicit interaction zones
→ Interaction example: "How patient consent (healthcare) applies to loan decisioning (fintech)"
```

---

---

## Edge Cases

### Edge Case 1: Test Codebases That Artificially Inflate Scores

**Problem**: A codebase with comprehensive test fixtures imports Razorpay SDK for testing, but never uses it in production. Score counts full Tier 1 (10 pts) inflating fintech domain detection.

**Solution**:
- Check if Razorpay import is in production code path (src/, app/) or test-only (tests/, fixtures/)
- If test-only: **Discount by 50%** or apply 5 pts instead of 10 pts
- If production import + test usage: **Full 10 pts** (signal is valid even if mostly tested)
- Document this assumption in detection report: "Razorpay signal found in test fixtures; actual production usage unclear"

**Example**:
```python
# tests/fixtures/payment_fixtures.py
import razorpay  # Used only for test fixtures
def mock_razorpay_response():
    return {'status': 'captured'}

# No actual production code uses razorpay
```

**Scoring**: 5 pts (discounted) instead of 10, or exclude entirely if NEVER imported in src/.

---

### Edge Case 2: Microservices Where Domain Signals Are Spread Across Repos

**Problem**: A fintech system is split into 5 microservices in separate repos. Razorpay is only in payment-service repo, CIBIL only in credit-service repo. Scanning single repo misses cross-repo signals.

**Solution**:
- **Scope is per-repo** — detector runs on provided codebase path only
- If user provides parent directory with multiple service repos: glob across all
- Document in report: "Multi-service architecture detected. Fintech score is for payment-service only; credit-service not scanned"
- **Recommendation**: Run detector on each service separately and aggregate scores manually

**Example**:
```bash
# If parent dir contains:
└── platform/
    ├── payment-service/  → Razorpay (10 pts)
    ├── credit-service/   → CIBIL (10 pts)
    ├── user-service/     → SAML (10 pts)
    └── api-gateway/      → API Gateway (2 pts)

# Run detector on each, then manually sum:
Fintech: 20 pts (payment + credit)
Enterprise: 12 pts (user + api-gateway)
→ Only fintech ≥ 15 (if summing across services)
```

---

### Edge Case 3: Legacy Codebases With Commented-Out Domain Code

**Problem**: Old fintech system has loan models and CIBIL integration commented out (replaced by new system). Grepping for these still finds them, inflating fintech score.

**Solution**:
- Check if signal is in **active code path** (executed) vs. **commented out** (dead code)
- Commented-out Tier 1 signals: **Exclude entirely (0 pts)** or discount to 2 pts if highly indicative
- In detection report: "CIBIL integration found in commented code (line 45); excluded from active signal count"
- Use git blame to confirm when code was commented (if very old, exclude)

**Example**:
```python
# old_credit_service.py (commented out in 2023)

# class CibilIntegration:  # DEPRECATED - use new bureau service
#     def fetch_score(self, pan):
#         return CibilClient().get_score(pan)

# Grep finds "cibil" and "CibilClient", but code is dead
# Scoring: 0 pts (or 2 pts if unsure, pending code review)
```

---

### Edge Case 4: Config Files With Domain Keywords But No Logic

**Problem**: Docker Compose file has service named `healthcare-db`, environment variable `HIPAA_ENABLED=true`, but no actual HIPAA code in app.

**Solution**:
- **Config file names/labels alone = 0 pts**
- **Config values (HIPAA_ENABLED=true) = 0 pts** unless paired with actual HIPAA enforcement code
- Only count if corresponding logic exists in source code (PHI encryption, audit logging)
- Detection pattern: grep in src/, app/, lib/ only; skip config/infra naming

**Example**:
```yaml
# docker-compose.yml
services:
  healthcare-db:
    image: postgres
    environment:
      HIPAA_ENABLED: true  # ← Just a flag, no validation in code

# Scoring: 0 pts unless actual HIPAA code exists
```

---

### Edge Case 5: Library Defaults That Overlap With Domain Patterns

**Problem**: Django's default `User` model includes a `groups` field (RBAC-like). Is this a Tier 2 RBAC signal for enterprise?

**Solution**:
- **Framework defaults = 0 pts**
- **Domain-specific RBAC = 5 pts** (e.g., custom role_manager, permission matrix, LDAP binding)
- Distinguish by checking:
  - Is custom RBAC logic written? (role hierarchy, permission evaluation, policy engine)
  - Or just using framework defaults without extension?
- If using framework defaults only: **0 pts**
- If building domain-specific RBAC on top: **5 pts**

**Example**:
```python
# Django default User model
from django.contrib.auth.models import User  # Has .groups field

# Does NOT count as RBAC signal (framework default)

# But this WOULD count:
class RoleManager:
    def has_permission(self, user_id, resource, action):
        # Custom policy evaluation
        role = self.get_user_role(user_id)
        return self.policy_engine.evaluate(role, resource, action)
```

---

### Edge Case 6: False Positive: Variable Named After Domain Concept, Different Context

**Problem**: E-commerce app has a `settlement` process for calculating commission splits, unrelated to fintech settlement.

**Solution**:
- Grep for signal ("settlement") but requires **context validation**
- Check surrounding code: Is this payment settlement (fintech) or commission settlement (generic)?
- If generic context: **0 pts**
- If fintech context (payment gateway, reconciliation): **2 pts (Tier 3)**

---

---

## Scoring Worked Example

### Example: Indian Fintech Lending Platform (Kissht-like)

**Codebase**: Loan origination system with payment processing.

**Step 1: Scan for Signals**

Using grep patterns from catalog:

```bash
# Tier 1: Definitive signals
grep -r "razorpay" requirements.txt → FOUND: razorpay==1.3.0  ✓
grep -r "cibil\|experian" src/ → FOUND: CibilClient() in src/credit.py:12  ✓
grep -r "aadhaar\|pan_number" src/ → FOUND: validate_aadhaar() in src/kyc.py:45  ✓
grep -r "emi_calculator\|emi_schedule" src/ → FOUND: EMICalculator class in src/lending.py:67  ✓

# Tier 2: Strong signals
grep -r "razorpay_payment_id\|X-Razorpay-Signature" src/ → FOUND: webhook_signature_verify() in src/webhook.py:23  ✓
grep -r "NACH\|nach_mandate" src/ → FOUND: NAACHMandate model in src/models.py:156  ✓
grep -r "gst\|tax_rate" src/ → FOUND: calculate_gst() in src/billing.py:34  ✓
grep -r "RBI\|DLG" src/ docs/ → FOUND: RBI_DLG_2022 config in src/compliance.py:8  ✓

# Tier 3: Supporting signals
grep -r "kyc\|compliance" src/ → FOUND: KYCStatus enum in src/kyc.py:5  ✓
grep -r "loan_disbursement" src/ → FOUND: LoanStatus.DISBURSED in src/models.py:89  ✓
grep -r "idempotency" src/ → FOUND: idempotency_key in src/payment.py:112  ✓
```

**Step 2: Tally Points**

```
Tier 1 Signals Found (10 pts each):
  ✓ Razorpay SDK import (10)
  ✓ CIBIL API client (10)
  ✓ Aadhaar validation module (10)
  ✓ EMI schedule calculator (10)
  → Subtotal: 40 points

Tier 2 Signals Found (5 pts each):
  ✓ Razorpay webhook handler (5)
  ✓ NACH mandate processing (5)
  ✓ GST calculation (5)
  ✓ RBI DLG compliance config (5)
  → Subtotal: 20 points

Tier 3 Signals Found (2 pts each):
  ✓ KYC flow module (2)
  ✓ loan_disbursement state (2)
  ✓ Idempotency keys on payment (2)
  → Subtotal: 6 points

TOTAL FINTECH SCORE: 40 + 20 + 6 = 66 points
```

**Step 3: Calculate Confidence**

```
Signals found: 11 distinct signals
Possible signals: ~50 per domain (estimated max)
Base confidence: (11 / 50) × 100 = 22%

Confidence modifier based on tier distribution:
- 4 Tier-1 signals (highest value) → Multiply by 1.0 (strong indicators)
- 4 Tier-2 signals (medium value) → Multiply by 0.9 (supporting)
- 3 Tier-3 signals (weak value) → Multiply by 0.8 (contextual)

Adjusted confidence = 22% × ((4×1.0 + 4×0.9 + 3×0.8) / 11) = 22% × 0.91 ≈ 87%

FINTECH CONFIDENCE: 87% (High Confidence)
```

**Step 4: Apply Activation Rules**

```
Fintech Score: 66 points
Threshold: ≥ 15 points
Confidence: 87% (≥ 50% floor)

Result: ✓ FINTECH MODE ACTIVATED
```

**Step 5: Present Results to User**

```markdown
## Domain Detection Results

**Fintech Mode**: ACTIVATED
- Score: 66 / 100 points
- Confidence: 87% (High)
- Signals detected: 11 across 3 tiers

Key signals:
  - Razorpay integration (T1)
  - CIBIL credit pull (T1)
  - Aadhaar KYC validation (T1)
  - EMI calculation engine (T1)
  - RBI DLG compliance (T2)
  - NACH mandate processing (T2)

**Healthcare Mode**: NOT DETECTED (0 signals, score: 0)

**Enterprise Mode**: NOT DETECTED (0 signals, score: 0)

**Activated Domains**: Fintech only

**Documentation Plan**:
  - Full fintech mode with PCI-DSS compliance section
  - RBI DLG 2022 audit checklist
  - PII inventory (Aadhaar, PAN, CIBIL scores)
  - Payment flow with Razorpay webhook diagram
  - EMI calculation documented
  - Indian payment ecosystem context

**Ready to generate?** [Y/N]
```

---

### Example 2: Enterprise SaaS with No Fintech Domain

**Codebase**: B2B analytics dashboard.

```bash
# Scan for fintech signals
grep -r "razorpay\|stripe" src/ → NOT FOUND
grep -r "cibil\|experian" src/ → NOT FOUND
grep -r "aadhaar\|pan_number" src/ → NOT FOUND
grep -r "emi\|loan" src/ → NOT FOUND

# Scan for enterprise signals
grep -r "saml\|okta" src/ → FOUND: SAMLRequest parsing in src/auth/sso.py:45  ✓
grep -r "tenant_id.*WHERE" src/ → FOUND in all queries, 20+ matches  ✓
grep -r "SOC2\|audit_log" src/ docs/ → FOUND: audit_middleware in src/core.py:67  ✓

# Point tally
Enterprise Signals:
  Tier 1: SAML (10), Multi-tenant (10) = 20 points
  Tier 2: Audit logging (5), RBAC (5) = 10 points
  → Total: 30 points ✓ ACTIVATED
```

---

---

## Implementation Notes

- **Scanning**: Phase 2 (Domain Detection) runs detector as part of workflow
- **Output**: Detection report included in handoff package intro with point-per-signal breakdown
- **Calibration**: Update tier weights annually based on false positive rate
- **Extensions**: Add new domains (IoT, ML, Gaming, etc.) following same 4-tier structure
- **Accuracy**: Test detector against 20+ real codebases to validate thresholds
- **Coverage**: Aim for 0 missed domains (false negatives < 5%) and <10% false positives

When all thresholds remain below 15: Use agnostic mode. The codebase may be early-stage, a utility library, or genuinely domain-agnostic. Handoff guide defaults to solid engineering practices without domain assumptions.

---

## Quick Grep Reference Card

```bash
# Fintech Quick Scan
grep -r "razorpay\|cashfree\|cibil\|aadhaar\|emi" requirements.txt package.json src/

# Healthcare Quick Scan
grep -r "hipaa\|phi\|hl7\|fhir\|epic" requirements.txt package.json src/

# Enterprise Quick Scan
grep -r "saml\|okta\|tenant_id\|soc2\|istio" requirements.txt package.json src/ config/
```

---

**EOF**
