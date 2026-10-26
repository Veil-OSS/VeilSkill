# Veil skill

An agent skill that lets AI agents and apps connect to [Veil](https://veil.rip), the identity and signing-key directory. Veil maps accounts people already use (Discord, GitHub, email, domain, Fediverse) to a card of signing keys, with every change recorded in a public, witnessed transparency log.

With this skill installed, an agent can:

- Look up who owns an account or key
- Verify who signed a message, even if the account was stolen
- Read cards, key history and transparency-log proofs
- Add Veil badges and widgets to a site
- Call any of the 59 documented Veil endpoints

## Install

```bash
npx skills add itzheropvp/VeilSkill
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
| `scripts/veil.py` | Command-line client with no dependencies. Covers every public read and message verification |
| `references/endpoints.md` | All 59 endpoints (method, path, access level, summary) plus detailed parameters for the core ones |
| `references/signed-requests.md` | How signed writes work (card creation, account linking), without ever handling private keys |

## The bundled client

Requires Python 3 only.

```bash
python scripts/veil.py lookup --github 109546049        # account -> card number
python scripts/veil.py card 1                            # full card and proof
python scripts/veil.py summary 1                         # small metadata only
python scripts/veil.py verify --block-file signed.txt    # check a signature block
python scripts/veil.py key-active <64-hex> --t 1767225600
python scripts/veil.py get /v1/identities/1/orgs         # any public GET path
python scripts/veil.py doc verify-message                # live contract for one endpoint
python scripts/veil.py --help
```

Add `--dry-run` to print a request without sending it. Output is JSON. Errors go to stderr with a non-zero exit code, and 429/503 responses are retried once after `Retry-After`.

## Good to know

- Public reads, card lookups and message verification need no API key.
- `valid` is the overall verification verdict. A signature can match after its key was revoked, so never rely on `signatureOk` alone.
- A 503 is never a successful verification.
- `POST /v1/verify` sends the message text to Veil. For private checks, use `https://veil.rip/verify`, which runs in the browser.
- Writes (creating or changing cards) need the owner's device key. The skill never asks for, generates or stores private keys.

## Staying current

Veil is still evolving. The live endpoint index is at `https://veil.rip/v1/integrations`, and each endpoint's current contract is at `https://veil.rip/v1/integrations/{id}`. If a call behaves differently from this skill, run `python scripts/veil.py doc <id>` and trust the live contract.

## Links

- Docs: https://veil.rip/docs
- Transparency log: https://log.veil.rip
