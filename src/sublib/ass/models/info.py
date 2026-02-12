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
    



    def set_all(self, data: dict[str, Any]) -> None:
        for k, v in data.items():
            self[k] = v

    def to_dict(self) -> dict[str, Any]:
        return {**self._fields, **self._extra}

    @property
    def diagnostics(self) -> list:
        return self._diagnostics

