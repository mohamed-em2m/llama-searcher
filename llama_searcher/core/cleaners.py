import re
from typing import Tuple, Optional
from lxml import html
from llama_searcher.utils.logger import logger

SECTION_TAGS = {
    "section",
    "article",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}


def get_html_content(
    html_text: str,
    remove_tags: Tuple[str, ...] = ("script", "style"),
    remove_comments: bool = False,
    remove_lines: bool = True,  # Maintained from signature
    remove_spaces: bool = True,
    indent_val: int = 2,
) -> Optional[str]:
    if not html_text:
        return None

    try:
        # Parse HTML with lxml
        doc = html.fromstring(html_text)

        # Remove specified tags
        for tag_name in remove_tags:
            for tag in doc.xpath(f"//{tag_name}"):
                tag.getparent().remove(tag)

        # Get body or root element
        body = doc.xpath("//body")
        if body:
            body = body[0]
        else:
            body = doc

        # Remove comments if requested
        if remove_comments:
            for comment in body.xpath("//comment()"):
                comment.getparent().remove(comment)

        def recurse(node):
            pieces = []

            # Handle text content of current node
            if node.text:
                txt = node.text.strip()
                if txt:
                    if remove_spaces:
                        txt = re.sub(r"\s+", " ", txt)
                    pieces.append(txt)

            # Process child elements
            for child in node:
                if isinstance(
                    child.tag, str
                ):  # Skip comments and other non-element nodes
                    name = child.tag.lower()

                    # Section boundary
                    if name in SECTION_TAGS:
                        inner = recurse(child).strip()
                        pieces.append("\n\n" + inner + "\n\n")
                    elif name == "li":
                        inner = recurse(child).strip()
                        pieces.append("- " + inner + " ")
                    else:
                        pieces.append(recurse(child))

                # Handle tail text (text that comes after the element)
                if child.tail:
                    txt = child.tail.strip()
                    if txt:
                        if remove_spaces:
                            txt = re.sub(r"\s+", " ", txt)
                        pieces.append(txt)

            return "".join(pieces)

        out = recurse(body).strip()
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out

    except Exception as e:
        logger.error(f"Error in get_html_content: {e}")
        return None
