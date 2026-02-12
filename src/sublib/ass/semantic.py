"""Semantic Parsing Engine for ASS models."""
from __future__ import annotations
from typing import TYPE_CHECKING, Any

from sublib.ass.naming import normalize_key, AssEventType
from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection, RawRecord
    from sublib.ass.models.info import AssScriptInfo
    from sublib.ass.models.style import AssStyle, AssStyles
    from sublib.ass.models.event import AssEvent, AssEvents

class SemanticParser:
    """Orchestrates the conversion of RawRecords to Typed Domain Models."""

    def ingest_script_info(self, raw: RawSection) -> AssScriptInfo:
        """Ingest [Script Info] section."""
        from sublib.ass.models.info import AssScriptInfo, INFO_IDENTITY_SCHEMA
        info = AssScriptInfo(original_name=raw.original_name)
        info.comments = list(raw.comments)
        
        # 1. Aggregate records (Last-one-wins)
        aggregated: dict[str, tuple[str, str, int]] = {}
        for record in raw.records:
            norm_k = normalize_key(record.descriptor)
            if norm_k in aggregated:
                info.diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Duplicate key '{record.raw_descriptor}' in [Script Info]",
                    record.line_number, "DUPLICATE_KEY"
                ))
            aggregated[norm_k] = (record.raw_descriptor, record.value, record.line_number)

        # 2. Detect Version
        script_type = 'v4.00+'
        if 'scripttype' in aggregated:
            raw_st, val, ln = aggregated['scripttype']
            if val in ('v4.00', 'v4.00+'):
                script_type = val
            else:
                info.diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Invalid ScriptType '{val}', defaulting to 'v4.00+'",
                    ln, "INVALID_SCRIPTTYPE"
                ))
            aggregated['scripttype'] = (raw_st, script_type, ln)
        else:
            info.diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                "Missing 'ScriptType' in [Script Info], defaulting to 'v4.00+'",
                raw.line_number, "MISSING_SCRIPTTYPE"
            ))
            info['scripttype'] = script_type
        
        # 3. Ingest
        for norm_k, (raw_key, value, line_number) in aggregated.items():
            self._ingest_info_field(info, norm_k, value, raw_key, line_number, script_type)
            
        return info

    def _ingest_info_field(self, info: AssScriptInfo, norm_key: str, value: str, raw_key: str, line_number: int, script_type: str):
        # Version Check logic (moved from AssScriptInfo.set)
        if norm_key in info.VERSION_FIELDS:
            min_ver = info.VERSION_FIELDS[norm_key]
            if min_ver == "v4.00+" and "v4" in script_type.lower() and "+" not in script_type:
                info.diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Field '{raw_key or norm_key}' is v4.00+ specific but ScriptType is '{script_type}'",
                    line_number, "VERSION_MISMATCH"
                ))
        
        if raw_key:
            info._display_names[norm_key] = raw_key
            
        info[norm_key] = value

    def ingest_styles(self, raw: RawSection, style_format: list[str] | None = None, auto_fill: bool = True) -> AssStyles:
        """Ingest [V4+ Styles] section."""
        from sublib.ass.models.style import AssStyles, AssStyle, STYLE_IDENTITY_SCHEMA
        styles = AssStyles(original_name=raw.original_name)
        styles.comments = list(raw.comments)
        
        if style_format:
            styles.raw_format_fields = list(style_format)
        else:
            styles.raw_format_fields = list(raw.raw_format_fields) if raw.raw_format_fields else None
            
        file_format_fields = raw.format_fields
        if not file_format_fields:
            styles.diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, "Missing Format line in Styles section", raw.line_number, "MISSING_FORMAT"))
            return styles

        for record in raw.records:
            if normalize_key(record.descriptor) == 'style':
                parts = [p.strip() for p in record.value.split(',', len(file_format_fields)-1)]
                data = {name: val for name, val in zip(file_format_fields, parts)}
                
                style = self.create_style(data, record.line_number, auto_fill, styles.diagnostics)
                styles.set(style)
            else:
                styles._custom_records.append(record)
                
        return styles

    def create_style(self, data: dict[str, str], line_number: int = 0, auto_fill: bool = True, diagnostics: list[Diagnostic] | None = None) -> AssStyle:
        """Create AssStyle from raw string dictionary."""
        from sublib.ass.models.style import AssStyle, STYLE_IDENTITY_SCHEMA
        parsed_fields = {}
        extra_fields = {}
        
        for k, v in data.items():
            norm_k = normalize_key(k)
            v_str = str(v).strip()
            
            if norm_k in STYLE_IDENTITY_SCHEMA:
                schema = STYLE_IDENTITY_SCHEMA[norm_k]
                parsed_fields[schema.normalized_key] = schema.convert(v_str, diagnostics=diagnostics, line_number=line_number)
            else:
                extra_fields[norm_k] = v_str
        
        if auto_fill:
            for norm_key, schema in STYLE_IDENTITY_SCHEMA.items():
                if norm_key == schema.normalized_key and norm_key not in parsed_fields:
                    parsed_fields[norm_key] = schema.default
                    
        return AssStyle(parsed_fields, extra_fields=extra_fields)

    def ingest_events(self, raw: RawSection, script_type: str | None = None, event_format: list[str] | None = [], auto_fill: bool = True) -> AssEvents:
        """Ingest [Events] section."""
        from sublib.ass.models.event import AssEvents, AssEvent, EVENT_IDENTITY_SCHEMA
        events = AssEvents(original_name=raw.original_name)
        events.comments = list(raw.comments)
        
        if event_format:
            events.raw_format_fields = list(event_format)
        else:
            events.raw_format_fields = list(raw.raw_format_fields) if raw.raw_format_fields else None
            
        file_format_fields = raw.format_fields
        if not file_format_fields:
            events.diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, "Missing Format line in Events section", raw.line_number, "MISSING_FORMAT"))
            return events

        # Determine Ingestion Slice logic
        is_v4 = script_type and 'v4' in script_type.lower() and '+' not in script_type
        if event_format:
            ingest_keys = {normalize_key(f) for f in event_format}
        elif event_format is None:
            ingest_keys = set(file_format_fields)
        else:
            if is_v4:
                ingest_keys = {'layer', 'start', 'end', 'style', 'name', 'marginl', 'marginr', 'marginv', 'effect', 'text', 'marked'}
            else:
                ingest_keys = {'layer', 'start', 'end', 'style', 'name', 'marginl', 'marginr', 'marginv', 'effect', 'text'}

        standard_descriptors = {normalize_key(t) for t in AssEventType.get_standard_types()}
        for record in raw.records:
            try:
                parts = [p.strip() for p in record.value.split(',', len(file_format_fields)-1)]
                record_dict = {name: val for name, val in zip(file_format_fields, parts)}
                
                # Apply Slicing Filter
                filtered_dict = {k: v for k, v in record_dict.items() if k in ingest_keys}
                
                if normalize_key(record.descriptor) in standard_descriptors:
                    event = self.create_event(filtered_dict, record.descriptor, record.line_number, auto_fill, events.diagnostics)
                    events.append(event)
                    
                    # Field count check
                    actual_count = len(record.value.split(','))
                    expected_count = len(file_format_fields)
                    if actual_count < expected_count:
                        events.diagnostics.append(Diagnostic(
                            DiagnosticLevel.WARNING,
                            f"Field count mismatch in event at line {record.line_number}: found {actual_count}, expected {expected_count}",
                            record.line_number, "FIELD_COUNT_MISMATCH"
                        ))
                else:
                    events._custom_records.append(record)
            except Exception as e:
                events.diagnostics.append(Diagnostic(DiagnosticLevel.ERROR, f"Failed to parse event: {e}", record.line_number, "EVENT_PARSE_ERROR"))

        return events

    def create_event(self, data: dict[str, str], event_type: str = "Dialogue", line_number: int = 0, auto_fill: bool = True, diagnostics: list[Diagnostic] | None = None) -> AssEvent:
        """Create AssEvent from raw string dictionary."""
        from sublib.ass.models.event import AssEvent, EVENT_IDENTITY_SCHEMA
        parsed_fields = {}
        extra_fields = {}
        
        for k, v in data.items():
            norm_k = normalize_key(k)
            v_str = str(v).strip()
            
            if norm_k in EVENT_IDENTITY_SCHEMA:
                schema = EVENT_IDENTITY_SCHEMA[norm_k]
                parsed_fields[schema.normalized_key] = schema.convert(v_str, diagnostics=diagnostics, line_number=line_number)
            else:
                extra_fields[norm_k] = v_str
        
        if auto_fill:
            for norm_key, schema in EVENT_IDENTITY_SCHEMA.items():
                if norm_key == schema.normalized_key and norm_key not in parsed_fields:
                    parsed_fields[norm_key] = schema.default
                    
        return AssEvent(parsed_fields, type=event_type, line_number=line_number, extra_fields=extra_fields)
