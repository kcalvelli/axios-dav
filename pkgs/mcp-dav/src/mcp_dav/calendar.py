"""Calendar tools for MCP server - parse and manage .ics files"""

import os
import uuid
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from icalendar import Calendar, Event


@dataclass
class CalendarEvent:
    """Normalized calendar event"""
    uid: str
    summary: str
    start: str  # ISO8601
    end: str    # ISO8601
    all_day: bool
    location: Optional[str] = None
    description: Optional[str] = None
    calendar: Optional[str] = None
    file_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


class CalendarManager:
    """Manages calendar data from local vdirsyncer directories"""

    def __init__(self, calendars_path: str = "~/.calendars"):
        """Initialize CalendarManager.

        Args:
            calendars_path: Path(s) to calendars directory. Can be a single path
                           or multiple paths separated by colons (like PATH).
                           Example: "~/.calendars:~/.calendars-external"
        """
        # Support multiple paths separated by colons
        self.calendars_paths = [
            Path(p.strip()).expanduser()
            for p in calendars_path.split(":")
            if p.strip()
        ]
        # Keep first path as primary for backwards compatibility
        self.calendars_path = self.calendars_paths[0] if self.calendars_paths else Path("~/.calendars").expanduser()

    def _parse_datetime(self, dt) -> tuple[str, bool]:
        """Parse icalendar datetime to ISO8601 string and all_day flag"""
        if dt is None:
            return "", False

        # Handle date vs datetime
        if hasattr(dt, 'dt'):
            dt = dt.dt

        if isinstance(dt, date) and not isinstance(dt, datetime):
            # All-day event
            return dt.isoformat(), True
        elif isinstance(dt, datetime):
            # Timed event - convert to ISO8601
            if dt.tzinfo is not None:
                # Convert to UTC
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ"), False
            else:
                return dt.strftime("%Y-%m-%dT%H:%M:%S"), False
        else:
            return str(dt), False

    def _parse_ics_file(self, file_path: Path, calendar_name: str) -> List[CalendarEvent]:
        """Parse a single .ics file and return events"""
        events = []

        try:
            with open(file_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())

            for component in cal.walk():
                if component.name == "VEVENT":
                    uid = str(component.get('uid', ''))
                    summary = str(component.get('summary', 'No title'))

                    start_str, all_day = self._parse_datetime(component.get('dtstart'))
                    end_dt = component.get('dtend')
                    if end_dt:
                        end_str, _ = self._parse_datetime(end_dt)
                    else:
                        end_str = start_str

                    location = component.get('location')
                    description = component.get('description')

                    event = CalendarEvent(
                        uid=uid,
                        summary=summary,
                        start=start_str,
                        end=end_str,
                        all_day=all_day,
                        location=str(location) if location else None,
                        description=str(description) if description else None,
                        calendar=calendar_name,
                        file_path=str(file_path)
                    )
                    events.append(event)

        except Exception as e:
            # Log but don't fail on individual file errors
            import sys
            sys.stderr.write(f"[WARN] Failed to parse {file_path}: {e}\n")

        return events

    def list_events(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                    calendar: Optional[str] = None) -> List[CalendarEvent]:
        """
        List calendar events in date range.

        Args:
            start_date: Start date (ISO8601), defaults to today
            end_date: End date (ISO8601), defaults to 30 days from start
            calendar: Optional calendar name to filter by

        Returns:
            List of CalendarEvent objects
        """
        # Parse date range
        if start_date:
            try:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                start = datetime.now()
        else:
            start = datetime.now()

        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                end = start + timedelta(days=30)
        else:
            end = start + timedelta(days=30)

        # Normalize to date for comparison
        start_date_only = start.date() if isinstance(start, datetime) else start
        end_date_only = end.date() if isinstance(end, datetime) else end

        all_events = []

        # Walk through all calendar paths
        for calendars_path in self.calendars_paths:
            if not calendars_path.exists():
                continue

            for cal_dir in calendars_path.iterdir():
                if not cal_dir.is_dir():
                    continue

                cal_name = cal_dir.name

                # Filter by calendar if specified
                if calendar and cal_name != calendar:
                    continue

                # Find .ics files (may be nested in subdirectories)
                for ics_file in cal_dir.rglob("*.ics"):
                    events = self._parse_ics_file(ics_file, cal_name)
                    all_events.extend(events)

        # Filter by date range
        filtered = []
        for event in all_events:
            if not event.start:
                continue

            try:
                # Parse event start date
                event_start = event.start[:10]  # Get YYYY-MM-DD
                event_date = date.fromisoformat(event_start)

                if start_date_only <= event_date <= end_date_only:
                    filtered.append(event)
            except (ValueError, IndexError):
                # Include events with unparseable dates
                filtered.append(event)

        # Sort by start time
        filtered.sort(key=lambda e: e.start)

        return filtered

    def search_events(self, query: str, calendar: Optional[str] = None,
                      limit: int = 50) -> List[CalendarEvent]:
        """
        Search events by text in summary, description, or location.

        Args:
            query: Search string (case-insensitive)
            calendar: Optional calendar name to filter by
            limit: Maximum results to return

        Returns:
            List of matching CalendarEvent objects
        """
        query_lower = query.lower()
        matches = []

        # Search through all calendar paths
        for calendars_path in self.calendars_paths:
            if not calendars_path.exists():
                continue

            for cal_dir in calendars_path.iterdir():
                if not cal_dir.is_dir():
                    continue

                cal_name = cal_dir.name

                if calendar and cal_name != calendar:
                    continue

                for ics_file in cal_dir.rglob("*.ics"):
                    events = self._parse_ics_file(ics_file, cal_name)

                    for event in events:
                        # Search in summary, description, location
                        searchable = " ".join(filter(None, [
                            event.summary,
                            event.description,
                            event.location
                        ])).lower()

                        if query_lower in searchable:
                            matches.append(event)

                            if len(matches) >= limit:
                                return matches

        return matches

    def create_event(self, summary: str, start: str, end: str,
                     calendar: str, location: Optional[str] = None,
                     description: Optional[str] = None,
                     all_day: bool = False) -> CalendarEvent:
        """
        Create a new calendar event.

        Args:
            summary: Event title
            start: Start datetime (ISO8601)
            end: End datetime (ISO8601)
            calendar: Calendar name to create event in
            location: Optional location
            description: Optional description
            all_day: Whether this is an all-day event

        Returns:
            Created CalendarEvent
        """
        # Find calendar directory (search all paths)
        cal_dir = None
        for calendars_path in self.calendars_paths:
            candidate = calendars_path / calendar
            if candidate.exists():
                cal_dir = candidate
                break
            # Try to find matching subdirectory
            if calendars_path.exists():
                for subdir in calendars_path.iterdir():
                    if subdir.is_dir() and calendar.lower() in subdir.name.lower():
                        cal_dir = subdir
                        break
            if cal_dir:
                break

        if not cal_dir:
            raise ValueError(f"Calendar not found: {calendar}")

        # Generate UID
        uid = str(uuid.uuid4())

        # Create icalendar event
        cal = Calendar()
        cal.add('prodid', '-//mcp-dav//mcp-dav//')
        cal.add('version', '2.0')

        event = Event()
        event.add('uid', uid)
        event.add('summary', summary)
        event.add('dtstamp', datetime.now())

        # Parse and add dates
        if all_day:
            start_dt = date.fromisoformat(start[:10])
            end_dt = date.fromisoformat(end[:10])
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
        else:
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            except ValueError:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)

        if location:
            event.add('location', location)
        if description:
            event.add('description', description)

        cal.add_component(event)

        # Write to file
        file_name = f"{uid}.ics"
        file_path = cal_dir / file_name

        with open(file_path, 'wb') as f:
            f.write(cal.to_ical())

        return CalendarEvent(
            uid=uid,
            summary=summary,
            start=start,
            end=end,
            all_day=all_day,
            location=location,
            description=description,
            calendar=calendar,
            file_path=str(file_path)
        )

    def get_free_busy(self, start_date: str, end_date: str,
                      calendars: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Get busy time slots in date range.

        Args:
            start_date: Start date (ISO8601)
            end_date: End date (ISO8601)
            calendars: Optional list of calendars to check

        Returns:
            List of busy periods with start/end times
        """
        busy_periods = []

        # Get all events in range
        events = self.list_events(start_date, end_date)

        # Filter by calendars if specified
        if calendars:
            events = [e for e in events if e.calendar in calendars]

        # Extract busy periods (exclude all-day events from free/busy)
        for event in events:
            if not event.all_day:
                busy_periods.append({
                    "start": event.start,
                    "end": event.end,
                    "summary": event.summary
                })

        # Sort by start time
        busy_periods.sort(key=lambda p: p["start"])

        return busy_periods
