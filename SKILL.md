---
name: wechat-chat-export-windows
description: Safely export one contact's readable WeChat 4.x chat history and referenced media from a logged-in Windows PC. Use for local Weixin/WeChat database discovery, read-only-first key recovery, explicitly approved temporary hook capture, stable snapshots, offline decryption, contact-scoped extraction, HTML/Excel delivery, and completeness verification. Do not use for remote accounts, credential recovery, surveillance, or exporting conversations the user is not authorized to access.
---

# Windows WeChat chat export

Export only data from the user's own logged-in Windows account and keep the original WeChat data tree unchanged.

Before touching a process or database, record the target display name, time range, requested media types, and output formats. Treat display names as selectors, not stable IDs.

## Required authorization gates

- Begin with read-only discovery and read-only key recovery.
- Memory scanning may request only process query/read rights.
- Do not install a hook, write process memory, inject a thread, restart/exit WeChat, or change login state without explicit approval for that action.
- Approval for a temporary hook does not imply approval to restart WeChat. Ask separately if startup capture becomes necessary.
- Never print or persist a plaintext database key. Protect it with Windows DPAPI, use it only in memory, and remove the temporary protected blob after verified delivery.
- Do not send messages, open remote links, upload chat data, or use cloud conversion services.

## Workflow

Read [references/windows-v4-workflow.md](references/windows-v4-workflow.md) before performing an export. Follow its decision tree, stop conditions, and verification checklist.

Use [scripts/snapshot_db_storage.py](scripts/snapshot_db_storage.py) when copying a live `db_storage` tree. Accept the copy only when the complete source inventory is unchanged across the copy interval.

Use [scripts/validate_sqlite_tree.py](scripts/validate_sqlite_tree.py) after offline decryption. Do not extract contact or message content until all required databases pass SQLite checks.

## Deliverables

Default to:

- a local HTML archive with an adjacent assets directory;
- an Excel message index when the spreadsheet skill is available;
- a machine-readable manifest containing counts, date range, type counts, media resolved/missing counts, source version, and file hashes.

Copy only media referenced by the selected conversation. Keep decrypted databases and other contacts' data out of the deliverables.

Report what was exported, what could not be resolved, how completeness was checked, whether WeChat was restored to its prior running state, and which sensitive temporary files remain.
