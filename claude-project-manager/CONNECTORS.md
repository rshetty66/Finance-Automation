# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user connects in that category. For example, `~~project tracker` might mean Jira, Linear, Asana, or any other project tracker with an MCP server.

Plugins are tool-agnostic — they describe workflows in terms of categories rather than specific products.

## Connectors for this plugin

| Category | Placeholder | Included server | Other options |
|----------|-------------|-----------------|---------------|
| Project tracker | `~~project tracker` | Atlassian (Jira) | Linear, Asana, monday.com, ClickUp |
| Email | `~~email` | Gmail | Microsoft 365 (Outlook) |
| Calendar | `~~calendar` | Google Calendar | Microsoft 365 |
| Whiteboard | `~~whiteboard` | — (not available) | Miro, FigJam |

## Included MCP servers

- **atlassian** — Jira issue management: search, read, create, update, transitions
- **gmail** — Email: search, read threads, create drafts (no direct send)
- **google-calendar** — Calendar: read events, create events, search by date/participant

## Customization

To use alternative services (e.g., Linear instead of Jira):
1. Replace the MCP server URL in `.mcp.json`
2. The `~~placeholder` references in skills remain unchanged
3. Claude adapts tool calls to the connected service automatically

## Known limitations

- Gmail: no direct send (draft only), no attachments via MCP
- Calendar: no recurring events, no free/busy check
- Whiteboard: no MCP server available (April 2026)
