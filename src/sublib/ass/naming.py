"""ASS Naming standardization logic."""

# Canonical names for normalization
STANDARD_SECTION_NAMES = {
    'script info': 'Script Info',
    'v4 styles': 'V4 Styles',
    'v4+ styles': 'V4+ Styles',
    'events': 'Events',
    'fonts': 'Fonts',
    'graphics': 'Graphics',
}

# Descriptor normalization (Section -> {lower_case -> Standard})
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

# Format field normalization (mapped by section for differentiation control)
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

def get_standard_name(raw_name: str, context: str | None = None) -> str:
    """Normalize a name to its canonical version if known.
    
    Args:
        raw_name: Original string from file
        context: Context for normalization:
                - 'SECTION': section headers
                - 'FIELD:section': format fields (e.g., 'FIELD:events', 'FIELD:v4+ styles')
                - 'section': descriptors within a section (e.g., 'events', 'script info')
    """
    clean = raw_name.strip()
    key = clean.lower()
    
    if context == 'SECTION':
        return STANDARD_SECTION_NAMES.get(key, clean)
    
    if context and context.startswith('FIELD:'):
        # Extract section part, handle v4/v4+ styles both as 'styles' for fields
        section_part = context[6:].lower()
        key_collapsed = key.replace(" ", "")
        
        # Determine mapping category
        category = 'events' if 'events' in section_part else 'styles'
        return STANDARD_FIELD_NAMES.get(category, {}).get(key_collapsed, clean)
        
    if context and context.lower() in STANDARD_DESCRIPTOR_NAMES:
        return STANDARD_DESCRIPTOR_NAMES[context.lower()].get(key, clean)
        
    return clean
