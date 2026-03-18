# Mobile Monetization Reference Guide

Comprehensive guide to monetizing mobile apps across iOS and Android platforms with best practices, code examples, and policy compliance.

## Table of Contents

1. [ASO (App Store Optimization)](#aso)
2. [In-App Purchases](#in-app-purchases)
3. [StoreKit 2 (iOS)](#storekit-2)
4. [Google Play Billing Library](#google-play-billing)
5. [RevenueCat Integration](#revenuecat)
6. [Ad Monetization](#ad-monetization)
7. [Paywall Design](#paywall-design)
8. [Pricing Strategies](#pricing-strategies)
9. [Receipt Validation](#receipt-validation)
10. [Analytics & Metrics](#analytics)
11. [App Store Policies](#policies)

---

## ASO (App Store Optimization) {#aso}

App Store Optimization drives discoverability and increases conversion rates from search to install.

### Keyword Strategy

**Best Practices:**
- Research keywords with 5,000-50,000 monthly searches
- Use long-tail keywords (3-4 words) for less competition
- Include variations: brand + category, problem + solution
- Monitor seasonal trends and competitor strategies

**App Store Fields:**
```
Keyword field (100 chars total iOS):
"fitness tracker, workout, health tracker, exercise"

Subtitle (30 chars iOS):
"Track workouts & reach goals"

Description highlights (iOS):
- Benefits first, features second
- Short paragraphs (2-3 sentences)
- Include 2-3 primary keywords naturally
```

### Screenshot Strategy

**iOS Screenshot Best Practices:**
```
Frame 1: Headline + Value Proposition
- "Track 50+ Workouts"
- Large, readable text (18pt minimum)

Frame 2: Key Feature Demonstration
- Show app UI in action
- Highlight unique differentiator

Frame 3: Social Proof
- "5★ Rating from 50K+ Users"
- Include testimonial

Frame 4: CTA & Benefits Summary
- "Start Free for 7 Days"
- List top 3 benefits
```

**Android Screenshot Best Practices:**
- Resolution: 1080x1920px (recommended)
- Include app name and logo
- Use consistent branding
- Avoid text > 40% of screen
- Show real app UI, not mockups

### A/B Testing Framework

**Test Methodology:**
```
Duration: 2-4 weeks minimum
Sample size: 1,000+ impressions per variant
Metrics to track:
- Install conversion rate
- Cost per install (CPI)
- Day 1 retention
- Day 7 retention

iOS Testing (Limited):
- Screenshots (up to 3 variants)
- Video previews (30-60 seconds)
- Promotional art
- Rating changes (monitor only)

Android Testing (A/B Testing):
- Icon (major impact on CTR)
- Screenshots (test top 2 most critical)
- Feature graphics
- Description text
```

### Rating & Review Management

**Strategy:**
```
Prompt timing for positive experiences:
- Post-achievement unlocks
- After successful feature completion
- Not before major paywalls

Response strategy:
- Reply to all reviews within 24 hours
- Address negative feedback professionally
- Thank positive reviewers
- Include version-specific fixes in updates

Target rating: 4.3+ stars minimum
Monitor: Sentiment analysis on new reviews
Action: Escalate rating drops > 5%
```

---

## In-App Purchases {#in-app-purchases}

Three main IAP types for different monetization strategies.

### Purchase Types

**1. Consumable Products**
```
- Used once, can be repurchased
- Examples: coins, gems, energy refills
- Revenue model: impulse purchases
- Implementation: Track locally, server validates

Typical pricing:
$0.99 - $9.99 for small quantities
$19.99 - $99.99 for bundles with bonus (20% extra)
```

**2. Non-Consumable Products**
```
- Purchased once, permanent unlock
- Examples: premium features, ad removal
- Revenue model: single payment barrier
- Implementation: Restore purchases via App Store/Play Store

Typical structure:
- Ad-free version: $2.99 - $4.99
- Full feature unlock: $4.99 - $9.99
- Lifetime premium: $19.99 - $49.99
```

**3. Auto-Renewable Subscriptions**
```
- Recurring charge (weekly, monthly, yearly)
- Highest LTV potential
- Implementation: Handle expiration/renewal server-side

Typical pricing tiers:
- Weekly: $0.99 - $2.99 (churn risk ~70%)
- Monthly: $4.99 - $19.99 (balanced tier)
- Yearly: $39.99 - $99.99 (15-25% discount vs monthly)

Free trial: 3-7 days standard
Introductory pricing: 50% off first month common
```

---

## StoreKit 2 (iOS) {#storekit-2}

Modern Swift framework for handling iOS in-app purchases.

### Product Configuration

```swift
import StoreKit

// Define product IDs matching App Store Connect
let productIds = [
    "com.example.app.gems.small",
    "com.example.app.gems.large",
    "com.example.app.premium.monthly",
    "com.example.app.premium.yearly",
]

// Fetch products from App Store
struct StoreManager: ObservableObject {
    @Published var products: [Product] = []
    @Published var purchasedProductIds: Set<String> = []

    func fetchProducts() async {
        do {
            let fetchedProducts = try await Product.products(for: productIds)
            DispatchQueue.main.async {
                self.products = fetchedProducts.sorted {
                    productIds.firstIndex(of: $0.id) ?? .max <
                    productIds.firstIndex(of: $1.id) ?? .max
                }
            }
        } catch {
            print("Failed to fetch products: \(error)")
        }
    }
}
```

### Purchase Flow

```swift
// Initiate purchase
@MainActor
func purchase(_ product: Product) async -> Transaction? {
    do {
        let result = try await product.purchase()

        switch result {
        case .success(let verification):
            let transaction = try checkVerified(verification)
            await transaction.finish()
            return transaction

        case .userCancelled:
            print("User cancelled purchase")
            return nil

        case .pending:
            print("Purchase pending - awaiting approval")
            return nil

        @unknown default:
            return nil
        }
    } catch {
        print("Purchase failed: \(error)")
        return nil
    }
}

// Verify transaction signature
func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
    switch result {
    case .unverified(let unverified, let error):
        throw PurchaseError.unverifiedTransaction(error)
    case .verified(let verified):
        return verified
    }
}
```

### Subscription Status Monitoring

```swift
// Track subscription status in real-time
class SubscriptionManager: ObservableObject {
    @Published var isSubscribed = false
    @Published var subscriptionInfo: SubscriptionInfo?

    private var transactionListener: Task<Void, Error>?

    func startListeningForTransactions() {
        transactionListener = Task {
            for await result in Transaction.updates {
                do {
                    let transaction = try checkVerified(result)
                    await updateSubscriptionStatus(transaction)
                    await transaction.finish()
                } catch {
                    print("Failed to verify transaction: \(error)")
                }
            }
        }
    }

    @MainActor
    private func updateSubscriptionStatus(_ transaction: Transaction) async {
        guard let subscription = try? await Product.products(
            for: [transaction.productID]
        ).first?.subscription else { return }

        if let group = subscription.subscriptionGroup {
            if let currentStatus = try? await group.currentEntitlements.first {
                let renewalInfo = currentStatus.renewalInfo
                let productId = currentStatus.product.id

                self.isSubscribed = renewalInfo?.isExpired == false
                self.subscriptionInfo = SubscriptionInfo(
                    productId: productId,
                    expirationDate: renewalInfo?.expirationDate ?? Date(),
                    isAutoRenewing: renewalInfo?.willAutoRenew ?? false,
                    renewalDate: renewalInfo?.nextRenewalDate ?? Date()
                )
            }
        }
    }

    deinit {
        transactionListener?.cancel()
    }
}

struct SubscriptionInfo {
    let productId: String
    let expirationDate: Date
    let isAutoRenewing: Bool
    let renewalDate: Date

    var daysRemaining: Int {
        Calendar.current.dateComponents([.day], from: Date(), to: expirationDate).day ?? 0
    }
}
```

### Restoring Purchases

```swift
@MainActor
func restorePurchases() async {
    do {
        try await AppStore.sync()

        for await result in Transaction.currentEntitlements {
            let transaction = try checkVerified(result)
            await updatePurchasedStatus(transaction.productID)
        }
    } catch {
        print("Failed to restore purchases: \(error)")
    }
}
```

---

## Google Play Billing Library {#google-play-billing}

Kotlin implementation for Android in-app purchases.

### Setup & Configuration

```kotlin
// build.gradle.kts
dependencies {
    implementation("com.android.billingclient:billing:6.1.0")
}

// AndroidManifest.xml
<uses-permission android:name="com.android.vending.BILLING" />
```

### BillingClient Initialization

```kotlin
import com.android.billingclient.api.*

class BillingManager(context: Context) {
    private lateinit var billingClient: BillingClient

    init {
        billingClient = BillingClient.newBuilder(context)
            .setListener { billingResult, purchases ->
                handlePurchaseUpdate(billingResult, purchases)
            }
            .enablePendingPurchases()
            .build()
    }

    fun startConnection(onReady: () -> Unit) {
        billingClient.startConnection(
            object : BillingClientStateListener {
                override fun onBillingSetupFinished(billingResult: BillingResult) {
                    if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                        onReady()
                    }
                }

                override fun onBillingServiceDisconnected() {
                    startConnection(onReady)
                }
            }
        )
    }
}
```

### Product Query & Display

```kotlin
// Query products from Play Console
suspend fun queryProducts(
    productType: String = BillingClient.ProductType.INAPP
): List<ProductDetails> = suspendCancellableCoroutine { continuation ->

    val productList = listOf(
        "com.example.gems.small",
        "com.example.gems.large",
        "com.example.premium.monthly",
        "com.example.premium.yearly"
    )

    val queryProductDetailsParams = QueryProductDetailsParams.newBuilder()
        .setProductIds(productList)
        .setProductType(productType)
        .build()

    billingClient.queryProductDetailsAsync(queryProductDetailsParams) {
        billingResult, productDetailsList ->

        if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
            continuation.resume(productDetailsList)
        } else {
            continuation.resumeWithException(
                Exception("Failed to query products: ${billingResult.debugMessage}")
            )
        }
    }
}
```

### Purchase Flow

```kotlin
// Launch purchase flow
fun launchPurchaseFlow(
    activity: Activity,
    productDetails: ProductDetails
) {
    val productDetailsParamsList = listOf(
        BillingFlowParams.ProductDetailsParams.newBuilder()
            .setProductDetails(productDetails)
            // For subscriptions, specify offer token
            .setOfferToken(
                productDetails.subscriptionOfferDetails?.firstOrNull()?.offerToken ?: ""
            )
            .build()
    )

    val billingFlowParams = BillingFlowParams.newBuilder()
        .setProductDetailsParamsList(productDetailsParamsList)
        .build()

    billingClient.launchBillingFlow(activity, billingFlowParams)
}

// Handle purchase result
private fun handlePurchaseUpdate(
    billingResult: BillingResult,
    purchases: MutableList<Purchase>?
) {
    when (billingResult.responseCode) {
        BillingClient.BillingResponseCode.OK -> {
            purchases?.forEach { purchase ->
                if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
                    handleSuccessfulPurchase(purchase)
                }
            }
        }
        BillingClient.BillingResponseCode.USER_CANCELED -> {
            Log.i("BillingManager", "User cancelled purchase")
        }
        else -> {
            Log.e("BillingManager", "Error: ${billingResult.debugMessage}")
        }
    }
}
```

### Subscription Management

```kotlin
// Query subscription status
suspend fun querySubscriptionStatus(
    accountId: String
): SubscriptionStatus? = suspendCancellableCoroutine { continuation ->

    val queryPurchaseParams = QueryPurchasesParams.newBuilder()
        .setProductType(BillingClient.ProductType.SUBS)
        .build()

    billingClient.queryPurchasesAsync(queryPurchaseParams) {
        billingResult, purchasesList ->

        val subscription = purchasesList.firstOrNull { purchase ->
            purchase.accountIdentifiers?.obfuscatedAccountId == accountId
        }

        continuation.resume(
            subscription?.let { purchase ->
                SubscriptionStatus(
                    productId = purchase.products.first(),
                    purchaseToken = purchase.purchaseToken,
                    orderId = purchase.orderId,
                    purchaseTime = purchase.purchaseTime,
                    isAutoRenewing = purchase.isAutoRenewing,
                    acknowledged = purchase.isAcknowledged
                )
            }
        )
    }
}

// Acknowledge purchase (required within 3 days)
fun acknowledgePurchase(purchaseToken: String) {
    val acknowledgeParams = AcknowledgePurchaseParams.newBuilder()
        .setPurchaseToken(purchaseToken)
        .build()

    billingClient.acknowledgePurchase(acknowledgeParams) { billingResult ->
        if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
            Log.i("BillingManager", "Purchase acknowledged successfully")
        }
    }
}

data class SubscriptionStatus(
    val productId: String,
    val purchaseToken: String,
    val orderId: String?,
    val purchaseTime: Long,
    val isAutoRenewing: Boolean,
    val acknowledged: Boolean
)
```

---

## RevenueCat Integration {#revenuecat}

Cross-platform subscription management and analytics.

### Setup & Configuration

```swift
// iOS - Swift
import RevenueCat

// AppDelegate or App initialization
func setupRevenueCat() {
    Purchases.logLevel = .debug
    Purchases.configure(withAPIKey: "your_revenuecat_api_key")

    // Set user ID (optional but recommended)
    Purchases.shared.identify("user_123") { customerInfo, error in
        if let error = error {
            print("Failed to identify user: \(error)")
        }
    }
}

// Subscribe to customer info updates
func subscribeToCustomerInfoUpdates() {
    Purchases.shared.customerInfoStream
        .receive(on: DispatchQueue.main)
        .sink { customerInfo in
            updateUserEntitlements(customerInfo)
        }
        .store(in: &cancellables)
}
```

```kotlin
// Android - Kotlin
import com.revenuecat.purchases.Purchases
import com.revenuecat.purchases.LogLevel

fun setupRevenueCat(context: Context) {
    Purchases.debugLogsEnabled = true
    Purchases.configure(context, "your_revenuecat_api_key")

    // Set user ID
    Purchases.sharedInstance.identify("user_123") { error ->
        if (error != null) {
            Log.e("RevenueCat", "Failed to identify user: ${error.message}")
        }
    }
}
```

### Offering Management

```swift
// Fetch offerings
@MainActor
func fetchOfferings() async {
    do {
        let offerings = try await Purchases.shared.offerings()

        if let current = offerings.current {
            // Use current offering
            displayPackages(current.availablePackages)
        }

        // Custom logic for specific offerings
        if let premiumOffering = offerings.offering(identifier: "premium") {
            for package in premiumOffering.availablePackages {
                print("\(package.identifier): \(package.localizedPriceString)")
            }
        }
    } catch {
        print("Failed to fetch offerings: \(error)")
    }
}

// Display offerings in UI
func displayPackages(_ packages: [Package]) {
    for package in packages {
        let priceString = package.localizedPriceString
        let periodString = package.product.subscriptionPeriod?.stringRepresentation ?? "lifetime"

        print("\(package.identifier): \(priceString)/\(periodString)")
    }
}
```

### Purchase & Entitlement Tracking

```swift
// Make purchase
@MainActor
func purchasePackage(_ package: Package) async -> Bool {
    do {
        let (transaction, customerInfo) = try await Purchases.shared.purchase(package: package)

        // Check if purchase was successful
        if customerInfo.entitlements["premium"]?.isActive == true {
            return true
        }
    } catch let error as PurchasesErrorCode {
        print("Purchase error: \(error)")
    } catch {
        print("Unexpected error: \(error)")
    }
    return false
}

// Check entitlements
@MainActor
func checkEntitlements() async {
    do {
        let customerInfo = try await Purchases.shared.customerInfo()

        let isPremium = customerInfo.entitlements["premium"]?.isActive == true
        let isLifetime = customerInfo.entitlements["lifetime"]?.isActive == true

        DispatchQueue.main.async {
            self.updateUIWithEntitlements(isPremium: isPremium, isLifetime: isLifetime)
        }
    } catch {
        print("Failed to check entitlements: \(error)")
    }
}
```

### Analytics Events

```swift
// Track custom events
Purchases.shared.track(
    event: "premium_feature_accessed",
    properties: ["feature": "offline_mode"]
)

// Revenue tracking (automatic for subscriptions)
// RevenueCat automatically tracks:
// - MRR (Monthly Recurring Revenue)
// - Churn rate
// - Renewal rate
// - LTV per user
```

---

## Ad Monetization {#ad-monetization}

Multiple ad formats and mediation strategies.

### AdMob Setup

```swift
// iOS - Swift
import GoogleMobileAds

// Initialize Google Mobile Ads SDK
func setupAdMob() {
    GADMobileAds.sharedInstance().start()
}

// Request configuration
func requestConfiguration() -> GADRequestConfiguration {
    let requestConfiguration = GADRequestConfiguration()

    // Add test devices
    requestConfiguration.testDeviceIdentifiers = ["33BE2250B43518CCDA7DE426D04EE232"]

    return requestConfiguration
}
```

### Banner Ads

```swift
// Banner Ad Controller
class BannerAdView: UIViewRepresentable {
    func makeUIView(context: Context) -> GADBannerView {
        let banner = GADBannerView(adSize: GADAdSizeBanner)
        banner.adUnitID = "ca-app-pub-xxxxxxxxxxxxxxxx/yyyyyyyyyyyyyy"
        banner.rootViewController = UIApplication.shared.windows.first?.rootViewController
        banner.load(GADRequest())

        return banner
    }

    func updateUIView(_ uiView: GADBannerView, context: Context) {}
}

// Usage in SwiftUI
struct ContentView: View {
    var body: some View {
        VStack {
            Text("Your content here")

            BannerAdView()
                .frame(height: 50)
        }
    }
}
```

### Interstitial Ads

```swift
class InterstitialAdManager: NSObject, GADFullScreenContentDelegate {
    var interstitialAd: GADInterstitialAd?

    func loadInterstitialAd() {
        let request = GADRequest()

        GADInterstitialAd.load(
            withAdUnitID: "ca-app-pub-xxxxxxxxxxxxxxxx/yyyyyyyyyyyyyy",
            request: request
        ) { [weak self] ad, error in
            if let error = error {
                print("Failed to load interstitial ad: \(error)")
                return
            }
            self?.interstitialAd = ad
            ad?.fullScreenContentDelegate = self
        }
    }

    func showInterstitialAd() {
        guard let interstitialAd = interstitialAd else { return }

        guard let rootViewController = UIApplication.shared.windows.first?.rootViewController else {
            return
        }

        interstitialAd.present(fromRootViewController: rootViewController)
    }

    // Reload after dismiss
    func adDidDismissFullScreenContent(_ ad: GADFullScreenPresentingAd) {
        loadInterstitialAd()
    }
}
```

### Rewarded Ads

```swift
class RewardedAdManager: NSObject, GADFullScreenContentDelegate {
    var rewardedAd: GADRewardedAd?
    var rewardCompletion: (() -> Void)?

    func loadRewardedAd() {
        let request = GADRequest()

        GADRewardedAd.load(
            withAdUnitID: "ca-app-pub-xxxxxxxxxxxxxxxx/yyyyyyyyyyyyyy",
            request: request
        ) { [weak self] ad, error in
            if let error = error {
                print("Failed to load rewarded ad: \(error)")
                return
            }
            self?.rewardedAd = ad
            ad?.fullScreenContentDelegate = self
        }
    }

    func showRewardedAd() {
        guard let rewardedAd = rewardedAd else { return }

        guard let rootViewController = UIApplication.shared.windows.first?.rootViewController else {
            return
        }

        rewardedAd.present(
            fromRootViewController: rootViewController,
            userDidEarnRewardHandler: { [weak self] in
                self?.rewardCompletion?()
            }
        )
    }

    func adDidDismissFullScreenContent(_ ad: GADFullScreenPresentingAd) {
        loadRewardedAd()
    }
}
```

### Ad Mediation

```swift
// Google Ad Manager mediation configuration
// Configured via Google Ad Manager dashboard

// Mediation Partners:
// - AppLovin
// - Mintegral
// - IronSource
// - Vungle
// - InMobi
// - Chartboost

// Mediation setup in code
func setupMediation() {
    let mediationExtras = GADMediationExtras()

    // Configure mediation networks
    GADMobileAds.sharedInstance().requestConfiguration().registerExtras(
        mediationExtras,
        forNetwork: "com.google.ads.mediation.applovin"
    )
}
```

---

## Paywall Design {#paywall-design}

User-friendly paywall strategies and conversion optimization.

### Paywall Timing Strategy

```
Show paywall at critical moments:

1. Feature Lock (Hard Paywall)
   - Before accessing premium feature
   - After free trial expiration
   - User already understands value

2. Context-Driven (Soft Paywall)
   - After meaningful achievement
   - Post-engagement milestone
   - Contextual offer relevant to action

3. Upgrade Prompts (Gentle Paywall)
   - Suggestion to unlock all features
   - No blocking of current feature
   - Option to continue with limits

Best Practice Frequency:
- First paywall: Day 3-7 (user has tried app)
- Second paywall: Day 14+ (demonstrated value)
- Maximum: 2 paywalls per session
```

### Paywall UI Components

```swift
struct PremiumPaywall: View {
    @EnvironmentObject var purchaseManager: PurchaseManager
    @State private var selectedPackage: Package?

    var body: some View {
        VStack(spacing: 20) {
            // Header
            VStack(spacing: 8) {
                Image(systemName: "star.fill")
                    .font(.system(size: 40))
                    .foregroundColor(.yellow)

                Text("Unlock Premium")
                    .font(.title2)
                    .fontWeight(.bold)

                Text("Access all features and remove ads")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            .padding(.top, 20)

            // Benefits List
            VStack(alignment: .leading, spacing: 12) {
                BenefitRow(icon: "checkmark.circle.fill", text: "Unlimited downloads")
                BenefitRow(icon: "checkmark.circle.fill", text: "Ad-free experience")
                BenefitRow(icon: "checkmark.circle.fill", text: "Priority support")
                BenefitRow(icon: "checkmark.circle.fill", text: "Exclusive features")
            }
            .padding(.horizontal, 20)

            Spacer()

            // Pricing Options
            VStack(spacing: 12) {
                ForEach(purchaseManager.availablePackages, id: \.identifier) { package in
                    PricingCard(
                        package: package,
                        isSelected: selectedPackage?.identifier == package.identifier,
                        action: { selectedPackage = package }
                    )
                }
            }
            .padding(.horizontal, 20)

            // CTA Button
            Button(action: {
                if let package = selectedPackage {
                    purchaseManager.purchase(package)
                }
            }) {
                Text("Start Free Trial")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 20)

            // Disclaimer
            Text("Free for 7 days, then \(selectedPackage?.localizedPriceString ?? "$0")/month. Cancel anytime.")
                .font(.caption2)
                .foregroundColor(.gray)
                .padding(.horizontal, 20)
                .padding(.bottom, 10)
        }
        .background(Color(.systemBackground))
    }
}

struct BenefitRow: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.green)
                .font(.system(size: 16, weight: .semibold))

            Text(text)
                .font(.subheadline)

            Spacer()
        }
    }
}

struct PricingCard: View {
    let package: Package
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                VStack(alignment: .leading) {
                    Text(displayName)
                        .font(.headline)

                    Text(package.localizedPriceString)
                        .font(.title3)
                        .fontWeight(.bold)
                }

                Spacer()

                if let savingsPercentage = savingsPercentage {
                    Text("Save \(savingsPercentage)%")
                        .font(.caption2)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(4)
                }
            }

            Text(periodDescription)
                .font(.caption)
                .foregroundColor(.gray)
        }
        .padding(12)
        .background(isSelected ? Color.blue.opacity(0.1) : Color(.systemGray6))
        .border(isSelected ? Color.blue : Color.clear, width: 2)
        .cornerRadius(8)
        .onTapGesture(perform: action)
    }

    var displayName: String {
        switch package.identifier {
        case "monthly": return "Monthly"
        case "yearly": return "Yearly (Best Value)"
        default: return package.identifier.capitalized
        }
    }

    var periodDescription: String {
        guard let period = package.product.subscriptionPeriod else {
            return "One-time purchase"
        }
        return "Renews every \(period.stringRepresentation)"
    }

    var savingsPercentage: Int? {
        // Calculate savings for yearly vs monthly
        return nil // Implement calculation logic
    }
}
```

### Paywall Conversion Optimization

```
A/B Test Elements:

1. Headline Variations
   - "Unlock Premium" vs "Go Pro"
   - Emotional vs Feature-focused

2. Benefit Ordering
   - Most valuable first
   - Risk reversal (money-back guarantee)

3. CTA Button Text
   - "Start Free Trial" vs "Continue"
   - "7 Days Free" vs "Subscribe Now"

4. Pricing Display
   - Monthly equivalent shown for yearly
   - Crossed-out original price
   - "Save $X/year" messaging

5. Trial Length
   - 3 days: Faster conversion, higher churn
   - 7 days: Balanced approach
   - 14 days: Higher conversion, lower initial revenue

Metrics to Track:
- Paywall impression rate (% of users seeing it)
- Paywall conversion rate (% who purchase)
- Average revenue per user seeing paywall
- Time to first purchase
- Trial-to-paid conversion rate
```

---

## Pricing Strategies {#pricing-strategies}

Regional and promotional pricing approaches.

### Localized Pricing

```
PPP (Purchasing Power Parity) Strategy:

Monthly Subscription Base: $9.99
- United States: $9.99
- Canada: CAD $11.99
- UK: £7.99
- Germany: €8.99
- India: ₹199
- Brazil: R$ 29.99

Yearly Subscription (30% discount):
- United States: $69.99/year
- Germany: €62.99/year
- India: ₹1,299/year

Implementation:
- App Store/Play Store handle automatically
- RevenueCat supports localized pricing
- Consider App Store's recommended pricing

Price Points by Market:
Tier 1 (Low income): $0.99-$4.99
Tier 2 (Middle income): $4.99-$9.99
Tier 3 (High income): $9.99-$19.99
```

### Promotional Offers

```swift
// Promotional Offer Configuration
class PromotionalOfferManager {

    func createPromotionalOffer() -> PromotionalOffer {
        return PromotionalOffer(
            identifier: "vip_welcome",
            displayName: "Welcome Back",
            discountPrice: 4.99,
            period: .monthly,
            duration: 3, // 3 months
            type: .payAsYouGo
        )
    }

    // Reactivation offer for churned users
    func createWinBackOffer(for userId: String) -> PromotionalOffer {
        return PromotionalOffer(
            identifier: "winback_50off",
            displayName: "50% Off First Month",
            discountPrice: 2.49, // 50% of $4.99
            period: .monthly,
            duration: 1,
            type: .payAsYouGo,
            eligibility: .specific(userIds: [userId])
        )
    }

    // Limited-time offer
    func createTimebasedOffer() -> PromotionalOffer {
        return PromotionalOffer(
            identifier: "holiday_sale",
            displayName: "Holiday Special",
            discountPrice: 3.99,
            period: .monthly,
            duration: 2,
            startDate: Date(),
            endDate: Date().addingTimeInterval(30 * 24 * 3600), // 30 days
            type: .payAsYouGo
        )
    }

    // Grace Period (prevent churn)
    func enableGracePeriod(days: Int = 5) {
        // Extend subscription if payment fails
        // Allow users to retain access while billing retries
        // Settings in App Store/Google Play Console
    }
}

// Grace Period Benefits:
// - Reduces churn from payment failures
// - Allows retry with updated payment method
// - Extends subscription if billing recovers
```

### Pricing Psychology

```
Strategies:

1. Charm Pricing
   - $4.99 vs $5.00
   - $99.99 vs $100.00
   - Psychological impact on perception

2. Price Anchoring
   - Show original price struck through
   - Display alternative (more expensive) plan
   - Makes current offer seem valuable

3. Bundle Discounting
   - Yearly = 20-25% discount vs monthly
   - Family plan = 30% discount per seat
   - Shows value of commitment

4. Tiered Pricing
   - Good/Better/Best structure
   - Most users choose middle tier
   - Drives average revenue up

Example Tier Structure:
┌─────────────────────────────────┐
│ Basic (Popular)                 │
│ $4.99/month                     │
│ • Core features                 │
│ • Ad-supported                  │
│ ≈40% of users convert to this   │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Pro ★ BEST VALUE ★              │
│ $9.99/month (or $99.99/year)    │
│ • All features                  │
│ • Ad-free                       │
│ • Priority support              │
│ ≈45% of conversions             │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Family                          │
│ $14.99/month (up to 5 people)   │
│ • All Pro features              │
│ • For entire family             │
│ ≈15% of conversions             │
└─────────────────────────────────┘
```

---

## Receipt Validation {#receipt-validation}

Server-side verification of purchases.

### Apple Receipt Validation

```swift
// Client: Send receipt to server
func validateAppleReceipt(receiptData: Data) {
    let receiptString = receiptData.base64EncodedString()

    var request = URLRequest(url: URL(string: "https://your-server.com/validate-receipt")!)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")

    let body = ["receipt": receiptString]
    request.httpBody = try? JSONSerialization.data(withJSONObject: body)

    URLSession.shared.dataTask(with: request) { data, response, error in
        // Handle response
    }.resume()
}
```

```javascript
// Server: Validate Apple Receipt (Node.js/Express)
const axios = require('axios');

async function validateAppleReceipt(receiptData) {
    const payload = {
        'receipt-data': receiptData,
        'password': process.env.APPLE_SHARED_SECRET
    };

    const sandboxUrl = 'https://sandbox.itunes.apple.com/verifyReceipt';
    const productionUrl = 'https://buy.itunes.apple.com/verifyReceipt';

    try {
        let response = await axios.post(sandboxUrl, payload);

        if (response.data.status === 21007) {
            // Sandbox receipt, try production
            response = await axios.post(productionUrl, payload);
        }

        if (response.data.status === 0) {
            const receipt = response.data.receipt;

            // Verify bundle ID, product ID, expiration
            if (receipt.bundle_id === 'com.example.app' &&
                receipt.in_app[0].product_id === 'com.example.premium') {

                const expirationMs = parseInt(receipt.in_app[0].expires_date_ms);
                const isExpired = expirationMs < Date.now();

                return {
                    valid: true,
                    productId: receipt.in_app[0].product_id,
                    expiresAt: new Date(expirationMs),
                    isExpired: isExpired
                };
            }
        }

        return { valid: false, error: 'Invalid receipt status' };
    } catch (error) {
        console.error('Receipt validation error:', error);
        return { valid: false, error: error.message };
    }
}
```

### Google Play Billing Validation

```kotlin
// Client: Send purchase token to server
fun validateGooglePlayPurchase(purchaseToken: String, productId: String) {
    val payload = mapOf(
        "packageName" to BuildConfig.APPLICATION_ID,
        "productId" to productId,
        "token" to purchaseToken
    )

    // Send to your server for validation
    apiService.validatePurchase(payload).enqueue(object : Callback<ValidationResponse> {
        override fun onResponse(call: Call<ValidationResponse>, response: Response<ValidationResponse>) {
            if (response.isSuccessful) {
                val validation = response.body()
                handleValidationResult(validation)
            }
        }

        override fun onFailure(call: Call<ValidationResponse>, t: Throwable) {
            Log.e("Validation", "Failed to validate: ${t.message}")
        }
    })
}
```

```javascript
// Server: Validate Google Play Purchase (Node.js)
const { google } = require('googleapis');

async function validateGooglePlayPurchase(packageName, productId, token) {
    const androidpublisher = google.androidpublisher({
        version: 'v3',
        auth: googleAuth // Configured with service account credentials
    });

    try {
        const result = await androidpublisher.inappproducts.list({
            packageName: packageName
        });

        const purchase = await androidpublisher.inappproducts.get({
            packageName: packageName,
            sku: productId
        });

        // Validate purchase token
        const purchaseValidation = await androidpublisher.purchases.products.get({
            packageName: packageName,
            productId: productId,
            token: token
        });

        const purchaseData = purchaseValidation.data;

        if (purchaseData.purchaseState === 0) { // 0 = Purchased
            return {
                valid: true,
                productId: productId,
                purchaseTime: new Date(parseInt(purchaseData.purchaseTimeMillis)),
                autoRenewing: purchaseData.autoRenewing,
                orderId: purchaseData.orderId
            };
        }

        return { valid: false, error: 'Purchase not in valid state' };
    } catch (error) {
        console.error('Google Play validation error:', error);
        return { valid: false, error: error.message };
    }
}
```

### Receipt Caching & Expiration

```swift
// Cache validated receipt
class ReceiptCache {
    private var cache: [String: Receipt] = [:]
    private var cacheTimestamps: [String: Date] = [:]

    func cacheReceipt(_ receipt: Receipt, forUser userId: String) {
        cache[userId] = receipt
        cacheTimestamps[userId] = Date()
    }

    func getReceipt(forUser userId: String) -> Receipt? {
        guard let receipt = cache[userId],
              let timestamp = cacheTimestamps[userId] else {
            return nil
        }

        // Invalidate cache after 1 hour
        if Date().timeIntervalSince(timestamp) > 3600 {
            cache.removeValue(forKey: userId)
            cacheTimestamps.removeValue(forKey: userId)
            return nil
        }

        return receipt
    }
}
```

---

## Analytics & Metrics {#analytics}

Key metrics for monetization tracking.

### Critical Metrics

```
LTV (Lifetime Value):
- Total revenue per user over app lifetime
- Formula: ARPU × Average Subscription Duration
- Target: Optimize to > 5x CAC
- Tracking: Sum revenue events per user

ARPU (Average Revenue Per User):
- Monthly Recurring Revenue / Monthly Active Users
- Formula: MRR / MAU
- Benchmark: $0.50-$2.00 for F2P apps
- Target: Improve 10-15% monthly

ARPPU (Average Revenue Per Paying User):
- Total revenue / Paying user count
- Higher metric = better monetization
- Benchmark: $2.00-$5.00/month
- Action: Increase paying user percentage

Conversion Rate:
- % of users who make first purchase
- Target: 1-5% for F2P apps
- Benchmark: 2-3% for typical apps
- KPI: Month-over-month growth tracking

Trial-to-Paid Conversion:
- % of free trial users who convert to paid
- Target: 15-40% depending on category
- Action: Optimize paywall timing/messaging

Churn Rate:
- % of users cancelling subscription monthly
- Benchmark: 2-5% monthly churn
- Target: Reduce by improving value proposition
- Action: Implement retention features

Retention Curves:
Day 1: 100% (baseline)
Day 7: 20-40% (app quality indicator)
Day 30: 5-15% (engagement quality)
```

### Implementation Examples

```swift
// Analytics tracking
class AnalyticsManager {
    static let shared = AnalyticsManager()

    // Track purchase events
    func trackPurchaseCompleted(
        productId: String,
        price: Decimal,
        currency: String,
        transactionId: String
    ) {
        let parameters: [String: Any] = [
            "product_id": productId,
            "price": price,
            "currency": currency,
            "transaction_id": transactionId,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]

        Analytics.logEvent("purchase_completed", parameters: parameters)
    }

    // Track paywall impression
    func trackPaywallShown(
        reason: String,
        packageDisplayed: [String]
    ) {
        Analytics.logEvent("paywall_shown", parameters: [
            "reason": reason,
            "packages": packageDisplayed.joined(separator: ","),
            "timestamp": Date().timeIntervalSince1970
        ])
    }

    // Track subscription events
    func trackSubscriptionEvent(
        event: String,
        productId: String,
        expirationDate: Date
    ) {
        Analytics.logEvent("subscription_\(event)", parameters: [
            "product_id": productId,
            "renewal_date": expirationDate.timeIntervalSince1970
        ])
    }

    // Custom LTV tracking
    func trackUserMonetization(
        userId: String,
        lifetime_value: Decimal,
        subscription_status: String
    ) {
        Crashlytics.crashlytics().setUserID(userId)
        Crashlytics.crashlytics().setCustomValue(lifetime_value, forKey: "ltv")
        Crashlytics.crashlytics().setCustomValue(subscription_status, forKey: "sub_status")
    }
}

// Usage
AnalyticsManager.shared.trackPurchaseCompleted(
    productId: "com.example.premium.monthly",
    price: 4.99,
    currency: "USD",
    transactionId: transaction.id
)

AnalyticsManager.shared.trackPaywallShown(
    reason: "feature_locked",
    packageDisplayed: ["monthly", "yearly"]
)
```

### Dashboard Metrics

```
Daily/Weekly Reporting:
┌──────────────────────────────────────┐
│ Revenue                              │
│ Today: $2,145 (+15% vs yesterday)    │
│ 7-day average: $1,890/day            │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ New Subscriptions                    │
│ Today: 234 (+8%)                     │
│ Conversion rate: 3.2%                │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Churn Rate (Monthly)                 │
│ Current: 4.2% (-0.3% improvement)    │
│ Target: < 3%                         │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Active Subscriptions                 │
│ Current: 12,450 (+156 net)           │
│ MRR: $45,680                         │
└──────────────────────────────────────┘

Cohort Analysis:
Track users by acquisition date
- Day 1 retention: 35%
- Day 7 retention: 12%
- Day 30 retention: 4%
- LTV prediction: $8.50
```

---

## App Store Policies {#policies}

Compliance requirements for monetization.

### App Store Review Guidelines

```
1. Subscription Requirements (iOS):

Transparency:
- Clearly disclose subscription terms before purchase
- Show price, duration, renewal frequency
- Display cancellation method prominently
- Include link to privacy policy and T&Cs

Free Trial Requirements:
- Minimum 3 days (can be longer)
- Disable auto-renewal during trial
- Send renewal reminder 3 days before
- Honor cancellation requests immediately

Restrictions:
- No misleading free trial terms
- Cannot collect payment method for free trial
  (except for conversion to paid)
- Must allow easy cancellation (same method as signup)
- Cannot use misleading trial language

Refund Policy:
- Refund request within 45 days of purchase
- Process within 7-10 business days
- No restocking fees

2. In-App Purchase Requirements:

Product Restrictions:
- No illegal content
- No gambling/lotteries (with exceptions)
- No gift cards or currency redemption
- No access to illegal services

Pricing Rules:
- Prices must remain consistent across regions
- Cannot use "limited time" pricing for trials
- Introductory pricing must be clearly labeled

3. App Store Commission:

Standard Rate: 30% (can be 15% for subscriptions after 1 year)
Exceptions:
- Reader apps: 15% (but cannot direct to external purchase)
- Certain nonprofits: 15%
- Some government services: Exemptions apply
```

### Google Play Policy Compliance

```
1. Billing Requirements:

Subscription Transparency:
- Clear, prominent disclosure of subscription terms
- Full price breakdown visible before purchase
- Easy cancellation method (in-app or account settings)
- Renewal reminders 3 days before auto-renewal

Free Trial Policy:
- Clearly state trial length and terms
- Auto-renew only after explicit consent
- Allow cancellation anytime during trial
- Charge full price first time if user doesn't cancel

Restricted Products:
- No gambling or lotteries
- No gift cards or coupons
- Age-appropriate content only
- No sexual content

2. Billing Code Requirements:

- Acknowledge purchases within 3 days
- Complete refunds for refund requests
- Process cancellations immediately
- Provide receipt/proof of purchase

3. Play Store Commission:

Standard Rate: 15% (reduced from 30% in 2022)
Special Programs:
- Google Play Pass: Developer sets own subscription
- App Bundles: Reduced commission for targeted pricing

4. Policies Enforcement:

Violations can result in:
- App removal from store
- Developer account suspension
- Inability to publish new apps
- Loss of 30/15 days of revenue

Common rejection reasons:
- Misleading pricing
- Difficult cancellation process
- Non-functional payment system
- Policy violation in marketing
```

### Best Practices for Compliance

```
1. Transparency Checklist:

□ Subscription terms visible before purchase
□ Price shown in user's local currency
□ Renewal date/frequency clearly stated
□ Easy cancellation available in-app
□ Privacy policy and T&Cs accessible
□ Contact support information provided

2. User Communication:

Before Purchase:
- Clear CTA button text ("Subscribe", "Continue")
- Show exact billing date and amount
- Explain what user gets for the price
- Display trial length (if applicable)

After Purchase:
- Send order confirmation immediately
- Provide receipt with all details
- Include cancellation instructions
- Link to account management

3. Testing Before Launch:

□ Test all payment flows in sandbox
□ Verify receipt validation works
□ Test cancellation flow end-to-end
□ Validate refund processing
□ Check automatic renewal logic
□ Test with multiple payment methods

4. Post-Launch Monitoring:

- Monitor refund request rates (target: < 5%)
- Track user complaints about billing
- Monitor app store review sentiment
- Track cancellation reasons
- Analyze payment failure rates

Problem Resolution:
- Respond to negative reviews within 24 hours
- Offer refunds for billing issues
- Fix technical problems immediately
- Update app description if policy changes
```

---

## Summary Checklist

Monetization Implementation Checklist:

iOS:
- [ ] StoreKit 2 integration complete
- [ ] Products configured in App Store Connect
- [ ] Subscription renewal logic tested
- [ ] Receipt validation working server-side
- [ ] Paywall UI designed and optimized
- [ ] A/B testing framework in place
- [ ] Analytics events configured
- [ ] Privacy policy updated
- [ ] Review guidelines compliance verified

Android:
- [ ] Google Play Billing Library integrated
- [ ] Products configured in Google Play Console
- [ ] Purchase acknowledgment implemented
- [ ] Subscription status tracking working
- [ ] Receipt validation server-side verified
- [ ] Paywall design matches iOS
- [ ] Analytics events configured
- [ ] Play Store policies reviewed and complied

Cross-Platform:
- [ ] RevenueCat or similar configured
- [ ] Pricing strategy finalized
- [ ] Regional pricing implemented
- [ ] Ad mediation setup complete
- [ ] Analytics dashboards created
- [ ] Support process for billing issues defined
- [ ] Launch plan includes monetization strategy

---

**Last Updated:** March 2026

**References:**
- Apple StoreKit 2 Documentation
- Google Play Billing Library
- RevenueCat SDK
- Google AdMob
- App Store Review Guidelines
- Google Play Policies
