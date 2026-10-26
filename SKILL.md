---
name: veil
description: Connect an app, bot or agent to Veil (veil.rip), the identity and signing-key directory. Use this skill whenever the user mentions Veil, veil.rip, a Veil card, a Veil signature block, or wants to look up who owns an account or key, check who signed a message (even if the account was stolen), verify a card or its transparency log, add a Veil badge or widget, or call any Veil API endpoint. Also use it when building messaging-app features such as sender verification, key lookup by Discord/GitHub/email/domain/Fediverse account, or signed-message checks, even if the user does not say "Veil" explicitly but is integrating with the veil.rip docs.
---

# Veil integration

Veil maps an account people already know (Discord, GitHub, email, domain, Fediverse) to a **card** that holds that person's signing keys, with every change recorded in a public, witnessed transparency log. An integration uses it to answer two questions: *which key belongs to this account?* and *did that key sign this message?*

Base URL: `https://veil.rip`. Log host: `https://log.veil.rip`. Docs: `https://veil.rip/docs`.
Public reads, card lookups and message verification need **no API key** and can run from a browser, bot or server.

## Fastest path: the bundled client

`scripts/veil.py` is a stdlib-only Python CLI (no installs) that covers every public read and message verification. Run it instead of hand-writing requests.

```bash
python scripts/veil.py lookup --github 109546049        # account -> card number
python scripts/veil.py card 1                            # full card + proof
python scripts/veil.py summary 1                         # small metadata only
python scripts/veil.py verify --block-file signed.txt    # check a signature block
python scripts/veil.py key-active <64-hex> --t 1767225600
python scripts/veil.py get /v1/identities/1/orgs         # any public GET path
python scripts/veil.py doc verify-message                # live contract for one endpoint
python scripts/veil.py --help
```

Add `--dry-run` to print the exact request without sending it. Output is JSON; errors go to stderr with a non-zero exit code, and 429/503 responses are retried once after `Retry-After` (capped at 30s).

## Which endpoint for which job

| Goal | Call |
|---|---|
| Find the card for an account/key | `GET /v1/lookup?<one param>` (`discord`, `github`, `email`, `domain`, `fediverse`, `key`, `fingerprint`) |
| Read the full signed card and proof | `GET /u/{card}.json` (person) or `GET /o/{card}.json` (organisation) |
| Show a name/logo/badges in a UI | `GET /v1/identities/{n}/summary` (labels only, no proof) |
| Check a signed message | `POST /v1/verify` with `{"block": "..."}` (optionally `at`) |
| Is this key valid at time T? | `GET /v1/keys/{key}/active-at?t=<unix seconds>` |
| Who holds this key? | `GET /v1/keys/{key}` |
| Poll for changes | `GET /v1/identities/{n}/versions?latest=true`, `GET /v1/identities/{n}/events?after=<id>` |
| Verify independently | card `proof`, `/v1/identities/{n}/versions/{k}/proof`, `GET /v1/log` |
| Show a card on a site | badge `/{kind}/{card}/badge.svg`, widget `/{kind}/{card}/embed`, or `/embed.js` |

The complete list of all 59 endpoints (method, path, access level, summary) and detailed parameters for the core ones are in `references/endpoints.md`. Read it when you need an endpoint not shown above.

## Recipes

**Verify the sender of a message in a messaging app.** Take the signature block the sender pasted, `POST /v1/verify {"block": block}`, and trust `valid`, not `signatureOk`. If you know when the message was published from a source you trust (your server's receive time), pass it as `at` (Unix seconds); a date the signer wrote proves nothing. For a bot or any account check, use raw mode with `key`, `message`, `signature` plus `platform` and `subject` so Veil also confirms that identity held the sending account at that time. Use the platform's stable account ID for bots, never the display name.

**Resolve "who is this account?"** `lookup` with the exact platform ID (Discord: 17-20 digit user ID; GitHub: numeric ID, not the login), then `summary` for display data. Supply exactly one lookup parameter; a 404 means no card, not an error in your code. Display names are not unique, so never identify someone by name alone.

**Remember a person or organisation.** Store the permanent card number `n`. Aliases can change or be reassigned to another card.

**Keep a cache fresh.** Fetch `versions?latest=true&limit=1` rather than the whole history on every poll, and follow `next`/`before` cursors until `null` when paging (pages can be shorter than `limit`).

**Independent verification (no trust in the server's verdict).** Fetch the full card, recompute commitments, verify signatures, follow `prev` through the version chain, check the inclusion proof against a signed checkpoint, and pin the expected log and witness policy (`GET /v1/log`, log `policy`/`witnesses`). `/v1/log` and `/v1/verify` verdicts are the server's own checks.

## Rules that prevent real mistakes

- `valid` is the overall verdict. A signature can still match (`signatureOk: true`) after its key was revoked, while `valid` is false for the current time. Read `keyState` and `reason`.
- A `503` (including `log_unavailable`) is **never** a successful verification. Retry later; do not fall back to "assume valid".
- The `/v1/identities/{n}/summary` endpoint carries no proof. Use the full card for any authorisation decision.
- An organisation invitation is not membership. Only accepted memberships count; check roles in the signed records.
- `POST /v1/verify` sends the message text to Veil. If privacy matters, point users to `https://veil.rip/verify` (checks in the browser; data after `#` never leaves it) or verify locally.
- Rate limits: 300 reads/min/IP (verification counts as a read), 30 writes/min/IP, 10 signed writes/min/key. On 429 wait `Retry-After` seconds.
- Errors are `{"error":{"code","message"}}`: 400 invalid input, 401 bad/missing signature, 403 key not allowed, 404 none found, 409 state changed (re-read, then retry), 410 card erased, 422 failed a domain rule or account proof, 503 service/log unavailable.

## Writes (cards, organisations, account proofs)

Anything that changes a card is a **signed request** made by the owner's device key. These calls are for local or server clients only (CORS does not open them to other websites). Never ask for, generate on the owner's behalf, store, or transmit a private key, and never send one to Veil. If the user wants a write, prepare the unsigned record/request and explain the signing step; have them sign with their own device. The signing format (headers, canonical bytes, record fields) is in `references/signed-requests.md`.

## Staying current

Veil is still evolving. The machine-readable index at `GET /v1/integrations` carries a `revision` field and every endpoint's contract is at `GET /v1/integrations/{id}` (same ids as the docs slugs, e.g. `verify-message`). If a call behaves differently from this skill, run `python scripts/veil.py doc <id>` and trust the live contract.
