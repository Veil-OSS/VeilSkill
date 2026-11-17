# Veil skill

A skill for connecting apps and agents to [Veil](https://veil.pub), the public directory of cryptographic identities. Veil maps accounts people already use (Discord, GitHub, email, domain, Fediverse) to a card of signing keys, with every change recorded in a public, witnessed transparency log.

With this skill installed, an agent can:

- Look up who owns an account or a key, by its stable ID or by the name people know
- Verify who signed a message, even if the account was stolen
- Verify who signed a file or a release, with a Veil key or with an SSH, OpenPGP or minisign key the card proves
- Read cards, key history and transparency-log proofs, and check them in your own code with log format 2
- Read a card's account alerts and signed statements
- Add Sign in with Veil (OpenID Connect) to an app, with the checks that make a login provable
- Add Veil badges and widgets to a site
- Read the current contracts for all 129 documented Veil endpoints

## Install

```bash
npx skills add Veil-OSS/VeilSkill
```

The CLI asks which agents to install it for. To install this skill from a repo that holds several, add `--skill veil`.

## Use

Once installed, ask your agent in plain language. The skill activates when you mention Veil, veil.pub, a Veil card or signature block, Sign in with Veil, or sender verification in a messaging app.

Examples:

- "Which Veil card holds this public key?"
- "Verify this signed message with Veil."
- "Add sender verification to my chat app using Veil."
- "Put a Veil badge in my README."
- "Check the proof of Veil card 1 in Python."
- "Does this release archive carry a signature from Veil card 1?"
- "Which Veil card belongs to this GitHub login?"
- "Add Sign in with Veil to my Express app."

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | Instructions the agent reads: which endpoint to use for which job, recipes, and rules that prevent mistakes |
| `scripts/veil.py` | Command-line client with no dependencies. Public reads, format 2 reads, message and file verification, and bearer quota status |
| `references/endpoints.md` | All 129 endpoints (method, path, access level, summary) plus detailed parameters for the core ones |
| `references/format-2.md` | Log format 2: what changed for verifiers, hashes, the index bundle, keys from elsewhere and the checks to run |
| `references/sign-in.md` | Sign in with Veil: the OpenID Connect provider, apps, scopes and claims, tokens, and the checks on the signed consent |
| `references/api-keys.md` | Optional bearer keys, shared quotas, lifecycle and device-signed management |
| `references/responses-and-errors.md` | Response fields, nested objects, headers, error codes, caching and retry rules |
| `references/signed-requests.md` | How signed writes work (labels, bodies, operations, card creation, account linking, keys from elsewhere, alerts and statements), without ever handling private keys |
| `tests/test_veil.py` | Loopback checks for credentials, retries, headers, conditional reads, file output, file hashing and request paths |

## The bundled client

Requires Python 3 only. The examples use card 1 (a person, alias `gab`) and card 2 (the Veil organisation, alias `veil`).

```bash
python scripts/veil.py lookup --key 73ad6159583a43f8ad230a215b758db680efcd3ce32ab8e83c622eeca883e68a   # key -> card number
python scripts/veil.py lookup --account github:Gabriele73   # a name or an ID, with the platform when you know it
python scripts/veil.py card 1                            # full card and proof
python scripts/veil.py org veil                          # organisation card, by number or alias
python scripts/veil.py summary 1                         # small metadata only
python scripts/veil.py verify --block-file signed.txt    # check a signature block
python scripts/veil.py verify --signature-file SHA256SUMS.veil --list-file SHA256SUMS --file veil-0.1.4-darwin-arm64.zip
python scripts/veil.py verify --signature-file notes.txt.sig --file notes.txt --card 1   # an SSH, OpenPGP or minisign signature
python scripts/veil.py keys-file 1 --format allowed_signers   # the card's SSH keys for git and ssh-keygen
python scripts/veil.py alerts 1                          # account alerts in force
python scripts/veil.py card-statements o veil            # an organisation's signed statements
python scripts/veil.py canary                            # Veil's warrant canary
python scripts/veil.py key-active "$KEY_HEX" --t 1793260000
python scripts/veil.py authority 1                       # format 2: versions that changed who can sign
python scripts/veil.py labels 1                          # format 2: the chain of labels
python scripts/veil.py members 2                         # format 2: a page of members with its proof
python scripts/veil.py set-path 1 keys --key "$KEY_HEX"  # format 2: path of one state item
python scripts/veil.py get /v1/identities/1/orgs         # any public GET path
python scripts/veil.py doc verify-message                # live contract for one endpoint
python scripts/veil.py --output openapi.json openapi     # the OpenAPI 3.1 description
python scripts/veil.py --api-key-env VEIL_API_KEY quota   # inspect shared quotas
python scripts/veil.py --include-headers doc lookup       # response fields and headers
python scripts/veil.py doc errors --lang it                # error guide in Italian
python scripts/veil.py --output badge.svg get /o/2/badge.svg
python scripts/veil.py --help
```

`statements N --from I --size S` reads the next page of a card's staff statements. Take both values from the card's `index.statementsNext`, or pass that path to `get`.

File verification hashes the file on your machine and sends the hash, its name and the signature. The file's bytes never leave it.

Put global options before the command. `--dry-run` previews the request without sending it and redacts credentials. JSON responses are formatted for reading, and `--output` saves the exact response bytes. `--include-headers` writes the HTTP status and headers to stderr. `--if-none-match` sends a stored `ETag`, and a `304` leaves the output file untouched. Errors exit non-zero. Transient read and verification failures get at most one retry, and waits above 30 seconds return the error rather than retrying early.

Run `python3 -m unittest discover -s tests -v` (or `python3 tests/test_veil.py`) to check the client. HTTP fixtures stay on loopback.

## Good to know

- Public reads, card lookups and verification need no API key, at 300 requests a minute per IP. Optional server or local keys share an owner allowance, normally 600 requests a minute plus a 120 a minute verification bucket.
- Create keys at [API keys](https://veil.pub/developers), available in the profile menu. Use `--api-key-env VEIL_API_KEY` to read a bearer secret from server configuration. Never put one in a frontend bundle.
- The live reference has 129 endpoints and 18 guides, with response fields, types, nullability, nested objects, headers and selected JSON examples. [Responses and errors](https://veil.pub/docs/errors) explains 139 searchable codes and recovery actions. The same contract is at `https://veil.pub/openapi.json` as OpenAPI 3.1.
- `/v1` paths, documented fields and error codes stay. A removal is announced on the [API changelog](https://veil.pub/docs/changelog) at least 90 days ahead.
- The directory moved from `veil.rip` to `veil.pub` on 6 November 2026. The old host answers with permanent redirects and its API still answers in place, so update stored addresses when you can.
- Since 28 October 2026 the directory uses log format 2. `GET /v1/log` says `"format": 2`. The log is read at `https://log.veil.pub`, and its origin is still named `log.veil.rip/staging-1` because that name is signed into every checkpoint.
- A lookup by name says so. A match with `"stale": true` rests on a name Veil could not confirm lately, and names can change hands. Store the platform's stable ID (`subject`) and the card number.
- Card JSON has a weak `ETag`. Revalidate with `If-None-Match` and a `304` saves the download, but the checks still run on the stored bytes.
- Pictures are PNG (APNG included), GIF or SVG, up to 2 MiB, named by hash in the signed version, with the bytes sent beside it.
- `valid` is the overall verification verdict. A signature can match after its key was revoked, so never rely on `signatureOk` alone.
- A 503 is never a successful verification.
- `POST /v1/verify` sends the message text to Veil. For private checks, use `https://veil.pub/verify`, which runs in the browser. File checks send only a hash.
- Sign in with Veil is standard OpenID Connect. The `veil` scope adds a consent signed by the person's own device key, which an app can check against the public log on its own.
- Writes (creating or changing cards) need the owner's device key. The skill never asks for, generates or stores private keys.

## Staying current

Veil keeps growing. The detail JSON includes `responses`, `responseObjects`, `responseHeaders` and `errorDetails`, and keeps `response` and `errors`. The live endpoint index is at `https://veil.pub/v1/integrations`, and each endpoint's current contract is at `https://veil.pub/v1/integrations/{id}`. If a call behaves differently from this skill, run `python scripts/veil.py doc <id>` and trust the live contract.

## Links

- Docs: https://veil.pub/docs
- API changelog: https://veil.pub/docs/changelog
- OpenAPI: https://veil.pub/openapi.json
- Transparency log: https://log.veil.pub
