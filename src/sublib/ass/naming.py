import re

# Canonical mapping (normalized_key -> Canonical Name)
# Key is lowercase with collapsed spaces.
STANDARD_SECTION_NAMES = {
    'script info': 'Script Info',
    'v4 styles': 'V4 Styles',
    'v4+ styles': 'V4+ Styles',
    'events': 'Events',
    'fonts': 'Fonts',
    'graphics': 'Graphics',
}

# Descriptor normalization (Section -> {normalized_key -> Canonical Name})
STANDARD_DESCRIPTOR_NAMES = {
    'script info': {
        'scripttype': 'ScriptType',
        'title': 'Title',
        'playresx': 'PlayResX',
        'playresy': 'PlayResY',
        'wrapstyle': 'WrapStyle',
        'scaledborderandshadow': 'ScaledBorderAndShadow',
        'collisions': 'Collisions',
        'ycbcr matrix': 'YCbCr Matrix',
        'timer': 'Timer',
    },
    'v4 styles': {
        'format': 'Format',
        'style': 'Style',
    },
    'v4+ styles': {
        'format': 'Format',
        'style': 'Style',
    },
    'events': {
        'format': 'Format',
        'dialogue': 'Dialogue',
        'comment': 'Comment',
        'picture': 'Picture',
        'sound': 'Sound',
        'movie': 'Movie',
        'command': 'Command',
    }
}

# Format field normalization (mapped by normalized section key)
STANDARD_FIELD_NAMES = {
    'styles': {
        'name': 'Name',
        'fontname': 'Fontname',
        'fontsize': 'Fontsize',
        'primarycolour': 'PrimaryColour',
        'secondarycolour': 'SecondaryColour',
        'tertiarycolour': 'TertiaryColour',
        'outlinecolour': 'OutlineColour',
        'backcolour': 'BackColour',
        'bold': 'Bold',
        'italic': 'Italic',
        'underline': 'Underline',
        'strikeout': 'StrikeOut',
        'scalex': 'ScaleX',
        'scaley': 'ScaleY',
        'spacing': 'Spacing',
        'angle': 'Angle',
        'borderstyle': 'BorderStyle',
        'outline': 'Outline',
        'shadow': 'Shadow',
        'alignment': 'Alignment',
        'encoding': 'Encoding',
        'marginl': 'MarginL',
        'marginr': 'MarginR',
        'marginv': 'MarginV',
        'marginleft': 'MarginL',    # Alias
        'marginright': 'MarginR',   # Alias
        'marginvertical': 'MarginV', # Alias
    },
    'events': {
        'layer': 'Layer',
        'marked': 'Marked',
        'start': 'Start',
        'end': 'End',
        'style': 'Style',
        'name': 'Name',
        'marginl': 'MarginL',
        'marginr': 'MarginR',
        'marginv': 'MarginV',
        'effect': 'Effect',
        'text': 'Text',
        'marginleft': 'MarginL',    # Alias
        'marginright': 'MarginR',   # Alias
        'marginvertical': 'MarginV', # Alias
    }
}

def normalize_key(name: str) -> str:
    """Standardize a string for use as an internal identity key.
    
    1. Lowercase
    2. Replace all whitespace (including tabs, newlines, etc) with single ASCII space
    3. Strip leading/trailing whitespace
    """
    if not name: return ""
    # Collapse whitespace
    key = re.sub(r'\s+', ' ', name)
    return key.strip().lower()

def get_canonical_name(name_or_key: str, context: str | None = None) -> str:
    """Lookup the pretty/canonical name for a given raw name or normalized key.
    
    Args:
        name_or_key: Original name from file or already normalized key
        context: Context for normalization:
                - 'SECTION': section headers
                - 'FIELD:section': format fields (e.g., 'FIELD:events', 'FIELD:v4+ styles')
                - 'section': descriptors within a section (e.g., 'events', 'script info')
    """
    key = normalize_key(name_or_key)
    
    if context == 'SECTION':
        return STANDARD_SECTION_NAMES.get(key, name_or_key.strip() if name_or_key else "")
    
    if context and context.startswith('FIELD:'):
        # Extract section part, handle v4/v4+ styles both as 'styles' for fields
        section_part = normalize_key(context[6:])
        
        # Determine mapping category
        category = 'events' if 'events' in section_part else 'styles'
        return STANDARD_FIELD_NAMES.get(category, {}).get(key, name_or_key.strip() if name_or_key else "")
        
    if context:
        ctx_key = normalize_key(context)
        if ctx_key in STANDARD_DESCRIPTOR_NAMES:
            return STANDARD_DESCRIPTOR_NAMES[ctx_key].get(key, name_or_key.strip() if name_or_key else "")
        
    return name_or_key.strip() if name_or_key else ""
