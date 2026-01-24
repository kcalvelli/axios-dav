# Contacts Write Operations Specification

## Overview

This spec defines the write operations for contacts management via the MCP server: create, update, and delete.

---

## ADDED Requirements

### Requirement: Create Contact

The MCP server MUST provide a `create_contact` tool that creates a new contact in the local address book.

#### Scenario: Create contact with minimal fields

**Given** the MCP server is running
**And** an addressbook named "Personal" exists at `~/.contacts/Personal/`
**When** the AI calls `create_contact` with:
```json
{
  "formatted_name": "John Doe",
  "addressbook": "Personal"
}
```
**Then** a new VCF file is created at `~/.contacts/Personal/{uid}.vcf`
**And** the VCF contains valid vCard 3.0 format
**And** the response includes the created contact with its UID
**And** the response includes a note about running `vdirsyncer sync`

#### Scenario: Create contact with full details

**Given** the MCP server is running
**And** an addressbook named "Work" exists
**When** the AI calls `create_contact` with:
```json
{
  "formatted_name": "Jane Smith",
  "addressbook": "Work",
  "first_name": "Jane",
  "last_name": "Smith",
  "emails": ["jane@example.com", "jsmith@corp.com"],
  "phones": [{"type": "CELL", "number": "+1-555-1234"}],
  "organization": "Example Corp",
  "title": "Engineer"
}
```
**Then** a new VCF file is created with all specified fields
**And** the VCF is parseable by vdirsyncer

#### Scenario: Create contact in non-existent addressbook

**Given** the MCP server is running
**And** no addressbook named "NonExistent" exists
**When** the AI calls `create_contact` with addressbook "NonExistent"
**Then** the response includes an error message
**And** no file is created

---

### Requirement: Update Contact

The MCP server MUST provide an `update_contact` tool that modifies an existing contact.

#### Scenario: Update contact by UID

**Given** a contact with UID "abc-123" exists at `~/.contacts/Personal/abc-123.vcf`
**When** the AI calls `update_contact` with:
```json
{
  "uid": "abc-123",
  "title": "Senior Engineer"
}
```
**Then** a backup is created at `~/.contacts/Personal/abc-123.vcf.bak`
**And** only the `title` field is updated in the original file
**And** all other fields remain unchanged
**And** the response includes the updated contact
**And** the response includes the backup path

#### Scenario: Update contact by name

**Given** a contact named "John Doe" exists
**When** the AI calls `update_contact` with:
```json
{
  "name": "John Doe",
  "organization": "New Company"
}
```
**Then** the first matching contact is updated
**And** the response includes the updated contact

#### Scenario: Update contact adds new field

**Given** a contact exists without a `notes` field
**When** the AI calls `update_contact` with a `notes` value
**Then** the `notes` field is added to the contact
**And** existing fields are preserved

#### Scenario: Update non-existent contact

**Given** no contact with UID "does-not-exist" exists
**When** the AI calls `update_contact` with that UID
**Then** the response includes an error message
**And** no files are modified

---

### Requirement: Delete Contact

The MCP server MUST provide a `delete_contact` tool that removes a contact.

#### Scenario: Delete contact by UID

**Given** a contact with UID "abc-123" exists at `~/.contacts/Personal/abc-123.vcf`
**When** the AI calls `delete_contact` with `uid: "abc-123"`
**Then** a backup is created at `~/.contacts/Personal/abc-123.vcf.bak`
**And** the original VCF file is deleted
**And** the response confirms deletion with the contact's name
**And** the response includes the backup path
**And** the response includes a note about running `vdirsyncer sync`

#### Scenario: Delete contact by name

**Given** a contact named "John Doe" exists at `~/.contacts/Personal/john-doe-uid.vcf`
**When** the AI calls `delete_contact` with `name: "John Doe"`
**Then** a backup is created at `~/.contacts/Personal/john-doe-uid.vcf.bak`
**And** the first matching contact is deleted
**And** the response confirms deletion with backup path

#### Scenario: Delete non-existent contact

**Given** no contact with UID "does-not-exist" exists
**When** the AI calls `delete_contact` with that UID
**Then** the response includes an error message
**And** no files are deleted

---

### Requirement: Backup Before Destructive Operations

The MCP server MUST create a backup of VCF files before update or delete operations to protect against data loss.

#### Scenario: Backup created before update

**Given** a contact exists at `~/.contacts/Personal/contact.vcf`
**When** the AI calls `update_contact` for that contact
**Then** a backup is created at `~/.contacts/Personal/contact.vcf.bak` BEFORE modification
**And** the backup contains the original unmodified content
**And** subsequent updates overwrite the previous backup

#### Scenario: Backup created before delete

**Given** a contact exists at `~/.contacts/Personal/contact.vcf`
**When** the AI calls `delete_contact` for that contact
**Then** a backup is created at `~/.contacts/Personal/contact.vcf.bak` BEFORE deletion
**And** the backup can be restored by renaming to `.vcf`

#### Scenario: Backup is not synced

**Given** a backup file exists at `~/.contacts/Personal/contact.vcf.bak`
**When** the user runs `vdirsyncer sync`
**Then** the `.bak` file is ignored (not synced to remote)

---

## Cross-References

- **Calendar Write Operations**: `create_event` in `calendar.py` provides the implementation pattern
- **Contacts Read Operations**: Existing `list_contacts`, `search_contacts`, `get_contact` for addressbook discovery
- **Google CardDAV Issues**: Known data loss issues documented at https://evertpot.com/google-carddav-issues/

---

## Implementation Notes

### VCF File Format

Generated files MUST use vCard 3.0 format for maximum compatibility:

```
BEGIN:VCARD
VERSION:3.0
UID:{uuid4}
FN:{formatted_name}
N:{last_name};{first_name};;;
EMAIL;TYPE=INTERNET:{email}
TEL;TYPE={type}:{number}
ORG:{organization}
TITLE:{title}
NOTE:{notes}
ADR;TYPE={type}:;;{street};{city};{region};{postal};{country}
END:VCARD
```

### File Naming

- New contacts: `{addressbook}/{uid}.vcf`
- UIDs: Generated using `uuid.uuid4()`
- Filenames match UID for easy lookup

### Error Handling

All tools return structured errors matching existing patterns:
```json
{"error": "Addressbook not found: NonExistent"}
```

### Sync Note

Create, update, and delete operations include in response:
```json
{"_note": "Contact modified locally. Run 'vdirsyncer sync' to sync to remote."}
```

### Backup Strategy

Update and delete operations include backup path in response:
```json
{
  "_backup": "~/.contacts/Personal/abc-123.vcf.bak",
  "_note": "Backup created. Run 'vdirsyncer sync' to sync changes to remote."
}
```

Backup behavior:
- File extension: `.vcf.bak`
- Location: Same directory as original
- Overwrites previous backup (only latest backup retained)
- Not synced by vdirsyncer (ignores non-`.vcf` files)
- Restorable by renaming back to `.vcf`

### Google CardDAV Warning

Due to known issues with Google's CardDAV implementation:
- Data may be silently discarded during sync
- Write operations may take 10-20 seconds
- ~15% of vCards may be rejected

The backup strategy mitigates local data loss, but users should be aware of Google-specific limitations. Other providers (Fastmail, Nextcloud, etc.) do not have these issues.
