# MCP Auto-Sync Specification

## Overview

This spec defines automatic vdirsyncer sync behavior after MCP write operations, with graceful failure handling and timeout protection.

---

### Requirement: Auto-sync after mutations

The MCP server MUST automatically run `vdirsyncer sync` after any successful local write operation (create, update, delete). The sync SHALL be non-blocking to the mutation result — a local write that succeeds MUST be reported as successful regardless of sync outcome.

#### Scenario: Successful sync after create event

- **WHEN** `create_event` writes a new `.ics` file successfully
- **THEN** the server runs `vdirsyncer sync`
- **AND** the response includes `_sync: {"success": true}`
- **AND** the `_note` field is no longer present

#### Scenario: Successful sync after create contact

- **WHEN** `create_contact` writes a new `.vcf` file successfully
- **THEN** the server runs `vdirsyncer sync`
- **AND** the response includes `_sync: {"success": true}`

#### Scenario: Successful sync after update contact

- **WHEN** `update_contact` modifies a `.vcf` file successfully
- **THEN** the server runs `vdirsyncer sync`
- **AND** the response includes `_sync: {"success": true}`

#### Scenario: Successful sync after delete contact

- **WHEN** `delete_contact` removes a `.vcf` file successfully
- **THEN** the server runs `vdirsyncer sync`
- **AND** the response includes `_sync: {"success": true}`

---

### Requirement: Graceful sync failure

When `vdirsyncer sync` fails, the MCP server MUST still return the local mutation as successful and report the sync failure in a structured `_sync` field.

#### Scenario: Network failure during sync

- **WHEN** a mutation succeeds locally
- **AND** `vdirsyncer sync` fails due to network error
- **THEN** the response reports the local mutation as successful
- **AND** the response includes `_sync: {"success": false, "error": "<error message>"}`

#### Scenario: Auth expired during sync

- **WHEN** a mutation succeeds locally
- **AND** `vdirsyncer sync` fails due to authentication error
- **THEN** the response reports the local mutation as successful
- **AND** the `_sync.error` field contains the authentication error message

#### Scenario: vdirsyncer not found

- **WHEN** a mutation succeeds locally
- **AND** `vdirsyncer` is not on PATH
- **THEN** the response reports the local mutation as successful
- **AND** the response includes `_sync: {"success": false, "error": "vdirsyncer not found on PATH"}`

---

### Requirement: Sync timeout

The MCP server MUST enforce a 30-second timeout on `vdirsyncer sync` to prevent hung processes from blocking tool responses indefinitely.

#### Scenario: Sync exceeds timeout

- **WHEN** a mutation succeeds locally
- **AND** `vdirsyncer sync` does not complete within 30 seconds
- **THEN** the sync process is terminated
- **AND** the response includes `_sync: {"success": false, "error": "sync timed out after 30s"}`
- **AND** the local mutation is still reported as successful
