# Unknowns

## Technical Unknowns

### Google CardDAV Reliability
- **Question**: How unreliable is Google's CardDAV implementation in practice?
- **Evidence**: vdirsyncer docs warn it's "a disaster in terms of data safety"
- **Impact**: May need Google People API as alternative backend
- **Status**: TBD - test with real usage

### OAuth Token Refresh
- **Question**: How does vdirsyncer handle OAuth token refresh?
- **Evidence**: vdirsyncer manages token refresh automatically
- **Impact**: Need to understand failure modes
- **Status**: TBD - test token expiry scenarios

### Multi-Calendar Sync Performance
- **Question**: What's the sync performance with many calendars?
- **Evidence**: No data yet
- **Impact**: May need sync optimization for heavy users
- **Status**: TBD - benchmark with real accounts

## Design Unknowns

### Shared OAuth Credentials
- **Question**: Should calendar and contacts share OAuth credentials?
- **Evidence**: Google allows same OAuth app for both
- **Impact**: Affects option structure
- **Status**: Recommend yes - simpler UX

### Conflict Resolution UX
- **Question**: How should users be notified of sync conflicts?
- **Evidence**: vdirsyncer handles silently based on config
- **Impact**: May want journald logging or notifications
- **Status**: TBD

## Integration Unknowns

### cairn Integration Pattern
- **Question**: How exactly will cairn import and configure cairn-dav?
- **Evidence**: Follow cairn-mail pattern
- **Impact**: Need to align module interface
- **Status**: Design with cairn compatibility in mind
