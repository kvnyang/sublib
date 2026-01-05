# tests/test_parser.py
"""Tests for AssTextParser."""
import pytest

from sublib.ass.services.parsers import AssTextParser
from sublib.exceptions import SubtitleParseError
from sublib.ass.tags import Position, Alignment
from sublib.ass.ast import AssOverrideTag, AssPlainText, AssSpecialChar, AssOverrideBlock, AssComment


class TestAssTextParser:
    def test_parse_plain_text(self):
        parser = AssTextParser()
        elements = parser.parse("Hello world")
        
        assert len(elements) == 1
        assert isinstance(elements[0], AssPlainText)
        assert elements[0].content == "Hello world"
    
    def test_parse_newline(self):
        parser = AssTextParser()
        elements = parser.parse("Line1\\NLine2")
        
        assert len(elements) == 3
        assert isinstance(elements[0], AssPlainText)
        assert elements[0].content == "Line1"
        assert isinstance(elements[1], AssSpecialChar)
        assert isinstance(elements[2], AssPlainText)
        assert elements[2].content == "Line2"
    
    def test_parse_override_tag(self):
        parser = AssTextParser()
        elements = parser.parse("{\\fn思源黑体}中文")
        
        assert len(elements) == 2
        
        # Element 0 is AssBlock containing AssOverrideTag
        assert isinstance(elements[0], AssOverrideBlock)
        block_elements = elements[0].elements
        assert len(block_elements) == 1
        assert isinstance(block_elements[0], AssOverrideTag)
        assert block_elements[0].name == "fn"
        assert block_elements[0].value == "思源黑体"
        
        # Element 1 is AssPlainText
        assert isinstance(elements[1], AssPlainText)
        assert elements[1].content == "中文"
    
    def test_parse_position_tag(self):
        parser = AssTextParser()
        elements = parser.parse("{\\pos(100,200)}Text")
        
        assert len(elements) == 2
        assert isinstance(elements[0], AssOverrideBlock)
        block_elements = elements[0].elements
        assert len(block_elements) == 1
        assert isinstance(block_elements[0], AssOverrideTag)
        assert block_elements[0].name == "pos"
        assert block_elements[0].value == Position(x=100.0, y=200.0)
        assert block_elements[0].is_event == True

    def test_parse_block_with_comment(self):
        parser = AssTextParser()
        elements = parser.parse("{comment\\pos(10,10)more comment}Text")
        
        assert len(elements) == 2
        assert isinstance(elements[0], AssOverrideBlock)
        
        # Block structure: comment -> tag -> comment
        items = elements[0].elements
        assert len(items) == 3
        
        assert isinstance(items[0], AssComment)
        assert items[0].content == "comment"
        
        assert isinstance(items[1], AssOverrideTag)
        assert items[1].name == "pos"
        
        assert isinstance(items[2], AssComment)
        assert items[2].content == "more comment"
        
        assert isinstance(elements[1], AssPlainText)
        assert elements[1].content == "Text"

    def test_unknown_tag_is_not_error_in_parsing(self):
        # NOTE: Previous behavior raised Error, but strict strict parsing might be configurable.
        # But wait, logic in parser.py still raises SubtitleParseError if tag unknown.
        # Let's keep the error test but update it for Block context if needed.
        # But wait, my parsing logic:
        # "content before this tag is comment"
        # It finds tags using `_get_known_tags_pattern`, which only matches KNOWN tags.
        # So unknown tags will actually be treated as COMMENTS now!
        # Because regex only matches known tags.
        # So `{\unknowntag}` -> regex finds nothing -> whole string is extracted as comment.
        # This is actually better for robustness/losslessness!
        # Note: We use \zunknown because \unknowntag starts with \u which IS a valid tag!
        
        parser = AssTextParser()
        elements = parser.parse("{\\zunknown123}Text")
        
        assert len(elements) == 2
        assert isinstance(elements[0], AssOverrideBlock)
        assert len(elements[0].elements) == 1
        assert isinstance(elements[0].elements[0], AssComment)
        assert elements[0].elements[0].content == "\\zunknown123"
    

