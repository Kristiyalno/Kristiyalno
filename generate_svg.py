import urllib.request, json, re, os, math

token = os.environ["GITHUB_TOKEN"]
username = "Kristiyalno"

req = urllib.request.Request(
    f"https://api.github.com/users/{username}/repos?sort=pushed&per_page=3&type=owner",
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
)
with urllib.request.urlopen(req) as resp:
    repos = json.loads(resp.read())

color_sets = [
    ("#7c3aed", "#a855f7", "#6366f1"),
    ("#0ea5e9", "#38bdf8", "#6366f1"),
    ("#10b981", "#34d399", "#0ea5e9"),
]

card_w = 260
pad_x = 18
text_w = card_w - pad_x * 2  # 224px usable

CHAR_W_BOLD_14 = 8.2   # name font
CHAR_W_NORMAL_11 = 6.3 # desc font

def wrap_text(text, max_px, char_w):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if len(test) * char_w <= max_px:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

svg_files = []
max_card_h = 0

card_data = []
for i, repo in enumerate(repos[:3]):
    raw_name = repo["name"]
    desc = repo.get("description") or "No description"
    pushed = repo["pushed_at"][:10]
    url = repo["html_url"]
    c = color_sets[i]
    begin = str(i * -4) + "s"

    name_lines = wrap_text(raw_name, text_w, CHAR_W_BOLD_14)
    desc_lines = wrap_text(desc, text_w, CHAR_W_NORMAL_11)

    # layout:
    # 16px top pad
    # name lines: 20px each
    # 8px gap
    # "last push" line: 18px
    # 6px gap
    # desc lines: 16px each
    # 16px bottom pad

    name_block_h = len(name_lines) * 20
    desc_block_h = len(desc_lines) * 16
    card_h = 16 + name_block_h + 8 + 18 + 6 + desc_block_h + 16

    card_data.append((raw_name, name_lines, desc_lines, pushed, url, c, begin, card_h))
    if card_h > max_card_h:
        max_card_h = card_h

# all cards same height = tallest one
for i, (raw_name, name_lines, desc_lines, pushed, url, c, begin, _) in enumerate(card_data):
    card_h = max_card_h

    # build text elements
    text_els = ""
    y = 16
    for line in name_lines:
        y += 20
        text_els += (
            '<text x="' + str(pad_x) + '" y="' + str(y) + '" '
            'font-family="\'Segoe UI\',system-ui,sans-serif" '
            'font-size="14" font-weight="700" fill="#f8f8f2">' + line + '</text>'
        )

    y += 8 + 18
    text_els += (
        '<text x="' + str(pad_x) + '" y="' + str(y) + '" '
        'font-family="\'Segoe UI\',system-ui,sans-serif" '
        'font-size="11" fill="#bd93f9" font-weight="500">last push: ' + pushed + '</text>'
    )

    y += 6
    for line in desc_lines:
        y += 16
        text_els += (
            '<text x="' + str(pad_x) + '" y="' + str(y) + '" '
            'font-family="\'Segoe UI\',system-ui,sans-serif" '
            'font-size="11" fill="#ccc9d0">' + line + '</text>'
        )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg"'
        ' width="' + str(card_w) + '" height="' + str(card_h) + '"'
        ' viewBox="0 0 ' + str(card_w) + ' ' + str(card_h) + '">'
        '<defs>'
        '<linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0%">'
        '<animate attributeName="stop-color"'
        ' values="' + c[0] + ';' + c[1] + ';' + c[2] + ';' + c[1] + ';' + c[0] + '"'
        ' dur="8s" begin="' + begin + '" repeatCount="indefinite"/>'
        '</stop>'
        '<stop offset="100%">'
        '<animate attributeName="stop-color"'
        ' values="' + c[2] + ';' + c[0] + ';' + c[1] + ';' + c[0] + ';' + c[2] + '"'
        ' dur="8s" begin="' + begin + '" repeatCount="indefinite"/>'
        '</stop>'
        '</linearGradient>'
        '</defs>'
        '<rect width="' + str(card_w) + '" height="' + str(card_h) + '" rx="14" fill="#0d1117"/>'
        '<rect width="' + str(card_w) + '" height="' + str(card_h) + '" rx="14" fill="url(#grad)" opacity="0.18"/>'
        '<rect width="' + str(card_w) + '" height="' + str(card_h) + '" rx="14" fill="none" stroke="url(#grad)" stroke-width="1.5" opacity="0.6"/>'
        + text_els +
        '</svg>'
    )

    filename = "card-" + str(i) + ".svg"
    with open(filename, "w") as f:
        f.write(svg)
    svg_files.append((filename, url, card_h))

imgs = "&nbsp;&nbsp;".join(
    '<a href="' + url + '"><img src="' + fname + '" width="260" height="' + str(h) + '"/></a>'
    for fname, url, h in svg_files
)
block = '<div align="center">\n\n' + imgs + '\n\n</div>'

with open("README.md", "r") as f:
    content = f.read()

pattern = r"(<!--START_SECTION:active-repos-->).*?(<!--END_SECTION:active-repos-->)"
replacement = "<!--START_SECTION:active-repos-->\n" + block + "\n<!--END_SECTION:active-repos-->"
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open("README.md", "w") as f:
    f.write(new_content)

print("Done.")