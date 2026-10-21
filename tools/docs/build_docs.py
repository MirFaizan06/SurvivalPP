"""Builds the GitHub Pages site (docs/) from tools/docs/pages/*.html fragments + CHANGELOG.md.
    python tools/docs/build_docs.py
Add a page: drop a fragment into pages/, add it to PAGES. The version shown comes from tools/version.json."""
import html, json, re, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'docs'
VER = '.'.join(map(str, json.loads((ROOT / 'tools' / 'version.json').read_text())['version']))
REPO = 'https://github.com/MirFaizan06/SurvivalPP'

PAGES = [  # (file, nav title, page title)
    ('index.html', 'Home', 'Survival++ | Eclipsed Realms'),
    ('world.html', 'World & Survival', 'World & Survival'),
    ('creatures.html', 'Creatures', 'Animals, Monsters & Bosses'),
    ('systems.html', 'Systems', 'Stasis Chambers, Sanctum & Crafting'),
    ('changelog.html', 'Changelog', 'Changelog'),
]

TEMPLATE = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - Survival++</title>
<meta name="description" content="Survival++ | Eclipsed Realms - a survival expansion for Minecraft Bedrock by Tech Bytes Design.">
<link rel="icon" href="img/icon_1024.png"><link rel="stylesheet" href="style.css"></head>
<body>
<header class="site"><div class="bar">
<a class="brand" href="index.html"><img src="img/icon_1024.png" alt=""><span>Survival++ <small>Eclipsed Realms</small></span></a>
<nav>{nav}</nav></div></header>
<main>{body}</main>
<footer>Survival++ | Eclipsed Realms v{ver} &middot; by Tech Bytes Design &middot; <a href="{repo}">GitHub</a> &middot;
Not an official Minecraft product; not approved by or associated with Mojang or Microsoft.</footer>
</body></html>'''


def md_inline(s):
    s = html.escape(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s


def changelog_html():
    out, in_list = ['<h1>Changelog</h1><p class="lead">Every release, newest first. Version numbers are <code>major.minor.patch</code>.</p><div class="log">'], False
    for line in (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8').splitlines():
        if line.startswith('# ') or not line.strip():
            continue
        if line.startswith('## '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h2>{md_inline(line[3:])}</h2>')
        elif line.startswith('### '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h3>{md_inline(line[4:])}</h3>')
        elif line.startswith('- '):
            if not in_list: out.append('<ul>'); in_list = True
            out.append(f'<li>{md_inline(line[2:])}</li>')
        elif line.startswith('All notable'):
            continue
        else:
            out.append(f'<p>{md_inline(line)}</p>')
    if in_list: out.append('</ul>')
    out.append('</div>')
    return '\n'.join(out)


def main():
    OUT.mkdir(exist_ok=True)
    shutil.copy(HERE / 'style.css', OUT / 'style.css')
    (OUT / '.nojekyll').write_text('')
    for fname, nav_title, title in PAGES:
        nav = ''.join(f'<a href="{f}"{" class=on" if f == fname else ""}>{n}</a>' for f, n, _ in PAGES)
        body = changelog_html() if fname == 'changelog.html' else (HERE / 'pages' / fname).read_text(encoding='utf-8').replace('{VER}', VER)
        (OUT / fname).write_text(TEMPLATE.format(title=html.escape(title), nav=nav, body=body, ver=VER, repo=REPO), encoding='utf-8')
    print('docs built ->', OUT, f'(v{VER})')


if __name__ == '__main__':
    main()
