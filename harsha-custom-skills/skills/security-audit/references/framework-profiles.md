# Framework Detection Profiles

This document provides detection logic and audit-relevant file locations for major web frameworks. Use this during reconnaissance (Phase 1) to identify the tech stack and target files.

---

## Detection Logic

Run these checks in order during codebase reconnaissance. For each framework detected, note the relevant security-critical files for focused auditing.

---

## Node.js / Express

### Detection Signals
- `package.json` exists with `express` in dependencies
- Entry files: `app.js`, `server.js`, `index.js`, `src/index.js`
- Middleware chain pattern: `app.use(...)`

### Security-Critical Files

| Category | Paths | What to Audit |
|----------|-------|---------------|
| Entry/Config | `app.js`, `server.js`, `src/app.js` | Middleware order, helmet/security headers |
| Routes | `routes/**/*.js`, `src/routes/**` | Auth middleware presence, input handling |
| Controllers | `controllers/**/*.js`, `src/controllers/**` | Business logic, data access patterns |
| Middleware | `middleware/**/*.js`, `src/middleware/**` | Auth checks, error handling |
| Auth | Files containing `passport`, `jwt`, `auth` | Token validation, session config |
| Config | `.env`, `config/*.js`, `config/**/*.json` | Secrets, debug flags, CORS settings |
| Database | Files with `mongoose`, `sequelize`, `knex` | Query construction, raw queries |

### Framework-Specific Patterns

```javascript
// Helmet check - should be near top of middleware
app.use(helmet());

// Session security check
session({
  cookie: { secure: true, httpOnly: true, sameSite: 'strict' }
})

// CSRF check
app.use(csrf());

// Rate limiting check
app.use(rateLimit({ ... }));
```

---

## Django (Python)

### Detection Signals
- `manage.py` + `settings.py` present
- `wsgi.py` or `asgi.py` in project root
- Apps structure: `apps/*/`, with `views.py`, `models.py`

### Security-Critical Files

| Category | Paths | What to Audit |
|----------|-------|---------------|
| Settings | `settings.py`, `*/settings/*.py` | DEBUG, SECRET_KEY, ALLOWED_HOSTS, CSP |
| URLs | `urls.py` (multiple, one per app) | Route patterns, auth requirements |
| Views | `views.py`, `*/views/**/*.py` | @csrf_exempt, raw SQL, user input |
| Models | `models.py`, `*/models/**/*.py` | Field validation, permissions |
| Auth | `auth.py`, files with `authenticate` | Password handling, session config |
| Templates | `templates/**/*.html` | safe filter usage, XSS patterns |
| Middleware | `middleware.py`, `MIDDLEWARE` in settings | Security middleware order |

### Framework-Specific Patterns

```python
# Settings checks
DEBUG = False  # Must be False in production
SECRET_KEY = os.environ.get('SECRET_KEY')  # Not hardcoded
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CSRF exemption (dangerous)
@csrf_exempt  # Flag this!

# Raw SQL (dangerous)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # Flag this!
```

---

## Flask (Python)

### Detection Signals
- `requirements.txt` or `Pipfile` with `flask`
- `from flask import` in Python files
- `app = Flask(__name__)` pattern

### Security-Critical Files

| Category | Paths | What to Audit |
|----------|-------|---------------|
| App | `app.py`, `run.py`, `wsgi.py`, `src/app.py` | Config, secret key, debug mode |
| Routes | `routes/**/*.py`, `blueprints/**/*.py` | @app.route decorators, input handling |
| Config | `config.py`, `.env`, `instance/config.py` | SECRET_KEY, DEBUG, database URLs |
| Auth | Files with `flask-login`, `flask-jwt` | Token handling, session config |
| Templates | `templates/**/*.html`, `**/*.jinja2` | safe filter, autoescape settings |
| Forms | Files with `flask-wtf`, `wtforms` | CSRF protection, validation |

### Framework-Specific Patterns

```python
# Debug check
app.run(debug=False)  # Must be False in production
app.config['DEBUG'] = False

# Secret key check
app.secret_key = os.environ.get('SECRET_KEY')  # Not hardcoded

# Template safety
{{ user_content|safe }}  # Flag this - XSS risk
{% autoescape false %}  # Flag this
```

---

## Next.js

### Detection Signals
- `next.config.js` or `next.config.mjs` present
- `pages/` or `app/` directory structure
- `package.json` with `next` dependency

### Security-Critical Files

| Category | Paths | What to Audit |
|----------|-------|---------------|
| Config | `next.config.js`, `next.config.mjs` | Headers, rewrites, security headers |
| API Routes | `pages/api/**/*.ts`, `app/api/**/route.ts` | Input validation, auth checks |
| Middleware | `middleware.ts` in project root | Auth verification, redirects |
| Auth | Files with `next-auth`, `auth.ts` | JWT config, session handling |
| Server Components | `app/**/*.tsx` (Server Components) | Data fetching, database access |
| Client Components | `'use client'` files | Client-side data handling |

### Framework-Specific Patterns

```typescript
// next.config.js security headers
headers: async () => [
  {
    source: '/:path*',
    headers: [
      { key: 'X-Frame-Options', value: 'DENY' },
      { key: 'X-Content-Type-Options', value: 'nosniff' },
    ],
  },
],

// API route auth check
export async function GET(req: Request) {
  const session = await getServerSession();  // Must check this
  if (!session) return new Response('Unauthorized', { status: 401 });
}

// Middleware auth
export function middleware(request: NextRequest) {
  const token = request.cookies.get('token');
  // Verify token here
}
```

---

## Spring Boot (Java)

### Detection Signals
- `pom.xml` with `spring-boot-starter` or `build.gradle` with spring
- `@SpringBootApplication` annotation
- `src/main/java/**/Application.java`

### Security-Critical Files

| Category | Paths | What to Audit |
|----------|-------|---------------|
| Config | `application.properties`, `application.yml` | Credentials, debug settings |
| Security | `**/SecurityConfig.java`, `**/WebSecurityConfig.java` | Auth config, CORS, CSRF |
| Controllers | `**/*Controller.java` | @RequestMapping, input handling |
| Services | `**/*Service.java` | Business logic, authorization |
| Repositories | `**/*Repository.java` | @Query annotations, native queries |
| Filters | `**/*Filter.java` | Request processing, auth |

### Framework-Specific Patterns

```java
// Security config check
@EnableWebSecurity
public class SecurityConfig {
    // CSRF should not be disabled without good reason
    http.csrf().disable();  // Flag this!

    // CORS configuration
    http.cors().configurationSource(corsConfigurationSource());
}

// SQL injection in @Query
@Query(value = "SELECT * FROM users WHERE name = " + name, nativeQuery = true)  // Flag!

// Input binding
@PostMapping
public User create(@RequestBody User user) {  // Check for mass assignment
```

---

## FastAPI (Python)

### Detection Signals
- `requirements.txt` with `fastapi`
- `from fastapi import` in Python files
- `app = FastAPI()` pattern

### Security-Critical Files

| Category | Paths | What to Audit |
|----------|-------|---------------|
| App | `main.py`, `app.py`, `src/main.py` | CORS config, middleware |
| Routes | `routers/**/*.py`, `api/**/*.py` | Depends(), input handling |
| Auth | `auth.py`, `security.py`, files with `OAuth2` | Token validation, dependencies |
| Config | `config.py`, `.env`, `settings.py` | Secrets, database URLs |
| Models | `models.py`, `schemas.py` | Pydantic validation, database models |

### Framework-Specific Patterns

```python
# CORS check
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Flag this - too permissive
)

# Auth dependency
@app.get("/protected")
async def protected(user: User = Depends(get_current_user)):  # Good pattern
    pass

# SQL injection check
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # Flag!
```

---

## Ruby on Rails

### Detection Signals
- `Gemfile` with `rails`
- `config/routes.rb` exists
- `app/` directory with `controllers/`, `models/`, `views/`

### Security-Critical Files

| Category | Paths | What to Audit |
|----------|-------|---------------|
| Config | `config/application.rb`, `config/environments/*.rb` | Security settings |
| Routes | `config/routes.rb` | Route definitions, constraints |
| Controllers | `app/controllers/**/*.rb` | Strong params, auth |
| Models | `app/models/**/*.rb` | Validations, scopes, SQL |
| Views | `app/views/**/*.erb` | html_safe, raw usage |
| Initializers | `config/initializers/*.rb` | Devise, auth configuration |

### Framework-Specific Patterns

```ruby
# Strong parameters check
params.permit(:name, :email)  # Good - explicit allowlist
params.permit!  # Flag this - allows all params

# Auth check
before_action :authenticate_user!  # Should be present on protected controllers

# XSS patterns
<%= raw user_content %>  # Flag this
<%= user_content.html_safe %>  # Flag this

# SQL injection
User.where("name = '#{params[:name]}'")  # Flag this!
```

---

## Quick Detection Script

Run this to identify frameworks in a codebase:

```bash
#!/bin/bash
echo "=== Framework Detection ==="

# Node.js/Express
[ -f "package.json" ] && grep -q '"express"' package.json && echo "Detected: Express (Node.js)"

# Next.js
[ -f "next.config.js" ] || [ -f "next.config.mjs" ] && echo "Detected: Next.js"

# Django
[ -f "manage.py" ] && [ -f "*/settings.py" -o -d "*/settings" ] && echo "Detected: Django"

# Flask
grep -rq "from flask import" --include="*.py" 2>/dev/null && echo "Detected: Flask"

# FastAPI
grep -rq "from fastapi import" --include="*.py" 2>/dev/null && echo "Detected: FastAPI"

# Spring Boot
[ -f "pom.xml" ] && grep -q "spring-boot" pom.xml && echo "Detected: Spring Boot"
[ -f "build.gradle" ] && grep -q "spring" build.gradle && echo "Detected: Spring Boot (Gradle)"

# Rails
[ -f "Gemfile" ] && grep -q "rails" Gemfile && echo "Detected: Ruby on Rails"

# Supabase
[ -f "supabase/config.toml" ] && echo "Detected: Supabase"
[ -f "package.json" ] && grep -q "@supabase/supabase-js" package.json 2>/dev/null && echo "Detected: Supabase Client"
[ -d "supabase/migrations" ] && echo "Detected: Supabase Migrations"
[ -d "supabase/functions" ] && echo "Detected: Supabase Edge Functions"
```

---

## Supabase (Backend-as-a-Service)

### Detection Signals
- `package.json` with `@supabase/supabase-js` in dependencies
- `supabase/config.toml` exists
- `supabase/migrations/` directory with `.sql` files
- `supabase/functions/` directory (Edge Functions)
- Environment variables: `SUPABASE_URL`, `SUPABASE_ANON_KEY`

### Security-Critical Files

| Category | Paths | What to Audit |
|----------|-------|---------------|
| Client Init | Files with `createClient`, `createBrowserClient`, `createServerClient` | Service role key exposure, proper client type |
| Migrations | `supabase/migrations/**/*.sql` | RLS enablement, destructive DDL, policy completeness |
| RLS Policies | `.sql` files with `CREATE POLICY` | Overly permissive policies, FOR ALL usage |
| Edge Functions | `supabase/functions/**/*.ts` | Auth verification, CORS, env var handling |
| Auth Config | Files with `supabase.auth.*` | OAuth redirects, email confirmation, rate limits |
| Storage | Files with `supabase.storage.*` | Public buckets, upload validation, storage policies |
| Env Files | `.env*`, `supabase/config.toml` | Service role key not in client-accessible vars |
| Middleware | Server-side auth middleware files | Session verification, token refresh handling |

### Framework-Specific Patterns

```typescript
// CRITICAL: Service role key must NEVER be in client code
// BAD - exposed to browser
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY!)

// GOOD - anon key for client
const supabase = createBrowserClient(url, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!)

// GOOD - service role only on server
const supabase = createClient(url, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
  auth: { autoRefreshToken: false, persistSession: false }
})
```

```sql
-- CRITICAL: Every table MUST have RLS enabled
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- GOOD: Separate policies per operation
CREATE POLICY "select_own" ON public.documents FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "insert_own" ON public.documents FOR INSERT WITH CHECK (auth.uid() = user_id);

-- BAD: Overly permissive
CREATE POLICY "allow_all" ON public.documents FOR ALL USING (true);
```

### Common Supabase + Next.js Stack

When Supabase is used with Next.js, pay special attention to:
1. **Server Components vs Client Components**: Service role key must only be in Server Components
2. **Middleware auth**: `middleware.ts` should verify Supabase session
3. **Route Handlers**: `app/api/**/route.ts` must validate auth before data access
4. **Server Actions**: Verify auth in every server action that accesses Supabase

---

## Multi-Framework Projects

Some projects use multiple frameworks (e.g., Next.js frontend + FastAPI backend). In such cases:

1. Identify all frameworks present
2. Audit each layer separately using respective profiles
3. Pay special attention to integration points (API boundaries, auth token passing)
4. Check CORS configuration between frontend and backend
5. Verify auth is validated on both sides where applicable
