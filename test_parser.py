import pytest
from output_parser import parse_output

def test_parse_output_valid():
    output = """
    system
    <START>
    Title: Example Title
    Description: Example Description
    Price Range: $10-$20
    <END>
    Extra content here.
    """
    result = parse_output(output)
    assert result["title"] == "Example Title"
    assert result["description"] == "Example Description"
    assert result["price_range"] == "$10-$20"

def test_parse_output_empty():
    output = "No markers present"
    result = parse_output(output)
    assert result["title"] == ""
    assert result["description"] == ""
    assert result["price_range"] == ""

def test_parse_output_partial():
    output = """
    <START>
    Title: Test Title
    Description: Test Description
    <END>
    """
    result = parse_output(output)
    assert result["title"] == "Test Title"
    assert result["description"] == "Test Description"
    assert result["price_range"] == ""