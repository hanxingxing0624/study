import re
from markdown import Markdown


def render_markdown(content: str, note_link_resolver=None) -> str:
    md = Markdown(
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "guess_lang": True,
            },
        },
    )
    if note_link_resolver:
        content = resolve_wikilinks(content, note_link_resolver)
    return md.convert(content)


def resolve_wikilinks(content: str, resolver) -> str:
    def replace_link(match):
        title = match.group(1)
        resolved_url = resolver(title)
        if resolved_url:
            return f'<a href="{resolved_url}" class="wiki-link">{title}</a>'
        return match.group(0)

    return re.sub(r"\[\[([^\]]+)\]\]", replace_link, content)
