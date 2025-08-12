"""
MCP plugin for Google Keep integration.
Provides tools for interacting with Google Keep notes through MCP.
"""

import json
from mcp.server.fastmcp import FastMCP
from .keep_api import get_client, serialize_note

mcp = FastMCP("keep")

# Search/List Operations

@mcp.tool()
def find(query="", include_archived: bool = True, include_trashed: bool = False) -> str:
    """
    Find notes based on a search query.
    
    Args:
        query (str, optional): A string to match against the title and text
        include_archived (bool, optional): Include archived notes in results (default: True)
        include_trashed (bool, optional): Include trashed notes in results (default: False)
        
    Returns:
        str: JSON string containing the matching notes with their id, title, text, pinned status, color and labels
    """
    keep = get_client()
    
    if include_archived and include_trashed:
        # Get all notes
        notes = keep.find(query=query)
    elif include_archived:
        # Get active + archived notes (exclude trashed)
        active_notes = list(keep.find(query=query, archived=False, trashed=False))
        archived_notes = list(keep.find(query=query, archived=True, trashed=False))
        notes = active_notes + archived_notes
    elif include_trashed:
        # Get active + trashed notes (exclude archived)
        active_notes = list(keep.find(query=query, archived=False, trashed=False))
        trashed_notes = list(keep.find(query=query, archived=False, trashed=True))
        notes = active_notes + trashed_notes
    else:
        # Get only active notes
        notes = keep.find(query=query, archived=False, trashed=False)
    
    notes_data = [serialize_note(note) for note in notes]
    return json.dumps(notes_data)

@mcp.tool()
def get_pinned_notes(query="") -> str:
    """
    Get only pinned notes (active, non-archived, non-trashed).
    
    Args:
        query (str, optional): A string to match against the title and text
        
    Returns:
        str: JSON string containing pinned notes
    """
    keep = get_client()
    notes = keep.find(query=query, archived=False, trashed=False)
    
    # Filter for only pinned notes
    pinned_notes = [note for note in notes if note.pinned]
    
    notes_data = [serialize_note(note) for note in pinned_notes]
    return json.dumps(notes_data)

@mcp.tool()
def get_archived_notes(query="") -> str:
    """
    Get only archived notes.
    
    Args:
        query (str, optional): A string to match against the title and text
        
    Returns:
        str: JSON string containing archived notes
    """
    keep = get_client()
    notes = keep.find(query=query, archived=True, trashed=False)
    
    notes_data = [serialize_note(note) for note in notes]
    return json.dumps(notes_data)

@mcp.tool()
def get_trashed_notes(query="") -> str:
    """
    Get only trashed notes.
    
    Args:
        query (str, optional): A string to match against the title and text
        
    Returns:
        str: JSON string containing trashed notes
    """
    keep = get_client()
    notes = keep.find(query=query, archived=False, trashed=True)
    
    notes_data = [serialize_note(note) for note in notes]
    return json.dumps(notes_data)

# Add Operations

@mcp.tool()
def create_note(title: str = None, text: str = None) -> str:
    """
    Create a new note with title and text.
    
    Args:
        title (str, optional): The title of the note
        text (str, optional): The content of the note
        
    Returns:
        str: JSON string containing the created note's data
    """
    keep = get_client()
    note = keep.createNote(title=title, text=text)
    
    keep.sync()  # Ensure the note is created and labeled on the server
    
    return json.dumps(serialize_note(note))

# Update Operations

@mcp.tool()
def update_note(note_id: str, title: str = None, text: str = None) -> str:
    """
    Update a note's properties.
    
    Args:
        note_id (str): The ID of the note to update
        title (str, optional): New title for the note
        text (str, optional): New text content for the note
        
    Returns:
        str: JSON string containing the updated note's data
        
    Raises:
        ValueError: If the note doesn't exist or cannot be modified
    """
    keep = get_client()
    note = keep.get(note_id)
    
    if not note:
        raise ValueError(f"Note with ID {note_id} not found")
    
    
    if title is not None:
        note.title = title
    if text is not None:
        note.text = text
    
    keep.sync()  # Ensure changes are saved to the server
    return json.dumps(serialize_note(note))

@mcp.tool()
def set_note_color(note_id: str, color: str) -> str:
    """
    Set the color of a note.
    
    Args:
        note_id (str): The ID of the note to update
        color (str): The color to set. Valid values: WHITE, RED, ORANGE, YELLOW, GREEN, TEAL, BLUE, CERULEAN, PURPLE, PINK, BROWN, GRAY
        
    Returns:
        str: Success message
        
    Raises:
        ValueError: If the note doesn't exist, color is invalid, or note cannot be modified
    """
    keep = get_client()
    note = keep.get(note_id)
    
    if not note:
        raise ValueError(f"Note with ID {note_id} not found")
    
    
    # Get the ColorValue enum from the note
    ColorValue = type(note.color)
    
    # Map string colors to enum values
    color_mapping = {
        'WHITE': ColorValue.White,
        'RED': ColorValue.Red,
        'ORANGE': ColorValue.Orange,
        'YELLOW': ColorValue.Yellow,
        'GREEN': ColorValue.Green,
        'TEAL': ColorValue.Teal,
        'BLUE': ColorValue.Blue,
        'CERULEAN': ColorValue.DarkBlue,
        'PURPLE': ColorValue.Purple,
        'PINK': ColorValue.Pink,
        'BROWN': ColorValue.Brown,
        'GRAY': ColorValue.Gray
    }
    
    color_upper = color.upper()
    if color_upper not in color_mapping:
        valid_colors = ', '.join(color_mapping.keys())
        raise ValueError(f"Invalid color '{color}'. Valid colors: {valid_colors}")
    
    old_color = note.color.name
    note.color = color_mapping[color_upper]
    keep.sync()
    
    return json.dumps({"message": f"Note {note_id} color changed from {old_color} to {note.color.name}"})

@mcp.tool()
def archive_note(note_id: str) -> str:
    """
    Archive an active note.
    
    Args:
        note_id (str): The ID of the note to archive
        
    Returns:
        str: Success message
        
    Raises:
        ValueError: If the note doesn't exist, is already archived, or cannot be modified
    """
    keep = get_client()
    note = keep.get(note_id)
    
    if not note:
        raise ValueError(f"Note with ID {note_id} not found")
    
    if note.archived:
        raise ValueError(f"Note with ID {note_id} is already archived")
    
    if note.trashed:
        raise ValueError(f"Note with ID {note_id} is in trash and cannot be archived")
    
    note.archived = True
    keep.sync()
    return json.dumps({"message": f"Note {note_id} archived successfully"})

@mcp.tool()
def unarchive_note(note_id: str) -> str:
    """
    Unarchive a note (move it back to active notes).
    
    Args:
        note_id (str): The ID of the archived note to unarchive
        
    Returns:
        str: Success message
        
    Raises:
        ValueError: If the note doesn't exist, is not archived, or cannot be modified
    """
    keep = get_client()
    note = keep.get(note_id)
    
    if not note:
        raise ValueError(f"Note with ID {note_id} not found")
    
    if not note.archived:
        raise ValueError(f"Note with ID {note_id} is not archived")
    
    
    note.archived = False
    keep.sync()
    return json.dumps({"message": f"Note {note_id} unarchived successfully"})

@mcp.tool()
def restore_note(note_id: str) -> str:
    """
    Restore a trashed note back to active notes.
    
    Args:
        note_id (str): The ID of the trashed note to restore
        
    Returns:
        str: Success message
        
    Raises:
        ValueError: If the note doesn't exist, is not trashed, or cannot be modified
    """
    keep = get_client()
    note = keep.get(note_id)
    
    if not note:
        raise ValueError(f"Note with ID {note_id} not found")
    
    if not note.trashed:
        raise ValueError(f"Note with ID {note_id} is not in trash")
    
    
    note.untrash()
    keep.sync()
    return json.dumps({"message": f"Note {note_id} restored from trash"})

# Delete Operations

@mcp.tool()
def delete_note(note_id: str) -> str:
    """
    Delete a note (mark for deletion).
    
    Args:
        note_id (str): The ID of the note to delete
        
    Returns:
        str: Success message
        
    Raises:
        ValueError: If the note doesn't exist or cannot be modified
    """
    keep = get_client()
    note = keep.get(note_id)
    
    if not note:
        raise ValueError(f"Note with ID {note_id} not found")
    
    
    note.delete()
    keep.sync()  # Ensure deletion is saved to the server
    return json.dumps({"message": f"Note {note_id} marked for deletion"})

@mcp.tool()
def delete_archived_note(note_id: str) -> str:
    """
    Permanently delete an archived note (moves to trash).
    
    Args:
        note_id (str): The ID of the archived note to delete
        
    Returns:
        str: Success message
        
    Raises:
        ValueError: If the note doesn't exist, is not archived, or cannot be modified
    """
    keep = get_client()
    note = keep.get(note_id)
    
    if not note:
        raise ValueError(f"Note with ID {note_id} not found")
    
    if not note.archived:
        raise ValueError(f"Note with ID {note_id} is not archived")
    
    
    note.delete()
    keep.sync()
    return json.dumps({"message": f"Archived note {note_id} moved to trash"})

# Utility Operations

@mcp.tool()
def get_labels(include_archived: bool = True, include_trashed: bool = False) -> str:
    """
    Analyze all labels across notes and return counts for label management.
    
    Args:
        include_archived (bool, optional): Include archived notes in analysis (default: True)
        include_trashed (bool, optional): Include trashed notes in analysis (default: False)
        
    Returns:
        str: JSON string containing label analysis with counts, sorted by usage
    """
    keep = get_client()
    
    # Get all notes based on include parameters
    if include_archived and include_trashed:
        # Get all notes
        notes = keep.find()
    elif include_archived:
        # Get active + archived notes (exclude trashed)
        active_notes = list(keep.find(archived=False, trashed=False))
        archived_notes = list(keep.find(archived=True, trashed=False))
        notes = active_notes + archived_notes
    elif include_trashed:
        # Get active + trashed notes (exclude archived)
        active_notes = list(keep.find(archived=False, trashed=False))
        trashed_notes = list(keep.find(archived=False, trashed=True))
        notes = active_notes + trashed_notes
    else:
        # Get only active notes
        notes = keep.find(archived=False, trashed=False)
    
    # Convert to list if it's a generator
    if hasattr(notes, '__iter__') and not isinstance(notes, list):
        notes = list(notes)
    
    # Count labels
    label_counts = {}
    total_notes = len(notes)
    notes_with_labels = 0
    notes_without_labels = 0
    
    for note in notes:
        note_labels = list(note.labels.all())
        
        if note_labels:
            notes_with_labels += 1
            for label in note_labels:
                label_name = label.name
                label_id = label.id
                
                if label_name not in label_counts:
                    label_counts[label_name] = {
                        'id': label_id,
                        'name': label_name,
                        'count': 0,
                        'percentage': 0.0
                    }
                
                label_counts[label_name]['count'] += 1
        else:
            notes_without_labels += 1
    
    # Calculate percentages and sort by count
    for label_data in label_counts.values():
        label_data['percentage'] = round((label_data['count'] / total_notes) * 100, 2)
    
    # Sort labels by count (descending)
    sorted_labels = sorted(label_counts.values(), key=lambda x: x['count'], reverse=True)
    
    # Prepare summary
    analysis = {
        'summary': {
            'total_notes_analyzed': total_notes,
            'notes_with_labels': notes_with_labels,
            'notes_without_labels': notes_without_labels,
            'total_unique_labels': len(label_counts),
            'label_coverage_percentage': round((notes_with_labels / total_notes) * 100, 2) if total_notes > 0 else 0
        },
        'labels': sorted_labels
    }
    
    return json.dumps(analysis)

@mcp.tool()
def get_note_colors() -> str:
    """
    Get available note colors and their current usage statistics.
    
    Returns:
        str: JSON string containing available colors and usage statistics
    """
    keep = get_client()
    
    # Get a sample note to access ColorValue enum
    notes = list(keep.find())
    if not notes:
        return json.dumps({"available_colors": [], "usage": {}})
    
    ColorValue = type(notes[0].color)
    
    # Get all available colors
    available_colors = []
    for color in ColorValue:
        available_colors.append({
            'name': color.name,
            'value': color.value,
            'api_name': color.name.upper()
        })
    
    # Get current color usage from all notes
    result = find()
    all_notes = json.loads(result)
    
    color_usage = {}
    for note in all_notes:
        color = note.get('color', 'DEFAULT')
        if color not in color_usage:
            color_usage[color] = 0
        color_usage[color] += 1
    
    return json.dumps({
        "available_colors": available_colors,
        "usage_statistics": color_usage,
        "total_notes": len(all_notes)
    })

def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
    