# Sign in with Veil

Read this when an app lets people sign in with their Veil card. Sources: the [sign-in guide](https://veil.pub/docs/sign-in-with-veil), which holds two complete examples, the discovery document and the per-endpoint entries (`python scripts/veil.py doc oidc-token`).

Sign in with Veil is OpenID Connect. Any maintained OIDC library works against it. What it adds is a proof the app can check on its own: the person's device key signs each login, and the public log says that key is on the card. An app that runs the checks in "Veil's own checks" does not have to take the server's word for who signed in. An app that stops at the standard checks trusts Veil's server the way it would trust any other provider.

## The provider

| Item | Value |
|---|---|
| Issuer | `https://veil.pub` |
| Discovery | `GET https://veil.pub/.well-known/openid-configuration` |
| Authorization | `GET /oidc/authorize` |
| Token | `POST /oidc/token` |
| UserInfo | `GET` or `POST /oidc/userinfo` |
| Keys | `GET /oidc/jwks` |
| Registration | `POST /oidc/register` (RFC 7591) |
| Revocation | `POST /oidc/revoke` (RFC 7009) |
| Introspection | `POST /oidc/introspect` (RFC 7662), confidential apps only |
| Logout | `GET /oidc/logout` (RP-initiated) |

- Authorization code flow only, with the answer in the query. There is no implicit or hybrid flow.
- PKCE with `S256` is required for every app, confidential ones included.
- Every authorization answer carries `iss` (RFC 9207). Compare it with the issuer.
- ID tokens are signed with `EdDSA` by default, or `ES256` when the app asks for it.
- An app authenticates with `client_secret_basic`, `private_key_jwt` or `none` (a public app).
- Request objects, `request_uri` and the `claims` parameter are not supported. Neither is front-channel or back-channel logout.
- Only discovery and the keys answer cross-origin. A browser app needs a backend for the token call, or runs as a public app from its own origin through a redirect.
- API keys play no part under `/oidc/`. An `Authorization` header there is the app's or the person's own credential.

Read the endpoints from discovery and never hard-code them.

## Register an app

**From a card (preferred).** Open [veil.pub/developers](https://veil.pub/developers) and add the app. A person registers for their own card and an organisation through an accepted owner. A card holds at most 20 apps. The client id is `veil_app_` and 32 hex characters. A confidential app with `client_secret_basic` gets a secret, `veil_secret_…`, shown once. The consent page calls the app verified when the card proves the domain of the app's site and of every https redirect URI.

The same thing over the API is a device-signed call: `POST /v1/developer/accounts/{n}/oidc-clients` answers `201` with `{client, secret}`. `GET` on the same path lists the apps, `PATCH /{id}` changes the name, the site, the redirect and logout URIs, the ID token algorithm and the logo, `DELETE /{id}` ends the app and its tokens, and `POST /{id}/secret` issues a new secret while the old one stops at once. The type and the authentication method cannot change.

**Without a card.** `POST /oidc/register` takes RFC 7591 metadata and answers `201` with `client_id` and, for `client_secret_basic`, `client_secret` once. Such an app is never verified and ends 30 days after registration (`veil_expires_at`). The limit is ten registrations an hour per IP.

```bash
curl -fsS --json '{"client_name":"CLI notes","redirect_uris":["http://127.0.0.1/callback"],"token_endpoint_auth_method":"none"}' \
  'https://veil.pub/oidc/register'
```

Redirect URIs are exact https addresses, without a fragment or user information. `http` is accepted only on the loopback interface, for native apps. A loopback redirect matches on any port and always shows the consent page.

## The authorization request

| Parameter | Rule |
|---|---|
| `response_type` | `code` |
| `client_id`, `redirect_uri` | As registered. The redirect URI matches exactly |
| `scope` | Space separated, with `openid` |
| `code_challenge`, `code_challenge_method` | The 43-character S256 challenge and `S256` |
| `state` | At most 1024 characters. Required for the consent check below |
| `nonce` | At most 512 characters |
| `prompt` | `none`, `login`, `consent` or `select_account` |
| `max_age` | `0` asks for a fresh signature, like `prompt=login` |
| `ui_locales` | `it` shows the consent page in Italian |

The server keeps the request for 30 minutes and shows the consent page on `veil.pub`. The person's browser signs the consent with a device key of their card. There is no password and no session cookie that could stand in for the key. A card that already approved the app for the same scopes signs without a click.

## Scopes and claims

| Scope | Claims |
|---|---|
| `openid` | `sub`, `auth_time`, `amr`, `sid` |
| `profile` | `name`, `picture`, `preferred_username`, `profile` |
| `veil` | `veil_version`, `veil_log`, `veil_good_standing`, `veil_standing_reasons`, and `veil_consent` in the ID token |
| `veil:accounts` | `veil_accounts`: `[{platform, id, handle, url, verified_at}]` |
| `veil:orgs` | `veil_orgs`: `[{n, name, role}]` |
| `veil:keys` | `veil_keys`: `{devices, external}` |

- `sub` is the card number as a string. It never changes hands silently: a takeover is public and takes 7 days. Identify the person by `sub` and never by `name`, `preferred_username` or a linked account's handle.
- `amr` is `["veil-key"]`.
- `veil_log` is `{origin, index, size, root}`: the log entry of the card version at login and the checkpoint the server read.
- `veil_good_standing` is false when `veil_standing_reasons` has any of `suspended`, `closing`, `takeover`, `name_hidden`, `key_revoked` or `key_banned`.
- `veil_consent` is `{text, signature, key, alg}`: the text the device key signed for this login.
- `veil_accounts` lists the accounts the card proved. `id` is the platform's stable subject, which is the value to store.

## Tokens

| Token | Form | Life |
|---|---|---|
| Authorization code | Opaque | 10 minutes, single use |
| Access token | `veil_at_…` | 10 minutes |
| Refresh token | `veil_rt_…` | 30 days, rotated at every use, at most 90 days after the login |
| ID token | JWT with `kid` | 10 minutes |

`POST /oidc/token` takes a form (`application/x-www-form-urlencoded`, at most 16 KiB, each parameter once) with `grant_type=authorization_code`, `code`, `redirect_uri` and `code_verifier`, or `grant_type=refresh_token` with `refresh_token`. The answer is `{access_token, token_type: "Bearer", expires_in: 600, refresh_token?, id_token, scope}`.

```bash
curl -fsS -u "$CLIENT_ID:$CLIENT_SECRET" \
  -d grant_type=authorization_code -d code="$CODE" -d code_verifier="$VERIFIER" \
  --data-urlencode redirect_uri=https://app.example.org/callback "https://veil.pub/oidc/token"
```

A code or a refresh token used twice ends every token of its login. The server keeps tokens only as hashes. The signing keys rotate with a 30-day overlap, and `kid` is the RFC 7638 thumbprint, so read `/oidc/jwks` again when a `kid` is unknown.

UserInfo answers from the card as it is now. A revoked key, an open takeover or a suspension changes the answer at once, and a suspended card answers `401 veil_suspended`. Ask it again before anything that matters instead of trusting an old ID token.

## Standard checks

1. On the callback, compare `state` with the session's and `iss` with the issuer. Stop on `error`.
2. Exchange the code with the PKCE verifier.
3. Verify the ID token's signature with the key its `kid` names, using that key's own algorithm and never the header's choice. In `openid-client` 6 turn on `enableNonRepudiationChecks`.
4. Check `iss`, `aud`, `azp` when present, `exp`, `iat` and `nonce`.

## Veil's own checks

These need the `veil` scope. They are what makes a login provable.

1. `veil_consent.alg` is `ed25519` and `veil_consent.text` starts with `veil-rubrica:oidc-consent:v1\n`. The rest is canonical JSON with `v`, `iss`, `card`, `key`, `client`, `redirect`, `scopes`, `nonce`, `state`, `challenge`, `request` and `time`.
2. Verify `veil_consent.signature` (hex) over the UTF-8 bytes of `text` with `veil_consent.key` (hex Ed25519).
3. The consent is for this login: `challenge` equals the S256 challenge of your verifier, `state` is the SHA-256 of your `state` in hex, `nonce` and `client` are yours, `iss` is the issuer, `key` equals `veil_consent.key` and `card` equals `sub`.
4. `GET /v1/keys/{key}` names the card and the version that added the key (`addedIn`), with role `device`. `GET /v1/identities/{sub}` gives the card's `token` and current `version`. `veil_version` lies between the two.
5. For each version from `addedIn` to the current one, read `GET /v1/identities/{sub}/versions/{v}/proof`. The entry's label names the card's token and version `v`, and its `prev` is the label hash of the version before. The RFC 6962 inclusion proof leads to the checkpoint root. The checkpoint note carries the log's signature and the witness quorum of the policy you pinned (`https://log.veil.pub/staging-1/policy`), names the origin in `veil_log` and is not smaller than `veil_log.size`.
6. The label at `addedIn` adds the key with `{"op":"addKey","role":"device"}` and no later label revokes it. The proof of `veil_version` sits at `veil_log.index`.

Steps 4 to 6 take one request per version since the key was added, so cache what you verified per card and continue from there. The sign-in guide has this whole sequence in Node and in Python, and Veil's conformance test runs both examples.

## What the person sees and controls

`GET /v1/identities/{n}/oidc-apps`, signed by the card, lists the apps the card signed in to with the last five logins of each and the consent its key signed. `POST /v1/identities/{n}/oidc-apps/{client}/revoke` makes an app forget the consent and ends its tokens. `GET /oidc/logout` with `id_token_hint` ends the tokens of that login and sends the browser back only to a post-logout address the app registered exactly.

## Errors and limits

Endpoints under `/oidc/` answer errors in the OAuth shape, `{"error": "...", "error_description": "..."}` with `Cache-Control: no-store`, and not in the `error` object of the rest of the API. A rate limit still answers 429 with the usual envelope and `Retry-After`.

| Where | Error | Meaning |
|---|---|---|
| Callback | `access_denied` | The person refused |
| Callback | `login_required`, `consent_required` | `prompt=none` could not answer without the person |
| Token | `invalid_grant` | The code or refresh token is invalid, expired, used, revoked or another app's, or the verifier does not match. Start again and never retry a code |
| Token | `invalid_client` | The app did not authenticate with the method it registered |
| Token | `invalid_scope` | A refresh asked for more than the login granted, or left out `openid` |
| Registration | `invalid_redirect_uri`, `invalid_client_metadata` | Read `error_description` and fix that field |
| Registration | `temporarily_unavailable` | Too many apps without a card right now. Register from a card |
| UserInfo | `invalid_token`, `veil_suspended` | Refresh or sign in again. A suspended card gets no claims |

Limits: 1200 requests a minute per IP on the back channel, 600 a minute per app and 60 authorization requests a minute per IP.
