"""ASS Script Info model."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from sublib.ass.models.raw import RawSection

from sublib.ass.naming import normalize_key, get_canonical_name




from .base import AssCoreSection


from .schema import FieldSchema, AssStructuredRecord

def _format_timer(v: float) -> str:
    return f"{v:.4f}"

def _format_bool_yes_no(v: bool) -> str:
    return "yes" if v else "no"

INFO_SCHEMA = {
    'scripttype': FieldSchema("v4.00+", str, canonical_name='ScriptType', python_prop='script_type'),
    'title': FieldSchema("", str, canonical_name='Title', python_prop='title'),
    'playresx': FieldSchema(384, int, canonical_name='PlayResX', python_prop='play_res_x'),
    'playresy': FieldSchema(288, int, canonical_name='PlayResY', python_prop='play_res_y'),
    'wrapstyle': FieldSchema(0, int, canonical_name='WrapStyle', python_prop='wrap_style'),
    'scaledborderandshadow': FieldSchema(True, bool, _format_bool_yes_no, canonical_name='ScaledBorderAndShadow', python_prop='scaled_border_and_shadow'),
    'collisions': FieldSchema("Normal", str, canonical_name='Collisions', python_prop='collisions'),
    'ycbcr_matrix': FieldSchema("None", str, canonical_name='YCbCr Matrix', python_prop='ycbcr_matrix'),
    'timer': FieldSchema(100.0, float, _format_timer, canonical_name='Timer', python_prop='timer'),
}

INFO_IDENTITY_SCHEMA = {s.normalized_key: s for s in INFO_SCHEMA.values()}
# Support aliases
INFO_IDENTITY_SCHEMA[normalize_key('Original Script')] = FieldSchema("", str, canonical_name='Original Script', python_prop='original_script')
INFO_IDENTITY_SCHEMA[normalize_key('Original Translation')] = FieldSchema("", str, canonical_name='Original Translation', python_prop='original_translation')
INFO_IDENTITY_SCHEMA[normalize_key('Original Editing')] = FieldSchema("", str, canonical_name='Original Editing', python_prop='original_editing')
INFO_IDENTITY_SCHEMA[normalize_key('Original Timing')] = FieldSchema("", str, canonical_name='Original Timing', python_prop='original_timing')
INFO_IDENTITY_SCHEMA[normalize_key('Synch Point')] = FieldSchema("", str, canonical_name='Synch Point', python_prop='synch_point')
INFO_IDENTITY_SCHEMA[normalize_key('Script Updated By')] = FieldSchema("", str, canonical_name='Script Updated By', python_prop='script_updated_by')
INFO_IDENTITY_SCHEMA[normalize_key('Update Details')] = FieldSchema("", str, canonical_name='Update Details', python_prop='update_details')


class AssScriptInfo(AssStructuredRecord):
    """Intelligent container for [Script Info] section with automatic type conversion and validation."""
    
    # Version-specific fields (field name: min_version)
    VERSION_FIELDS = {
        "wrapstyle": "v4.00+",
        "scaledborderandshadow": "v4.00+",
        "ycbcr matrix": "v4.00+",
    }

    def __init__(self, data: dict[str, Any] | None = None, original_name: str = "Script Info"):
        # Use object.__setattr__ to bypass the base class __setattr__ which traps everything as fields
        object.__setattr__(self, 'name', normalize_key("script info"))
        object.__setattr__(self, 'original_name', original_name)
        object.__setattr__(self, 'comments', [])
        object.__setattr__(self, '_diagnostics', [])
        object.__setattr__(self, '_display_names', {})
        
        super().__init__(INFO_IDENTITY_SCHEMA)
        
        if data:
            self.set_all(data)
    
    @classmethod
    def from_raw(cls, raw: RawSection) -> AssScriptInfo:
        """Layer 2: Semantic ingestion from a RawSection."""
        from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
        info = cls(original_name=raw.original_name)
        info.comments = list(raw.comments)
        
        # Pass 1: Aggregate records (Last-one-wins)
        aggregated: dict[str, tuple[str, str, int]] = {}
        for record in raw.records:
            norm_k = normalize_key(record.descriptor)
            if norm_k in aggregated:
                info._diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Duplicate key '{record.raw_descriptor}' in [Script Info]",
                    record.line_number, "DUPLICATE_KEY"
                ))
            aggregated[norm_k] = (record.raw_descriptor, record.value, record.line_number)

        # Pass 2: Detect Version
        script_type = 'v4.00+'
        if 'scripttype' in aggregated:
            raw_st, val, ln = aggregated['scripttype']
            if val in ('v4.00', 'v4.00+'):
                script_type = val
            else:
                info._diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Invalid ScriptType '{val}', defaulting to 'v4.00+'",
                    ln, "INVALID_SCRIPTTYPE"
                ))
            aggregated['scripttype'] = (raw_st, script_type, ln)
        else:
            info._diagnostics.append(Diagnostic(
                DiagnosticLevel.WARNING,
                "Missing 'ScriptType' in [Script Info], defaulting to 'v4.00+'",
                raw.line_number, "MISSING_SCRIPTTYPE"
            ))
            info['scripttype'] = script_type
        
        # Pass 3: Ingest
        for norm_k, (raw_key, value, line_number) in aggregated.items():
            info.set(norm_k, value, raw_key=raw_key, line_number=line_number, script_type=script_type)
            
        return info

    def set(self, key: str, value: Any, raw_key: str | None = None, line_number: int = 0, script_type: str | None = None) -> None:
        """Set a property with optional diagnostic reporting."""
        norm_key = normalize_key(key)
        
        if raw_key:
            self._display_names[norm_key] = raw_key

        # 1. Version Check
        if script_type and norm_key in self.VERSION_FIELDS:
            min_ver = self.VERSION_FIELDS[norm_key]
            if min_ver == "v4.00+" and "v4" in script_type.lower() and "+" not in script_type:
                from sublib.ass.diagnostics import Diagnostic, DiagnosticLevel
                self._diagnostics.append(Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Field '{raw_key or key}' is v4.00+ specific but ScriptType is '{script_type}'",
                    line_number, "VERSION_MISMATCH"
                ))

        # 2. Assign via __setitem__ (handles conversion via schema)
        self[norm_key] = value

    def render(self) -> str:
        """Render the complete section."""
        lines = [f"[{self.original_name}]"]
        for comment in self.comments:
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
            if norm_k in self._fields or norm_k in self._extra:
                lines.append(self._render_line(norm_k))
                written_keys.add(norm_k)
        
        for norm_k in sorted(set(self._fields.keys()) | set(self._extra.keys())):
            if norm_k not in written_keys:
                lines.append(self._render_line(norm_k))
                
        return "\n".join(lines)

    def _render_line(self, norm_key: str) -> str:
        # Get canonical or raw display name
        # Prioritize Schema's Canonical Name (Normalization)
        if norm_key in self._schema:
            display_name = self._schema[norm_key].canonical_name
        # Fallback to captured display name (Fidelity for custom fields)
        else:
            display_name = self._display_names.get(norm_key, norm_key.title())
                
        val = self.get(norm_key)
        if norm_key in self._schema:
            formatted = self._schema[norm_key].format(val)
        else:
            formatted = str(val)
            
        return f"{display_name}: {formatted}"

    def set_all(self, data: dict[str, Any]) -> None:
        for k, v in data.items():
            self.set(k, v)

    def to_dict(self) -> dict[str, Any]:
        return {**self._fields, **self._extra}

    @property
    def diagnostics(self) -> list:
        return self._diagnostics

