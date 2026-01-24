#!/usr/bin/env python3
"""
MCP DAV Server - Calendar and Contacts access via MCP protocol

Provides tools for AI agents to:
- List and search calendar events
- Create new calendar events
- Check free/busy times
- List and search contacts
"""

import sys
import json
import os
from typing import Any, Dict, List, Optional

from .calendar import CalendarManager
from .contacts import ContactsManager


class MCPServer:
    """MCP protocol server for calendar and contacts access"""

    VERSION = "0.1.0"

    def __init__(self, calendars_path: str = None, contacts_path: str = None):
        # Use environment variables or defaults
        calendars_path = calendars_path or os.environ.get("MCP_DAV_CALENDARS", "~/.calendars")
        contacts_path = contacts_path or os.environ.get("MCP_DAV_CONTACTS", "~/.contacts")

        self.calendar = CalendarManager(calendars_path)
        self.contacts = ContactsManager(contacts_path)

        sys.stderr.write(f"[INFO] MCP DAV Server v{self.VERSION} ready\n")
        sys.stderr.write(f"[INFO] Calendars: {calendars_path}\n")
        sys.stderr.write(f"[INFO] Contacts: {contacts_path}\n")

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP JSON-RPC request"""

        method = request.get("method")
        req_id = request.get("id")
        params = request.get("params", {})

        try:
            if method == "initialize":
                return self._make_response(req_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "mcp-dav",
                        "version": self.VERSION
                    }
                })

            elif method == "notifications/initialized":
                # Client notification, no response needed
                return None

            elif method == "tools/list":
                return self._make_response(req_id, {
                    "tools": self._get_tools()
                })

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = self._handle_tool_call(tool_name, arguments)
                return self._make_response(req_id, result)

            else:
                # Unknown method - return empty response for notifications
                if req_id is None:
                    return None
                raise ValueError(f"Unknown method: {method}")

        except Exception as e:
            sys.stderr.write(f"[ERROR] {e}\n")
            return self._make_error(req_id, -32603, str(e))

    def _get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools"""
        return [
            # Calendar tools
            {
                "name": "list_events",
                "description": "List calendar events in a date range. Returns events with summary, start/end times, location, and calendar name.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in ISO8601 format (YYYY-MM-DD). Defaults to today."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in ISO8601 format (YYYY-MM-DD). Defaults to 30 days from start."
                        },
                        "calendar": {
                            "type": "string",
                            "description": "Optional calendar name to filter by."
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "search_events",
                "description": "Search calendar events by text in summary, description, or location.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search text (case-insensitive)."
                        },
                        "calendar": {
                            "type": "string",
                            "description": "Optional calendar name to filter by."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default: 50).",
                            "default": 50
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            },
            {
                "name": "create_event",
                "description": "Create a new calendar event. After creation, run 'vdirsyncer sync' to sync to remote.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Event title."
                        },
                        "start": {
                            "type": "string",
                            "description": "Start datetime in ISO8601 format (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD for all-day)."
                        },
                        "end": {
                            "type": "string",
                            "description": "End datetime in ISO8601 format."
                        },
                        "calendar": {
                            "type": "string",
                            "description": "Calendar name to create event in (e.g., 'Family')."
                        },
                        "location": {
                            "type": "string",
                            "description": "Optional event location."
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional event description."
                        },
                        "all_day": {
                            "type": "boolean",
                            "description": "Whether this is an all-day event.",
                            "default": False
                        }
                    },
                    "required": ["summary", "start", "end", "calendar"],
                    "additionalProperties": False
                }
            },
            {
                "name": "get_free_busy",
                "description": "Get busy time slots in a date range. Useful for finding available meeting times.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in ISO8601 format (YYYY-MM-DD)."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in ISO8601 format (YYYY-MM-DD)."
                        },
                        "calendars": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of calendar names to check."
                        }
                    },
                    "required": ["start_date", "end_date"],
                    "additionalProperties": False
                }
            },
            # Contacts tools
            {
                "name": "list_contacts",
                "description": "List contacts from address book.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "addressbook": {
                            "type": "string",
                            "description": "Optional addressbook name to filter by."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default: 100).",
                            "default": 100
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "search_contacts",
                "description": "Search contacts by name, email, phone, or organization.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search text (case-insensitive)."
                        },
                        "addressbook": {
                            "type": "string",
                            "description": "Optional addressbook name to filter by."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default: 50).",
                            "default": 50
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            },
            {
                "name": "get_contact",
                "description": "Get detailed information for a single contact.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "uid": {
                            "type": "string",
                            "description": "Contact UID."
                        },
                        "name": {
                            "type": "string",
                            "description": "Contact name (partial match)."
                        }
                    },
                    "additionalProperties": False
                }
            }
        ]

    def _handle_tool_call(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call and return result"""

        # Calendar tools
        if tool_name == "list_events":
            events = self.calendar.list_events(
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
                calendar=args.get("calendar")
            )
            return self._format_result([e.to_dict() for e in events])

        elif tool_name == "search_events":
            events = self.calendar.search_events(
                query=args.get("query", ""),
                calendar=args.get("calendar"),
                limit=args.get("limit", 50)
            )
            return self._format_result([e.to_dict() for e in events])

        elif tool_name == "create_event":
            event = self.calendar.create_event(
                summary=args["summary"],
                start=args["start"],
                end=args["end"],
                calendar=args["calendar"],
                location=args.get("location"),
                description=args.get("description"),
                all_day=args.get("all_day", False)
            )
            result = event.to_dict()
            result["_note"] = "Event created locally. Run 'vdirsyncer sync' to sync to remote calendar."
            return self._format_result(result)

        elif tool_name == "get_free_busy":
            busy = self.calendar.get_free_busy(
                start_date=args["start_date"],
                end_date=args["end_date"],
                calendars=args.get("calendars")
            )
            return self._format_result({"busy_periods": busy})

        # Contacts tools
        elif tool_name == "list_contacts":
            contacts = self.contacts.list_contacts(
                addressbook=args.get("addressbook"),
                limit=args.get("limit", 100)
            )
            return self._format_result([c.to_dict() for c in contacts])

        elif tool_name == "search_contacts":
            contacts = self.contacts.search_contacts(
                query=args.get("query", ""),
                addressbook=args.get("addressbook"),
                limit=args.get("limit", 50)
            )
            return self._format_result([c.to_dict() for c in contacts])

        elif tool_name == "get_contact":
            contact = self.contacts.get_contact(
                uid=args.get("uid"),
                name=args.get("name")
            )
            if contact:
                return self._format_result(contact.to_dict())
            else:
                return self._format_result({"error": "Contact not found"})

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _format_result(self, data: Any) -> Dict[str, Any]:
        """Format tool result for MCP response"""
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(data, indent=2, default=str)
                }
            ]
        }

    def _make_response(self, req_id: Any, result: Any) -> Dict[str, Any]:
        """Create JSON-RPC success response"""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result
        }

    def _make_error(self, req_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    def run(self):
        """Main server loop - read from stdin, write to stdout"""

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = self.handle_request(request)

                if response is not None:
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                sys.stderr.write(f"[ERROR] Invalid JSON: {e}\n")
                error_resp = self._make_error(None, -32700, "Parse error")
                print(json.dumps(error_resp), flush=True)

            except Exception as e:
                sys.stderr.write(f"[ERROR] Unexpected error: {e}\n")
                error_resp = self._make_error(None, -32603, str(e))
                print(json.dumps(error_resp), flush=True)


def main():
    """Entry point"""

    if "--version" in sys.argv:
        print(f"mcp-dav {MCPServer.VERSION}")
        sys.exit(0)

    if "--help" in sys.argv:
        print("Usage: mcp-dav [OPTIONS]")
        print()
        print("MCP server for calendar and contacts access.")
        print()
        print("Options:")
        print("  --version             Show version")
        print("  --help                Show this help")
        print()
        print("Environment variables:")
        print("  MCP_DAV_CALENDARS     Path to calendars (default: ~/.calendars)")
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
        sys.exit(0)

    # Parse custom paths from environment
    calendars_path = os.environ.get("MCP_DAV_CALENDARS")
    contacts_path = os.environ.get("MCP_DAV_CONTACTS")

    # Create and run server
    server = MCPServer(
        calendars_path=calendars_path,
        contacts_path=contacts_path
    )

    try:
        server.run()
    except KeyboardInterrupt:
        sys.stderr.write("\n[INFO] Shutting down gracefully\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
