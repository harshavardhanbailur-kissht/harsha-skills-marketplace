::: {.summary}
When a Loan-Against-Property application arrives, an automated engine reads the customer's
credit-bureau report, bank-statement data and risk-model scores, then returns three things:
**approve or reject**, the **program** (NORMAL or SARAL), and a **draft offer** — amount, tenure
and interest rate. A human credit officer still makes the final call on many cases.
:::

## Who and what is this?

Before any credit assessment, the engine sorts the application three ways:

- **Channel.** An online lead gets the full assessment; a branch / LOS case gets a lighter check; any other source is rejected.
- **Product.** A fresh loan or a balance-transfer-plus-top-up runs through the main engine. An internal top-up runs through a separate engine and needs a still-running existing loan.
- **Age.** The main applicant must be **21–63**; a co-applicant only needs to be **18+** (no upper limit); and the loan must finish before the applicant turns **65**.

## The knockout checks

Failing **any one** rejects the application, and the engine names the check that failed.

| Check | Rejected when |
|---|---|
| Credit score | It falls between **300 and 650**. (650+ is fine; 300 or below is handled separately.) |
| Serious past default | 90+ days overdue in last 12 months; a recent 30-day delinquency on a large loan; write-off ≥ ₹10,000; or a court suit in the last 12 months. |
| Current dues | Credit-card dues ≥ ₹5,000; other loan dues ≥ ₹1,000; or microfinance dues > ₹1,000. |
| Risk & fraud | Either risk score above its cut-off; failed digital-footprint checks; or a failed bank-to-government identity match. |

::: {.note title="The low / no-score exception"}
A score of **300 or below — including new-to-credit customers — is _not_ auto-rejected.**
It routes to a path that approves only if the bank statement is clean and verified (Account
Aggregator) and the digital / model checks pass.
:::

## How much, for how long, at what rate

The engine takes **income** from the best available source, assumes up to **70% of income** can
go to EMIs, subtracts existing EMIs, and converts the affordable EMI into a loan amount.

| Loan amount | Interest rate | Tenure |
|---|---|---|
| ₹5–7 lakh | **24%** | 5–7 years |
| ₹7–10 lakh | **22%** | up to 7 years |
| ₹10–15 lakh | **20%** | up to 7 years (10 if bank-verified) |
| SARAL (₹75k–3 lakh) | **26%** | up to 7 years |

## Four things worth knowing

::: {.warn title="1 - Some customers are hardcoded to bypass checks"}
The live ruleset contains specific borrower reference numbers forced to pass certain checks. Worth a deliberate review and sign-off.
:::

::: {.warn title="2 - One check does nothing"}
The bureau-vintage check always returns pass — it looks like a gate but never stops anyone.
:::

::: {.warn title="3 - The 28% rate is actually 26%"}
Internally the top band is labelled 28% but computes 26%. Confirm which was intended.
:::
