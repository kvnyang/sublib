# tests/test_parser.py
"""Tests for AssTextParser."""
import pytest

from sublib.ass.parser import AssTextParser
from sublib.exceptions import SubtitleParseError
from sublib.ass.tags import Position, Alignment
from sublib.ass.elements import AssOverrideTag, AssPlainText, AssNewLine


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
        assert isinstance(elements[1], AssNewLine)
        assert elements[1].hard == True
        assert isinstance(elements[2], AssPlainText)
        assert elements[2].content == "Line2"
    
    def test_parse_override_tag(self):
        parser = AssTextParser()
        elements = parser.parse("{\\fn思源黑体}中文")
        
        assert len(elements) == 2
        assert isinstance(elements[0], AssOverrideTag)
        assert elements[0].name == "fn"
        assert elements[0].value == "思源黑体"
        assert isinstance(elements[1], AssPlainText)
        assert elements[1].content == "中文"
    
    def test_parse_position_tag(self):
        parser = AssTextParser()
        elements = parser.parse("{\\pos(100,200)}Text")
        
        assert len(elements) == 2
        assert isinstance(elements[0], AssOverrideTag)
        assert elements[0].name == "pos"
        assert elements[0].value == Position(x=100.0, y=200.0)
        assert elements[0].is_event == True
    
    def test_parse_unknown_tag_raises_error(self):
        parser = AssTextParser()
        
        with pytest.raises(SubtitleParseError):
            parser.parse("{\\unknowntag123}Text")
    

