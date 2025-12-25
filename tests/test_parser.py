# tests/test_parser.py
"""Tests for AssTextParser."""
import pytest

from sublib import AssTextParser, SubtitleParseError, Position, Alignment
from sublib.formats.ass.elements import AssOverrideTag, AssPlainText, AssNewLine


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
    
    def test_get_event_tags(self):
        parser = AssTextParser()
        elements = parser.parse("{\\pos(100,200)\\an8}{\\fn思源黑体}Text")
        
        event_tags = parser.get_event_tags(elements)
        
        assert "pos" in event_tags
        assert event_tags["pos"] == Position(x=100.0, y=200.0)
        assert "an" in event_tags
        assert event_tags["an"] == Alignment(value=8)
        assert "fn" not in event_tags  # inline, not event-level
    
    def test_get_text_segments(self):
        parser = AssTextParser()
        elements = parser.parse("{\\fn思源黑体\\b1}中文{\\fn微软雅黑}English")
        
        segments = parser.get_text_segments(elements)
        
        assert len(segments) == 2
        
        # First segment
        tags1, text1 = segments[0]
        assert text1 == "中文"
        assert len(tags1) == 2
        assert tags1[0].name == "fn"
        assert tags1[0].value == "思源黑体"
        assert tags1[1].name == "b"
        assert tags1[1].value == 1
        
        # Second segment
        tags2, text2 = segments[1]
        assert text2 == "English"
        assert len(tags2) == 1
        assert tags2[0].name == "fn"
        assert tags2[0].value == "微软雅黑"
