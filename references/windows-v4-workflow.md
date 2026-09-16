# Windows WeChat 4.x export workflow

Use this reference for a complete export of one known contact from a local, logged-in Windows WeChat/Weixin installation.

## 1. Confirm scope and evidence boundary

Collect these inputs before reading message content:

- contact display name or remark;
- all history or an exact time range;
- whether to include images, voice, video, files, stickers, quoted messages, calls, and system notices;
- preferred readable outputs;
- whether the user authorizes only read access, or also an explicitly approved temporary startup hook.

The user must be authorized to access the local account and conversation. Do not infer authority over another Windows profile, another account, a remote device, or deleted/cloud-only records.

## 2. Discover the actual installation read-only

Use the running executable and file version as the authority; the version remembered by the user may be stale after auto-update.

Inventory without reading message content:

- `Weixin.exe` / `WeChat.exe` processes and executable paths;
- exact file version;
- the current account's `xwechat_files/<account>/db_storage`, `msg`, and `resource` roots;
- database/media file counts and byte sizes;
- legacy `WeChat Files` or phone-backup directories, reported separately from current desktop data.

Do not expose the full account ID in the final report unless necessary.

## 3. Recover the database key: read-only first

Prefer an audited, source-available implementation compatible with the exact installed build. Pin the source revision and inspect it before execution.

For a read-only memory scanner:

- request only `PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`;
- reject code paths using `PROCESS_ALL_ACCESS`, `WriteProcessMemory`, remote allocation, remote threads, or hooks;
- inspect all Weixin processes because 4.x separates functions across processes;
- account for build-specific `Weixin.dll` key masking when the implementation supports it;
- validate every candidate against page 1 of a current encrypted database;
- never log raw candidates or the successful key.

Stop after a bounded attempt. Do not silently switch from memory reading to injection.

## 4. Temporary hook path: explicit approval only

Use this path only after the user explicitly allows a temporary hook. Audit the exact source and binary provenance first. Current public implementations may allocate/write remote memory and create remote threads even when they do not alter chat databases.

Recommended sources to audit, not blindly trust:

- `LifeArchiveProject/WeChatDataAnalysis` for the Windows 4.x export/decryption flow;
- `H3CoF6/py_wx_key` for the native key-capture implementation.

Operational rules:

1. Install only the database-key hook; do not enable image-key hooks unless separately needed and approved.
2. If the database was already open and no key event occurs, remove the hook before deciding what to do next.
3. Ask separately before exiting/restarting WeChat. Warn about unsent drafts and possible phone confirmation.
4. Prefer a normal tray-menu exit. Do not force-kill an interactive WeChat process unless the user explicitly approves and no safer path remains.
5. During startup capture, identify the final main process rather than a short-lived launcher.
6. Validate the captured key against an encrypted message database before storing it.
7. Persist only a DPAPI-protected blob; keep the plaintext key in memory and zero mutable buffers.
8. Always call the hook cleanup routine in `finally`, including on timeout or interruption.
9. Confirm hook removal before copying data.

If WeChat crashes, requests unexpected credentials, or the hook cannot be cleanly removed, stop and report the exact state.

## 5. Create a stable database snapshot

Never decrypt or query the original encrypted database tree in place.

Copy the complete `db_storage` tree, including `-wal`, `-shm`, and journal siblings. Use `scripts/snapshot_db_storage.py`; it compares every source file's size and nanosecond modification time before and after copying and rejects a changing interval.

If a stable live interval cannot be obtained:

- request permission to exit WeChat normally and retry; or
- use an authorized volume snapshot mechanism.

Do not accept a single copied `.db` while ignoring its WAL companions. Record source and snapshot file counts and total bytes.

## 6. Decrypt offline

Use a source-pinned decryptor matching the database format. Keep relative directories to avoid collisions between same-named databases.

Requirements:

- unprotect the DPAPI key only inside the decrypting process;
- never place the key in a command line, log, report, or export;
- write decrypted databases only under a private work directory;
- capture per-database key mode, page failures, HMAC warnings, and SQLite diagnostics;
- fail closed if required message, contact, resource, or hardlink databases do not pass validation.

Some WeChat 4.x databases can emit HMAC warnings while still producing a structurally valid database. Treat `PRAGMA quick_check`/`integrity_check`, schema readability, and targeted row-count sanity checks as the acceptance evidence; do not ignore failed pages or malformed outputs.

Run `scripts/validate_sqlite_tree.py` after decryption.

## 7. Resolve the intended contact

Inspect schemas before writing queries; table and column names change across versions.

Search only plausible identity fields such as remark, nickname, alias, username, and normalized display name. Return the minimum information needed to disambiguate. If more than one contact matches, ask the user to choose; do not dump the address book.

Once confirmed, record the stable internal contact/talker ID and use that ID for all message queries. Never use the display name as the final join key.

## 8. Extract and normalize messages

Discover all message shards, commonly `message_0.db` through `message_N.db`. Query every shard and union records for the stable talker ID.

Normalize at least:

- stable message ID and local sequence;
- timestamp with the local timezone;
- sender direction/name;
- message type and subtype;
- readable text or type-specific summary;
- reply/quote relationship;
- original resource identifiers needed for media resolution;
- source shard and source row identifier for traceability.

Deduplicate by stable message identity, not rendered text. Sort by timestamp, then local sequence/message ID. Keep unknown types as explicit `unknown(type, subtype)` rows instead of dropping them.

Map common types only after verifying the current schema and payload format: text, image, voice, video, file, location, contact card, link/app message, transfer/red packet notice, call notice, sticker, quoted/recalled/system message.

## 9. Resolve media without broad copying

Use message payloads plus resource/hardlink/media databases to find local files. Search only for identifiers referenced by the selected conversation.

- Images may be plain, `.dat`, XOR-obfuscated, or AES-encrypted; prefer keys derived locally from account configuration when available.
- Voice is often Silk and may need offline decoding to a widely playable format.
- Videos and files are usually copied as-is after hash verification.
- Preserve the original filename when safe; sanitize traversal characters and resolve collisions deterministically.
- Do not download expired CDN media unless the user separately authorizes network access.

For every media message, record `resolved`, `missing`, `expired`, `decode_failed`, or `unsupported`, plus the local relative path when available.

## 10. Produce readable outputs

### HTML

Generate a local archive that works without a server or internet connection. Use relative asset links, lazy-load large images, provide audio/video controls, show file links and hashes, and visibly label missing media. For very large chats, paginate by month/year or use a lightweight local index instead of one enormous DOM.

### Excel

Use the spreadsheet skill and its required artifact workflow. Suggested columns:

`序号, 时间, 发送者, 方向, 类型, 正文或摘要, 媒体相对路径, 媒体状态, 消息ID, 来源分片`

Keep the sheet filterable and frozen at the header. Put aggregate counts and date range on a summary sheet. Do not embed gigabytes of media in the workbook.

### Manifest

Write a JSON manifest with:

- exact WeChat version and export time;
- selected contact display name and internal ID (the latter may be hashed in the user-facing copy);
- total messages, earliest/latest timestamp, counts by type/direction/year;
- resolved/missing media counts by category;
- output file hashes and sizes;
- known limitations and snapshot consistency evidence.

## 11. Verify before delivery

Require all applicable checks:

- snapshot inventory was stable and complete;
- required decrypted databases passed SQLite validation;
- contact match was unique or user-confirmed;
- all message shards were queried;
- no duplicate stable message IDs remain;
- first/last timestamps and type totals are plausible;
- HTML opens locally and every relative link is checked;
- Excel inspection shows the expected sheets, filters, rows, date cells, and no formula errors;
- media files exist, have non-zero size, and are playable/readable where decoding was claimed;
- user-facing outputs contain only the selected conversation and referenced media.

Do not claim completeness when WAL content was omitted, a shard failed, or media resolution is partial. Quantify gaps.

## 12. Restore state and clean up

Restore WeChat to its prior running/logged-in state when practical, and report if it remains headless, logged out, or awaiting confirmation.

After the user-facing outputs are verified:

- remove the DPAPI-protected temporary key and zero in-memory buffers;
- keep decrypted databases and snapshots in the private work area until delivery is accepted or the user approves deletion;
- never place decrypted databases, other contacts' content, or key material in the output folder;
- state exactly what sensitive temporary data remains and where.

## Stop conditions

Stop and ask for direction when:

- the account/contact match is ambiguous;
- the exact build is unsupported;
- a tool's behavior differs materially from its audited source;
- a supposedly read-only path requires injection;
- hook cleanup cannot be confirmed;
- a stable snapshot cannot be obtained;
- required databases fail integrity checks;
- completion requires logout, credential entry, network download, or another scope expansion not yet approved.
