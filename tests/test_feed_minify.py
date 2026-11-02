# This file is part of Feed-Minify for Pelican
#
# Copyright (C) 2026 Ysard
#
# Shinxsearch for Pelican is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Shinxsearch for Pelican is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinxsearch for Pelican.
# If not, see <http://www.gnu.org/licenses/>.
"""The test suite covers comment removal in both feed HTML fields, processing of
multiple feed items, preservation of non-HTML metadata, skipping missing/empty
or non-string values and registration on Pelican's `feed_generated` signal.
Tests also cover HTML validation and content removal for Atom feeds.
"""
import logging
from types import SimpleNamespace

import pytest

from pelican.plugins import feed_minify


@pytest.mark.parametrize(
    "codepoint",
    [
        0x0000,
        0x0008,
        0x000B,
    ],
    ids=lambda cp: f"U+{cp:04X}",
)
def test_characters_rejects_invalid_xml_10_characters(codepoint, caplog):
    """Characters forbidden by XML 1.0 must be detected"""
    item = {
        "title": "An article",
        "content": f"before{chr(codepoint)}after",
    }
    feed = SimpleNamespace(items=[item])

    with caplog.at_level(logging.ERROR):
        feed_minify.minify_feed(context={}, feed=feed)

    message = caplog.text

    # The error must identify the offending character.
    assert f"U+{codepoint:04X}" in message

    # The error must report its position in the input string.
    assert "Position: 6" in message

    # The error must provide the surrounding context.
    assert repr(item["content"]) in message


def test_atom_remove_content(monkeypatch):
    """Test effect of ATOM_FEED_SUMMARY_ONLY global setting on Atom feed

    The content should be removed. Thus the description of the feed will
    only contain the summaries.
    """
    class FakeAtomFeed:
        def __init__(self, items=None):
            self.items = items or []

    item = {
        "title": "An article",
        "link": "https://example.com/",
        "content": "<p>Body</p>",
        "description": "<p>Summary</p>",
    }

    feed = FakeAtomFeed(items=[item])

    monkeypatch.setattr(
        # Patch the real namespace not the imported one via __init__.py
        feed_minify.feed_minify,
        "Atom1Feed",
        FakeAtomFeed,
    )

    feed_minify.minify_feed(context={"ATOM_FEED_SUMMARY_ONLY": True}, feed=feed)

    # The item is modified in place
    item = feed.items[0]
    assert item["content"] is None
    assert "Summary" in item["description"]


def test_minify_feed_processes_content_and_description():
    """Check the removing of comments in content & description fields"""
    item = {
        "title": "An article",
        "content": "<p>Body</p><!-- body comment -->",
        "description": "<p>Summary</p><!-- summary comment -->",
    }
    feed = SimpleNamespace(items=[item])

    feed_minify.minify_feed(context={}, feed=feed)

    assert "<!--" not in item["content"]
    assert "<!--" not in item["description"]
    assert "Body" in item["content"]
    assert "Summary" in item["description"]


def test_minify_feed_processes_multiple_items():
    """Check the removing of comments for multiple articles in a feed"""
    feed = SimpleNamespace(
        items=[
            {"title": "First", "content": "<p>First</p><!-- comment -->"},
            {"title": "Second", "content": "<p>Second</p><!-- comment -->"},
        ]
    )

    feed_minify.minify_feed(context={}, feed=feed)

    assert all("<!--" not in item["content"] for item in feed.items)
    assert "First" in feed.items[0]["content"]
    assert "Second" in feed.items[1]["content"]


def test_minify_feed_does_not_modify_title_or_other_metadata():
    """Check that only content & description field are modified"""
    title = "<b>Title</b><!-- deliberately not treated as a feed HTML field -->"
    item = {
        "title": title,
        "link": "https://example.test/article/",
        "author_name": "Author",
        "content": "<p>Body</p><!-- remove this -->",
        "custom_metadata": "<p>Leave this untouched</p><!-- keep this -->",
    }
    feed = SimpleNamespace(items=[item])

    feed_minify.minify_feed(context={}, feed=feed)

    assert item["title"] == title
    assert item["link"] == "https://example.test/article/"
    assert item["author_name"] == "Author"
    assert item["custom_metadata"] == "<p>Leave this untouched</p><!-- keep this -->"
    assert "<!--" not in item["content"]


def test_minify_feed_skips_missing_empty_and_non_string_values(monkeypatch):
    """Check behavior if field value is missing, empty, or with wrong type"""
    def unexpected_minify(*args, **kwargs):
        pytest.fail("minify_html.minify must not be called for empty/non-string values")

    monkeypatch.setattr(feed_minify.minify_html, "minify", unexpected_minify)

    feed = SimpleNamespace(
        items=[
            {},
            {"content": None, "description": None},
            {"content": "", "description": ""},
            {"content": 123, "description": ["not", "HTML"]},
        ]
    )

    feed_minify.minify_feed(context={}, feed=feed)

    assert feed.items[1]["content"] is None
    assert feed.items[2]["content"] == ""
    assert feed.items[3]["content"] == 123
    assert feed.items[3]["description"] == ["not", "HTML"]


def test_register_connects_minifier_to_feed_generated(monkeypatch):
    """Check the registration on the `feed_generated` signal"""
    connected_receivers = []

    class FakeSignal:
        def connect(self, receiver):
            connected_receivers.append(receiver)

    monkeypatch.setattr(
        feed_minify.signals,
        "feed_generated",
        FakeSignal(),
    )

    feed_minify.register()

    assert connected_receivers == [feed_minify.minify_feed]
