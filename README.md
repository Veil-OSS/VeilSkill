# Veil skill

A skill for connecting apps and agents to [Veil](https://veil.rip), the identity and signing-key directory. Veil maps accounts people already use (Discord, GitHub, email, domain, Fediverse) to a card of signing keys, with every change recorded in a public, witnessed transparency log.

With this skill installed, an agent can:

- Look up who owns an account or key
- Verify who signed a message, even if the account was stolen
- Read cards, key history and transparency-log proofs
- Add Veil badges and widgets to a site
- Read the current contracts for all 65 documented Veil endpoints

## Install

```bash
npx skills add Veil-OSS/VeilSkill
```

The CLI asks which agents to install it for. To install this skill from a repo that holds several, add `--skill veil`.

## Use

Once installed, just ask your agent in plain language. The skill activates when you mention Veil, veil.rip, a Veil card or signature block, or sender verification in a messaging app.

Examples:

- "Look up the Veil card for GitHub user 109546049."
- "Verify this signed message with Veil."
- "Add sender verification to my chat app using Veil."
- "Put a Veil badge in my README."

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | Instructions the agent reads: which endpoint to use for which job, recipes, and rules that prevent mistakes |
| `scripts/veil.py` | Command-line client with no dependencies. Public reads, message verification and bearer quota status |
| `references/endpoints.md` | All 65 endpoints (method, path, access level, summary) plus detailed parameters for the core ones |
| `references/api-keys.md` | Optional bearer keys, shared quotas, lifecycle and device-signed management |
| `references/responses-and-errors.md` | Response fields, nested objects, headers, error codes and retry rules |
| `tests/test_veil.py` | Loopback checks for credentials, retries, headers, conditional reads and file output |
| `references/signed-requests.md` | How signed writes work (card creation, account linking), without ever handling private keys |

## The bundled client

Requires Python 3 only.

```bash
python scripts/veil.py lookup --github 109546049        # account -> card number
python scripts/veil.py card 1                            # full card and proof
python scripts/veil.py summary 1                         # small metadata only
python scripts/veil.py verify --block-file signed.txt    # check a signature block
python scripts/veil.py key-active "$KEY_HEX" --t 1767225600
python scripts/veil.py get /v1/identities/1/orgs         # any public GET path
python scripts/veil.py doc verify-message                # live contract for one endpoint
python scripts/veil.py --api-key-env VEIL_API_KEY quota   # inspect shared quotas
python scripts/veil.py --include-headers doc lookup       # response fields and headers
python scripts/veil.py doc errors --lang it                # error guide in Italian
python scripts/veil.py --output badge.svg get /o/veil/badge.svg
python scripts/veil.py --help
```

Put global options before the command. `--dry-run` previews the request without sending it and redacts credentials. JSON responses are formatted for reading; `--output` saves exact response bytes. `--include-headers` writes HTTP status and headers to stderr. Errors exit non-zero. Transient read/verification failures get at most one retry, and waits above 30 seconds return the error rather than retrying early.

Run `python3 -m unittest discover -s tests -v` to check the client. HTTP fixtures stay on loopback.

## Good to know

- Public reads, card lookups and message verification need no API key. Optional server/local keys share an owner allowance, normally 600 requests/minute plus a 120/minute verification bucket.
- Create keys at [API keys](https://veil.rip/developers), available in the profile menu. Use `--api-key-env VEIL_API_KEY` to read a bearer secret from server configuration. Never put one in a frontend bundle.
- The live reference now has 65 endpoints and 10 guides, with response fields, types, nullability, nested objects, headers and selected JSON examples. [Responses and errors](https://veil.rip/docs/errors) explains 74 searchable codes and recovery actions.
- `valid` is the overall verification verdict. A signature can match after its key was revoked, so never rely on `signatureOk` alone.
- A 503 is never a successful verification.
- `POST /v1/verify` sends the message text to Veil. For private checks, use `https://veil.rip/verify`, which runs in the browser.
- Writes (creating or changing cards) need the owner's device key. The skill never asks for, generates or stores private keys.

## Staying current

Veil is still evolving. The detail JSON includes `responses`, `responseObjects`, `responseHeaders` and `errorDetails`, while retaining `response` and `errors`. The live endpoint index is at `https://veil.rip/v1/integrations`, and each endpoint's current contract is at `https://veil.rip/v1/integrations/{id}`. If a call behaves differently from this skill, run `python scripts/veil.py doc <id>` and trust the live contract.

## Links

- Docs: https://veil.rip/docs
- Transparency log: https://log.veil.rip
