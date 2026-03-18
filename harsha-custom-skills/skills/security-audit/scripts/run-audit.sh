#!/bin/bash
# run-audit.sh - Pre-compute all grep patterns for security audit
# Usage: bash scripts/run-audit.sh [target-directory] [output-directory]
# Defaults: target=. output=./audit-workdir

set -e

TARGET_DIR="${1:-.}"
OUTPUT_DIR="${2:-./audit-workdir}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Security Audit Pre-Computation ===" >&2
echo "Target: $TARGET_DIR" >&2
echo "Output: $OUTPUT_DIR" >&2
echo "" >&2

# Create output structure
mkdir -p "$OUTPUT_DIR/grep-results"
mkdir -p "$OUTPUT_DIR/script-results"
mkdir -p "$OUTPUT_DIR/file-lists"

# ==================================================
# Phase 1: File Inventory
# ==================================================
echo "=== Phase 1: File Inventory ===" >&2

find "$TARGET_DIR" -type f \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/vendor/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/venv/*" \
  -not -path "*/.venv/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/.next/*" \
  -not -path "*/coverage/*" \
  -not -path "*/.tox/*" \
  > "$OUTPUT_DIR/file-lists/all-files.txt" 2>/dev/null || true

# Categorized file lists
grep -E '\.(js|ts|jsx|tsx)$' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/js-ts-files.txt" 2>/dev/null || true
grep -E '\.py$' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/python-files.txt" 2>/dev/null || true
grep -E '\.java$' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/java-files.txt" 2>/dev/null || true
grep -E '\.go$' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/go-files.txt" 2>/dev/null || true
grep -E '\.rb$' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/ruby-files.txt" 2>/dev/null || true
grep -E '\.php$' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/php-files.txt" 2>/dev/null || true
grep -E '\.(html|ejs|hbs|pug|jinja2?|vue|erb|jsp)$' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/template-files.txt" 2>/dev/null || true
grep -Ei '(routes?|controllers?|handlers?|api|middleware|views?|endpoints?)/' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/route-controller-files.txt" 2>/dev/null || true
grep -Ei '(auth|session|login|jwt|passport|token)' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/auth-files.txt" 2>/dev/null || true
grep -E '\.(json|ya?ml|toml|ini|cfg|conf|properties)$' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/config-files.txt" 2>/dev/null || true
grep -E '\.env' "$OUTPUT_DIR/file-lists/all-files.txt" \
  > "$OUTPUT_DIR/file-lists/env-files.txt" 2>/dev/null || true

FILE_COUNT=$(wc -l < "$OUTPUT_DIR/file-lists/all-files.txt" | tr -d ' ')
echo "Files found: $FILE_COUNT" >&2

# ==================================================
# Phase 2: Domain-specific Grep Scans
# ==================================================
echo "" >&2
echo "=== Phase 2: Grep Scans ===" >&2

# --- INJECTION DOMAIN ---
echo "  Scanning: injection" >&2
{
  echo "### SQL Injection"
  grep -rn 'query.*+.*req\.' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'execute.*%s' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn '\.format(.*input' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'f".*SELECT.*{' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn "f'.*SELECT.*{" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'executeQuery.*+' --include="*.java" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'Sprintf.*SELECT' --include="*.go" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### NoSQL Injection"
  grep -rn '\$where' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn '\$regex.*req\.' --include="*.js" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'JSON\.parse.*req\.' --include="*.js" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Command Injection"
  grep -rn 'os\.system(' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'subprocess.*shell=True' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'child_process\.exec(' --include="*.js" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'exec(.*\${' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'Runtime\.getRuntime()\.exec' --include="*.java" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Template Injection"
  grep -rn 'render_template_string(' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'Template(.*input' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/injection.txt"

# --- XSS-CSRF DOMAIN ---
echo "  Scanning: xss-csrf" >&2
{
  echo "### DOM XSS"
  grep -rn 'innerHTML' --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'outerHTML' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'document\.write' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'dangerouslySetInnerHTML' --include="*.jsx" --include="*.tsx" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'v-html' --include="*.vue" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'eval(' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Template XSS"
  grep -rn '|safe' --include="*.html" --include="*.jinja" --include="*.jinja2" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'mark_safe' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn '<%=.*%>' --include="*.ejs" "$TARGET_DIR" 2>/dev/null || true
  grep -rn '{{{' --include="*.hbs" --include="*.handlebars" "$TARGET_DIR" 2>/dev/null || true
  grep -rn '@Html\.Raw' --include="*.cshtml" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### CSRF"
  grep -rn 'csrf.*false' --include="*.js" --include="*.py" --include="*.rb" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'csrf_exempt' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'protect_from_forgery.*except' --include="*.rb" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### postMessage"
  grep -rn 'postMessage(' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'addEventListener.*message' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/xss-csrf.txt"

# --- AUTH-SESSION DOMAIN ---
echo "  Scanning: auth-session" >&2
{
  echo "### JWT"
  grep -rn 'jwt\.sign' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'jwt\.verify' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'algorithm.*none' -i --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'JWT_SECRET' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'PyJWT\|import jwt' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Session/Cookie"
  grep -rn 'httpOnly.*false' -i --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'secure.*false' -i --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'sameSite.*none' -i --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'express-session\|cookie-session' --include="*.js" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Password/Auth"
  grep -rn 'bcrypt\|argon2\|scrypt' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'md5\|sha1' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Timing Attack"
  grep -rn '===.*password\|password.*===' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'timingSafeEqual' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/auth-session.txt"

# --- ACCESS CONTROL DOMAIN ---
echo "  Scanning: access-control" >&2
{
  echo "### IDOR"
  grep -rn 'params\.id\|params\[.id.\]' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'findById(req\.params' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'request\.args\.get.*id' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Routes without Auth Middleware"
  grep -rn 'router\.\(get\|post\|put\|delete\|patch\)(' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn '@app\.route' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Role/Permission"
  grep -rn 'role.*=.*admin\|isAdmin' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'req\.user\.role\|currentUser\.role' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Privilege Escalation"
  grep -rn '\.update.*role\|role.*=.*req\.' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/access-control.txt"

# --- CRYPTO-DATA DOMAIN ---
echo "  Scanning: crypto-data" >&2
{
  echo "### Weak Hash"
  grep -rn 'createHash.*md5\|createHash.*sha1' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'hashlib\.md5\|hashlib\.sha1' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Weak Encryption"
  grep -rn 'DES\|3DES\|RC4\|Blowfish' --include="*.js" --include="*.ts" --include="*.py" --include="*.java" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'createCipher\b' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'ECB' --include="*.js" --include="*.ts" --include="*.py" --include="*.java" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Insecure Random"
  grep -rn 'Math\.random()' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'random\.random()\|random\.randint' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Hardcoded Keys"
  grep -rn "key.*=.*['\"].\{16,\}['\"]" --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn "iv.*=.*['\"]" --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/crypto-data.txt"

# --- SECRETS DOMAIN ---
echo "  Scanning: secrets" >&2
{
  echo "### AWS Keys"
  grep -rn 'AKIA[0-9A-Z]\{16\}' "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Private Keys"
  grep -rn '\-\-\-\-\-BEGIN.*PRIVATE KEY' "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### GitHub Tokens"
  grep -rn 'ghp_[a-zA-Z0-9]\{36\}' "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'github_pat_' "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Stripe Keys"
  grep -rn 'sk_live_[a-zA-Z0-9]\{24\}' "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'sk_test_[a-zA-Z0-9]\{24\}' "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Google API Keys"
  grep -rn 'AIza[0-9A-Za-z_-]\{35\}' "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Database URLs"
  grep -rn 'mongodb://[^:]\+:[^@]\+@' "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'postgres://[^:]\+:[^@]\+@' "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'mysql://[^:]\+:[^@]\+@' "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Generic Secrets"
  grep -rn "password\s*=\s*['\"][^'\"]\+['\"]" -i --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn "secret\s*=\s*['\"][^'\"]\+['\"]" -i --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/secrets.txt"

# --- CONFIG-HEADERS DOMAIN ---
echo "  Scanning: config-headers" >&2
{
  echo "### Security Headers"
  grep -rn 'Strict-Transport-Security\|X-Content-Type-Options\|X-Frame-Options' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'helmet\|lusca' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### CORS"
  grep -rn 'Access-Control-Allow-Origin' --include="*.js" --include="*.ts" --include="*.py" --include="*.java" "$TARGET_DIR" 2>/dev/null || true
  grep -rn "cors(\|allowedOrigins\|origin.*\*" --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Debug Mode"
  grep -rn 'DEBUG.*=.*True\|DEBUG.*=.*1' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'app\.debug\s*=\s*True' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'NODE_ENV.*development' "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/config-headers.txt"

# --- LOGGING-MONITORING DOMAIN ---
echo "  Scanning: logging-monitoring" >&2
{
  echo "### Sensitive Data in Logs"
  grep -rn 'console\.log.*password\|console\.log.*token\|console\.log.*secret' -i --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'logger.*password\|logger.*token\|logger.*api.key' -i --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'console\.log.*req\.body' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Log Injection"
  grep -rn 'console\.log.*\`.*\${' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/logging-monitoring.txt"

# --- ERROR HANDLING DOMAIN ---
echo "  Scanning: error-handling" >&2
{
  echo "### Stack Trace Exposure"
  grep -rn 'res\.send.*err\.stack\|res\.json.*stack' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'res\.status.*\.send.*err\b' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Exception Details in Response"
  grep -rn 'catch.*res\.\(send\|json\).*e\.message' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'except.*return.*str(e)' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Auth Error Oracle"
  grep -rn 'user not found\|invalid user\|no such user' -i --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'wrong password\|invalid password\|incorrect password' -i --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/error-handling.txt"

# --- CONCURRENCY DOMAIN ---
echo "  Scanning: concurrency" >&2
{
  echo "### Balance/Inventory TOCTOU"
  grep -rn 'balance.*-=\|balance.*+=\|balance.*=.*balance' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'inventory.*-=\|stock.*-=\|quantity.*-=' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Non-Atomic Counters"
  grep -rn 'counter++\|count++\|sequence++' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Double Submit"
  grep -rn 'app\.post.*payment\|router\.post.*charge' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Database Transactions"
  grep -rn '\.transaction\|BEGIN\|COMMIT\|ROLLBACK\|FOR UPDATE' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/concurrency.txt"

# --- API ENDPOINT DOMAIN ---
echo "  Scanning: api-endpoint" >&2
{
  echo "### Rate Limiting"
  grep -rn 'app\.post.*login\|router\.post.*auth' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'express-rate-limit\|rateLimit\|rate.limit' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Mass Assignment"
  grep -rn '\.create(req\.body)\|\.update(req\.body)' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'params\.permit!' --include="*.rb" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### SSRF"
  grep -rn 'fetch(.*req\.\|axios(.*req\.' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'requests\.get.*param' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Input Size"
  grep -rn 'bodyParser\.json()\|express\.json()' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Pagination"
  grep -rn 'find()\|findAll()\|\.all()' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/api-endpoint.txt"

# --- INPUT-OUTPUT DOMAIN ---
echo "  Scanning: input-output" >&2
{
  echo "### Path Traversal"
  grep -rn 'path\.join.*req\.\|path\.resolve.*req\.' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'readFile.*req\.\|readFileSync.*req\.' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'os\.path\.join.*request\|open.*request\.' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### File Upload"
  grep -rn 'multer()\|upload\.single\|upload\.array' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'originalname\|filename.*req\.' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Unsafe Deserialization"
  grep -rn 'pickle\.loads\|pickle\.load(' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'yaml\.load\|yaml\.unsafe_load' --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'ObjectInputStream\|readObject' --include="*.java" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Type Coercion"
  grep -rn '==\s*false\|==\s*null\|==\s*undefined' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/input-output.txt"

# --- BUSINESS LOGIC DOMAIN ---
echo "  Scanning: business-logic" >&2
{
  echo "### Price from Client"
  grep -rn 'req\.body\.price\|req\.body\.amount\|req\.body\.total' --include="*.js" --include="*.ts" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Coupon/Discount"
  grep -rn 'coupon\|discount\|promo' -i --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Workflow/State"
  grep -rn 'order.*status\|payment.*status\|workflow.*state' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Checkout/Payment"
  grep -rn 'checkout\|processOrder\|processPayment' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Trial/Subscription"
  grep -rn 'trialEnd\|expiresAt\|validUntil' --include="*.js" --include="*.ts" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/business-logic.txt"

# --- DATABASE SECURITY DOMAIN (Supabase/Postgres) ---
echo "  Scanning: database-security" >&2
{
  echo "### Service Role Key Exposure"
  grep -rn 'SUPABASE_SERVICE_ROLE\|service_role' --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" --include="*.vue" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'NEXT_PUBLIC.*SERVICE_ROLE\|VITE.*SERVICE_ROLE\|REACT_APP.*SERVICE_ROLE' "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'eyJ[a-zA-Z0-9_-]\{50,\}' --include="*.ts" --include="*.js" --include="*.tsx" --include="*.env*" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Missing RLS"
  grep -rn 'CREATE TABLE' --include="*.sql" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'ENABLE ROW LEVEL SECURITY\|DISABLE ROW LEVEL SECURITY' --include="*.sql" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'USING\s*(true)\|WITH CHECK\s*(true)' --include="*.sql" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'FOR ALL' --include="*.sql" "$TARGET_DIR" 2>/dev/null | grep -i 'policy' || true
  echo ""
  echo "### Unsafe Supabase Queries"
  grep -rn '\.rpc(.*\`\|\.rpc(.*+\|\.rpc(.*\${' --include="*.ts" --include="*.js" --include="*.tsx" "$TARGET_DIR" 2>/dev/null || true
  grep -rn '\.select(\`\|\.select(.*+\|\.select(.*\${' --include="*.ts" --include="*.js" --include="*.tsx" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Connection Security"
  grep -rn 'postgresql://\|postgres://\|pg://' --include="*.ts" --include="*.js" --include="*.py" --include="*.env*" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'sslmode.*disable\|ssl.*false' --include="*.ts" --include="*.js" --include="*.py" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Supabase Auth Issues"
  grep -rn 'supabase\.from(' --include="*.tsx" --include="*.jsx" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'signInWithOAuth\|resetPasswordForEmail' --include="*.ts" --include="*.js" --include="*.tsx" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Storage Security"
  grep -rn 'createBucket.*public.*true\|\.upload(' --include="*.ts" --include="*.js" --include="*.tsx" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'storage\.objects\|storage\.buckets' --include="*.sql" "$TARGET_DIR" 2>/dev/null || true
  echo ""
  echo "### Edge Function Security"
  grep -rn 'Access-Control-Allow-Origin.*\*' "$TARGET_DIR/supabase/functions/" 2>/dev/null || true
  grep -rn 'Deno\.env\.get' "$TARGET_DIR/supabase/functions/" 2>/dev/null || true
  echo ""
  echo "### Migration Safety"
  grep -rn 'DROP TABLE\|DROP COLUMN\|TRUNCATE\|DROP SCHEMA' --include="*.sql" "$TARGET_DIR" 2>/dev/null || true
  grep -rn 'EXECUTE.*||' --include="*.sql" "$TARGET_DIR" 2>/dev/null || true
} > "$OUTPUT_DIR/grep-results/database-security.txt"

# ==================================================
# Phase 3: SAST Pre-Scan (Semgrep)
# ==================================================
echo "" >&2
echo "=== Phase 3: SAST Pre-Scan ===" >&2

mkdir -p "$OUTPUT_DIR/sast-results"

if command -v semgrep &> /dev/null; then
  echo "  Running: Semgrep security audit ruleset" >&2
  semgrep scan --config p/security-audit --config p/owasp-top-ten \
    --json --output "$OUTPUT_DIR/sast-results/semgrep.json" \
    "$TARGET_DIR" 2>/dev/null || echo '{"errors": ["semgrep scan failed"]}' > "$OUTPUT_DIR/sast-results/semgrep.json"

  # Also generate SARIF for CI/CD integration
  semgrep scan --config p/security-audit \
    --sarif --output "$OUTPUT_DIR/sast-results/semgrep.sarif" \
    "$TARGET_DIR" 2>/dev/null || true

  SEMGREP_COUNT=$(python3 -c "import json; d=json.load(open('$OUTPUT_DIR/sast-results/semgrep.json')); print(len(d.get('results',[])))" 2>/dev/null || echo "?")
  echo "  Semgrep findings: $SEMGREP_COUNT" >&2
else
  echo "  Semgrep not found. Install: pip install semgrep" >&2
  echo "  SAST cross-referencing provides 96.9% detection against adversarial code." >&2
  echo "  Strongly recommended for prompt injection defense." >&2
  echo '{"note": "semgrep not installed", "results": []}' > "$OUTPUT_DIR/sast-results/semgrep.json"
fi

# ==================================================
# Phase 4: Run Python Scripts
# ==================================================
echo "" >&2
echo "=== Phase 4: Python Scripts ===" >&2

if [ -f "$SCRIPT_DIR/check-secrets.py" ]; then
  echo "  Running: check-secrets.py" >&2
  python3 "$SCRIPT_DIR/check-secrets.py" "$TARGET_DIR" > "$OUTPUT_DIR/script-results/secrets-scan.json" 2>/dev/null || echo '{"error": "check-secrets.py failed"}' > "$OUTPUT_DIR/script-results/secrets-scan.json"
else
  echo '{"error": "check-secrets.py not found"}' > "$OUTPUT_DIR/script-results/secrets-scan.json"
fi

if [ -f "$SCRIPT_DIR/scan-dependencies.py" ]; then
  echo "  Running: scan-dependencies.py" >&2
  python3 "$SCRIPT_DIR/scan-dependencies.py" "$TARGET_DIR" > "$OUTPUT_DIR/script-results/dependency-scan.json" 2>/dev/null || echo '{"error": "scan-dependencies.py failed"}' > "$OUTPUT_DIR/script-results/dependency-scan.json"
else
  echo '{"error": "scan-dependencies.py not found"}' > "$OUTPUT_DIR/script-results/dependency-scan.json"
fi

# ==================================================
# Phase 5: Summary
# ==================================================
echo "" >&2
echo "=== Scan Complete ===" >&2
echo "Results in: $OUTPUT_DIR" >&2
echo "" >&2
echo "Grep results:" >&2
ls -la "$OUTPUT_DIR/grep-results/" 2>/dev/null | tail -n +2 >&2 || true
echo "" >&2
echo "SAST results:" >&2
ls -la "$OUTPUT_DIR/sast-results/" 2>/dev/null | tail -n +2 >&2 || true
echo "" >&2
echo "Script results:" >&2
ls -la "$OUTPUT_DIR/script-results/" 2>/dev/null | tail -n +2 >&2 || true
echo "" >&2
echo "Lines per domain:" >&2
wc -l "$OUTPUT_DIR/grep-results/"* 2>/dev/null | grep -v total >&2 || true
echo "" >&2
echo "Total grep matches: $(cat "$OUTPUT_DIR/grep-results/"* 2>/dev/null | grep -v '^###' | grep -v '^$' | wc -l | tr -d ' ')" >&2
