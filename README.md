# google-keep-mcp

An MCP server for Google Keep. Apply the power of AI to organize, update, or just export your Keep notes.

## Features

### Search/List Operations

- `find` - Search for notes based on a query string
- `get_pinned_notes` - Get pinned notes (with optional search)
- `get_archived_notes` - Get archived notes (with optional search)
- `get_trashed_notes` - Get trashed notes (with optional search)

### Add Operations

- `create_note` - Create a new note with title and text

### Update Operations

- `update_note` - Update a note's title and text
- `set_note_color` - Set the color of a note (12 colors available)
- `archive_note` - Archive a note
- `unarchive_note` - Unarchive a note
- `restore_note` - Restore a trashed note back to an active note

### Delete Operations

- `delete_note` - Mark a note for deletion
- `delete_archived_note` - Permanently delete an archived note

### Utility Operations

- `get_labels` - Get all labels (with their usage count) for notes
- `get_note_colors` - Get available note colors and usage statistics

## How to use

1. Add the MCP server to your MCP servers:

```json
  "mcpServers": {
    "google-keep-mcp": {
      "command": "pipx",
      "args": [
        "run",
        "google-keep-mcp"
      ],
      "env": {
        "GOOGLE_EMAIL": "Your Google Email",
        "GOOGLE_MASTER_TOKEN": "Your Google Master Token"
      }
    }
  }
```

2. Add your credentials:

- `GOOGLE_EMAIL`: Your Google account email address
- `GOOGLE_MASTER_TOKEN`: Your Google account master token

Will you will need to create a master token (unless you have a Google Enterprise account, and can access the Google Keep API directly). Follow these steps:

- Goto https://myaccount.google.com/apppasswords and create an app password
- Run this docker command `docker run --rm -it breph/ha-google-home_get-token` and enter your gmail address and app password (make sure it doesn't have a space at the end)
- Obtain your master token. **Be careful with this token, it has access to everything in your Google account.**

> [!TIP]
> Stuck? Check https://github.com/leikoilja/ha-google-home/issues/890#issuecomment-2515002294, https://gkeepapi.readthedocs.io/en/latest/#obtaining-a-master-token and https://github.com/simon-weber/gpsoauth?tab=readme-ov-file#alternative-flow for more information.

## Publishing

To publish a new version to PyPI:

1. Update the version in `pyproject.toml`
2. Build the package:
   ```bash
   pipx run build
   ```
3. Upload to PyPI:
   ```bash
   pipx run twine upload --repository pypi dist/*
   ```
