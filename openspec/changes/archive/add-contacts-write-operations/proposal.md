# Proposal: Add Contacts Write Operations

## Summary

Add create, update, and delete operations to the contacts MCP server, bringing it to parity with calendar functionality.

## Problem

The MCP server currently supports write operations for calendar (via `create_event`) but only read operations for contacts (`list_contacts`, `search_contacts`, `get_contact`). This asymmetry limits AI agents' ability to manage contacts, forcing users to use khard CLI directly.

## Goals

1. Add `create_contact` tool to create new VCF contacts
2. Add `update_contact` tool to modify existing contacts
3. Add `delete_contact` tool to remove contacts
4. Follow the same pattern as calendar's `create_event` (local write + sync reminder)
5. Support the same addressbook selection pattern used in read operations

## Non-Goals

- Automatic sync triggering (users run `vdirsyncer sync` manually, matching calendar behavior)
- Batch operations (can be added later if needed)
- Contact merging/deduplication (complex logic, separate proposal)
- Google People API integration (future enhancement if CardDAV proves insufficient)

## Design

### New MCP Tools

| Tool | Purpose | Required Args |
|------|---------|---------------|
| `create_contact` | Create a new contact | `formatted_name`, `addressbook` |
| `update_contact` | Modify existing contact | `uid` OR `name` |
| `delete_contact` | Delete a contact | `uid` OR `name` |

### Implementation Approach

Follow the established pattern from `calendar.py`:

1. **ContactsManager** gets new methods: `create_contact()`, `update_contact()`, `delete_contact()`
2. **VCF file generation** using `vobject` library (already a dependency)
3. **UID-based file naming** matching vdirsyncer conventions: `{uid}.vcf`
4. **Server.py** exposes new tools with appropriate input schemas
5. **Return note** reminds users to run `vdirsyncer sync`
6. **Backup before destructive operations** - update/delete create `.vcf.bak` backup files

### Backup Strategy

Before `update_contact` or `delete_contact` modifies/removes a VCF file:
1. Copy original to `{filename}.bak` in the same directory
2. Proceed with the operation
3. Return backup path in response for user awareness

This protects against:
- Google CardDAV's known data loss issues (silently discards properties)
- Accidental deletions
- Sync conflicts

Backups are local-only and not synced (vdirsyncer ignores `.bak` files).

### VCF Structure

Generated VCF files follow vCard 3.0 format:
```
BEGIN:VCARD
VERSION:3.0
UID:{uuid}
FN:{formatted_name}
N:{last};{first};;;
EMAIL;TYPE=INTERNET:{email}
TEL;TYPE=CELL:{phone}
ORG:{organization}
END:VCARD
```

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| VCF format incompatibility | Contacts won't sync | Use vobject library for standards compliance |
| Accidental deletion | Data loss | Require explicit UID or exact name match; create `.bak` backup |
| Partial updates overwriting data | Data loss | Update modifies only specified fields; create `.bak` backup |
| Google CardDAV data loss | Properties silently discarded | Backup before write; warn in response |
| Google CardDAV slow writes | 10-20s per operation | Document limitation; no mitigation possible |
| Google CardDAV rejections | ~15% of vCards rejected | Use conservative vCard 3.0 format; backup original |

### Google CardDAV Limitations (Discovered)

Google's CardDAV implementation has known issues that affect write reliability:
- **Data loss**: Silently discards vCard properties it doesn't recognize
- **Slow writes**: 10-20 seconds per write operation
- **High rejection rate**: ~15% of vCards rejected without clear errors
- **Identifier replacement**: Google replaces UIDs with proprietary identifiers

These issues are documented by [vdirsyncer](https://vdirsyncer.pimutils.org/en/stable/config.html) and [independent analysis](https://evertpot.com/google-carddav-issues/). Our backup strategy mitigates data loss risk. Other CardDAV providers (Fastmail, Nextcloud) do not have these issues.

**Future consideration**: Google People API could provide a more reliable alternative for Google-specific users.

## Success Criteria

- [ ] `create_contact` creates valid VCF files that vdirsyncer syncs successfully
- [ ] `update_contact` preserves unmodified fields
- [ ] `delete_contact` removes local VCF file
- [ ] All new tools appear in `tools/list` MCP response
- [ ] Error handling matches existing patterns (tool returns error dict, doesn't throw)
