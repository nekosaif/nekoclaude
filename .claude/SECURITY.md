# SECURITY.md

## Threat model

This is a **single-user, local-network tool**. It trusts the operator fully and runs with the operator's own filesystem permissions. The trust boundary is the network interface the server binds to:

- `127.0.0.1` (default): trust is local-only; same as running any other dev server.
- `100.100.10.10` (current — Tailscale): trust extends to every device on the operator's tailnet. **There is no authentication on the HTTP surface.** Anyone who can reach the bound interface can read and modify any `.claude/` directory the operator added as a target, including writing arbitrary catalog skills that then get installed into those targets.

If you don't trust everything on your tailnet (or if you change the bind to a wider interface), put this behind an authenticating reverse proxy or basic auth.

## Reporting a vulnerability

This is a personal project with no external contact channel. If you find a real issue, open an issue on the repo where you got this code. There is no SLA.

## Secrets and credentials

The tool itself stores no credentials.

It does read and write:

- `~/.claude/settings.json` and project `.claude/settings.local.json` — these may include API keys or tokens if the operator put them there. The tool surfaces those values in the **Installed** panel and in JSON-body editor textareas. **Do not screenshare while editing settings if your settings contain secrets.**
- `~/.claude/plugins/installed_plugins.json` — read-only; contains no secrets but does include marketplace identifiers.

The tool invokes `git clone` for catalog updates. Auth for git is delegated entirely to the operator's `~/.ssh/`, `~/.gitconfig`, and git credential helpers. Cloning a private repo requires the operator's machine to be configured for it.

## Dependencies

Python dependencies live in `pyproject.toml`; pinned versions are resolved by `uv sync` into `uv.lock`.

- No automatic CVE scanning is configured. Run `uv tool run pip-audit` manually before pulling new deps if you care.
- Frontend dependencies (HTMX, Alpine, Tailwind) are loaded from public CDNs (unpkg, jsdelivr, cdn.tailwindcss.com). A compromised CDN would allow arbitrary JS execution in the UI. Mitigation: SRI hashes are NOT pinned currently. For a production deployment, vendor those scripts locally and add `integrity=` attributes.

## Known weaknesses (accepted as-is)

- **No auth on the HTTP server.** See threat model above.
- **No CSRF protection.** Same-origin policy is the only barrier. The HTMX forms include no CSRF token; an attacker who can get the operator to load a malicious HTML page on the tailnet could trigger state-changing requests. Acceptable risk for the personal-tool use case.
- **Arbitrary git URLs are clone-able.** The "Add skill from git" form accepts any URL. Cloning a malicious repo into `catalog/skills/<slug>/` doesn't execute anything by itself, but a follow-up install + apply puts those files in `~/.claude/skills/<slug>/` where they could be loaded by Claude Code. Operators should treat the catalog like they would `~/.local/bin` — only add what they trust.
- **The doc-scaffold prompt file is dropped into the project's `.claude/` directory** and the user is told to `claude < .claude/.nekoclaude-handoff-prompt.md`. Anyone who can write to that project directory can replace the prompt before the user runs it. Tolerable since the project is presumably the operator's own.
- **No sandboxing on `git clone`.** A malicious post-checkout hook in a cloned skill would run inside the operator's session if their git config has such hooks enabled. Stock git does not run post-checkout hooks on `git clone --depth 1`; if the operator's `~/.gitconfig` enables them, that's their config.
