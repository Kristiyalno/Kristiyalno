import urllib.request, json, re, os, sys

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

card_w = 260
card_h = 110
gap = 16
pad = 20
total_w = pad * 2 + card_w * 3 + gap * 2
total_h = card_h + pad * 2

color_sets = [
    ("#7c3aed", "#a855f7", "#6366f1"),
    ("#0ea5e9", "#38bdf8", "#6366f1"),
    ("#10b981", "#34d399", "#0ea5e9"),
]

def truncate(text, maxlen):
    return text if len(text) <= maxlen else text[:maxlen - 1] + "\u2026"

cards_svg = ""
for i, repo in enumerate(repos[:3]):
    x = pad + i * (card_w + gap)
    y = pad
    name = truncate(repo["name"], 24)
    desc = truncate(repo.get("description") or "No description", 80)
    pushed = repo["pushed_at"][:10]
    c = color_sets[i]
    grad_id = "grad" + str(i)
    begin = str(i * -4) + "s"

    line1 = desc[:38]
    line2 = desc[38:] if len(desc) > 38 else ""

    extra_line = ""
    if line2:
        extra_line = (
            '<text x="' + str(x + 18) + '" y="' + str(y + 90) + '" '
            'font-family="\'Segoe UI\',system-ui,sans-serif" '
            'font-size="11" fill="#ccc9d0">' + line2 + '</text>'
        )

    cards_svg += (
        '<defs>'
        '<linearGradient id="' + grad_id + '" x1="0" y1="0" x2="1" y2="1">'
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
        '<clipPath id="clip' + str(i) + '">'
        '<rect x="' + str(x) + '" y="' + str(y) + '" width="' + str(card_w) + '" height="' + str(card_h) + '" rx="14"/>'
        '</clipPath>'
        '</defs>'
        '<rect x="' + str(x) + '" y="' + str(y) + '" width="' + str(card_w) + '" height="' + str(card_h) + '" rx="14"'
        ' fill="url(#' + grad_id + ')" opacity="0.18"/>'
        '<rect x="' + str(x) + '" y="' + str(y) + '" width="' + str(card_w) + '" height="' + str(card_h) + '" rx="14"'
        ' fill="none" stroke="url(#' + grad_id + ')" stroke-width="1.5" opacity="0.6"/>'
        '<text x="' + str(x + 18) + '" y="' + str(y + 34) + '" font-family="\'Segoe UI\',system-ui,sans-serif"'
        ' font-size="14" font-weight="700" fill="#f8f8f2">' + name + '</text>'
        '<text x="' + str(x + 18) + '" y="' + str(y + 56) + '" font-family="\'Segoe UI\',system-ui,sans-serif"'
        ' font-size="11" fill="#bd93f9" font-weight="500">last push: ' + pushed + '</text>'
        '<text x="' + str(x + 18) + '" y="' + str(y + 76) + '" font-family="\'Segoe UI\',system-ui,sans-serif"'
        ' font-size="11" fill="#ccc9d0">' + line1 + '</text>'
        + extra_line
    )

svg = (
    '<svg xmlns="http://www.w3.org/2000/svg"'
    ' width="' + str(total_w) + '" height="' + str(total_h) + '"'
    ' viewBox="0 0 ' + str(total_w) + ' ' + str(total_h) + '">'
    '<rect width="' + str(total_w) + '" height="' + str(total_h) + '" fill="#0d1117" rx="16"/>'
    + cards_svg +
    '</svg>'
)

with open("active-projects.svg", "w") as f:
    f.write(svg)

with open("README.md", "r") as f:
    content = f.read()

img_line = '<img src="active-projects.svg" alt="active projects" width="100%"/>'
pattern = r"(<!--START_SECTION:active-repos-->).*?(<!--END_SECTION:active-repos-->)"
replacement = "<!--START_SECTION:active-repos-->\n" + img_line + "\n<!--END_SECTION:active-repos-->"
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open("README.md", "w") as f:
    f.write(new_content)

print("Done.")
