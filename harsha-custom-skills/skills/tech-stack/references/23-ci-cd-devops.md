# CI/CD & DevOps Tech Stack Reference (2025-2026)

**Last Updated:** February 2026
**Research Focus:** GitHub Actions, Docker, Coolify, Kamal, Terraform, Pulumi

## Executive Summary (5-line TL;DR)
- GitHub Actions is default CI/CD for most teams; note new $0.002/min platform charge in 2026 for private repos
- Docker + multi-stage builds for all containerized deployments; Kamal 2 for simple VPS-based deploys
- Coolify (self-hosted Heroku alternative) for startups wanting $0 CI/CD with Docker Compose workflows
- Terraform remains IaC standard but Pulumi gaining for TypeScript teams wanting real programming language
- GitLab CI for teams needing integrated DevSecOps; Buildkite for high-scale custom runners

---

## Table of Contents

1. [GitHub Actions](#github-actions)
2. [Container Registries](#container-registries)
3. [Docker & Containerization](#docker--containerization)
4. [Deployment Tools](#deployment-tools)
5. [Infrastructure as Code (IaC)](#infrastructure-as-code)
6. [Decision Logic & IF/THEN Rules](#decision-logic--ifthen-rules)

---

## GitHub Actions

### Free Tier Limits (2025-2026)

| Aspect | Details |
|--------|---------|
| **Free Minutes/Month** | 2,000 minutes for private repositories |
| **Public Repositories** | Unlimited (standard GitHub-hosted runners) |
| **Storage** | 500MB per workspace |
| **Self-Hosted Runners** | Currently free (control plane billing postponed) |

**Sources:**
- [GitHub Actions Pricing Changes 2026](https://resources.github.com/actions/2026-pricing-changes-for-github-actions/)
- [GitHub Actions Billing Documentation](https://docs.github.com/billing/managing-billing-for-github-actions/about-billing-for-github-actions)

### Pricing Changes (January 1, 2026)

- **Hosted Runner Price Reduction:** 39% price cut on GitHub-hosted runners
- **Control Plane Fee:** $0.002 per minute across all workflows (applies to all Actions workloads, not just private repos)
- **Public Repository Exemption:** No impact on public repositories
- **Self-Hosted Runner Fee:** Originally announced for March 1, 2026, but GitHub is postponing this billing change to re-evaluate

**Critical Note:** GitHub postponed the self-hosted runner per-minute charge, so currently there is no direct cost for self-hosted runners beyond your own infrastructure expenses.

**Sources:**
- [GitHub Actions Pricing Changes - Official](https://resources.github.com/actions/2026-pricing-changes-for-github-actions/)
- [GitHub Walks Back Self-Hosted Runner Charges](https://www.theregister.com/2025/12/17/github_charge_dev_own_hardware/)
- [Cirrus Runners - Self-Hosted Pricing Analysis](https://cirrus-runners.app/blog/2025/12/16/new-pricing-of-self-hosted-github-actions-runners-explained/)

### Self-Hosted Runners

**Costs:**
- Control plane fee: Postponed (was $0.002/minute, now under re-evaluation)
- Infrastructure costs: Only pay for your own VM/hardware (AWS, Azure, on-prem, etc.)

**Key Features:**
- Docker support for running jobs in containers
- Custom hardware configurations
- No bandwidth limits
- Ideal for large-scale, repetitive workflows

**Use Case:** Best for organizations running 1000+ minutes/month or requiring specific hardware/security requirements.

**Sources:**
- [GitHub Self-Hosted Runners Documentation](https://docs.github.com/en/actions/hosting-your-own-runners)
- [WarpBuild - GitHub Actions Price Change](https://www.warpbuild.com/blog/github-actions-price-change)

### Common Workflows & Patterns (2025)

**1. Build & Test on Pull Request**
```yaml
name: Tests
on:
  pull_request:
    branches: [main, develop]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint
      - run: npm test
```

**2. Publish Docker Image**
```yaml
name: Publish Docker Image
on:
  push:
    branches: [main]
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
```

**3. Service Integration (Database Testing)**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
```

**4. Parallel Jobs**
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build
```

**Sources:**
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Building a CI/CD Workflow with GitHub Actions](https://resources.github.com/learn/pathways/automation/essentials/building-a-workflow-with-github-actions/)
- [FreeCodeCamp - GitHub Actions Guide](https://www.freecodecamp.org/news/automate-cicd-with-github-actions-streamline-workflow/)

---

## Container Registries

### Comparison Matrix (2025-2026)

| Registry | Private Repos | Storage | Data Transfer | Pull Rate Limits | GitHub Actions |
|----------|---------------|---------|----------------|------------------|-----------------|
| **Docker Hub Free** | 1 | Unlimited | 200 pulls/6hrs | 100 pulls/IP/day | Subject to limits |
| **GitHub Container Registry (GHCR)** | Unlimited | 500MB (private), Unlimited (public) | 1GB/month (private) | Unlimited | **Free & Unlimited** |
| **Cloudflare Registry** | N/A | N/A | See pricing | N/A | Via Workers |

### Docker Hub (2025)

**Free Tier Limits:**
- 100 anonymous pulls per 6 hours per IP address
- 200 pulls per 6 hours for authenticated Docker Personal users
- 1 private repository

**Recent Policy Updates:**
- Previously planned April 1, 2025 rate limit enforcement was postponed
- Current limits remain in effect as Docker evaluates developer feedback
- Unlimited pulls available for all paid Docker subscribers (with fair use policy)

**Rate Limiting Impact on CI/CD:**
Rate limits can cause pipeline throttling, unexpected build failures, and deployment delays.

**Sources:**
- [Docker Hub Rate Limits Announcement](https://www.docker.com/blog/revisiting-docker-hub-policies-prioritizing-developer-experience/)
- [The Hidden Costs of DockerHub](https://jeevisoft.com/blogs/2025/07/the-hidden-costs-of-dockerhub-when-free-isnt-really-free/)

### GitHub Container Registry (GHCR)

**Advantages:**
- Unlimited private repositories
- 500MB free storage for private images
- 1GB free outgoing data transfer per month (private images)
- **Unlimited free data transfer within GitHub Actions workflows**
- Better integration with GitHub Enterprise

**Key Benefits:**
- No rate limits on pulls
- Seamless GitHub Actions integration (no quota consumption)
- Public images: completely free storage and transfer

**Recommendation:** Best choice for GitHub-based teams with private repositories.

**Sources:**
- [Comparing Docker Hub and GHCR - JFrog](https://jfrog.com/devops-tools/article/comparing-docker-hub-and-github-container-registry/)
- [GitHub Container Registry vs Docker Hub Comparison](https://shipyard.build/blog/container-registries/)

### Cloudflare Registry

**Note:** Cloudflare does not currently offer a dedicated container registry service. Cloudflare Containers is compute-focused (Workers Containers), not a registry service.

---

## Docker & Containerization

### Multi-Stage Builds

**Purpose:** Reduce final image size and improve build efficiency by separating build-time and runtime dependencies.

**Best Practices (2025):**

**1. Separate Build and Runtime Stages**
```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/index.js"]
```

**2. Optimize Layer Caching**
- Place less frequently changed steps earlier in the Dockerfile
- Dependencies that change infrequently should be in earlier stages
- Application code (which changes frequently) should be in later stages

**3. Use Slim Base Images for Production**
- Build stage: Use full-featured image (e.g., `node:20`)
- Runtime stage: Use slim/alpine image (e.g., `node:20-alpine`)
- Reduces image size, attack surface, and vulnerabilities

**4. Named Stages for Clarity**
```dockerfile
FROM node:20 AS dependencies
FROM node:20-alpine AS runtime
FROM node:20-alpine AS test
```

**5. BuildKit Optimization**
- BuildKit only builds stages that the target stage depends on
- Can build stages in parallel when possible
- Enable with: `DOCKER_BUILDKIT=1 docker build .`

**Benefits:**
- Smaller final images (80-90% size reduction typical)
- Faster builds through better caching
- Reduced attack surface
- Clear separation of concerns

**Sources:**
- [Docker Multi-Stage Builds Documentation](https://docs.docker.com/build/building/multi-stage/)
- [Docker Multi-Stage Builds Best Practices](https://spacelift.io/blog/docker-multistage-builds)
- [Advanced Dockerfiles with BuildKit](https://www.docker.com/blog/advanced-dockerfiles-faster-builds-and-smaller-images-using-buildkit-and-multistage-builds/)

### Docker Compose for Local Development

**Use Cases:**
- Local development environment setup
- Testing multi-service applications locally
- Integration testing with real services (databases, caches)
- Onboarding new developers (single `docker-compose up` command)

**Advantages:**
- Simple YAML configuration
- Minimal learning curve
- Quick startup on local machines
- Native networking between services

**Example:**
```yaml
version: '3.9'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/myapp
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myapp
    volumes:
      - db_data:/var/lib/postgresql/data
volumes:
  db_data:
```

**When to Use vs Kubernetes:**
- **Docker Compose:** Local dev, small teams, learning orchestration
- **Kubernetes:** Production at scale, multi-region deployments, complex networking

**Sources:**
- [Docker Compose vs Kubernetes - Better Stack](https://betterstack.com/community/guides/scaling-docker/docker-compose-vs-kubernetes/)
- [Docker Compose vs Kubernetes Local Development](https://shipyard.build/blog/comparing-docker-kubernetes-local-dev/)

---

## Deployment Tools

### Coolify v4 (2025)

**Overview:** Open-source, self-hostable PaaS alternative to Vercel, Heroku, and Netlify.

**Key Features:**
- Deploy 280+ one-click services
- Support for static sites, APIs, full-stack applications, databases
- Multi-cloud deployment: AWS, Azure, DigitalOcean, Hetzner, Linode, Raspberry Pi
- Git integration: GitHub, GitLab, Bitbucket, Gitea
- Notifications: Discord, Telegram, Email
- Both self-hosted and managed Cloud options

**Pricing:**

| Plan | Cost | Features |
|------|------|----------|
| Self-Hosted | Free | Full feature set, manage your own servers |
| Coolify Cloud | $5/month base | Up to 2 servers, automatic backups, email notifications |
| Additional Servers | $3/month each | Scale beyond 2 servers |

**Use Cases:**
- Cost-conscious teams wanting Heroku-like experience
- Full control over infrastructure
- Multi-framework support needed
- Rapid deployment iterations

**Sources:**
- [Coolify Pricing Page](https://coolify.io/pricing/)
- [Coolify Documentation](https://coolify.io/docs/)
- [Coolify GitHub Repository](https://github.com/coollabsio/coolify)

### Kamal 2 (2025)

**Overview:** Modern deployment tool from Basecamp (37signals) for running web apps on VMs or bare metal without orchestration complexity.

**Key Differences from Kamal 1:**

| Feature | Kamal 1 | Kamal 2 |
|---------|---------|---------|
| Proxy | NGINX | Custom kamal-proxy |
| Multi-app | Single app | Multiple apps to same server |
| Multi-role | Limited | Web + background workers |
| Deployment | Slower | Faster with proxy commands |
| Configuration | Complex | Simplified |

**New Features in v2:**
- Maintenance mode
- Request pausing
- Canary deployments
- Multi-role deployments (separate web and worker containers)
- Faster deployment cycles

**Use Cases:**
- Rails/Phoenix applications
- Single-server to 50-server deployments
- Teams wanting simplicity over Kubernetes
- Direct container-to-VM deployments

**Adoption (2025):**
- Basecamp running all HEY deployments on Kamal 2
- Growing community adoption
- Latest release: v2.8.2 (March 2025)
- Framework support expanding beyond Rails

**Sources:**
- [Kamal 2.0 Release - 37signals](https://dev.37signals.com/kamal-2/)
- [Kamal Deployment Documentation](https://kamal-deploy.org/)
- [Deploying Multiple Apps with Kamal 2](https://www.honeybadger.io/blog/new-in-kamal-2/)

### SST Ion (v3) (2025)

**Overview:** Modern serverless infrastructure framework that replaced AWS CDK with Pulumi/Terraform backend.

**Major Architectural Shift:**

**SST v2 (Old):**
- Built on AWS CDK
- CloudFormation deployment
- Slower deployments
- AWS-only

**SST Ion (v3, Current):**
- Built on Pulumi + Terraform
- TypeScript version of Terraform providers
- Significantly faster deployments
- Multi-cloud support: AWS, Azure, Google Cloud, Cloudflare

**Key Improvements:**
- 30-50% faster deployments
- Better performance on updates (2nd+ deployments)
- Simpler mental model than CDK
- No need to learn CDK constructs

**CDK Compatibility Note:**
- L1 CloudFormation constructs can be migrated
- L2/L3 CDK Constructs have no direct replacements
- Need to migrate to Pulumi/Terraform equivalents
- Breaking change requiring code rewrites

**Multi-Cloud Example:**
```typescript
import * as aws from "@pulumi/aws";
import * as cloudflare from "@pulumi/cloudflare";

const bucket = new aws.s3.Bucket("website", {
  acl: "public-read",
});

const zone = new cloudflare.Zone("domain", {
  account_id: process.env.CLOUDFLARE_ACCOUNT_ID,
  zone: "example.com",
});
```

**Use Cases:**
- AWS serverless applications
- Multi-cloud deployments
- Teams familiar with Terraform
- Infrastructure requiring frequent updates

**Sources:**
- [SST v3 Blog Post](https://sst.dev/blog/sst-v3/)
- [SST Moving Away from CDK](https://sst.dev/blog/moving-away-from-cdk/)
- [AWS CDK vs Pulumi - Why SST Chose Pulumi](https://www.pulumi.com/blog/aws-cdk-vs-pulumi-why-sst-switched/)

---

## Infrastructure as Code

### Terraform vs Pulumi Comparison (2025)

#### Language & Syntax

| Aspect | Terraform | Pulumi |
|--------|-----------|--------|
| **Language** | HCL (custom DSL) | Python, Go, TypeScript, C#, Java |
| **Learning Curve** | Low (purpose-built) | Medium (general programming) |
| **Type Safety** | Limited | Full (depends on language) |
| **IDE Support** | Basic | Excellent (use language tooling) |
| **Ecosystem** | Large provider library | Terraform providers + native SDKs |

#### Key Differences

**1. Programming Model**

**Terraform (Declarative):**
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  acl    = "private"

  tags = {
    Name = "My Bucket"
  }
}
```

**Pulumi (Imperative):**
```python
import pulumi
import pulumi_aws as aws

bucket = aws.s3.Bucket("example",
    acl="private",
    tags={"Name": "My Bucket"})
```

**2. Testing & Integration**

**Terraform:**
- Terraform testing requires external frameworks (Terratest)
- Limited ability to validate before apply
- CI/CD integration via Terraform Cloud

**Pulumi:**
- Native language testing (unittest, pytest, Go testing)
- Unit test infrastructure before deployment
- Built-in policy as code with OPA
- Easier integration with existing dev workflows

**3. Parallelism & Performance**

CNCF Q2 2025 Benchmarks (5,000-resource Azure environment):
- **Pulumi:** 30% faster deployment due to parallel execution
- **Terraform Plan Phase:** 20% faster due to lightweight planner

**4. Ecosystem & Provider Support**

**Terraform:**
- 2,000+ providers
- Longest provider ecosystem
- Community-driven provider development

**Pulumi:**
- Wraps Terraform providers + native SDKs
- Same broad compatibility as Terraform
- Better tooling for complex logic

**5. Policy as Code**

**Terraform:**
- Sentinel (HashiCorp proprietary language)
- Limited to Terraform Cloud/Enterprise

**Pulumi:**
- Open Policy Agent (OPA) support
- Write policies in Rego or Python
- Works with all Pulumi deployments

#### Decision Matrix

**Choose Terraform if:**
- Team is operations-focused
- Multi-cloud with heavy Terraform usage
- Prefer declarative approach
- Already invested in Terraform ecosystem
- Need largest provider library

**Choose Pulumi if:**
- Team is developer-focused
- Need complex infrastructure logic
- Rapid iteration and testing required
- Want programming language flexibility
- Testing infrastructure is priority

#### Cost Comparison

| Tool | Free Tier | Standard | Enterprise |
|------|-----------|----------|------------|
| **Terraform** | Open source (terraform.io) | Cloud/Enterprise | CustomPricing |
| **Pulumi** | Open source | Free (Community) | Paid teams |

**Sources:**
- [Pulumi vs Terraform - Official Comparison](https://www.pulumi.com/docs/iac/comparisons/terraform/)
- [IaC Tools Comparison 2025](https://atmosly.com/knowledge/iac-tools-comparison-terraform-vs-pulumi-2025-guide/)
- [Spacelift - Pulumi vs Terraform](https://spacelift.io/blog/pulumi-vs-terraform)
- [CNCF Infrastructure Benchmarks](https://www.cncf.io/)

---

## Decision Logic & IF/THEN Rules

### CI/CD Platform Selection

```
IF project is open-source
  THEN use GitHub Actions (unlimited free minutes on public repos)

IF private repo with <2,000 minutes/month
  THEN use GitHub Actions free tier

IF private repo with >5,000 minutes/month
  AND need cost optimization
  THEN use self-hosted runners (infrastructure costs only)

IF need vendor independence
  THEN use self-hosted runners (not locked to GitHub)

IF using GitHub Enterprise
  THEN GitHub Actions pricing is favorable (per-minute cost lower)
```

### Container Registry Selection

```
IF using GitHub Actions
  AND storing private images
  THEN use GitHub Container Registry (unlimited free transfers in Actions)

IF team uses Docker ecosystem heavily
  AND has budget for Docker Pro
  THEN use Docker Hub (largest community, most images)

IF want minimal operational overhead
  AND building in GitHub
  THEN use GHCR (native integration, no external account)

IF multi-registry needed
  THEN use GHCR for private work
  AND Docker Hub for public work
```

### Deployment Tool Selection

```
IF need simple, cost-effective PaaS
  AND comfortable self-hosting
  THEN use Coolify ($5/month for 2 servers)

IF deploying Rails/Phoenix
  AND want simplicity over Kubernetes
  THEN use Kamal 2

IF serverless AWS architecture
  AND need fast iterations
  THEN use SST Ion

IF need multi-cloud
  AND serverless is primary
  THEN use SST Ion (Cloudflare, Azure, GCP support)

IF already using Heroku/Vercel
  AND want to reduce costs
  THEN evaluate Coolify self-hosted
```

### Infrastructure as Code Selection

```
IF team is primarily operators/DevOps
  THEN use Terraform (larger ecosystem, proven at scale)

IF team is primarily developers
  AND want language flexibility
  THEN use Pulumi

IF need complex conditional logic
  AND infrastructure validation
  THEN use Pulumi (testing advantages)

IF already invested in Terraform
  THEN avoid migration (switching costs high)

IF starting green-field multi-cloud
  THEN evaluate Pulumi (better language support)

IF need largest provider ecosystem
  THEN use Terraform (2,000+ providers)
```

### Containerization Strategy

```
IF building production images
  THEN always use multi-stage builds

IF want <100MB images
  THEN use Alpine base images

IF developing locally
  THEN use Docker Compose (simplest setup)

IF scaling to 100+ servers
  CONSIDER Kubernetes instead of Compose

IF images >500MB
  THEN review if multi-stage build optimization applied
```

---

## 2026 Outlook & Anticipated Changes

### GitHub Actions
- Control plane per-minute charge: $0.002/minute (applies to most workflows)
- Self-hosted runner charges: Postponed (likely 2026-2027)
- Expect further hosted runner price reductions as competition increases

### Container Registries
- Docker Hub rate limits likely to persist
- GHCR integration will deepen with GitHub ecosystem
- Expect more registry options from cloud providers

### Deployment Tools
- Kamal adoption will grow (Rails community primarily)
- SST Ion will see adoption as teams migrate from CDK
- Coolify will likely see growth from cost-conscious teams

### Infrastructure as Code
- Pulumi adoption growing among developer-focused teams
- Terraform remains dominant in operations/multi-cloud
- OpenTofu (Terraform fork) gaining some adoption

---

## References & Sources

### GitHub Actions
- [GitHub Actions Pricing Changes 2026](https://resources.github.com/actions/2026-pricing-changes-for-github-actions/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Billing Guide](https://docs.github.com/billing/managing-billing-for-github-actions/about-billing-for-github-actions)

### Docker & Registries
- [Docker Hub Rate Limits](https://www.docker.com/blog/revisiting-docker-hub-policies-prioritizing-developer-experience/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)

### Deployment Tools
- [Coolify](https://coolify.io/)
- [Kamal Deploy](https://kamal-deploy.org/)
- [SST Framework](https://sst.dev/)

### Infrastructure as Code
- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Terraform Documentation](https://www.terraform.io/docs/)
- [Pulumi vs Terraform Comparison](https://www.pulumi.com/docs/iac/comparisons/terraform/)

---

**Document Version:** 1.0
**Last Verified:** February 2026
**Maintainer Notes:** This document should be updated quarterly as pricing and features evolve rapidly in the CI/CD/DevOps space.

<!-- PRICING_STABILITY: MODERATE | Updated: 2026-03-03 | Tool/platform pricing changes annually. Verify before critical decisions. -->

---
## Related References
- [Monorepo Tooling & DX](./49-monorepo-dx-tooling.md) — Turborepo, Nx, pnpm workspaces CI/CD
- [Feature Flags & Experimentation](./57-feature-flags-experimentation.md) — Progressive delivery, canary deployments
- [Testing Strategies](./53-testing-strategies.md) — Test pyramid, CI integration patterns
- [DevOps & Platform Engineering](./48-devops-platform-engineering.md) — Platform team patterns
