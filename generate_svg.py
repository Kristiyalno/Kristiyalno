import urllib.request, json, re, os

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
card_h = 110

def truncate(text, maxlen):
    return text if len(text) <= maxlen else text[:maxlen - 1] + "\u2026"

svg_files = []

for i, repo in enumerate(repos[:3]):
    name = truncate(repo["name"], 24)
    desc = truncate(repo.get("description") or "No description", 80)
    pushed = repo["pushed_at"][:10]
    url = repo["html_url"]
    c = color_sets[i]
    begin = str(i * -4) + "s"

    line1 = desc[:38]
    line2 = desc[38:] if len(desc) > 38 else ""

    extra_line = ""
    if line2:
        extra_line = (
            '<text x="18" y="90" '
            'font-family="\'Segoe UI\',system-ui,sans-serif" '
            'font-size="11" fill="#ccc9d0">' + line2 + '</text>'
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
        '<rect width="' + str(card_w) + '" height="' + str(card_h) + '" rx="14"'
        ' fill="#0d1117"/>'
        '<rect width="' + str(card_w) + '" height="' + str(card_h) + '" rx="14"'
        ' fill="url(#grad)" opacity="0.18"/>'
        '<rect width="' + str(card_w) + '" height="' + str(card_h) + '" rx="14"'
        ' fill="none" stroke="url(#grad)" stroke-width="1.5" opacity="0.6"/>'
        '<text x="18" y="34" font-family="\'Segoe UI\',system-ui,sans-serif"'
        ' font-size="14" font-weight="700" fill="#f8f8f2">' + name + '</text>'
        '<text x="18" y="56" font-family="\'Segoe UI\',system-ui,sans-serif"'
        ' font-size="11" fill="#bd93f9" font-weight="500">last push: ' + pushed + '</text>'
        '<text x="18" y="76" font-family="\'Segoe UI\',system-ui,sans-serif"'
        ' font-size="11" fill="#ccc9d0">' + line1 + '</text>'
        + extra_line +
        '</svg>'
    )

    filename = "card-" + str(i) + ".svg"
    with open(filename, "w") as f:
        f.write(svg)
    svg_files.append((filename, url))

# Update README active-repos section with 3 linked images side by side
imgs = "".join(
    '<a href="' + url + '"><img src="' + fname + '" width="260" height="110"/></a>'
    for fname, url in svg_files
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