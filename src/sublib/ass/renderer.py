"""Rendering Engine for ASS models."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

from sublib.ass.naming import normalize_key, get_canonical_name

if TYPE_CHECKING:
    from sublib.ass.models.file import AssFile
    from sublib.ass.models.base import AssSection
    from sublib.ass.models.info import AssScriptInfo
    from sublib.ass.models.style import AssStyle, AssStyles
    from sublib.ass.models.event import AssEvent, AssEvents
    from sublib.ass.models.schema import AssStructuredRecord

class AssRenderer:
    """Orchestrates the serialization of Domain Models to ASS strings."""

    def render_file(self, ass_file: AssFile, auto_fill: bool = False) -> str:
        """Render the entire AssFile."""
        script_type = ass_file.script_info.get('scripttype', 'v4.00+')
        
        section_texts = []
        for section in ass_file.sections:
            text = self.render_section(section, script_type=script_type, auto_fill=auto_fill)
            if text:
                section_texts.append(text)
        
        return "\n\n".join(section_texts)

    def render_section(self, section: AssSection, script_type: str = "v4.00+", auto_fill: bool = False) -> str:
        """Polymorphic dispatch for section rendering."""
        from sublib.ass.models.info import AssScriptInfo
        from sublib.ass.models.style import AssStyles
        from sublib.ass.models.event import AssEvents
        from sublib.ass.models.base import AssRawSection

        if isinstance(section, AssScriptInfo):
            return self.render_script_info(section)
        elif isinstance(section, AssStyles):
            return self.render_styles(section, script_type=script_type, auto_fill=auto_fill)
        elif isinstance(section, AssEvents):
            return self.render_events(section, script_type=script_type, auto_fill=auto_fill)
        elif isinstance(section, AssRawSection):
            return section.render() # Raw sections still own their simple rendering
        return ""

    def render_script_info(self, info: AssScriptInfo) -> str:
        """Render [Script Info] section."""
        lines = [f"[{info.original_name}]"]
        for comment in info.comments:
            lines.append(f"; {comment}")
            
        standard_order = [
            'scripttype', 'title', 'original script', 'original translation', 
            'original editing', 'original timing', 'synch point', 'script updated by', 
            'update details', 'playresx', 'playresy', 'playdepth', 'timer', 
            'wrapstyle', 'scaledborderandshadow'
        ]
        
        written_keys = set()
        for k in standard_order:
            norm_k = normalize_key(k)
            if norm_k in info._fields or norm_k in info._extra:
                lines.append(self._render_info_line(info, norm_k))
                written_keys.add(norm_k)
        
        for norm_k in sorted(set(info._fields.keys()) | set(info._extra.keys())):
            if norm_k not in written_keys:
                lines.append(self._render_info_line(info, norm_k))
                
        return "\n".join(lines)

    def _render_info_line(self, info: AssScriptInfo, norm_key: str) -> str:
        name, value = self.render_field(info, norm_key)
        return f"{name}: {value}"

    def render_styles(self, styles: AssStyles, script_type: str = "v4.00+", auto_fill: bool = False) -> str:
        """Render [V4+ Styles] section."""
        lines = [f"[{styles.original_name}]"]
        for comment in styles.comments:
            lines.append(f"; {comment}")
            
        if styles.raw_format_fields:
            from sublib.ass.models.style import STYLE_IDENTITY_SCHEMA
            out_format = [
                STYLE_IDENTITY_SCHEMA[normalize_key(f)].canonical_name 
                if normalize_key(f) in STYLE_IDENTITY_SCHEMA else f 
                for f in styles.raw_format_fields
            ]
        else:
            out_format = styles.get_explicit_format(script_type)
            
        lines.append(f"Format: {', '.join(out_format)}")
        
        for style in styles:
            lines.append(self.render_style_row(style, out_format, auto_fill=auto_fill))
            
        for record in styles._custom_records:
            lines.append(f"{record.raw_descriptor}: {record.value}")
            
        return "\n".join(lines)

    def render_style_row(self, style: AssStyle, format_fields: list[str], auto_fill: bool = False) -> str:
        """Render a single style row."""
        descriptor = get_canonical_name("Style", context="v4+ styles")
        fields_str = self.render_record(style, format_fields, auto_fill=auto_fill)
        return f"{descriptor}: {fields_str}"

    def render_events(self, events: AssEvents, script_type: str = "v4.00+", auto_fill: bool = False) -> str:
        """Render [Events] section."""
        lines = [f"[{events.original_name}]"]
        for comment in events.comments:
            lines.append(f"; {comment}")
            
        if events.raw_format_fields:
            from sublib.ass.models.event import EVENT_IDENTITY_SCHEMA
            out_format = [
                EVENT_IDENTITY_SCHEMA[normalize_key(f)].canonical_name 
                if normalize_key(f) in EVENT_IDENTITY_SCHEMA else f 
                for f in events.raw_format_fields
            ]
        else:
            # Fallback for events - usually very standardized
            out_format = ['Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']

        lines.append(f"Format: {', '.join(out_format)}")
        
        for event in events:
            lines.append(self.render_event_row(event, out_format, auto_fill=auto_fill))
            
        for record in events._custom_records:
            lines.append(f"{record.raw_descriptor}: {record.value}")
            
        return "\n".join(lines)

    def render_event_row(self, event: AssEvent, format_fields: list[str], auto_fill: bool = False) -> str:
        """Render a single event row."""
        # Ensure AST-to-text normalization
        event._ensure_ast()
        
        descriptor = event._type
        fields_str = self.render_record(event, format_fields, auto_fill=auto_fill)
        return f"{descriptor}: {fields_str}"

    def render_record(self, record: AssStructuredRecord, format_fields: list[str], auto_fill: bool = False) -> str:
        """Render fields as a comma-separated string."""
        parts = []
        for raw_f in format_fields:
            norm_f = normalize_key(raw_f)
            
            if norm_f in record._schema:
                schema = record._schema[norm_f]
                val = getattr(record, schema.python_prop) if schema.python_prop else record._fields.get(schema.normalized_key)
                
                if val is None and auto_fill:
                    val = schema.default
                parts.append(schema.format(val) if val is not None else "")
            else:
                val = record._extra.get(norm_f, "")
                parts.append(str(val))
        return ",".join(parts)

    def render_field(self, record: AssStructuredRecord, norm_key: str, display_name: str | None = None) -> tuple[str, str]:
        """Render a single field as (display_name, formatted_value)."""
        if not display_name:
            if norm_key in record._schema:
                display_name = record._schema[norm_key].canonical_name
            else:
                display_name = norm_key.title()
                
        val = record.get(norm_key)
        if norm_key in record._schema:
            formatted = record._schema[norm_key].format(val)
        else:
            formatted = str(val)
            
        return display_name, formatted
