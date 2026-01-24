"""Contacts tools for MCP server - parse and manage .vcf files"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

import vobject


@dataclass
class Contact:
    """Normalized contact"""
    uid: str
    formatted_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    emails: Optional[List[str]] = None
    phones: Optional[List[Dict[str, str]]] = None
    organization: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    addresses: Optional[List[Dict[str, str]]] = None
    file_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for k, v in asdict(self).items():
            if v is not None and v != [] and v != "":
                result[k] = v
        return result


class ContactsManager:
    """Manages contacts data from local vdirsyncer directories"""

    def __init__(self, contacts_path: str = "~/.contacts"):
        self.contacts_path = Path(contacts_path).expanduser()

    def _parse_vcf_file(self, file_path: Path, addressbook_name: str) -> List[Contact]:
        """Parse a single .vcf file and return contacts"""
        contacts = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # vobject can parse multiple vcards in one file
            for vcard in vobject.readComponents(content):
                if vcard.name != 'VCARD':
                    continue

                # UID
                uid = ""
                if hasattr(vcard, 'uid'):
                    uid = str(vcard.uid.value)

                # Formatted name
                fn = ""
                if hasattr(vcard, 'fn'):
                    fn = str(vcard.fn.value)

                # Name components
                first_name = None
                last_name = None
                if hasattr(vcard, 'n'):
                    n = vcard.n.value
                    if hasattr(n, 'given'):
                        first_name = n.given
                    if hasattr(n, 'family'):
                        last_name = n.family

                # Emails
                emails = []
                if hasattr(vcard, 'email'):
                    for email in vcard.contents.get('email', []):
                        emails.append(str(email.value))

                # Phones
                phones = []
                if hasattr(vcard, 'tel'):
                    for tel in vcard.contents.get('tel', []):
                        phone_type = "CELL"
                        if hasattr(tel, 'params') and 'TYPE' in tel.params:
                            phone_type = ", ".join(tel.params['TYPE'])
                        phones.append({
                            "type": phone_type,
                            "number": str(tel.value)
                        })

                # Organization
                org = None
                if hasattr(vcard, 'org'):
                    org_val = vcard.org.value
                    if isinstance(org_val, list):
                        org = org_val[0] if org_val else None
                    else:
                        org = str(org_val)

                # Title
                title = None
                if hasattr(vcard, 'title'):
                    title = str(vcard.title.value)

                # Notes
                notes = None
                if hasattr(vcard, 'note'):
                    notes = str(vcard.note.value)

                # Addresses
                addresses = []
                if hasattr(vcard, 'adr'):
                    for adr in vcard.contents.get('adr', []):
                        addr_type = "HOME"
                        if hasattr(adr, 'params') and 'TYPE' in adr.params:
                            addr_type = ", ".join(adr.params['TYPE'])

                        addr_val = adr.value
                        address_parts = []
                        if hasattr(addr_val, 'street') and addr_val.street:
                            address_parts.append(addr_val.street)
                        if hasattr(addr_val, 'city') and addr_val.city:
                            address_parts.append(addr_val.city)
                        if hasattr(addr_val, 'region') and addr_val.region:
                            address_parts.append(addr_val.region)
                        if hasattr(addr_val, 'code') and addr_val.code:
                            address_parts.append(addr_val.code)
                        if hasattr(addr_val, 'country') and addr_val.country:
                            address_parts.append(addr_val.country)

                        if address_parts:
                            addresses.append({
                                "type": addr_type,
                                "formatted": ", ".join(address_parts)
                            })

                contact = Contact(
                    uid=uid,
                    formatted_name=fn,
                    first_name=first_name,
                    last_name=last_name,
                    emails=emails if emails else None,
                    phones=phones if phones else None,
                    organization=org,
                    title=title,
                    notes=notes,
                    addresses=addresses if addresses else None,
                    file_path=str(file_path)
                )
                contacts.append(contact)

        except Exception as e:
            import sys
            sys.stderr.write(f"[WARN] Failed to parse {file_path}: {e}\n")

        return contacts

    def list_contacts(self, addressbook: Optional[str] = None,
                      limit: int = 100) -> List[Contact]:
        """
        List all contacts.

        Args:
            addressbook: Optional addressbook name to filter by
            limit: Maximum results to return

        Returns:
            List of Contact objects
        """
        all_contacts = []

        if not self.contacts_path.exists():
            return []

        for addr_dir in self.contacts_path.iterdir():
            if not addr_dir.is_dir():
                continue

            addr_name = addr_dir.name

            if addressbook and addr_name != addressbook:
                continue

            # Find .vcf files (may be nested in subdirectories like "default/")
            for vcf_file in addr_dir.rglob("*.vcf"):
                contacts = self._parse_vcf_file(vcf_file, addr_name)
                all_contacts.extend(contacts)

                if len(all_contacts) >= limit:
                    break

            if len(all_contacts) >= limit:
                break

        # Sort by formatted name
        all_contacts.sort(key=lambda c: c.formatted_name.lower())

        return all_contacts[:limit]

    def search_contacts(self, query: str, addressbook: Optional[str] = None,
                        limit: int = 50) -> List[Contact]:
        """
        Search contacts by name, email, phone, or organization.

        Args:
            query: Search string (case-insensitive)
            addressbook: Optional addressbook name to filter by
            limit: Maximum results to return

        Returns:
            List of matching Contact objects
        """
        query_lower = query.lower()
        matches = []

        if not self.contacts_path.exists():
            return []

        for addr_dir in self.contacts_path.iterdir():
            if not addr_dir.is_dir():
                continue

            addr_name = addr_dir.name

            if addressbook and addr_name != addressbook:
                continue

            for vcf_file in addr_dir.rglob("*.vcf"):
                contacts = self._parse_vcf_file(vcf_file, addr_name)

                for contact in contacts:
                    # Build searchable text
                    searchable_parts = [
                        contact.formatted_name,
                        contact.first_name,
                        contact.last_name,
                        contact.organization,
                        contact.title,
                    ]

                    # Add emails
                    if contact.emails:
                        searchable_parts.extend(contact.emails)

                    # Add phone numbers
                    if contact.phones:
                        searchable_parts.extend(p.get("number", "") for p in contact.phones)

                    searchable = " ".join(filter(None, searchable_parts)).lower()

                    if query_lower in searchable:
                        matches.append(contact)

                        if len(matches) >= limit:
                            return matches

        # Sort by relevance (name starts with query first)
        matches.sort(key=lambda c: (
            0 if c.formatted_name.lower().startswith(query_lower) else 1,
            c.formatted_name.lower()
        ))

        return matches

    def get_contact(self, uid: str = None, name: str = None) -> Optional[Contact]:
        """
        Get a single contact by UID or name.

        Args:
            uid: Contact UID
            name: Contact name (partial match)

        Returns:
            Contact if found, None otherwise
        """
        if not uid and not name:
            return None

        if not self.contacts_path.exists():
            return None

        for addr_dir in self.contacts_path.iterdir():
            if not addr_dir.is_dir():
                continue

            for vcf_file in addr_dir.rglob("*.vcf"):
                contacts = self._parse_vcf_file(vcf_file, addr_dir.name)

                for contact in contacts:
                    if uid and contact.uid == uid:
                        return contact
                    if name and name.lower() in contact.formatted_name.lower():
                        return contact

        return None
