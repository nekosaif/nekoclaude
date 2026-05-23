Write `SECURITY.md` at the repo root.

Cover:

1. **Threat model in one paragraph** — what this codebase trusts, what it doesn't, and where the trust boundary is.
2. **Reporting a vulnerability** — preferred contact method, what info to include, expected response time. If unknown, leave a `<TODO: contact>` placeholder rather than inventing details.
3. **Secrets and credentials** — how they're stored, how they're rotated, what would happen if they leaked. Be specific: list the actual env vars / secret-manager paths used.
4. **Dependencies** — how upstream CVEs are tracked. Name the tool (dependabot, renovate, etc.) or be explicit that there isn't one yet.
5. **Known weaknesses** — what's accepted-as-is, with reasoning. Don't lie about a clean bill of health.

Be honest. A short, accurate SECURITY.md beats a long, aspirational one.
