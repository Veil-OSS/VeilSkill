# Veil skill

A skill for connecting apps and agents to [Veil](https://veil.rip), the public directory of cryptographic identities. Veil maps accounts people already use (Discord, GitHub, email, domain, Fediverse) to a card of signing keys, with every change recorded in a public, witnessed transparency log.

With this skill installed, an agent can:

- Look up who owns an account or key
- Verify who signed a message, even if the account was stolen
- Read cards, key history and transparency-log proofs, and check them in your own code with log format 2
- Add Veil badges and widgets to a site
- Read the current contracts for all 71 documented Veil endpoints

## Install

```bash
npx skills add Veil-OSS/VeilSkill
```

The CLI asks which agents to install it for. To install this skill from a repo that holds several, add `--skill veil`.

## Use

Once installed, ask your agent in plain language. The skill activates when you mention Veil, veil.rip, a Veil card or signature block, or sender verification in a messaging app.

Examples:

- "Which Veil card holds this public key?"
- "Verify this signed message with Veil."
- "Add sender verification to my chat app using Veil."
- "Put a Veil badge in my README."
- "Check the proof of Veil card 1 in Python."

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | Instructions the agent reads: which endpoint to use for which job, recipes, and rules that prevent mistakes |
| `scripts/veil.py` | Command-line client with no dependencies. Public reads, format 2 reads, message verification and bearer quota status |
| `references/endpoints.md` | All 71 endpoints (method, path, access level, summary) plus detailed parameters for the core ones |
| `references/format-2.md` | Log format 2: what changed for verifiers, hashes, the index bundle and the checks to run |
| `references/api-keys.md` | Optional bearer keys, shared quotas, lifecycle and device-signed management |
| `references/responses-and-errors.md` | Response fields, nested objects, headers, error codes, caching and retry rules |
| `references/signed-requests.md` | How signed writes work (labels, bodies, operations, card creation, account linking), without ever handling private keys |
| `tests/test_veil.py` | Loopback checks for credentials, retries, headers, conditional reads, file output and request paths |

## The bundled client

Requires Python 3 only. The examples use the cards that exist today: card 1 (a person) and card 2 (the Veil organisation).

```bash
python scripts/veil.py lookup --key 73ad6159583a43f8ad230a215b758db680efcd3ce32ab8e83c622eeca883e68a   # key -> card number
python scripts/veil.py card 1                            # full card and proof
python scripts/veil.py org 2                             # organisation card
python scripts/veil.py summary 1                         # small metadata only
python scripts/veil.py verify --block-file signed.txt    # check a signature block
python scripts/veil.py key-active "$KEY_HEX" --t 1793260000
python scripts/veil.py authority 1                       # format 2: versions that changed who can sign
python scripts/veil.py labels 1                          # format 2: the chain of labels
python scripts/veil.py members 2                         # format 2: a page of members with its proof
python scripts/veil.py set-path 1 keys --key "$KEY_HEX"  # format 2: path of one state item
python scripts/veil.py get /v1/identities/1/orgs         # any public GET path
python scripts/veil.py doc verify-message                # live contract for one endpoint
python scripts/veil.py --api-key-env VEIL_API_KEY quota   # inspect shared quotas
python scripts/veil.py --include-headers doc lookup       # response fields and headers
python scripts/veil.py doc errors --lang it                # error guide in Italian
python scripts/veil.py --output badge.svg get /o/2/badge.svg
python scripts/veil.py --help
```

`statements N --from I --size S` reads the next page of a card's staff statements. Take both values from the card's `index.statementsNext`, or pass that path to `get`.

Put global options before the command. `--dry-run` previews the request without sending it and redacts credentials. JSON responses are formatted for reading, and `--output` saves the exact response bytes. `--include-headers` writes the HTTP status and headers to stderr. `--if-none-match` sends a stored `ETag`, and a `304` leaves the output file untouched. Errors exit non-zero. Transient read and verification failures get at most one retry, and waits above 30 seconds return the error rather than retrying early.

Run `python3 -m unittest discover -s tests -v` (or `python3 tests/test_veil.py`) to check the client. HTTP fixtures stay on loopback.

## Good to know

- Public reads, card lookups and message verification need no API key. Optional server or local keys share an owner allowance, normally 600 requests a minute plus a 120 a minute verification bucket.
- Create keys at [API keys](https://veil.rip/developers), available in the profile menu. Use `--api-key-env VEIL_API_KEY` to read a bearer secret from server configuration. Never put one in a frontend bundle.
- The live reference has 71 endpoints and 10 guides, with response fields, types, nullability, nested objects, headers and selected JSON examples. [Responses and errors](https://veil.rip/docs/errors) explains 77 searchable codes and recovery actions.
- Since 28 October 2026 the directory uses log format 2 on `log.veil.rip/staging-1`. `GET /v1/log` says `"format": 2`. Cards were recreated there, so card 1 and card 2 have new IDs and fingerprints. Request signing, lookups, message verification and signature blocks work as before.
- Card JSON has a weak `ETag`. Revalidate with `If-None-Match` and a `304` saves the download, but the checks still run on the stored bytes.
- Pictures are PNG (APNG included), GIF or SVG, up to 2 MiB, named by hash in the signed version, with the bytes sent beside it.
- `valid` is the overall verification verdict. A signature can match after its key was revoked, so never rely on `signatureOk` alone.
- A 503 is never a successful verification.
- `POST /v1/verify` sends the message text to Veil. For private checks, use `https://veil.rip/verify`, which runs in the browser.
- Writes (creating or changing cards) need the owner's device key. The skill never asks for, generates or stores private keys.

## Staying current

Veil is still evolving. The detail JSON includes `responses`, `responseObjects`, `responseHeaders` and `errorDetails`, and keeps `response` and `errors`. The live endpoint index is at `https://veil.rip/v1/integrations`, and each endpoint's current contract is at `https://veil.rip/v1/integrations/{id}`. If a call behaves differently from this skill, run `python scripts/veil.py doc <id>` and trust the live contract.

## Links

- Docs: https://veil.rip/docs
- Transparency log: https://log.veil.rip
