---
title: Deployment Platform Comparison
auto_review: true
review_prompt: |
  Review this deployment platform comparison for accuracy.
  Focus on the "Eschewed Options" section - check if any of the
  reasons for not choosing those platforms are now outdated.
  Update pricing, features, and capabilities as needed.
review_context: |
  This document is used by our engineering team to make
  infrastructure decisions for hosting static sites and Next.js apps.
last_reviewed: 2024-06-15
review_interval_days: 30
---

# Deployment Platform Comparison

Last updated: June 2024

## Overview

This document compares deployment platforms for our static sites and Next.js applications.

## Our Choice: Vercel

We chose Vercel as our primary deployment platform for the following reasons:

- Native Next.js support (same company)
- Excellent developer experience
- Fast global CDN
- Built-in preview deployments
- Generous free tier for hobby projects

### Pricing (as of June 2024)

| Plan | Price | Bandwidth | Build Minutes |
|------|-------|-----------|---------------|
| Hobby | Free | 100 GB | 6,000/month |
| Pro | $20/user/month | 1 TB | 24,000/month |
| Enterprise | Custom | Custom | Custom |

## Eschewed Options

### GitHub Pages

**Why we didn't choose it:**

- No server-side rendering support
- Limited to static sites only
- No built-in preview deployments for PRs
- Custom domain SSL can be tricky

**When to reconsider:**

- Simple static documentation sites
- Open source project pages
- When budget is extremely tight

### Netlify

**Why we didn't choose it:**

- Next.js support historically lagged behind Vercel
- Build times were slower in our testing
- Some Next.js features required workarounds

**When to reconsider:**

- If Netlify's Next.js runtime improves significantly
- For projects not using Next.js
- If their form handling is needed

### Cloudflare Pages

**Why we didn't choose it:**

- Relatively new platform (less mature)
- Next.js support was experimental
- Fewer integrations available

**When to reconsider:**

- If using Cloudflare for other services
- When platform matures further
- For purely static sites

## Recommendation

For new projects using Next.js, continue using **Vercel**.

For simple static sites where cost is a concern, consider **GitHub Pages** or **Cloudflare Pages**.

Review this document monthly to ensure our platform choice remains optimal.
