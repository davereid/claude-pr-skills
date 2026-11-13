#!/usr/bin/env python3
"""Converts a drupal.org README.md to HTML for the project page.

Leaves out the title, the table of contents and the "For a full description
of the module" link to the project page, and turns in-page links into
plain text, since drupal.org's project page headings have no IDs. HTML
comments in the README are left out.

Relative links, such as docs/page.md, are made absolute with --base, the
URL of the project's files on its default branch, e.g.
https://git.drupalcode.org/project/<name>/-/blob/<branch>/

With --docs, the URL of the project's MkDocs site (e.g.
https://project.pages.drupalcode.org/<name>/), links to docs/<page>.md go to
the page's URL there instead.

Usage: python3 readme2html.py [--base=URL] [--docs=URL] README.md > README.html
"""

import html, re, sys
from urllib.parse import urljoin

base = docs = None
relative = []

def href(url):
    # Leave absolute URLs, site-absolute paths and mail links alone.
    if re.match(r'[a-z][a-z0-9+.-]*:|/', url, re.I):
        return url
    m = re.match(r'docs/(.+?)\.md(#.*)?$', url)
    if docs and m:
        # MkDocs serves docs/<page>.md at <page>/, and docs/index.md at the root.
        page = re.sub(r'(^|/)index$', r'\1', m.group(1))
        return docs + (page + '/' if page and not page.endswith('/') else page) + (m.group(2) or '')
    if base:
        return urljoin(base, url)
    relative.append(url)
    return url

def inline(t):
    codes = []
    def keep(m):
        codes.append('<code>' + html.escape(m.group(1), quote=False) + '</code>')
        return '\x00%d\x00' % (len(codes) - 1)
    t = re.sub(r'`([^`]+)`', keep, t)
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\(#[^)]+\)', r'\1', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{href(m.group(2))}">{m.group(1)}</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w])_(.+?)_(?![\w])', r'<em>\1</em>', t)
    return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m.group(1))], t)

if sys.argv[1:] in (['-h'], ['--help']):
    print(__doc__.strip()); sys.exit(0)
args = sys.argv[1:]
for a in [a for a in args if a.startswith(('--base=', '--docs='))]:
    url = a.split('=', 1)[1].rstrip('/') + '/'
    if a.startswith('--base='):
        base = url
    else:
        docs = url
    args.remove(a)
if len(args) != 1:
    sys.exit(__doc__.strip())

lines = open(args[0]).read().split('\n')
out, i, in_list, skip = [], 0, False, False
def close_list():
    global in_list
    if in_list:
        out.append('</ul>'); in_list = False
while i < len(lines):
    l = lines[i]
    if l.startswith('# '):
        i += 1; continue
    if l.startswith('<!--'):
        while '-->' not in lines[i]:
            i += 1
        i += 1; continue
    m = re.match(r'(#{2,3}) (.*)', l)
    if m:
        close_list()
        skip = m.group(2) == 'Table of contents'
        if not skip:
            n = len(m.group(1))
            out.append(f'\n<h{n}>{inline(m.group(2))}</h{n}>')
        i += 1; continue
    if skip:
        i += 1; continue
    fence = re.match(r'( *)```(\w*)', l)
    if fence:
        ind = len(fence.group(1)); lang = fence.group(2); code = []; i += 1
        while not re.match(r' *```', lines[i]):
            code.append(lines[i][ind:]); i += 1
        # Drupal.org's code filter escapes the contents of <?php ?> and <code>
        # blocks itself, and highlights <?php ?> blocks as PHP.
        if lang == 'php':
            pre = '<?php\n' + '\n'.join(code) + '\n?>'
        else:
            pre = '<code>' + '\n'.join(code) + '</code>'
        if ind and in_list and out[-1].endswith('</li>'):
            out[-1] = out[-1][:-5] + '\n' + pre + '</li>'
        else:
            close_list(); out.append(pre)
        i += 1; continue
    if l.startswith('- '):
        # The output is the project page, so leave out the link to it.
        if l.startswith('- For a full description of the module'):
            i += 1; continue
        if not in_list:
            out.append('<ul>'); in_list = True
        out.append('  <li>' + inline(l[2:]) + '</li>')
        i += 1; continue
    if l.strip() == '':
        if in_list and i + 1 < len(lines) and (lines[i+1].startswith('- ') or lines[i+1].startswith('    ')):
            i += 1; continue
        close_list(); i += 1; continue
    close_list()
    out.append('<p>' + inline(l) + '</p>')
    i += 1
close_list()
print('\n'.join(out).strip())
if relative:
    print('Relative links left as they are, which break on drupal.org; pass --base: '
          + ', '.join(relative), file=sys.stderr)
