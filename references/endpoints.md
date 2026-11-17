# Veil endpoint reference

Snapshot of [the live catalogue](https://veil.pub/v1/integrations), revision `eeb4170b004a4565`, reviewed 17 November 2026. It contains **129 endpoints and 18 guides**. Each endpoint ID is its docs slug and the key for `GET /v1/integrations/{id}`. The same contract is published as OpenAPI 3.1 at `GET /openapi.json`.

The detail JSON contains response status, content type, fields, nested objects, headers, selected examples and error recovery guidance. Read [responses and errors](responses-and-errors.md) before relying on an HTTP status or parsing a body. Fetch a current detail with `python scripts/veil.py doc <id>`.

`directory` uses `https://veil.pub`. `log` uses `https://log.veil.pub`. The directory moved from `veil.rip` on 6 November 2026. The old host answers with permanent redirects and its API still answers in place, so an integration written for `veil.rip` keeps working while you move it. The log's origin is still the string `log.veil.rip/staging-1`: it is signed into every checkpoint and never changes.

Access modes are `public` (anonymous, with optional bearer access only on eligible directory calls), `api-key` (bearer required), `signed` (device signature), `private-code` (secret URL token or OAuth credential), `public-write` (temporary unauthenticated operation) and `provider-callback` (OAuth return page). Browser modes distinguish anonymous `fetch`, `frame`, `navigation` and `local-or-server`.

The directory runs log format 2 since 28 October 2026. Six reads exist only on a format 2 log and are marked **Format 2** below. On a format 1 log they answer `400 wrong_format`. [Log format 2](format-2.md) explains the shapes they return and how to verify them.

Compatibility, from the [`changelog`](https://veil.pub/docs/changelog) guide: `/v1` paths, documented fields and error codes stay. New endpoints, fields and codes can appear at any time, so ignore fields you do not know and branch on `error.code`. A removal or a change of meaning is announced on that page at least 90 days ahead, and the affected responses carry `Deprecation` and `Sunset` headers. The catalogue's `revision` changes whenever the reference does.

## Guides

- [`start`](https://veil.pub/docs) Integrate Veil
- [`browser-apps`](https://veil.pub/docs/browser-apps) Call Veil from a website
- [`message-verification`](https://veil.pub/docs/message-verification) Verify a signed message
- [`external-keys`](https://veil.pub/docs/external-keys) Bring your public keys
- [`verify-files`](https://veil.pub/docs/verify-files) Verify signed files and releases
- [`cli`](https://veil.pub/docs/cli) Install the command line tool
- [`sharing`](https://veil.pub/docs/sharing) Show a card on your site
- [`discord-app`](https://veil.pub/docs/discord-app) Add the Veil app to Discord
- [`chat-api`](https://veil.pub/docs/chat-api) The Veil chat API
- [`chat`](https://veil.pub/docs/chat) Veil chat: your card is your account
- [`proofs`](https://veil.pub/docs/proofs) Verify a card independently
- [`signed-requests`](https://veil.pub/docs/signed-requests) Make a signed request
- [`limits`](https://veil.pub/docs/limits) Limits and errors
- [`api-reference`](https://veil.pub/docs/api-reference) API reference
- [`changelog`](https://veil.pub/docs/changelog) API changes and compatibility
- [`api-keys`](https://veil.pub/docs/api-keys) Use a developer API key
- [`sign-in`](https://veil.pub/docs/sign-in) Sign in with Veil
- [`errors`](https://veil.pub/docs/errors) Responses and errors

## Find people and cards

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`lookup`](https://veil.pub/docs/lookup) | `GET /v1/lookup` | directory | `public` / `fetch` | Find the card that holds one exact account, key or fingerprint, or read anything a person types (a username, a login, a profile address) with account. |
| [`account-address`](https://veil.pub/docs/account-address) | `GET /{platform}/{account}` | directory | `public` / `local-or-server` | An address that opens the card holding an account: veil.pub/github/<login>, veil.pub/discord/<username>. |
| [`person-card`](https://veil.pub/docs/person-card) | `GET /u/{card}.json`<br>`GET /u/{card}`<br>`GET /v1/identities/{n}` | directory | `public` / `fetch` | Read the full public card, signed record, proof and recent history. |
| [`organisation-card`](https://veil.pub/docs/organisation-card) | `GET /o/{card}.json`<br>`GET /o/{card}`<br>`GET /v1/organizations/{n}` | directory | `public` / `fetch` | Read an organisation, its signed membership record, public links and proof. |
| [`summary`](https://veil.pub/docs/summary) | `GET /v1/identities/{n}/summary` | directory | `public` / `fetch` | Get current metadata without downloading signed records, proofs or history. |
| [`card-alerts`](https://veil.pub/docs/card-alerts) | `GET /v1/identities/{n}/alerts` | directory | `public` / `fetch` | The alerts in force on the card's accounts, one per account, and every alert in the log, each with what a client checks it with. |
| [`card-statements`](https://veil.pub/docs/card-statements) | `GET /{kind}/{card}/statements.json`<br>`GET /{kind}/{card}/statements` | directory | `public` / `fetch` | A card's signed statements, newest first, each with what a client checks it with. The same address without .json is the page that checks them. |
| [`statement`](https://veil.pub/docs/statement) | `GET /v1/statements/{id}`<br>`GET /statements/{id}` | directory | `public` / `fetch` | One signed statement by its id, with its card and, for a retraction, the statement it retracts. /statements/{id} is its page, with a preview and an Article in JSON-LD. add .json for this JSON. |
| [`aliases`](https://veil.pub/docs/aliases) | `GET /v1/aliases/{kind}/{alias}` | directory | `public` / `fetch` | Check availability and find the permanent card behind a claimed alias. |
| [`platforms`](https://veil.pub/docs/platforms) | `GET /v1/platforms` | directory | `public` / `fetch` | Find the supported platforms, proof methods and their current availability. |

## Keys and signatures

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`key-info`](https://veil.pub/docs/key-info) | `GET /v1/keys/{key}` | directory | `public` / `fetch` | Look up a public key, the card holding it and its validity period. |
| [`key-at-time`](https://veil.pub/docs/key-at-time) | `GET /v1/keys/{key}/active-at` | directory | `public` / `fetch` | Ask whether a key was active at a particular time. |
| [`verify-message`](https://veil.pub/docs/verify-message) | `POST /v1/verify` | directory | `public` / `fetch` | Check a signature block or an explicit key, message and signature. This POST only reads. |
| [`verify-file`](https://veil.pub/docs/verify-file) | `POST /v1/verify` | directory | `public` / `fetch` | Check the signature of a file from its hash, or of a signed checksum list, against a card's keys. This POST only reads. |
| [`grant-key`](https://veil.pub/docs/grant-key) | `GET /v1/grant-key` | directory | `public` / `fetch` | Read the public key used to sign account-linking grants. |
| [`external-keys-file`](https://veil.pub/docs/external-keys-file) | `GET /u/{card}/keys.txt`<br>`GET /u/{card}.keys` | directory | `public` / `fetch` | Feed a person's SSH, minisign and OpenPGP public keys to git, ssh-keygen, a server, minisign or gpg: all of them, or one key by its fingerprint. |

## Versions and changes

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`versions`](https://veil.pub/docs/versions) | `GET /v1/identities/{n}/versions` | directory | `public` / `fetch` | Page through canonical records, signatures and openings. |
| [`history`](https://veil.pub/docs/history) | `GET /v1/identities/{n}/history` | directory | `public` / `fetch` | Read older version events and the account transfers around them. |
| [`version-proof`](https://veil.pub/docs/version-proof) | `GET /v1/identities/{n}/versions/{k}/proof` | directory | `public` / `fetch` | Get the inclusion proof for a particular version under the current checkpoint. |
| [`events`](https://veil.pub/docs/events) | `GET /v1/identities/{n}/events` | directory | `public` / `fetch` | Read takeover and publication-reconciliation events for a card. |
| [`takeovers`](https://veil.pub/docs/takeovers) | `GET /v1/takeovers` | directory | `public` / `fetch` | Read account transfer requests involving a card on either side. |
| [`authority`](https://veil.pub/docs/authority) | `GET /v1/identities/{n}/authority` | directory | `public` / `fetch` | Page through the versions that changed who can sign the card. **Format 2.** |
| [`statements`](https://veil.pub/docs/statements) | `GET /v1/identities/{n}/statements` | directory | `public` / `fetch` | Page through a card's counted staff statements after the first page in index.statements. **Format 2.** |
| [`labels`](https://veil.pub/docs/labels) | `GET /v1/identities/{n}/labels` | directory | `public` / `fetch` | Read the chain of labels alone, up to 1000 a page. **Format 2.** |
| [`version-v2`](https://veil.pub/docs/version-v2) | `GET /v1/identities/{n}/versions/{v}` | directory | `public` / `fetch` | Read one version whole: label, body, signature and log position. **Format 2.** |
| [`set-path`](https://veil.pub/docs/set-path) | `GET /v1/identities/{n}/sets/{set}/path` | directory | `public` / `fetch` | Get the sparse Merkle path of one item, or of its empty place, to update a set root. **Format 2.** |

## Organisations and public status

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`memberships`](https://veil.pub/docs/memberships) | `GET /v1/identities/{n}/orgs` | directory | `public` / `fetch` | Read a person's organisation memberships or an organisation's members. |
| [`staff-roles`](https://veil.pub/docs/staff-roles) | `GET /v1/staff` | directory | `public` / `fetch` | Identify Veil's official organisation and the powers of each staff role. |
| [`moderation`](https://veil.pub/docs/moderation) | `GET /v1/identities/{n}/moderation` | directory | `public` / `fetch` | Read the public status and moderation actions affecting a card. |
| [`moderation-entries`](https://veil.pub/docs/moderation-entries) | `GET /v1/moderation/entries` | directory | `public` / `fetch` | Page through public moderation, badge and badge-removal log entries. |
| [`badge-catalogue`](https://veil.pub/docs/badge-catalogue) | `GET /v1/badges/catalogue` | directory | `public` / `fetch` | Read badge IDs, labels and assignment rules. |
| [`card-badges`](https://veil.pub/docs/card-badges) | `GET /v1/identities/{n}/badges` | directory | `public` / `fetch` | Read a card's badges and removed badge history. |
| [`members`](https://veil.pub/docs/members) | `GET /v1/organizations/{n}/members` | directory | `public` / `fetch` | Read the members whose position starts with a prefix, with the proof to the members root. **Format 2.** |
| [`canary`](https://veil.pub/docs/canary) | `GET /v1/canary` | directory | `public` / `fetch` | Get the latest signed statement that no authority has asked Veil in secret for user data, with every earlier one. |
| [`canary-page`](https://veil.pub/docs/canary-page) | `GET /canary` | directory | `public` / `navigation` | Check the warrant canary's signature in the reader's browser. |
| [`about-page`](https://veil.pub/docs/about-page) | `GET /about` | directory | `public` / `local-or-server` | Who operates Veil, how to reach them, and what is still open. |

## Share and embed

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`oembed`](https://veil.pub/docs/oembed) | `GET /oembed` | directory | `public` / `fetch` | Get an embeddable card or link preview for a supported Veil URL. |
| [`badge-image`](https://veil.pub/docs/badge-image) | `GET /{kind}/{card}/badge.svg` | directory | `public` / `fetch` | Show a linked status badge in a README, profile or forum signature. |
| [`card-image`](https://veil.pub/docs/card-image) | `GET /{kind}/{card}/card.png` | directory | `public` / `fetch` | Read a 1200 by 630 PNG for a card's social preview. |
| [`contact-file`](https://veil.pub/docs/contact-file) | `GET /u/{card}.vcf` | directory | `public` / `fetch` | Download a person's card as a vCard for a phone or a mail client: the name, the card's address, the verified accounts and the 12 words. |
| [`statements-feed`](https://veil.pub/docs/statements-feed) | `GET /{kind}/{card}/statements.atom` | directory | `public` / `fetch` | A card's latest 50 statements as an Atom feed, for a feed reader, a Discord channel or a page. |
| [`logo`](https://veil.pub/docs/logo) | `GET /{kind}/{n}/logo.{format}` | directory | `public` / `fetch` | Read the image currently published on a person's or organisation's card. |
| [`widget`](https://veil.pub/docs/widget) | `GET /{kind}/{card}/embed` | directory | `public` / `frame` | Show a read-only card that verifies itself in the visitor's browser. |
| [`discord-image`](https://veil.pub/docs/discord-image) | `GET /u/{card}/discord.png`<br>`GET /u/{card}/discord.svg` | directory | `public` / `local-or-server` | Read a person's card drawn as a Discord profile, as a PNG or an SVG, for a README, a website or a chat. |
| [`discord-widget`](https://veil.pub/docs/discord-widget) | `GET /u/{card}/embed` | directory | `public` / `frame` | Show a person's card as a Discord profile that verifies itself and its keys in the visitor's browser. |
| [`embed-loader`](https://veil.pub/docs/embed-loader) | `GET /embed.js` | directory | `public` / `fetch` | Turn data-veil-card and data-veil-org elements into card frames. |
| [`robots`](https://veil.pub/docs/robots) | `GET /robots.txt` | directory | `public` / `local-or-server` | What search engines may crawl, and where the sitemap is. |
| [`favicon`](https://veil.pub/docs/favicon) | `GET /favicon.ico` | directory | `public` / `local-or-server` | The icon at the address crawlers try, as an ICO file. |
| [`sitemap`](https://veil.pub/docs/sitemap) | `GET /sitemap.xml`<br>`GET /sitemaps/pages.xml`<br>`GET /sitemaps/{file}` | directory | `public` / `local-or-server` | The public pages and cards a search engine may list, each card at its canonical address. |
| [`learn-index`](https://veil.pub/docs/learn-index) | `GET /learn` | directory | `public` / `navigation` | The index of the explainer pages: Veil compared with Keybase, Keyoxide and PGP keyservers, public key directories, checking a Discord account, signing releases, organisations and communities. |
| [`learn-page`](https://veil.pub/docs/learn-page) | `GET /learn/{slug}` | directory | `public` / `navigation` | One explainer page, written in English and in Italian, with its questions and answers. |
| [`preview-image`](https://veil.pub/docs/preview-image) | `GET /preview.png` | directory | `public` / `fetch` | Read the general directory preview image. |
| [`verify-page`](https://veil.pub/docs/verify-page) | `GET /verify` | directory | `public` / `navigation` | Open a message check that runs in the reader's browser. |
| [`verify-link`](https://veil.pub/docs/verify-link) | `GET /v/{n}/{signature}` | directory | `public` / `navigation` | Share a signed message with a server-generated social preview. |
| [`snippet-builder`](https://veil.pub/docs/snippet-builder) | `GET /embed` | directory | `public` / `frame` | Copy a card link, badge or widget with a live preview. |

## Transparency log

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`log-state`](https://veil.pub/docs/log-state) | `GET /v1/log` | directory | `public` / `fetch` | Identify the active log and read the checkpoint and witness state seen by the server. |
| [`log-about`](https://veil.pub/docs/log-about) | `GET /{log}/` | log | `public` / `navigation` | Read the log origin, verification key, daily request allowance and contact. |
| [`log-checkpoint`](https://veil.pub/docs/log-checkpoint) | `GET /{log}/checkpoint` | log | `public` / `fetch` | Read the log's signed size and Merkle root. |
| [`log-policy`](https://veil.pub/docs/log-policy) | `GET /{log}/policy` | log | `public` / `fetch` | Read the log key, witness keys and quorum rule. |
| [`log-witnesses`](https://veil.pub/docs/log-witnesses) | `GET /{log}/witnesses` | log | `public` / `fetch` | Read each configured witness's latest stored cosignature. |
| [`log-hash-tiles`](https://veil.pub/docs/log-hash-tiles) | `GET /{log}/tile/{level}/{index}`<br>`GET /{log}/tile/{level}/{index}.p/{width}` | log | `public` / `fetch` | Read C2SP hash tiles for inclusion and consistency proofs. |
| [`log-entry-tiles`](https://veil.pub/docs/log-entry-tiles) | `GET /{log}/tile/entries/{index}`<br>`GET /{log}/tile/entries/{index}.p/{width}` | log | `public` / `fetch` | Read C2SP bundles of public log entries. |

## Developer API keys

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`developer-account`](https://veil.pub/docs/developer-account) | `GET /v1/developer/accounts/{n}` | directory | `signed` / `local-or-server` | Read shared limits, quota balances, usage, keys and private activity. |
| [`developer-keys`](https://veil.pub/docs/developer-keys) | `GET /v1/developer/accounts/{n}/keys` | directory | `signed` / `local-or-server` | List key metadata without revealing secrets. |
| [`create-api-key`](https://veil.pub/docs/create-api-key) | `POST /v1/developer/accounts/{n}/keys` | directory | `signed` / `local-or-server` | A person or organisation owner signs the request to issue a secret bearer key. |
| [`revoke-api-key`](https://veil.pub/docs/revoke-api-key) | `DELETE /v1/developer/accounts/{n}/keys/{id}` | directory | `signed` / `local-or-server` | Permanently stop a key owned by this card. |
| [`api-key-audit`](https://veil.pub/docs/api-key-audit) | `GET /v1/developer/accounts/{n}/audit` | directory | `signed` / `local-or-server` | Inspect management receipts and the original device signatures. |
| [`rate-limit`](https://veil.pub/docs/rate-limit) | `GET /v1/rate-limit` | directory | `api-key` / `local-or-server` | Read your current owner and key quotas without spending the primary allowance. |
| [`oidc-clients`](https://veil.pub/docs/oidc-clients) | `GET /v1/developer/accounts/{n}/oidc-clients` | directory | `signed` / `local-or-server` | The apps a card registered for Sign in with Veil, without their secrets. |
| [`oidc-client-create`](https://veil.pub/docs/oidc-client-create) | `POST /v1/developer/accounts/{n}/oidc-clients` | directory | `signed` / `local-or-server` | A person or an organisation owner signs the registration. A confidential app with client_secret_basic gets its secret once. |
| [`oidc-client-update`](https://veil.pub/docs/oidc-client-update) | `PATCH /v1/developer/accounts/{n}/oidc-clients/{id}` | directory | `signed` / `local-or-server` | Name, site, redirect URIs, logout URIs, ID token algorithm and logo. The type and authentication stay. |
| [`oidc-client-delete`](https://veil.pub/docs/oidc-client-delete) | `DELETE /v1/developer/accounts/{n}/oidc-clients/{id}` | directory | `signed` / `local-or-server` | The app stops at once, and every token it holds ends. |
| [`oidc-client-secret`](https://veil.pub/docs/oidc-client-secret) | `POST /v1/developer/accounts/{n}/oidc-clients/{id}/secret` | directory | `signed` / `local-or-server` | A new client secret, shown once. the old one stops at once. |

## Sign in with Veil

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`oidc-discovery`](https://veil.pub/docs/oidc-discovery) | `GET /.well-known/openid-configuration` | directory | `public` / `fetch` | The discovery document of Sign in with Veil: issuer https://veil.pub, the endpoints, scopes, algorithms and methods. |
| [`oidc-jwks`](https://veil.pub/docs/oidc-jwks) | `GET /oidc/jwks` | directory | `public` / `fetch` | The public keys that sign ID tokens: one Ed25519 (EdDSA) and one P-256 (ES256), plus the previous pair for 30 days after a rotation. |
| [`oidc-authorize`](https://veil.pub/docs/oidc-authorize) | `GET /oidc/authorize` | directory | `public` / `local-or-server` | The authorization endpoint. It checks the app and its redirect URI, keeps the request 30 minutes and shows the consent page, where the person's device key signs. |
| [`oidc-request`](https://veil.pub/docs/oidc-request) | `GET /oidc/requests/{id}` | directory | `private-code` / `local-or-server` | The consent page's data: the app, whether a card vouches for it, the scopes, and the fields the consent text signs. |
| [`oidc-request-grant`](https://veil.pub/docs/oidc-request-grant) | `GET /oidc/requests/{id}/grant` | directory | `signed` / `local-or-server` | Signed by this browser's device key: whether its card already approved the app for these scopes, so the page signs without a click. |
| [`oidc-consent`](https://veil.pub/docs/oidc-consent) | `POST /oidc/requests/{id}/consent` | directory | `private-code` / `local-or-server` | The consent text signed by an active device key of a person's card. The server checks it against the card and its version in the verified log, keeps the login and gives the code. |
| [`oidc-deny`](https://veil.pub/docs/oidc-deny) | `POST /oidc/requests/{id}/deny` | directory | `private-code` / `local-or-server` | Uses the request and sends the app error=access_denied, or login_required and consent_required for prompt=none. |
| [`oidc-token`](https://veil.pub/docs/oidc-token) | `POST /oidc/token` | directory | `private-code` / `local-or-server` | The token endpoint: the code with its PKCE verifier, or a refresh token, for an access token, an ID token and a new refresh token. |
| [`oidc-userinfo`](https://veil.pub/docs/oidc-userinfo) | `GET /oidc/userinfo` | directory | `private-code` / `local-or-server` | The same claims as the ID token, from the card's state now: a revoked key, a takeover or a suspension changes the answer at once. |
| [`oidc-userinfo-post`](https://veil.pub/docs/oidc-userinfo-post) | `POST /oidc/userinfo` | directory | `private-code` / `local-or-server` | The same claims as the ID token, from the card's state now: a revoked key, a takeover or a suspension changes the answer at once. |
| [`oidc-revoke`](https://veil.pub/docs/oidc-revoke) | `POST /oidc/revoke` | directory | `private-code` / `local-or-server` | RFC 7009: the app revokes one of its tokens. A refresh token ends every token of its login. |
| [`oidc-introspect`](https://veil.pub/docs/oidc-introspect) | `POST /oidc/introspect` | directory | `private-code` / `local-or-server` | RFC 7662, for confidential apps: whether one of the app's own tokens is active now. |
| [`oidc-register`](https://veil.pub/docs/oidc-register) | `POST /oidc/register` | directory | `public-write` / `local-or-server` | RFC 7591, open: an app no card answers for. The consent page calls it unverified, and it is gone 30 days after registration. |
| [`oidc-logout`](https://veil.pub/docs/oidc-logout) | `GET /oidc/logout` | directory | `public` / `local-or-server` | RP-initiated logout. With id_token_hint the tokens of that login end. the browser goes back only to an address the app registered exactly. |
| [`oidc-client-logo`](https://veil.pub/docs/oidc-client-logo) | `GET /oidc/clients/{id}/logo.{ext}` | directory | `public` / `local-or-server` | The PNG or GIF an owner gave the app on /developers. |
| [`oidc-apps`](https://veil.pub/docs/oidc-apps) | `GET /v1/identities/{n}/oidc-apps` | directory | `signed` / `local-or-server` | The apps the card signed in to, with the last five logins of each and the consent its device key signed, so the owner can audit every login. |
| [`oidc-app-revoke`](https://veil.pub/docs/oidc-app-revoke) | `POST /v1/identities/{n}/oidc-apps/{client}/revoke` | directory | `signed` / `local-or-server` | The app forgets the card's consent, and every token it holds for the card ends. |

## Manage a card

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`create-person`](https://veil.pub/docs/create-person) | `POST /v1/identities` | directory | `signed` / `local-or-server` | Publish the first record, signed by the key named in that record. |
| [`publish-person`](https://veil.pub/docs/publish-person) | `POST /v1/identities/{n}/versions` | directory | `signed` / `local-or-server` | Change keys, linked accounts, alias or other signed card fields. |
| [`create-organisation`](https://veil.pub/docs/create-organisation) | `POST /v1/organizations` | directory | `signed` / `local-or-server` | Publish an organisation's first record, signed by its founder's active person key. |
| [`publish-organisation`](https://veil.pub/docs/publish-organisation) | `POST /v1/organizations/{n}/versions` | directory | `signed` / `local-or-server` | Publish a change authorised by an accepted owner or administrator. Role rules still apply. |
| [`salt-ticket`](https://veil.pub/docs/salt-ticket) | `POST /v1/salt-tickets` | directory | `public-write` / `local-or-server` | Commit the server's half of the first-version salt before the device chooses its half. |
| [`start-link`](https://veil.pub/docs/start-link) | `POST /v1/links/start` | directory | `signed` / `local-or-server` | Begin OAuth, email, domain or Fediverse proof for a card you can manage. |
| [`complete-link`](https://veil.pub/docs/complete-link) | `POST /v1/links/{state}/complete` | directory | `signed` / `local-or-server` | Complete a proof using the same key that started it. |
| [`link-state`](https://veil.pub/docs/link-state) | `GET /v1/links/{state}` | directory | `private-code` / `local-or-server` | Resume a proof with its secret state token. |
| [`oauth-callback`](https://veil.pub/docs/oauth-callback) | `GET /v1/links/callback/{platform}` | directory | `provider-callback` / `local-or-server` | Receive the redirect from Veil's configured Discord or GitHub application. |
| [`request-device`](https://veil.pub/docs/request-device) | `POST /v1/device-requests` | directory | `public-write` / `local-or-server` | Create a temporary pairing code for a new device's public key. |
| [`read-device-request`](https://veil.pub/docs/read-device-request) | `GET /v1/device-requests/{code}` | directory | `signed` / `local-or-server` | Read a pairing request with an active person key before adding the new device. |
| [`invite-accept`](https://veil.pub/docs/invite-accept) | `POST /v1/orgs/{n}/invites/{id}/accept` | directory | `signed` / `local-or-server` | The invited person signs with an active key. The JSON body contains nonce and timestamp. |
| [`invite-decline`](https://veil.pub/docs/invite-decline) | `POST /v1/orgs/{n}/invites/{id}/decline` | directory | `signed` / `local-or-server` | The invited person signs with an active key. The JSON body contains nonce and timestamp. |
| [`cancel-takeover`](https://veil.pub/docs/cancel-takeover) | `POST /v1/takeovers/{id}/cancel` | directory | `signed` / `local-or-server` | The current account holder signs to cancel an open transfer. |
| [`notices-state`](https://veil.pub/docs/notices-state) | `GET /v1/identities/{n}/notices` | directory | `signed` / `local-or-server` | An active key of the card reads its opt-in to email notices, with a signed GET. |
| [`notices-set`](https://veil.pub/docs/notices-set) | `PUT /v1/identities/{n}/notices` | directory | `signed` / `local-or-server` | An active key of the card opts in, with the language of the emails, or opts out. The body is {"on": true, "lang": "en" or "it"} or {"on": false}, with nonce and timestamp. |
| [`notices-unsubscribe`](https://veil.pub/docs/notices-unsubscribe) | `POST /v1/notices/unsubscribe` | directory | `public-write` / `local-or-server` | Opts a card out with the token of its emails' stop link, without a key: n and t in the query (a mail program's one-click POST, RFC 8058) or {"n", "token"} in the body. |
| [`notices-stop-page`](https://veil.pub/docs/notices-stop-page) | `GET /notices/stop` | directory | `public` / `local-or-server` | The page the email notices link to, to stop them without the card's key. |
| [`logo-preview-create`](https://veil.pub/docs/logo-preview-create) | `POST /v1/logo-previews` | directory | `signed` / `local-or-server` | Validate a profile image or organisation logo before including it in a signed record. |
| [`logo-preview-read`](https://veil.pub/docs/logo-preview-read) | `GET /v1/logo-previews/{hash}.{format}` | directory | `private-code` / `local-or-server` | Read a temporary image using the preview URL returned to its creator. |
| [`request-erasure`](https://veil.pub/docs/request-erasure) | `POST /v1/identities/{n}/erase` | directory | `signed` / `local-or-server` | An active person key or an organisation owner signs the erasure request. There is a 24-hour cancellation window. |
| [`cancel-erasure`](https://veil.pub/docs/cancel-erasure) | `POST /v1/identities/{n}/erase/cancel` | directory | `signed` / `local-or-server` | An active authorised key cancels erasure during its cancellation window. |
| [`publish-alert`](https://veil.pub/docs/publish-alert) | `POST /v1/identities/{n}/alerts` | directory | `signed` / `local-or-server` | The owner signs an alert about one of the card's linked accounts. From then on every lookup of that account opens with it, until a regained alert ends it. |
| [`publish-statement`](https://veil.pub/docs/publish-statement) | `POST /v1/identities/{n}/statements` | directory | `signed` / `local-or-server` | A person or an organisation publishes a statement with a title, a text and an optional link, or retracts an earlier one. The log's witnesses date it. |
| [`submit-report`](https://veil.pub/docs/submit-report) | `POST /v1/identities/{n}/reports` | directory | `signed` / `local-or-server` | An active person key submits a moderation report about a card. |
| [`start-move`](https://veil.pub/docs/start-move) | `POST /v1/moves` | directory | `signed` / `local-or-server` | Ask for a move for this browser's new key, signed by that key. The move is open ten minutes. |
| [`read-move`](https://veil.pub/docs/read-move) | `GET /v1/moves/{nonce}` | directory | `public` / `local-or-server` | Whether a move is still open, and its key. Never its card, nor whether it was approved. |
| [`approve-move`](https://veil.pub/docs/approve-move) | `POST /v1/moves/{nonce}/approve` | directory | `signed` / `local-or-server` | At the old address, signed by an active device key of the card: the card's next version that adds the move's key as a device, the receipt and the SHA-256 of the secret. Checked as a publication would be, kept and not published. |
| [`complete-move`](https://veil.pub/docs/complete-move) | `POST /v1/moves/{nonce}/complete` | directory | `signed` / `local-or-server` | At the new address, signed by the move's key, with the secret: the kept version is published through the same path as a card's next version. A second call gets the same answer. |
| [`discord-roles-page`](https://veil.pub/docs/discord-roles-page) | `GET /discord/linked-roles` | directory | `public` / `local-or-server` | The page Discord opens from a server's linked role: it reads this browser's card, shows what Discord will see and sends the person to Discord. Give it to the Developer Portal as the Linked Roles Verification URL. |
| [`discord-roles-callback`](https://veil.pub/docs/discord-roles-callback) | `GET /discord/linked-roles/callback` | directory | `provider-callback` / `local-or-server` | Where Discord sends the browser back with a code. The page proves nothing by itself: it gives a one-time return code to the browser that started, which signs the complete. |
| [`discord-roles-info`](https://veil.pub/docs/discord-roles-info) | `GET /v1/discord/linked-roles` | directory | `public` / `local-or-server` | Whether this server offers Discord linked roles, the Discord app, the scopes it asks for, the verification URL, and the five metadata fields exactly as registered on Discord. |
| [`discord-roles-start`](https://veil.pub/docs/discord-roles-start) | `POST /v1/discord/linked-roles/start` | directory | `signed` / `local-or-server` | Signed by an active device key of a card that already links a verified Discord account. Returns a random state bound to the card and the key, and Discord's consent page. |
| [`discord-roles-complete`](https://veil.pub/docs/discord-roles-complete) | `POST /v1/discord/linked-roles/{state}/complete` | directory | `signed` / `local-or-server` | Signed by the key that started, with the return code. The server trades Discord's code, checks that the Discord account is a verified account of the card, keeps the tokens encrypted and sends the facts. |
| [`discord-roles-list`](https://veil.pub/docs/discord-roles-list) | `GET /v1/identities/{n}/discord-roles` | directory | `signed` / `local-or-server` | The card's verified Discord accounts, what Discord would get now, and each connection with what Discord holds and why one ended. |
| [`discord-roles-disconnect`](https://veil.pub/docs/discord-roles-disconnect) | `POST /v1/identities/{n}/discord-roles/{discordId}/disconnect` | directory | `signed` / `local-or-server` | Sends Discord empty facts, empties the profile widget if any, revokes Veil's access and forgets the connection. On a connection that already ended it only forgets it. |

## Service reference

| ID | Method and path | Base | Access / browser | Purpose |
|---|---|---|---|---|
| [`catalogue`](https://veil.pub/docs/catalogue) | `GET /v1/integrations` | directory | `public` / `fetch` | Read the guides and endpoint index as JSON. |
| [`catalogue-entry`](https://veil.pub/docs/catalogue-entry) | `GET /v1/integrations/{id}` | directory | `public` / `fetch` | Read one guide or endpoint contract, including examples. |
| [`openapi`](https://veil.pub/docs/openapi) | `GET /openapi.json` | directory | `public` / `fetch` | The whole API as one OpenAPI 3.1 file, for a client generator, Postman or an API gateway. |

## Detailed contracts

Captured from the docs pages and checked against the live service on 17 November 2026. For the full field tables, nested types and errors, use `python scripts/veil.py doc <id>`. The examples use two live cards: card 1, the person Gabriele Todaro (alias `gab`), and card 2, the Veil organisation (alias `veil`).

### GET /v1/lookup

Exactly one query parameter. Errors: `400 invalid_parameter`, `404 not_found`, `409 ambiguous`, `410 erased`.

- `account`: anything a person types or pastes. The server reads it as every form it can be and looks each one up exactly: a Discord username or ID, a GitHub login, `@user@server`, an email, a domain, a profile address (`https://github.com/<login>`, `https://discord.com/users/<ID>`, `https://server/@user`, `https://bsky.app/profile/<handle>` read as its domain), a public key, a fingerprint, a card number, a card's address or an alias. The prefixes `github:<login>`, `discord:<username>` and `github:<digits>` pick one reading.
- `discord`: stable numeric user ID, 17 to 20 digits
- `github`: numeric account ID, not the login
- `email`: the complete address
- `domain`: the exact domain, no trailing dot, IDNs as their ASCII A-label
- `fediverse`: the complete `@user@server`
- `key`: an Ed25519 public key in hex, or the full composite key in base64 (URL-encode it). It also takes a public key from elsewhere as you would paste it: an OpenSSH line, an armoured OpenPGP public key, a minisign public key or an ML-DSA key in base64. A revoked key still finds its card.
- `fingerprint`: the 12 words (English or Italian) or the 60 digits. Also the fingerprint of a key from elsewhere: `SHA256:...` as `ssh-keygen -l` prints it, a minisign key ID in 16 hex digits, or the 40 hex digits of an OpenPGP fingerprint. An OpenPGP key ID is not enough.

Response: `identity` (the short card, including `alias` and `aliasUrl`), `match`, a nullable `takeover` with `toIdentity`, `openedAt` and `resolvesAt`, and with `account` also `understood`, every form the value was read as. Fetch the full card for its proof.

`match.by` names the parameter, or with `account` the form that matched (`github-login`, `discord-username`, `card`, `alias` or a parameter name), and `match.value` is the normalised value. A username or a login is matched whole, ignoring case, against the name the platform gave when the account was proved. The match then adds `platform`, `subject` (the stable ID), `handle`, `recorded` (that day), `checked` (the day of the last re-check that confirmed the name, GitHub only today) and `stale`.

```json
{"match": {"by": "github-login", "value": "gabriele73", "platform": "github", "subject": "109546049",
           "handle": "Gabriele73", "recorded": "2026-10-30", "stale": true},
 "understood": [{"by": "github-login", "value": "gabriele73"}],
 "identity": {"n": 1, "url": "https://veil.pub/u/1", "...": "..."}, "takeover": null}
```

That is `GET /v1/lookup?account=github:Gabriele73` today. `stale: true` means the platform's last word on that name is more than 2 days old. A name can pass to someone else and the ID cannot, so show the ID and the date, and do not open the card unasked. Only active links count: a pending takeover, an account the re-check found gone and the old login of a renamed GitHub account find nothing.

- `404 not_found` with `account` carries `understood`.
- `409 ambiguous` carries `understood` and `candidates`, each with `identity`, `match` and `takeover`, when the readings lead to more than one card. Show them all and let the reader choose. Never open the first.
- A card's alias (`match.by` is `alias`) is chosen by its owner and can equal someone else's GitHub login or Discord username. When `understood` also lists `github-login` or `discord-username`, say that the word is the card's chosen address and that no card holds it as a login or a username.
- `alert` appears when the card's owner declared the looked-up account stolen, abandoned or moved and has not declared it regained: `platform, subject, display, state, since, to, logIndex, publishedAt`. Show it before anything else.

Nothing in this answer is signed. Resolve the number, verify the full card, and check that its signed record holds an active link of `match.platform` whose subject is `match.subject`. Keep the ID as the account and treat the name as dated.

`GET /v1/lookup?key=73ad6159583a43f8ad230a215b758db680efcd3ce32ab8e83c622eeca883e68a` returns card 1 (that key was revoked in version 5), and so does `?github=109546049`.

### GET /{platform}/{account}

Addresses to share: `https://veil.pub/github/<login>`, `/discord/<username or ID>`, `/fediverse/<@user@server>`, `/email/<address>` and `/domain/<name>`. The answer is a `302` to the card when exactly one card holds the account and, for a username or a login, the platform gave or confirmed that name in the last 2 days. Otherwise it is a `302` to the front page's search with the same value (`/?q=github:<login>`). An address with an ID (`/discord/<ID>`, `/github/<numeric ID>`) always opens the card that holds the account, so prefer it in a profile. Optional `lang`. The answer is never cached and carries `X-Robots-Tag: noindex`.

### GET /u/{card}.json and /o/{card}.json

`card` is the permanent number or the current alias. Without `.json`, send `Accept: application/json`. `/v1/identities/{n}` and `/v1/organizations/{n}` need the permanent number. A person card has `n, id, url, type, keys, links, orgs, events, fingerprint, proof, historyBefore` and the other presentation fields. An organisation's JSON `type` is `organization` and it adds `members`. Errors include `404 not_found`, `410 erased` (with a public receipt) and `422 not_an_organization` on `/o/` for a person. A successful response can have `proof: null` when the server cannot verify the log at that moment. Keep such a card unverified.

On a format 2 log the card adds `format`, `current`, `authority`, `authorityNext`, `state`, `index` and `standing`, and `proof` carries the format 2 entry instead of the record. [format-2.md](format-2.md) lists every field.

Fields added since 29 October 2026:

- `external`: a person's public keys from elsewhere (SSH, OpenPGP, minisign and others), each with `type, fp, label, pub, addedIn, since, logIndex, proofOk`, the checkpoint its proof cites and a consistency proof to the card's checkpoint. The signed copies are in `state.external`.
- `alerts`: the account alerts in force, and `statements: {total, latest, url, feed}`, the card's signed statements.
- `waiting`: versions in the log that the witnesses have not cosigned yet. The card shows the version before until they do.
- A link's `check`: `{state, at, since, reported, lastOk}`, the server's periodic re-check of a domain, Fediverse or GitHub proof. `state` is `ok`, `failing` or `unreachable`. It is the server's word and is not part of the signed card.

Card JSON responses carry a weak `ETag` (a SHA-256 of the JSON bytes), `Cache-Control: private, no-cache, must-revalidate` and `Vary: Accept`. Send the tag back in `If-None-Match` and the server answers `304` with no body when the rebuilt card, with its current visibility, moderation and proof, has identical bytes. A changed record, checkpoint or moderation state changes the tag. Errors keep their own status. A 304 only saves the download. Re-check freshness, and keep a stored verdict only for the exact bytes you verified.

### GET /v1/identities/{n}/summary

Fields: `n, url, name, initials, type, version, keys, orgs, badges, nameHidden, logo, alias, aliasUrl`. `nameHidden` is a boolean here and `logo` can be null. Errors `404`, `410`. It carries no proof and is the same in both formats.

### GET /v1/aliases/{kind}/{alias}

`kind` is `u` or `o`. `alias` is 3 to 32 ASCII letters, digits, hyphens or underscores, starting with a letter and ending with a letter or digit. Response: `kind`, `alias`, `available`, `status` (`available`, `claimed`, `publishing`, `quarantined` or `reserved_name`), `url`, `identity` (`n` and permanent `url` when claimed), `reusableAt`, `quarantineDays` (30), `previousIdentity` and `reservedFor`. Availability does not reserve a name. Errors include `400 invalid_parameter` and `400 invalid_alias`.

The Veil organisation holds the alias `veil`, so `/o/veil.json` is card 2:

```json
{"kind": "o", "alias": "veil", "available": false, "status": "claimed", "url": "https://veil.pub/o/veil",
 "identity": {"n": 2, "url": "https://veil.pub/o/2"}, "reusableAt": null, "quarantineDays": 30,
 "previousIdentity": null, "reservedFor": null}
```

An alias is an address chosen by the card. A change or release stops the old address at once and starts 30 days of quarantine, during which only the previous holder can take it back. Store `n`.

### GET /v1/platforms

Returns `platforms` with IDs, translated labels, `method`, `methods`, `enabled`, `reason` and `organizations` (whether an organisation can link it). Use it to build account-linking choices.

### Account alerts and signed statements

Since 30 October 2026 a card can publish two kinds of signed entries of its own. An **alert** declares one linked account `stolen` (since a date), `abandoned`, `moved` (to another handle) or `regained`. A **statement** is a title, a text and an optional link, or the retraction of an earlier statement.

- `GET /v1/identities/{n}/alerts` returns `card`, `inForce` (one per account, the latest unless it is `regained`) and `alerts` (every alert in the log, newest first, at most 200). Each has `platform, subject, display, state, since, to, logIndex`.
- `GET /{kind}/{card}/statements.json` takes `before` and `limit` (1 to 100, default 20) and returns `card, total, statements, next, feed`. Each statement has `title, text, link, retracts, retractedBy, url`. `GET /{kind}/{card}/statements.atom` is the feed of the latest 50.
- `GET /v1/statements/{id}` returns `card`, `statement` and `retracts`. The id is the entry's position in the log.

Every item also carries what a reader needs to check it: `id`, `kind`, `n`, `signer` (`n` and `token` of the person whose key signed), `statement` (the canonical JSON as signed), `salt`, `entry`, `i`, `publishedAt`, `checkpoint` and `inclusion`. Check that `c` in the entry is `SHA-256(salt || statement)`, that the entry's signature over `"veil-rubrica:card-entry:v2\n"` + the entry without `signature` comes from a key active for the signer at position `i`, and that the entry is included in a checkpoint the log signed and a quorum cosigned. The list itself is the server's word and can leave an entry out.

An item still waiting for the witnesses answers `{id, kind, n, i, witnessed: false, sequencedAt, publishedAt: null}` without its text.

### GET /v1/keys/{key}

`key` is 64 hex characters of an Ed25519 key, or the Ed25519 half of a composite key. Response: `key, alg, ed25519, identity, device, role, state, addedIn, revokedIn, validFrom, validUntil`. Composite keys return the full key in `key`. Errors `400`, `404`.

### GET /v1/keys/{key}/active-at

Query `t` is Unix seconds (default now, range 0 to 253402300799). Response: `at, active, reason, validFrom, validUntil`. `reason` is `active`, `not_yet_valid` or `revoked`.

### POST /v1/verify (messages)

No device-signing headers. An optional bearer key needs `verify` scope. The JSON body takes one of two forms.

- Block mode: `block` (the full pasted signature block, at most 32768 characters) and an optional `at` (Unix seconds, default now). It cannot be combined with `key`, `message`, `signature`, `platform` or `subject`.
- Raw mode: `key`, `message` (the exact UTF-8 text) and `signature`. Ed25519 keys and signatures are hex. Composite keys and signatures are base64. The optional pair `platform` and `subject` checks account ownership at `at`.

Response: `valid` (the overall verdict), `signatureOk`, `identity`, `device`, `role`, `keyState`, `account` and `reason`. Block mode also returns `block`, the parsed block, and `key`, the matching key when one is found. HTTP 200 can carry `valid: false`, so read the fields to decide. Errors: `400 invalid_block`, `400 invalid_parameter`. From browsers use `fetch(..., {credentials: "omit"})`. This call is the same in both log formats.

Share links, from the guide, with `message` and `signatureBytes` from the signer and `cardNumber`:

```js
const b64u = b => btoa(String.fromCharCode(...b)).replaceAll("+","-").replaceAll("/","_").replace(/=+$/,"");
const m = b64u(new TextEncoder().encode(message)), s = b64u(signatureBytes);
const browserLink = `https://veil.pub/verify#u=${cardNumber}&m=${m}&s=${s}`;      // stays in browser, both algorithms
const previewLink = `https://veil.pub/v/${cardNumber}/${s}?m=${m}`;               // Ed25519 only, message <= 1500 UTF-8 bytes
```

### POST /v1/verify (files and releases)

Since 29 October 2026 the same call checks a signature over a file or a release. The server never sees the file: you hash it and send the hash.

- `signature`: the signature as the tool wrote it. The `.sig` of `ssh-keygen -Y sign -n file`, the `.asc` of gpg (or its binary `.sig` in base64), a `gpg --clear-sign` text, a `.minisig` file or a Veil block.
- `sha256`, `sha512` or `blake2b512`: the file's hash in hex. Send the one the signature uses.
- `name`: the file's name, at most 255 bytes. In a list, the line with this name is used.
- `list`: the exact text of the checksum list a detached signature covers (`SHA256SUMS` or `SHA512SUMS`, at most 1000 lines). A clear-signed list and a release's Veil block carry their own.
- Optional `format` (`ssh`, `pgp`, `minisign` or `veil`), `card` (needed for an OpenPGP signing subkey and for a key the card has removed) and `at`.

The response is the message verdict plus `format`, `external` (the key from elsewhere: `type, fp, label, addedIn, removedIn, signer`), `signedAt`, `atFrom` (`request`, `signature` or `now`), `covers` (`file` or `list`), `hash`, `file`, `list` and `match` (`name, alg, expected, ok`). `reason` adds `hash_mismatch` and `not_in_list`. Errors: `400 hash_needed`, `400 invalid_file_signature` and `422 file_needed` for a signature over the file's own bytes (a detached OpenPGP signature, a legacy minisign signature). For those use the page at `https://veil.pub/verify`, which hashes in the browser, or a signed checksum list.

A live example is the signed checksum list of the command line tool, `https://apt.veil.pub/releases/0.1.4/SHA256SUMS.veil`:

```json
{"signature": "<the text of SHA256SUMS.veil>", "name": "veil-0.1.4-darwin-arm64.zip",
 "sha256": "22d956b73a9d7ccf2e4f21f742ad3437b876f595a860155da501a6f1af259315"}
```

It answers `valid: true`, `format: "veil"`, `covers: "list"`, `identity.n: 1` and `match.ok: true`. A wrong hash answers `valid: false` with `reason: "hash_mismatch"`, and a name the list does not hold answers `reason: "not_in_list"`. Links to share: `https://veil.pub/verify?u=<card>&sha256=<hex>` and `https://veil.pub/verify#b=<block>`.

### GET /u/{card}/keys.txt and /u/{card}.keys

A person's public keys from elsewhere as a text file. `format` is `authorized_keys` (the default), `allowed_signers` (for git and `ssh-keygen -Y verify`), `minisign` or `pgp` (an armoured block for `gpg --import`). `fp` or `key` keeps one key, and the `+` of an SSH fingerprint is written `%2B`. `/u/{card}.keys` is the same file at the address `github.com/<user>.keys` made familiar. `allowed_signers` names each key with the card's verified email addresses and `veil.pub/u/<n>`. A key the card no longer holds is a `404`.

The file is the server's word. Each key's proof of possession is in `state.external` of the card JSON: the key signed a challenge that names the card, the device key and a cosigned checkpoint. [signed-requests.md](signed-requests.md#keys-from-elsewhere) has the challenge.

### GET /v1/grant-key

Returns `alg, key, format, signingPrefix` for account-linking grants. A grant is the directory's statement about an account proof: check its signature, scope and expiry. A grant alone does not publish a card version.

### GET /v1/identities/{n}/versions

Query: `after` (the version to continue after, default 0), `limit` (1 to 200, default 50), `latest=true` (only the latest version, cannot be combined with a nonzero `after`). `versions` is oldest first. Follow `next` as `after` until it is null. A 2 MiB byte budget can return fewer rows than `limit`. Errors `400`, `404`, `410`.

On a format 2 log each item is `{label, body, signature, signedBy, logIndex, publishedAt, entry}`, with `label` and `body` as canonical texts. Check that the body hashes to `label.body`, that each label's `prev` is the hash of the label before, and each signature against the authority before it. On a format 1 log each item has `record`, `salt` and `commitment` in place of `label` and `body`.

### GET /v1/identities/{n}/versions/{v} (format 2)

One version whole, in the shape of an item of `versions`, with `witnessed`. `404` when the version does not exist. After an asynchronous publication, read it every 2 seconds until `witnessed` is true.

### GET /v1/identities/{n}/authority (format 2)

Query: `after` (default 0) and `limit` (1 to 200, default 50). Response: `{"authority": [...], "next": k | null}`, the versions whose `label.auth` is not empty, oldest first, in the shape of `versions`. Pass `next` as `after`. The card's own `authority` field already holds the first 50, each with its log position `i` and `inclusion`.

### GET /v1/identities/{n}/statements (format 2)

The pages of **staff** statements after `index.statements` of the card. A card's own statements are at `/{kind}/{card}/statements.json`. Query: `from` (a log position, the `prev` of the last statement on the page before) and `size` (the checkpoint size of the card's index bundle). Both are required. Follow the card's `index.statementsNext` instead of building the query yourself. Response: `{"n", "size", "statements": [{"i", "entry", "inclusion", "by"}], "statementsNext": "<path>" | null}`, up to 200 statements newest first, with inclusion proofs in the tree of `size` entries. It also answers for a closed card. `400 invalid_parameter` for a `from` beyond `size`, `503 log_unavailable` when the log cannot be verified or an entry cannot be proven. Since 29 October 2026 another origin can read it.

### GET /v1/identities/{n}/labels (format 2)

Query: `after` (default 0) and `limit` (1 to 1000, default 1000). Response: `{"labels": ["<canonical label>", ...], "next": k | null}`, oldest first, with `null` for an erased version. A full page never changes and is served with `Cache-Control: public, max-age=31536000, immutable`. The last, shorter page is `no-cache`. Labels alone are enough to follow the `prev` chain. Bodies and signatures come from `versions`.

### GET /v1/identities/{n}/sets/{set}/path (format 2)

`set` is `keys`, `links`, `orgs` or `members`. Query `key` is the item key: a public key, the platform and subject separated by a newline (`%0A`), or a card token. Response: `n, version, set, key, position, item, proof, root`. `item` is `null` for a key that is not in the set, and the proof then starts from the empty leaf. A signer uses the path to compute the new set root after changing one item.

### GET /v1/organizations/{n}/members (format 2)

Query: `prefix` (standard base64 of the prefix bytes, empty for the first page) and `bits` (0 to 24, default the server's page depth). Response: `n, version, root, prefix, bits, items, proof, pages`, where each item is `{member, role, since}`. Compute the page's subtree root from `items`, fold `proof` up to `root`, and compare it with `state.roots.members` of the card. A page over 4096 members or a prefix of the wrong length is `400 invalid_parameter`. A person answers `422 not_an_organization`.

### GET /v1/identities/{n}/history

Query: `before` (an exclusive version cursor, omit it for the newest page) and `limit` (1 to 200, default 50). Response `events`. Pass the returned `before` for the next older page. `null` marks the first version. In format 2 the event kinds come from the operations: `created` or `founded`, `added`, `recovery`, `revoked`, `device` (a renamed key), `link`, `unlinked`, `invited`, `member_removed`, `role`, `joined`, `left`, `renamed`, `alias`, `alias_released`, `logo` and `logo_removed`.

### GET /v1/identities/{n}/versions/{k}/proof

The proof object of a full card, for version `k`. In format 2 it is `{version, labelHash, entry, logIndex, leafHash, checkpoint, inclusion, witnesses}`. Verify the entry, the leaf hash, the inclusion and the signed checkpoint. Errors `404`, `503 log_unavailable`.

### GET /v1/identities/{n}/events

Query `after` (a nonnegative event ID, default 0). Response `n, events, next`. Keep `next` and pass it as `after` on the next poll. These events are separate from the signed version history.

### GET /v1/takeovers

Query `identity` (required, a permanent card number). Response `identity` and `takeovers`, newest first, each with `from, to, status, openedAt, resolvesAt`. An open transfer has not changed the owner yet.

### GET /v1/identities/{n}/orgs

Response `n, type, memberships` with role, acceptance and removal state. An invitation is not an accepted membership.

### Staff, moderation and badges

- `GET /v1/staff`: `org` (the Veil organisation: `n`, `url`, `name`, `token`, `nameHidden`, `logo`) and `roles`, the actions each staff role may take. Today `org.n` is 2 and `org.token` equals `staffOrg` of `GET /v1/log`.
- `GET /v1/identities/{n}/moderation`: `n, banned, until, category, logIndex, actions, nameHidden`, the server's view of the card's moderation.
- `GET /v1/moderation/entries`: query `after` (an exclusive log index, default -1) and `limit` (1 to 500, default 200). Response `org, entries, next`. Follow `next` until null.
- `GET /v1/badges/catalogue`: every badge with `id`, `label` in both languages, `icon`, `derived`, `givenBy` and `description`.
- `GET /v1/identities/{n}/badges`: the card's badges with `badge, active, derived, source, icon, since, until, logIndex, role, removedAt`.

In format 2 the verified moderation and badges come from the signed statements in the card's index. These reads are the server's view.

### GET /v1/canary

The warrant canary. `status` is `current`, `stale` or `none`. `current` holds the latest statement (`id, date, lang, text, signer, key, alg, device, signature, block`), `maxAgeDays` is 35, `statement` gives the text in English and Italian with `{date}` where the ISO date goes, and `history` lists every statement, newest first.

This is the server's copy. To check it, read `current.block` as a signature block: its text must be the statement with the date, word for word, and a key of the signer's card must have made the signature. Count the 35 days from the signed date yourself, because `stale` is the server's word. `GET /canary` is the page that runs the check in the browser.

### GET /oembed

Query `url` (required: a Veil person, organisation or `/v/` URL), `format=json` (XML gives `501 format_not_implemented`), `maxwidth` (below 280 gives a link response) and `maxheight` (below 200 gives a link response). Cards return type `rich` with the widget HTML and a thumbnail. Verification links and small limits return type `link`. Errors `400`, `404`, `501`.

### Card images and files

`GET /{kind}/{n}/logo.{svg|png|gif}` serves the exact published picture at the `logo.url` of the card. Pictures are PNG (APNG included, as `image/png`), GIF (animated or not) or a restricted SVG, at most 2 MiB (2,097,152 bytes). PNG and GIF are at most 512 by 512 pixels. A matching `v` query allows one day of public caching. `size=64` or `size=128` on a PNG asks for a smaller display thumbnail. Read [responses-and-errors.md](responses-and-errors.md) for thumbnails. `404 not_found` for a missing or hidden picture, `410 erased`, and `422 not_a_person` or `422 not_an_organization` for the wrong `kind`.

- `GET /{kind}/{card}/card.png` (`theme`, `lang`): a server-rendered PNG with public card metadata, for link previews.
- `GET /u/{card}.vcf` (`lang`): a vCard 4.0 with the name, the card's address, verified email addresses, verified accounts as URLs, the picture and the fingerprint. Persons only, and never for a suspended, closed or name-hidden card.
- `GET /u/{card}/discord.png` and `.svg` (`theme`, `lang`): the card drawn for a Discord profile. The PNG is 1360 pixels wide and the SVG 680.
- `GET /u/{card}/embed?style=discord`: the widget in the same style, for a frame.

Each image is the server's rendering and verifies nothing in the viewing app.

### GET /v1/log

Response includes `origin, size, root, checkpoint, witnesses, quorum, signed, of, quorumMet`, freshness (`newestCosignatureAt`, `fresh`, `freshSeconds`) and consistency (`consistency`, `accepted`). These are the server's own checks. On a format 2 log it adds `"format": 2` and `"staffOrg"`, the token of the Veil organisation. A missing `format` means format 1. Today:

```json
{"origin": "log.veil.rip/staging-1", "quorum": 2, "of": 5, "format": 2, "staffOrg": "d8aKGsTCN1U_lB3NznVocg", "...": "..."}
```

The origin keeps its first name while the log is read at `https://log.veil.pub/staging-1/`. Pin the expected log and witness policy for independent verification. `503 log_unavailable`.

### POST /v1/identities (create-person)

Needs the `X-Public-Key` and `X-Signature` headers. On a format 2 log the JSON body is `label`, `body`, `signature`, the optional `pictureData`, `clientSalt` and `saltTicket` (both required for version 1), `nonce` (16 to 128 characters: letters, digits, `_`, `-`) and `timestamp` (Unix ms within 2 minutes of the server). A format 1 `record` answers `400 wrong_format`. Response `201` with `n, id, url, token, version, commitment, logIndex, publishedAt, checkpoint, witnessed, sequencedAt` after witnessed publication. In format 2 `commitment` is the label hash in hex. Errors include `422 invalid_op`, `422 label_mismatch`, `422 invalid_record`, `401 missing_signature`, `409 version_conflict`, `409 salt_ticket_invalid`, `409 key_already_used` and `503 log_unavailable`. [signed-requests.md](signed-requests.md) has the label, body and operations.

### Publishing without waiting for the witnesses

Since 8 November 2026 the four version routes, `POST /v1/identities/{n}/alerts` and `POST /v1/identities/{n}/statements` accept `Prefer: respond-async`. The server then answers `202` as soon as the log holds the entry, usually under a second, with `witnessed: false`, the final `logIndex`, and `publishedAt` and `checkpoint` null. The card keeps showing the version before until a quorum of witnesses cosigned a checkpoint that holds the new one. Read `GET /v1/identities/{n}/versions/{v}` (or `GET /v1/statements/{id}`) every 2 seconds until `witnessed` is true. Without the header the answer is the `201` of before. A `202` is not a publication yet: treat the change as done only when `witnessed` is true.

### POST /v1/links/start

Signed. Body: `identity` (the permanent number), `platform` (an ID from `/v1/platforms`), `subject` (required for email, domain and Fediverse, OAuth takes it from the platform) and an optional `method` (domains support `dns_txt` and `well_known`). Response `201` with `state, method, expiresAt, challenge`. Keep `state` private. Starting or completing a proof does not add the account to the card. A published version does.

### Alerts, statements and reports (signed writes)

- `POST /v1/identities/{n}/alerts`: body `statement` (`{platform, since, state, subject, time, to, type: "alert", v: 1}`), `salt` (32 random bytes in hex) and `entry` (`{text, signature}`). A device key or the recovery key signs. Persons only, at most 10 per card in 24 hours. Errors include `409 alert_in_force`, `409 alert_not_in_force`, `422 account_not_linked` and `429 alert_quota`.
- `POST /v1/identities/{n}/statements`: body `statement` (`{link, retracts, text, time, title, type: "statement", v: 1}`), `salt` and `entry`. A person signs with a device key, an organisation through an owner or an admin. At most 10 per card in 24 hours, retractions included. Errors include `409 already_retracted` and `429 statement_quota`.
- `POST /v1/identities/{n}/reports`: body `category` (`spam`, `impersonation`, `abuse`, `illegal` or `other`), `text` (1 to 2000 characters) and up to five HTTPS links in `evidence`. `201` with `id, target, category, state, createdAt`. Report contents are not public.

[signed-requests.md](signed-requests.md#alerts-and-statements) has the entry and its signature.

### Email notices

`GET` and `PUT /v1/identities/{n}/notices` (signed) read and set a person's opt-in to email notices: `n, on, lang, since, lastSentAt, email, mail, events, dailyCap`. The events are `takeover`, `device_added`, `device_revoked`, `backup_missing`, `proof_failing` and `key_idle`. Opting in needs a verified email link on the card, and the notices go to its oldest verified address, at most 3 per UTC day and then a digest. `POST /v1/notices/unsubscribe` is the stop link of each email. Errors: `422 no_verified_email`, `422 not_for_organizations`, `503 no_mail_transport`.

### Moving a browser to veil.pub

A key lives on the origin that made it. Since 6 November 2026 a browser whose key was made on `veil.rip` moves with `POST /v1/moves` (`201` with `nonce, key, expiresAt, approve`), `GET /v1/moves/{nonce}`, `POST /v1/moves/{nonce}/approve` and `POST /v1/moves/{nonce}/complete`. The new address makes a key of its own and the card adds it with a version signed at the old address, in the same browser. A move stays open for 10 minutes, and an IP can start 10 an hour. Veil's own pages run this flow. An integration never needs it.

### Discord Linked Roles

Since 17 November 2026 a person can connect their card to Discord's Linked Roles, so a server can give a role to members whose card is in good standing.

- `GET /v1/discord/linked-roles`: `available`, `application`, `platformName`, `scopes`, `widget`, `verificationUrl` and `metadata`. Today the facts are `card` (a card in good standing that lists this Discord account), `card_since` (the card's age in days), `linked_accounts`, `keys` and `org_member`.
- `POST /v1/discord/linked-roles/start` (signed): `201 {state, url, expiresAt, scopes}`. The state lasts ten minutes and works once.
- `POST /v1/discord/linked-roles/{state}/complete` (signed): the connection, with `discord`, `state`, `connectedAt`, `lastPushAt`, `nextPushAt`, `shown`, `retiredAt` and `reason`.
- `GET /v1/identities/{n}/discord-roles` (signed): `accounts`, `preview`, `reasons` and `connections`.
- `POST /v1/identities/{n}/discord-roles/{discordId}/disconnect` (signed).

Errors: `404 linked_roles_off`, `422 no_discord_link`, `409 discord_account_alert`, `409 not_in_good_standing`, `429 too_many_starts`. Members connect at `https://veil.pub/discord/linked-roles`. The [`discord-app`](https://veil.pub/docs/discord-app) guide covers the app's commands.

### Share and embed snippets

```markdown
[![Veil card](https://veil.pub/o/2/badge.svg)](https://veil.pub/o/2)
```

```html
<iframe src="https://veil.pub/o/2/embed" title="Veil organisation card"
  width="560" height="200" loading="lazy" referrerpolicy="no-referrer"></iframe>
<div data-veil-org="2"></div>   <!-- people: data-veil-card="N" -->
<script src="https://veil.pub/embed.js" async></script>
```

Use the number, which never changes. A snippet with an alias stops working when the alias changes. CSP: allow `frame-src https://veil.pub`, and `script-src https://veil.pub` if you use `embed.js`. Snippets that still point to `veil.rip` keep working through its redirects, but update them. Options: `data-theme`, `data-lang`. The SVG badge reports the server's status when it was generated and may be cached. The widget verifies the card in each visitor's browser, in format 2 as in format 1.

### Developer API responses

Read [API keys and shared quotas](api-keys.md) for management access, pagination and the quota response. An owner overview includes `owner`, `suspended`, `limits`, `quota`, `usage`, `history`, `keys`, `next`, `audit` and `permissions`. Overview and list calls never return secret material. Only creation returns a one-time `secret` with the key metadata.

The quota endpoint returns HTTP 200 with `owner`, `key`, `quota`, `rate`, `resource` and `retryAfter`. Reading it does not spend the primary allowance. Minute buckets refill continuously and daily caps reset at midnight UTC.

The same account routes register apps for Sign in with Veil (`/v1/developer/accounts/{n}/oidc-clients`). Read [sign-in.md](sign-in.md).

### GET /v1/integrations, /{id} and /openapi.json

Optional `lang=en|it`. The index has `revision`, `language`, `baseUrl`, `documentationUrl`, `groups` and `entries`. Each endpoint summary has `supportsBrowserFetch` and `browserMode`. A detail has `revision`, `language` and `entry`. Endpoint entries expose `responses`, `responseObjects`, `responseHeaders` and `errorDetails`, plus request parameters and the earlier summaries. A matching `If-None-Match` returns 304 with no body. Cache by revision, entry and language. The public reference can be cached for five minutes.

`GET /openapi.json` is the same catalogue as OpenAPI 3.1.0, in English. `info.version` is the date of the newest change in the changelog (`2026-11-17` today). Each operation carries `x-veil-entry` (its page here), `x-veil-access` and `x-veil-browser-mode`. A signed operation carries `x-veil-signature`, because OpenAPI cannot express how Veil signs canonical JSON. Every error response shares the `Error` schema and lists its codes in `x-veil-error-codes`.
