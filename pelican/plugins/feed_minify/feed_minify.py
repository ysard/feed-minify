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
"""A Pelican plugin to check & minify HTML fields before XML serialization into RSS & Atom feeds"""

import re
import logging

from pelican.plugins import signals  # pylint: disable=E0401
from feedgenerator import Atom1Feed  # pylint: disable=E0611
import minify_html  # pylint: disable=E0401

LOGGER = logging.getLogger(__name__)

# HTML fields used by feedgenerator:
# - Atom: content and description
# - RSS: description
HTML_FIELDS = ("content", "description")

INVALID_XML_CHARS = re.compile(
    r"[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]"
)


def xml_validation(item: dict, field: str, content: str) -> None:
    """Check XML feed for forbidden characters

    .. seealso:: https://www.w3.org/TR/xml/#charsets
    """
    match = INVALID_XML_CHARS.search(content) if content else None
    if match:
        pos = match.start()
        char = content[pos]
        err_context = content[max(0, pos - 30) : pos + 30]

        log_text = "[FEED DEBUG] Character not supported in XML 1.0!\n"
        log_text += f"  Article : {item.get('title')!r}\n"
        log_text += f"  URL     : {item.get('link')}\n"
        log_text += f"  Field   : {field}\n"
        log_text += f"  Position: {pos}\n"
        log_text += f"  Unicode : U+{ord(char):04X}\n"
        log_text += f"  Context : {err_context!r}"

        LOGGER.error(log_text)


def minify_feed(
    context: dict, feed: "Rss201rev2Feed | Atom1Feed", **kwargs  # pylint:disable=W0613
) -> None:
    """Check and minify HTML content before the feed is serialized"""
    if isinstance(feed, Atom1Feed):
        LOGGER.debug("Process Atom feed.")
    else:
        LOGGER.debug("Process RSS feed.")

    for item in feed.items:
        for field in HTML_FIELDS:
            content = item.get(field)
            if not isinstance(content, str) or not content:
                continue

            xml_validation(item, field, content)

            # Limit atom feeds to summaries only
            if (
                field == "content"
                and isinstance(feed, Atom1Feed)
                and context.get("ATOM_FEED_SUMMARY_ONLY")
            ):
                LOGGER.debug("Remove content from the Atom feed.")
                item["content"] = None
                continue

            # Minification
            minified = minify_html.minify(
                content,
                keep_comments=False,
                minify_css=False,
                minify_js=False,
            )

            if minified != content:
                LOGGER.debug(
                    "Feed HTML minified: %r (%s)",
                    item.get("title", "(untitled)"),
                    field,
                )
                item[field] = minified


def register():
    """Register callback invoked each time a feed gets generated"""
    signals.feed_generated.connect(minify_feed)
