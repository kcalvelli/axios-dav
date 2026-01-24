# Tasks: Add Contacts Write Operations

## Phase 1: ContactsManager Methods

- [x] **1.1** Add `create_contact()` method to `contacts.py`
  - Parameters: `formatted_name`, `addressbook`, optional `first_name`, `last_name`, `emails`, `phones`, `organization`, `title`, `notes`, `addresses`
  - Generate UUID for UID
  - Create VCF using vobject
  - Write to `{addressbook}/{uid}.vcf`
  - Return Contact object
  - Validation: Verify VCF is parseable by `_parse_vcf_file()`

- [x] **1.2** Add `_backup_vcf()` helper method to `contacts.py`
  - Parameters: `file_path`
  - Copy file to `{file_path}.bak` (overwrites previous backup)
  - Return backup path
  - Used by update and delete operations

- [x] **1.3** Add `update_contact()` method to `contacts.py`
  - Parameters: `uid` OR `name` (at least one required), plus any contact fields to update
  - **Create backup** of original VCF before modification
  - Load existing VCF, modify specified fields only, preserve others
  - Write back to same file
  - Return updated Contact object with `backup_path` field
  - Validation: Verify unmodified fields remain intact

- [x] **1.4** Add `delete_contact()` method to `contacts.py`
  - Parameters: `uid` OR `name` (at least one required)
  - Find contact file using `get_contact()` pattern
  - **Create backup** of VCF before deletion
  - Delete the VCF file
  - Return success dict with deleted contact info and `backup_path`
  - Validation: Verify file no longer exists, backup exists

## Phase 2: MCP Server Integration

- [x] **2.1** Add `create_contact` tool definition to `_get_tools()`
  - Input schema with all contact fields
  - Required: `formatted_name`, `addressbook`
  - Description: "Create a new contact. After creation, run 'vdirsyncer sync' to sync to remote."

- [x] **2.2** Add `update_contact` tool definition to `_get_tools()`
  - Input schema: `uid` OR `name` plus updateable fields
  - Description: "Update an existing contact. Only specified fields are modified."

- [x] **2.3** Add `delete_contact` tool definition to `_get_tools()`
  - Input schema: `uid` OR `name`
  - Description: "Delete a contact from the local addressbook."

- [x] **2.4** Add tool handlers in `_handle_tool_call()`
  - Call corresponding ContactsManager methods
  - Format results consistently with existing tools
  - Include sync reminder note in create/update/delete responses
  - Include backup path in update/delete responses

## Phase 3: Testing & Documentation

- [x] **3.1** Manual testing
  - Create contact via MCP tool
  - List contacts to verify creation
  - Update contact, verify changes and `.bak` file created
  - Delete contact, verify removal and `.bak` file created
  - Verify backup files are restorable (rename `.bak` back to `.vcf`)
  - Run `vdirsyncer sync` to verify VCF format compatibility

- [x] **3.2** Update help output in `main()`
  - Add `create_contact`, `update_contact`, `delete_contact` to tools list

- [x] **3.3** Update openspec specs
  - Create/update contacts capability spec

## Dependencies

- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 2
- Tasks within each phase can be parallelized

## Verification Checklist

- [x] `nix flake check` passes
- [x] MCP server starts without errors
- [x] All 3 new tools appear in `tools/list`
- [x] Created VCF files pass vdirsyncer sync
- [x] Update/delete operations create `.bak` backup files
- [x] Backup files are valid VCF and restorable
- [x] Error messages are user-friendly
- [x] Response includes backup path for update/delete operations
