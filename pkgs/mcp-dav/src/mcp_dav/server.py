#!/usr/bin/env python3
"""
MCP DAV Server - Calendar and Contacts access via MCP protocol

Uses FastMCP for protocol handling. Provides tools for AI agents to:
- List and search calendar events
- Create new calendar events
- Check free/busy times
- List and search contacts
- Create, update, and delete contacts
"""

import json
import os
import subprocess
import sys
from typing import Optional

from fastmcp import FastMCP

from .calendar import CalendarManager
from .contacts import ContactsManager

# Initialize FastMCP server
mcp = FastMCP("mcp-dav")

# Initialize managers (will be set up in main())
_calendar: Optional[CalendarManager] = None
_contacts: Optional[ContactsManager] = None


def _get_calendar() -> CalendarManager:
    """Get the calendar manager, initializing if needed."""
    global _calendar
    if _calendar is None:
        calendars_path = os.environ.get("MCP_DAV_CALENDARS", "~/.calendars")
        _calendar = CalendarManager(calendars_path)
    return _calendar


def _get_contacts() -> ContactsManager:
    """Get the contacts manager, initializing if needed."""
    global _contacts
    if _contacts is None:
        contacts_path = os.environ.get("MCP_DAV_CONTACTS", "~/.contacts")
        _contacts = ContactsManager(contacts_path)
    return _contacts


def _run_sync() -> dict:
    """Run vdirsyncer sync and return the result."""
    try:
        result = subprocess.run(
            ["vdirsyncer", "sync"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return {"success": True}
        else:
            error = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
            return {"success": False, "error": error}
    except FileNotFoundError:
        return {"success": False, "error": "vdirsyncer not found on PATH"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "sync timed out after 30s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# =============================================================================
# Calendar Tools
# =============================================================================


@mcp.tool()
def list_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    calendar: Optional[str] = None,
) -> str:
    """List calendar events in a date range. Returns events with summary, start/end times, location, and calendar name."""
    events = _get_calendar().list_events(
        start_date=start_date,
        end_date=end_date,
        calendar=calendar,
    )
    return json.dumps([e.to_dict() for e in events], indent=2, default=str)


@mcp.tool()
def search_events(
    query: str,
    calendar: Optional[str] = None,
    limit: int = 50,
) -> str:
    """Search calendar events by text in summary, description, or location."""
    events = _get_calendar().search_events(
        query=query,
        calendar=calendar,
        limit=limit,
    )
    return json.dumps([e.to_dict() for e in events], indent=2, default=str)


@mcp.tool()
def create_event(
    summary: str,
    start: str,
    end: str,
    calendar: str,
    location: Optional[str] = None,
    description: Optional[str] = None,
    all_day: bool = False,
) -> str:
    """Create a new calendar event. Automatically syncs to remote after creation."""
    event = _get_calendar().create_event(
        summary=summary,
        start=start,
        end=end,
        calendar=calendar,
        location=location,
        description=description,
        all_day=all_day,
    )
    result = event.to_dict()
    result["_sync"] = _run_sync()
    return json.dumps(result, indent=2, default=str)


@mcp.tool()
def get_free_busy(
    start_date: str,
    end_date: str,
    calendars: Optional[list[str]] = None,
) -> str:
    """Get busy time slots in a date range. Useful for finding available meeting times."""
    busy = _get_calendar().get_free_busy(
        start_date=start_date,
        end_date=end_date,
        calendars=calendars,
    )
    return json.dumps({"busy_periods": busy}, indent=2, default=str)


# =============================================================================
# Contacts Tools
# =============================================================================


@mcp.tool()
def list_contacts(
    addressbook: Optional[str] = None,
    limit: int = 100,
) -> str:
    """List contacts from address book."""
    contacts = _get_contacts().list_contacts(
        addressbook=addressbook,
        limit=limit,
    )
    return json.dumps([c.to_dict() for c in contacts], indent=2, default=str)


@mcp.tool()
def search_contacts(
    query: str,
    addressbook: Optional[str] = None,
    limit: int = 50,
) -> str:
    """Search contacts by name, email, phone, or organization."""
    contacts = _get_contacts().search_contacts(
        query=query,
        addressbook=addressbook,
        limit=limit,
    )
    return json.dumps([c.to_dict() for c in contacts], indent=2, default=str)


@mcp.tool()
def get_contact(
    uid: Optional[str] = None,
    name: Optional[str] = None,
) -> str:
    """Get detailed information for a single contact."""
    contact = _get_contacts().get_contact(uid=uid, name=name)
    if contact:
        return json.dumps(contact.to_dict(), indent=2, default=str)
    else:
        return json.dumps({"error": "Contact not found"}, indent=2)


@mcp.tool()
def create_contact(
    formatted_name: str,
    addressbook: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    emails: Optional[list[str]] = None,
    phones: Optional[list[dict]] = None,
    organization: Optional[str] = None,
    title: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Create a new contact. Automatically syncs to remote after creation."""
    try:
        contact = _get_contacts().create_contact(
            formatted_name=formatted_name,
            addressbook=addressbook,
            first_name=first_name,
            last_name=last_name,
            emails=emails,
            phones=phones,
            organization=organization,
            title=title,
            notes=notes,
        )
        result = contact.to_dict()
        result["_sync"] = _run_sync()
        return json.dumps(result, indent=2, default=str)
    except ValueError as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def update_contact(
    uid: Optional[str] = None,
    name: Optional[str] = None,
    formatted_name: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    emails: Optional[list[str]] = None,
    phones: Optional[list[dict]] = None,
    organization: Optional[str] = None,
    title: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Update an existing contact. Only specified fields are modified. Creates a backup before changes."""
    try:
        result = _get_contacts().update_contact(
            uid=uid,
            name=name,
            formatted_name=formatted_name,
            first_name=first_name,
            last_name=last_name,
            emails=emails,
            phones=phones,
            organization=organization,
            title=title,
            notes=notes,
        )
        result["_sync"] = _run_sync()
        return json.dumps(result, indent=2, default=str)
    except ValueError as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
def delete_contact(
    uid: Optional[str] = None,
    name: Optional[str] = None,
) -> str:
    """Delete a contact. Creates a backup before deletion."""
    try:
        result = _get_contacts().delete_contact(uid=uid, name=name)
        result["_sync"] = _run_sync()
        return json.dumps(result, indent=2, default=str)
    except ValueError as e:
        return json.dumps({"error": str(e)}, indent=2)


# =============================================================================
# Entry Point
# =============================================================================


def main():
    """Entry point - run the MCP server."""
    if "--version" in sys.argv:
        print("mcp-dav 0.1.0")
        sys.exit(0)

    if "--help" in sys.argv:
        print("Usage: mcp-dav [OPTIONS]")
        print()
        print("MCP server for calendar and contacts access.")
        print("Uses FastMCP for protocol handling.")
        print()
        print("Options:")
        print("  --version             Show version")
        print("  --help                Show this help")
        print()
        print("Environment variables:")
        print("  MCP_DAV_CALENDARS     Path(s) to calendars, colon-separated")
        print("                        (default: ~/.calendars)")
        print("                        Example: ~/.calendars:~/.calendars-external")
        print("  MCP_DAV_CONTACTS      Path to contacts (default: ~/.contacts)")
        print()
        print("Tools provided:")
        print("  list_events           List calendar events in date range")
        print("  search_events         Search events by text")
        print("  create_event          Create new calendar event")
        print("  get_free_busy         Get busy time slots")
        print("  list_contacts         List contacts")
        print("  search_contacts       Search contacts")
        print("  get_contact           Get contact details")
        print("  create_contact        Create new contact")
        print("  update_contact        Update existing contact")
        print("  delete_contact        Delete contact")
        sys.exit(0)

    # Log startup info to stderr
    calendars_path = os.environ.get("MCP_DAV_CALENDARS", "~/.calendars")
    contacts_path = os.environ.get("MCP_DAV_CONTACTS", "~/.contacts")
    sys.stderr.write(f"[INFO] MCP DAV Server v0.1.0 (FastMCP) ready\n")
    sys.stderr.write(f"[INFO] Calendars: {calendars_path}\n")
    sys.stderr.write(f"[INFO] Contacts: {contacts_path}\n")

    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()
