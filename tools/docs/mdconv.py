"""Tiny markdown subset -> HTML for the docs site: headings, paragraphs, bullet lists, > blockquotes, pipe tables, **bold**, *italic*, `code`, [links](url)."""
import html
import re


def md_inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![*\w])\*([^*]+)\*(?![*\w])', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s


def md_to_html(text, skip_first_h1=False):
    out, para, items, quote, table = [], [], [], [], []

    def flush():
        nonlocal para, items, quote, table
        if para:
            out.append('<p>' + md_inline(' '.join(para)) + '</p>')
            para = []
        if items:
            out.append('<ul>' + ''.join(f'<li>{md_inline(i)}</li>' for i in items) + '</ul>')
            items = []
        if quote:
            out.append('<blockquote>' + '<br>'.join(md_inline(q) for q in quote) + '</blockquote>')
            quote = []
        if table:
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in table if not re.match(r'^\s*\|?[\s:|-]+\|?\s*$', r)]
            if rows:
                head, body = rows[0], rows[1:]
                out.append('<div class="tablewrap"><table><tr>' + ''.join(f'<th>{md_inline(c)}</th>' for c in head) + '</tr>'
                           + ''.join('<tr>' + ''.join(f'<td>{md_inline(c)}</td>' for c in r) + '</tr>' for r in body) + '</table></div>')
            table = []

    first = True
    for line in text.splitlines():
        if line.startswith('# '):
            flush()
            if not (skip_first_h1 and first):
                out.append(f'<h1>{md_inline(line[2:])}</h1>')
            first = False
        elif line.startswith('## '):
            flush()
            out.append(f'<h2>{md_inline(line[3:])}</h2>')
        elif line.startswith('### '):
            flush()
            out.append(f'<h3>{md_inline(line[4:])}</h3>')
        elif line.startswith('|'):
            if para or items or quote:
                flush()
            table.append(line)
        elif line.startswith('> '):
            if para or items or table:
                flush()
            quote.append(line[2:])
        elif line.startswith('- '):
            if para or quote or table:
                flush()
            items.append(line[2:])
        elif not line.strip():
            flush()
        else:
            if items or quote or table:
                flush()
            para.append(line.strip())
    flush()
    return '\n'.join(out)
