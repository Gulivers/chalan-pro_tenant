"""Allowlist sanitizer for work-order notes stored as Quill HTML."""
from html import escape
from html.parser import HTMLParser

_ALLOWED_TAGS = {
    'p', 'br', 'strong', 'em', 'u', 's', 'ol', 'ul', 'li',
    'a', 'blockquote', 'h1', 'h2', 'h3', 'pre', 'span',
}
_SKIP_TAGS = {'script', 'style', 'iframe', 'object', 'embed', 'link', 'meta'}
_LIST_VALUES = {'ordered', 'bullet', 'checked', 'unchecked'}


def _safe_href(value: str) -> str | None:
    href = (value or '').strip()
    lowered = href.lower()
    if lowered.startswith(('http://', 'https://', 'mailto:')):
        return href
    if href.startswith('/') and not href.startswith('//'):
        return href
    return None


def _safe_class(value: str) -> str | None:
    tokens = [part for part in (value or '').split() if part.startswith('ql-')]
    return ' '.join(tokens) or None


class _NoteHtmlSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth or tag not in _ALLOWED_TAGS:
            return
        cleaned = []
        for name, value in attrs:
            name = (name or '').lower()
            if name.startswith('on'):
                continue
            if tag == 'a' and name == 'href':
                href = _safe_href(value or '')
                if href:
                    cleaned.append(('href', href))
                    cleaned.append(('rel', 'noopener noreferrer'))
            elif tag == 'li' and name == 'data-list' and (value or '') in _LIST_VALUES:
                cleaned.append(('data-list', value))
            elif name == 'class':
                css = _safe_class(value or '')
                if css:
                    cleaned.append(('class', css))
        attr_text = ''.join(f' {name}="{escape(val, quote=True)}"' for name, val in cleaned)
        if tag == 'br':
            self.parts.append('<br>')
            return
        self.parts.append(f'<{tag}{attr_text}>')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in _SKIP_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if self._skip_depth or tag not in _ALLOWED_TAGS or tag == 'br':
            return
        self.parts.append(f'</{tag}>')

    def handle_data(self, data):
        if self._skip_depth or not data:
            return
        self.parts.append(escape(data))


def sanitize_note_html(value):
    if value is None:
        return value
    text = str(value)
    if not text.strip():
        return text
    parser = _NoteHtmlSanitizer()
    parser.feed(text)
    parser.close()
    return ''.join(parser.parts)
