## MODIFIED Requirements

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
**And** the server runs `vdirsyncer sync` automatically
**And** the response includes `_sync` with the sync result

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
**And** the server runs `vdirsyncer sync` automatically
**And** the response includes `_sync` with the sync result

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
**And** the server runs `vdirsyncer sync` automatically
**And** the response includes `_sync` with the sync result

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
