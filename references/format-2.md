# Log format 2

Read this when you verify a card in your own code, or when you parse `current`, `authority`, `state` or `index` from a card. The checks below are the ones Veil's own pages run in the reader's browser. Their code is public at `https://veil.rip/assets/veil-v2.js` and `https://veil.rip/assets/veil-index-rules.js`, and it is the reference when this page and your results disagree.

## Which format is live

Since 28 October 2026 veil.rip publishes to the log `log.veil.rip/staging-1` in format 2. `GET /v1/log` says so:

```json
{"origin": "log.veil.rip/staging-1", "format": 2, "staffOrg": "d8aKGsTCN1U_lB3NznVocg", "quorum": 2, "of": 5, "...": "..."}
```

A missing `format` means format 1. `staffOrg` is the token of the Veil organisation (card 2). It is a parameter of the log's index and stays the same for the life of the log. Take the format from the log, never from a card alone. Veil's pages fail a format 1 card served under a format 2 log (`format_mismatch`) and refuse a format 2 log whose `GET /v1/log` has no `staffOrg` (`wrong_format`).

The cards were recreated on the new log. Card 1 (Gabriele Todaro, a person) and card 2 (the Veil organisation) kept their numbers, but their IDs, tokens and 12-word fingerprints are new. An ID or fingerprint stored for these numbers before 28 October 2026 will not match the current card. The earlier log, `log.veil.rip/test-1`, is in format 1 and frozen.

## What stays the same

- Checkpoints are C2SP signed notes. Verify the log signature with the key you pinned, count each witness key once against the policy quorum, and judge freshness by the quorum-th newest valid cosignature (15 minutes).
- Log leaves are RFC 6962: `SHA-256(0x00 || entry bytes)`, with inclusion proofs in hex, deepest sibling first. The log host still serves C2SP tiles.
- Signed write requests keep `veil-rubrica:request:v1`, the same headers, `nonce` and `timestamp`.
- Canonical JSON keeps its rules: object keys sorted by UTF-16 code units, no whitespace outside strings, integers in the JavaScript safe range, UTF-8 strings.
- Ed25519 keys and signatures are hex. Composite ML-DSA-65 + Ed25519 keys and signatures are base64, and both halves must verify.
- `GET /v1/lookup`, `/v1/identities/{n}/summary`, `/v1/keys/{key}`, `/v1/keys/{key}/active-at`, `POST /v1/verify`, signature blocks and verify links answer as before.
- A card keeps its presentation fields (`n`, `url`, `name`, `initials`, `since`, `id`, `idSalt`, `token`, `version`, `type`, `keys`, `links`, `orgs`, `members`, `events`, `fingerprint`, `badges`, `moderation`, `alias`, `aliasUrl` and the rest). `id` is still the hex hash of version 1, and the 12 words and 60 digits come from it in the same way.
- The error envelope, card numbers and alias rules do not change.

## What changed for verifiers

| Item | Format 1 | Format 2 |
|---|---|---|
| A version | One record with the full key and link history | A label (authority operations and hashes) and a body (the other operations and a salt) |
| Signed bytes of a version | `veil-rubrica:identity-version:v1\n` + canonical record | `veil-rubrica:identity-version:v2\n` + canonical label |
| `id` | `SHA-256(salt \|\| record)` of version 1, hex | `SHA-256("veil-rubrica:label:v2\n" \|\| label)` of version 1, hex |
| Log entry of a version | `{"c","n","token","v":1}`, a commitment | `{"key","label","signature","v":2}`, the signed label itself |
| Staff statements | A salted commitment `{"c","kind","org","v":1}`, with the action and target taken from the server's response | Signed entries with the action type, expiry, target, signer and the position of the previous statement |
| Closing of a card | Known from the server's 410 receipt | A signed closing entry that the reader checks |
| Index | None | `{"kind":"index","root","size","v":2}` entries written by the log |
| Card `proof` | `record`, `salt`, `commitment`, `signedBy`, `signature`, then entry, inclusion and checkpoint | `version`, `labelHash`, `entry`, `logIndex`, `leafHash`, `checkpoint`, `inclusion`, `witnesses` |
| Extra card fields | None | `format`, `current`, `authority`, `authorityNext`, `state`, `index`, `standing` |
| Moderation shown | `moderation` as the server reports it | Computed from the verified chain in `index.statements` |
| First visit | Reads and checks every version | Reads the card's index bundle, so the work does not grow with the history |

`v` is the integer 2 in labels, bodies and entries. A reader rejects `2.0`. Every number in a label or entry (`n`, `time`, `until`, `size`, `signer.n` and a statement's `prev`) is an integer from 0 to 2^53 - 1, with `n` and `signer.n` starting at 1. Labels and entries are canonical JSON with no extra fields, and the index ignores an entry in any other shape.

## Hashes and encodings

Every hash is SHA-256 over a domain prefix and the bytes below. Hashes inside labels, bodies, index values and proofs of sets are standard base64 with padding (44 characters). `id`, `proof.leafHash` and RFC 6962 inclusion hashes are hex.

| Use | Bytes |
|---|---|
| Label hash (`c`, `proof.labelHash`, the next label's `prev`, `id` in hex) | `"veil-rubrica:label:v2\n"` + label |
| Body hash (`label.body`) | `"veil-rubrica:body:v2\n"` + body |
| Version signature | `"veil-rubrica:identity-version:v2\n"` + label |
| Statement signature | `"veil-rubrica:statement-entry:v2\n"` + canonical entry without `signature` |
| Closing signature | `"veil-rubrica:close-entry:v2\n"` + canonical entry without `signature` |
| State head hash | `"veil-rubrica:state-head:v2\n"` + canonical `state.head` |
| State root (`label.state`) | `"veil-rubrica:state:v2\n"` + the 32-byte body `salt` + state head hash + the roots of `keys`, `links`, `orgs` and `members`, in that order |
| Position of a set item | `"veil-rubrica:set-key:v2\n"` + set name + `"\n"` + item key |
| Leaf of a set item | `0x00` + `"veil-rubrica:item:v2\n"` + canonical item |
| Position in the index | `"veil-rubrica:index-key:v2\n"` + card token |
| Leaf of the index | `0x00` + `"veil-rubrica:index-leaf:v2\n"` + canonical index value |
| Tree node | `0x01` + left + right |
| Empty leaf `E0` | `"veil-rubrica:empty:v2"`, with no newline. `E(h+1)` is the node of two `E(h)` |

The item key is the public key for `keys`, the platform and the subject joined by a newline for `links`, the organisation token for `orgs` and the member token for `members`. An empty set has the root `0iTvZb61d0+WGpOq5FlPLH3fZhujnMR7aFF0k80vNvA=`.

The salt in the state root keeps names and device names out of reach of anyone who only reads the public entry. When a card is erased, the body and its salt are deleted and the entry reveals nothing more.

## Sparse Merkle proofs

The four sets of a card's state and the index are sparse Merkle trees of depth 256.

- A position is 32 bytes. Bit `k`, from 0 to 255, is `(p[k / 8] >> (7 - k % 8)) & 1`, so bit 0 is the most significant bit of the first byte.
- Leaves sit at height 0 and the root at height 256. Going from height `h` to `h + 1`, the current node is the left child when bit `255 - h` of the position is 0, and the right child when it is 1.
- A proof is `{"bitmap": "<32 bytes, base64>", "siblings": ["<32 bytes, base64>", ...]}`. Bit `h` of the bitmap, read with the same bit rule, is 1 when the sibling at height `h` is not the empty `E(h)`. `siblings` lists only those, by increasing height.
- To verify, start from the leaf, or from `E0` to prove that a position is empty. For each height from 0 to 255 take the next sibling when the bitmap bit is 1, otherwise `E(h)`. The result must be the root and every sibling must be used.
- A page holds the items whose position starts with the same `bits` bits (`prefix` is those bits in base64, zero padded). Compute the subtree root at height `256 - bits` from the page items alone, then climb with the page proof. With `bits` 0 the page is the whole set and the proof is empty.

## The card JSON in format 2

`GET /u/{card}.json`, `/o/{card}.json`, `/v1/identities/{n}` and `/v1/organizations/{n}` add these fields.

| Field | Contents |
|---|---|
| `format` | `2` |
| `current` | The current version: `label` and `body` as canonical texts (the exact signed bytes, never re-serialise them), `signature`, `signedBy`, `logIndex`, `publishedAt` and `entry`, the log entry text |
| `authority` | The versions with a non-empty `auth` list, from version 1, at most 50. Each has the fields of `current` plus `i`, its log position, and `inclusion`, its RFC 6962 proof on the checkpoint of `index` |
| `authorityNext` | The version to pass as `after` to `GET /v1/identities/{n}/authority`, or `null` when `authority` is complete |
| `state` | The state after the current version: `head` (`alias`, `name`, `picture`, `type`), the whole `keys`, `links` and `orgs` sets, the first page of `members` (`prefix`, `bits`, `items`, `proof`, `pages`) and `roots` |
| `proof` | `version`, `labelHash` (base64), `entry`, `logIndex`, `leafHash` (hex), `checkpoint` (`size`, `root`, `note`), `inclusion` (hex) and `witnesses` |
| `index` | The card's index bundle on the same checkpoint as `proof`, or `null` when the server could not read or check it |
| `standing` | The log position of the card's latest staff statement as the server knows it, or `null`. The verified value is `index.value.standing` |

The index bundle:

```json
{"checkpoint": {"note": "<signed note with cosignatures>", "size": 4},
 "entry": {"i": 3, "entry": "{\"kind\":\"index\",\"root\":\"/ON4Oe5wuDI820ZuBEtu4AnlCEXDb2Ro+9tkxgvBkxg=\",\"size\":3,\"v\":2}", "inclusion": ["f67b512b...", "625fc3bf..."]},
 "value": {"auth": [[0, 1, "QGxgThvN4ptiKp4aZ2XaWjys6Pl3i0MnaC8x4+NIKc0="]], "closed": null, "latest": [0, 1, "QGxgThvN4ptiKp4aZ2XaWjys6Pl3i0MnaC8x4+NIKc0="], "standing": null},
 "proof": {"bitmap": "...", "siblings": ["..."]},
 "tail": [],
 "statements": [],
 "statementsNext": null}
```

These are card 1's values while the log had 4 entries. `entry` is the last index entry of the checkpoint, at position `i`, covering the entries before its `size`. `value` is `{"auth": [[i, n, c], ...], "closed": i | null, "latest": [i, n, c], "standing": i | null}`, where `i` is a log position, `n` a version number and `c` a label hash. `value` is `null` when the card is not in the index. `tail` lists every entry after the index entry up to the end of the checkpoint, each as `{i, entry, inclusion}`. `statements` is the first page of the card's staff statements, newest first, each as `{i, entry, inclusion, by}`, where `by` is only a hint at the signer's card number. It is `[]` without statements and `null` when the server could not read or prove the chain. `statementsNext` is the path of the next page, or `null`.

`proof.checkpoint` and `index.checkpoint` describe the same tree size and root. Their cosignature lines can come in a different order.

## Check the hashes of card 1

Version 1 of card 1 never changes, so it is a stable test vector:

```python
import base64, hashlib, json, urllib.request

card = json.load(urllib.request.urlopen("https://veil.rip/u/1.json"))
v1 = card["authority"][0]
label = v1["label"].encode()
assert hashlib.sha256(b"veil-rubrica:label:v2\n" + label).hexdigest() == card["id"]
# 406c604e1bcde29b622a9e1a6765da5a3cace8f9778b4327682f31e3e34829cd

body = v1["body"].encode()
body_hash = hashlib.sha256(b"veil-rubrica:body:v2\n" + body).digest()
assert base64.b64encode(body_hash).decode() == json.loads(v1["label"])["body"]

leaf = hashlib.sha256(b"\x00" + v1["entry"].encode()).hexdigest()
# the RFC 6962 leaf at position v1["i"], proven by v1["inclusion"]
```

The signature is Ed25519 by `73ad6159583a43f8ad230a215b758db680efcd3ce32ab8e83c622eeca883e68a` over `b"veil-rubrica:identity-version:v2\n" + label`.

## Verify a card

The index path below is what a first visit runs. Its cost does not depend on how many versions the card has.

1. Read `GET /v1/log` and require `format: 2` and `staffOrg`. Pin the log origin, its key and the witness policy (`https://log.veil.rip/staging-1/policy`) in your own configuration. Verify `index.checkpoint.note` with the log key and the witness quorum, and check freshness.
2. Check the RFC 6962 inclusion of `index.entry.entry` at `index.entry.i` in the checkpoint tree. The entry must be `{"kind":"index","root","size","v":2}`. Check each `tail` item the same way. The tail must cover every position from `index.entry.i + 1` to `checkpoint.size - 1`. Refuse a tail longer than 4096 entries (Veil's pages call this `index_stale`).
3. Fold `index.value` at the index position of the card's `token` with `index.proof`. The result must equal the root in the index entry. Then apply the tail entries about this card with the index rules below. A tail entry that the rules would ignore because of its signature fails the card instead of changing it.
4. For each `[i, n, c]` in `value.auth`, take the `authority` item at that `i`. Its entry must be included at `i`, and its label must hash to `c` and carry version `n`. For a person, the signature must verify with the entry's `key`, which must be active in the authority before that version, and version 1 is signed by the key its `auth` adds. An organisation's signers are checked in step 6. Apply the `auth` operations in order. The label hash of version 1, in hex, is `id`. Read further authority versions with `authorityNext` when it is not `null`.
5. Check the current version. Its label hashes to `value.latest[2]` and has version `value.latest[1]`. `proof.entry` is at `value.latest[0]`, which equals `proof.logIndex`, and `proof.leafHash` with `proof.inclusion` leads to the checkpoint root. For a person, the signature verifies with a key of the authority in force. The body hashes to `label.body`. Recompute the set roots from `state` and compare them with `state.roots`, then recompute the state root with the body salt and compare it with `label.state`. For a person, `state.keys` must hold exactly the keys of the authority you rebuilt. For an organisation, the owners and administrators in `members` must match its authority.
6. For an organisation, check the signer of every authority version and of the current one. `label.signer.identity` must have the required role in the authority rebuilt from the earlier versions, and the signing key must be active on the signer's own card at that log position. Read the signer's card for its index bundle on the same checkpoint and its authority versions below that position. `signer.n` is only a hint. For members, check the first page that comes with the card and a path (`GET /v1/identities/{n}/sets/members/path?key=<token>`) for each owner and administrator of the authority. Read other pages when you need them. No page may hold an owner or administrator that the authority lacks.
7. Check moderation from the signed statements. The first item of `index.statements` sits at `value.standing`, each `prev` is the `i` of the next item, and the last `prev` is `null`. Each entry is a statement of the Veil organisation (`org` equals `staffOrg`) about this card (`target` equals its token), and none comes after a closing. Verify each signature with its `key`, which must be active for `signer.identity` at position `i`, and check that the signer's role in the Veil organisation at that position allows `action.type`. Follow `statementsNext` until it is `null`.
8. For a closed card (HTTP 410), check `closed` as described under "Closings".

Report the card as in good standing only when every step holds. You can show the card before that. When `index` is `null`, `index.statements` is `null` or `proof` is `null`, the status is unknown, which is different from a failed check.

From the verified statements, compute what is in force:

- `ban_identity` lasts until `unban_identity`.
- `ban_identity_temporary` lasts until its `until` or an `unban_identity`, and does not replace a permanent ban.
- `ban_key` lasts until `unban_key` of the same key.
- `hide_name` and `hide_logo` last until `unhide_name` and `unhide_logo`.
- A badge lasts until `remove_badge` or its `until`.

The derived badges (`staff` and `official`) come from the verified state of the Veil organisation. A statement's category, reason and evidence stay private inside its commitment `c`, so the public part gives the action type, its expiry and who signed it.

Keep an anchor per card token: the ID, the last verified version and its label hash, and the authority at that point. On a later visit, refuse an index that points to an older version or to authority versions that differ from the ones you verified. If another token or another ID shows up under a number you know, treat it as a failure (`anchor`) and keep the old anchor.

The full check reads every version with `GET /v1/identities/{n}/versions` and verifies each body hash, each signature against the authority before it, each operation and the `prev` chain of label hashes. Card owners' devices run it on their own card.

## Log entries

| Kind | Entry |
|---|---|
| Version | `{"key","label","signature","v":2}` |
| Staff statement | `{"action":{"type","until"[,"key"][,"badge"]},"c","key","kind":"moderation"\|"badge","org","prev","signer":{"identity","n"},"target","time","v":2,"signature"}` |
| Closing | `{"key","kind":"closed","latest","signer":{"identity","n"},"time","token","v":2,"signature"}` |
| Index | `{"kind":"index","root","size","v":2}` |

In a version entry `key` is outside the signed label. The index checks the signature with that key only, so it must be active for the signer and written exactly as in the authority. In statements and closings `key` is inside the signed part.

A statement's `action.type` is one of `ban_identity`, `ban_identity_temporary`, `unban_identity`, `ban_key`, `unban_key`, `hide_name`, `unhide_name`, `hide_logo`, `unhide_logo`, `remove_profile`, `erase_for_user`, `cancel_erasure`, `assign_badge` and `remove_badge`. `until` is an integer only for `ban_identity_temporary` and `null` otherwise. `action.key` appears only for `ban_key` and `unban_key`, `action.badge` only for the two badge actions, and `kind` is `badge` exactly for those. `prev` is the position of the previous counted statement about the same card, or `null` for the first. `c` is the standard base64 of `SHA-256(salt || canonical statement)`, which stays private.

## Index rules

These rules are the same in the log server, the directory and the browser. They decide only who can sign. Other product rules, such as keeping one owner or the daily limits, stay with the directory server.

- A person's authority is the set of active keys, each with its `alg`. `addKey` adds a key that is not active, with role `device` or `recovery`. `revokeKey` removes an active key. Any other operation in `auth` voids the version. At most 64 keys can be active at once.
- An organisation's authority is its members with role `owner` or `admin`. In the Veil organisation every `invite`, `role` and `remove` counts, with any staff role (`owner`, `admin`, `moderator`, `support`), so its public state shows the whole staff. At most 1024 members can be in an authority.
- In an organisation only an `owner` invites an `owner`. An `owner` or `admin` invites other roles. Only an `owner` changes a role. Only an `owner` removes an `owner`, and an `owner` or `admin` removes the others. Rights come from the signer's role before the version. A version with an empty `auth` still needs an `owner` or `admin` signer.
- Version 1 of an organisation has exactly `[{"member": <signer.identity>, "op": "invite", "role": "owner"}]` in `auth` and is signed by an active key of that founder.
- A label with `signer` belongs to an organisation and one without belongs to a person. Version 1 fixes the type.
- Each signer is a person present in the index and not closed.
- A statement counts when its signer belongs to the Veil organisation with a role that allows `action.type`, and its `prev` equals the card's current standing. `ban_identity`, `unban_identity`, `ban_key`, `unban_key` and `remove_profile` need `owner` or `admin`. `ban_identity_temporary`, `hide_name`, `unhide_name`, `hide_logo` and `unhide_logo` also allow `moderator`. `erase_for_user` and `cancel_erasure` allow `owner`, `admin` and `support`. `assign_badge` and `remove_badge` allow all four roles.
- `ban_identity_temporary` counts only when `time < until` and `until` is at most 30 days (2,592,000 seconds) after `time`.
- On cards that belong to the Veil organisation at that point, a staff statement or closing counts only when the signer's rank is higher than the target's (`owner` 4, `admin` 3, `moderator` 2, `support` 1) or the signer is an `owner`.
- Nothing counts for a card after its closing, and a card that is not in the log receives no statements.

## Closings

A closed card answers HTTP 410 with the erasure receipt and, in format 2, `closed`, `format`, `id`, `type`, `token`, `n`, `index` and `authority`. Erasure deleted labels and bodies from the database, so each `authority` item takes `label` and `signature` from its log entry and has an empty `body`.

`closed` is `{"i", "entry", "inclusion", "signerN"}`. The entry must be included at `value.closed` and name this card's `token`. Its `latest` must be the label hash of the last counted version, so any version published after the closing was signed voids it. The signature must come from an active key of the card itself for a person, from an `owner` of the organisation with an active key of their own card, or from a staff member whose role allows `remove_profile` or `erase_for_user`. Only an `owner` of the Veil organisation can close it. `signerN` is a hint at the signer's card number: use it only when that card's token matches `signer.identity`. A closing that does not verify closes nothing.

## On the log host

The log serves `GET https://log.veil.rip/staging-1/index`, which returns `{"entry", "root", "size", "staffOrg"}` for its latest index entry, and `GET https://log.veil.rip/staging-1/index/<token>`, the index bundle of one card on the latest published checkpoint. A verifier can take the Veil organisation token from there and require `GET /v1/log` to name the same one.

## What the log shows

For each card the log shows the public keys with their roles and algorithms, version times, who signs an organisation's versions, its owners and administrators (the whole staff for the Veil organisation), and the type, expiry and signer of each staff action. Names, device names, linked accounts, pictures and moderation reasons stay out of the log.
