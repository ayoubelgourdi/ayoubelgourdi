"""
Fetches live GitHub stats for the user and regenerates profile_card.svg
in the "Linux terminal" style.

Run locally:
    GITHUB_TOKEN=xxxx GITHUB_USERNAME=ayoubelgourdi python scripts/generate_card.py

In GitHub Actions, GITHUB_TOKEN is provided automatically.
"""

import os
import html
import requests

USERNAME = os.environ.get("GITHUB_USERNAME", "ayoubelgourdi")
TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
REST = "https://api.github.com"
GRAPHQL = "https://api.github.com/graphql"


def get_user_info():
    r = requests.get(f"{REST}/users/{USERNAME}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def get_total_stars():
    stars = 0
    page = 1
    while True:
        r = requests.get(
            f"{REST}/users/{USERNAME}/repos",
            headers=HEADERS,
            params={"per_page": 100, "page": page, "type": "owner"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        stars += sum(repo.get("stargazers_count", 0) for repo in data)
        page += 1
    return stars


def get_total_commits():
    """Uses the GraphQL contributionsCollection (current year only, GitHub's own limit)."""
    if not TOKEN:
        return "N/A"
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    r = requests.post(
        GRAPHQL,
        headers=HEADERS,
        json={"query": query, "variables": {"login": USERNAME}},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    try:
        c = data["data"]["user"]["contributionsCollection"]
        return c["totalCommitContributions"] + c["restrictedContributionsCount"]
    except (KeyError, TypeError):
        return "N/A"


# ---------------------------------------------------------------------------
# Static personal info (edit this section to update your bio/skills)
# ---------------------------------------------------------------------------
STATIC_INFO = [
    ("header", "Info:"),
    ("kv", "Name:", "Ayoub Elgourdi", True),
    ("kv", "Age:", "20", False),
    ("kv", "Role:", "Web Developer", True),
    ("kv", "Location:", "Agadir, Morocco", True),
    ("kv", "Status:", "Learning & Building", True),
    ("gap",),
    ("section", "Languages:"),
    ("kv", "Programming:", "Python, JavaScript, TypeScript", True),
    ("kv", "Web:", "HTML, CSS", True),
    ("gap",),
    ("section", "Frameworks:"),
    ("kv", "Frontend:", "React, Next.js, Tailwind CSS", True),
    ("kv", "Backend:", "Node.js, Express.js", True),
    ("gap",),
    ("section", "Databases:"),
    ("kv", "SQL:", "MySQL, PostgreSQL", True),
    ("gap",),
    ("section", "Tools:"),
    ("kv", "VersionControl:", "Git, GitHub", True),
    ("kv", "Editors:", "VS Code, Cursor", True),
    ("kv", "OS:", "Linux", True),
    ("kv", "DevOps:", "Docker", True),
    ("gap",),
    ("section", "Contact:"),
    ("kv", "Email:", "devayoub26@gmail.com", True),
    ("kv", "LinkedIn:", "linkedin.com/in/ayoubelgourdi", True),
]


def build_svg(user, stars, commits):
    lines = list(STATIC_INFO)
    lines += [
        ("gap",),
        ("section", "GitHub Stats:"),
        ("kv", "Repos:", str(user.get("public_repos", "N/A")), False),
        ("kv", "Stars:", str(stars), False),
        ("kv", "Followers:", str(user.get("followers", "N/A")), False),
        ("kv", "Commits (this year):", str(commits), False),
    ]

    CHAR_W = 8.7
    LINE_H = 23
    FONT_SIZE = 14.5
    PAD_X = 34
    TITLEBAR_H = 40
    TOP_PAD = 30
    BOTTOM_PAD = 28
    key_col_chars = 22
    dots_target = 52

    def build_kv(key, val, quoted):
        key_pad = key + " " * max(key_col_chars - len(key), 1)
        dots_needed = max(dots_target - len(key_pad), 3)
        dots = "." * dots_needed
        val_disp = f'"{val}"' if quoted else val
        return key_pad, dots, val_disp

    max_chars = 0
    rendered = []
    for item in lines:
        if item[0] == "gap":
            rendered.append(("gap",))
            continue
        if item[0] == "header":
            text = item[1]
            dash_len = 68
            max_chars = max(max_chars, len(text) + dash_len)
            rendered.append(("header", text, dash_len))
            continue
        if item[0] == "section":
            text = item[1]
            max_chars = max(max_chars, len(text))
            rendered.append(("section", text))
            continue
        if item[0] == "kv":
            key, val, quoted = item[1], item[2], item[3]
            key_pad, dots, val_disp = build_kv(key, val, quoted)
            full_len = 2 + len(key_pad) + len(dots) + 1 + len(val_disp)
            max_chars = max(max_chars, full_len)
            rendered.append(("kv", key_pad, dots, val_disp))

    content_width_px = max_chars * CHAR_W
    total_width = PAD_X * 2 + content_width_px
    n_lines = len(rendered) + 1
    total_height_est = TITLEBAR_H + TOP_PAD + n_lines * LINE_H + BOTTOM_PAD + LINE_H

    COL_BG = "#1e1e2e"
    COL_TITLEBAR = "#181825"
    COL_HEADER = "#cdd6f4"
    COL_SECTION = "#cdd6f4"
    COL_KEY = "#fab387"
    COL_DOTS = "#585b70"
    COL_VALUE = "#a6e3a1"
    COL_VALUE_NUM = "#f9e2af"
    COL_SEP = "#45475a"
    COL_BORDER = "#313244"
    COL_PROMPT = "#a6e3a1"
    COL_PROMPT_SYM = "#cdd6f4"
    COL_ICON = "#9399b2"

    svg_parts = []
    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(total_width)}" '
        f'height="{int(total_height_est)}" viewBox="0 0 {int(total_width)} {int(total_height_est)}">'
    )
    svg_parts.append(
        '<defs><style>text { font-family: "SFMono-Regular", Consolas, '
        '"Liberation Mono", Menlo, monospace; }</style></defs>'
    )
    svg_parts.append(f'<rect x="0" y="0" width="{int(total_width)}" height="{int(total_height_est)}" fill="{COL_BG}" rx="10"/>')
    svg_parts.append(
        f'<rect x="0.5" y="0.5" width="{int(total_width)-1}" height="{int(total_height_est)-1}" '
        f'fill="none" stroke="{COL_BORDER}" stroke-width="1" rx="10"/>'
    )
    svg_parts.append(
        f'<path d="M0,10 Q0,0 10,0 L{int(total_width)-10},0 Q{int(total_width)},0 {int(total_width)},10 '
        f'L{int(total_width)},{TITLEBAR_H} L0,{TITLEBAR_H} Z" fill="{COL_TITLEBAR}"/>'
    )
    svg_parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{int(total_width)}" y2="{TITLEBAR_H}" stroke="{COL_BORDER}" stroke-width="1"/>')

    cy = TITLEBAR_H / 2
    svg_parts.append(f'<rect x="16" y="{cy-8}" width="16" height="16" rx="3" fill="{COL_BORDER}"/>')
    svg_parts.append(f'<text x="24" y="{cy+5}" font-size="11" fill="{COL_PROMPT}" text-anchor="middle">&gt;_</text>')
    svg_parts.append(f'<text x="42" y="{cy+5}" font-size="12.5" fill="{COL_HEADER}">{USERNAME}@github: ~/portfolio</text>')

    bx3 = int(total_width) - 24
    bx2 = bx3 - 28
    bx1 = bx2 - 28
    svg_parts.append(f'<circle cx="{bx1}" cy="{cy}" r="9" fill="{COL_BORDER}"/>')
    svg_parts.append(f'<rect x="{bx1-5}" y="{cy-0.5}" width="10" height="1.4" fill="{COL_ICON}"/>')
    svg_parts.append(f'<circle cx="{bx2}" cy="{cy}" r="9" fill="{COL_BORDER}"/>')
    svg_parts.append(f'<rect x="{bx2-4}" y="{cy-4}" width="8" height="8" fill="none" stroke="{COL_ICON}" stroke-width="1.3"/>')
    svg_parts.append(f'<circle cx="{bx3}" cy="{cy}" r="9" fill="#f38ba8"/>')
    svg_parts.append(f'<line x1="{bx3-4}" y1="{cy-4}" x2="{bx3+4}" y2="{cy+4}" stroke="#1e1e2e" stroke-width="1.4"/>')
    svg_parts.append(f'<line x1="{bx3-4}" y1="{cy+4}" x2="{bx3+4}" y2="{cy-4}" stroke="#1e1e2e" stroke-width="1.4"/>')

    ix = PAD_X
    y = TITLEBAR_H + TOP_PAD

    svg_parts.append(
        f'<text x="{ix}" y="{y}" font-size="{FONT_SIZE}" xml:space="preserve">'
        f'<tspan fill="{COL_PROMPT}">{USERNAME}</tspan>'
        f'<tspan fill="{COL_PROMPT_SYM}">@github:~$ </tspan>'
        f'<tspan fill="{COL_HEADER}">whoami --info</tspan>'
        f"</text>"
    )
    y += LINE_H * 1.6

    svg_parts.append(f'<text x="{ix}" y="{y}" font-size="{FONT_SIZE}" xml:space="preserve">')
    body = []
    for item in rendered:
        if item[0] == "gap":
            y += LINE_H * 0.55
            continue
        elif item[0] == "header":
            text, dash_len = item[1], item[2]
            body.append(
                f'<tspan x="{ix}" y="{y}" fill="{COL_HEADER}" font-weight="bold">{html.escape(text)}</tspan>'
                f'<tspan fill="{COL_SEP}">{html.escape("_"*dash_len)}</tspan>'
            )
            y += LINE_H
        elif item[0] == "section":
            text = item[1]
            body.append(f'<tspan x="{ix}" y="{y}" fill="{COL_SECTION}" font-weight="bold">{html.escape(text)}</tspan>')
            y += LINE_H
        elif item[0] == "kv":
            key_pad, dots, val_disp = item[1], item[2], item[3]
            val_color = COL_VALUE if val_disp.startswith('"') else COL_VALUE_NUM
            body.append(
                f'<tspan x="{ix}" y="{y}" fill="{COL_KEY}">{html.escape("  "+key_pad)}</tspan>'
                f'<tspan fill="{COL_DOTS}">{html.escape(dots+" ")}</tspan>'
                f'<tspan fill="{val_color}">{html.escape(val_disp)}</tspan>'
            )
            y += LINE_H
    svg_parts.extend(body)
    svg_parts.append("</text>")

    y += LINE_H * 0.6
    svg_parts.append(
        f'<text x="{ix}" y="{y}" font-size="{FONT_SIZE}" xml:space="preserve">'
        f'<tspan fill="{COL_PROMPT}">{USERNAME}</tspan>'
        f'<tspan fill="{COL_PROMPT_SYM}">@github:~$ </tspan>'
        f"</text>"
    )
    cursor_x = ix + CHAR_W * len(f"{USERNAME}@github:~$ ")
    svg_parts.append(
        f'<rect x="{cursor_x}" y="{y-13}" width="9" height="16" fill="{COL_HEADER}">'
        f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.4;0.5;0.9;1" '
        f'dur="1.2s" repeatCount="indefinite"/></rect>'
    )

    final_height = y + BOTTOM_PAD
    svg_parts.append("</svg>")
    svg = "\n".join(svg_parts)
    svg = svg.replace(f'height="{int(total_height_est)}"', f'height="{int(final_height)}"', 1)
    svg = svg.replace(f"0 {int(total_width)} {int(total_height_est)}", f"0 {int(total_width)} {int(final_height)}")
    svg = svg.replace(
        f'width="{int(total_width)}" height="{int(total_height_est)}" fill="{COL_BG}"',
        f'width="{int(total_width)}" height="{int(final_height)}" fill="{COL_BG}"',
    )
    svg = svg.replace(
        f'width="{int(total_width)-1}" height="{int(total_height_est)-1}"',
        f'width="{int(total_width)-1}" height="{int(final_height)-1}"',
    )
    return svg


def main():
    user = get_user_info()
    stars = get_total_stars()
    commits = get_total_commits()
    svg = build_svg(user, stars, commits)
    with open("profile_card.svg", "w") as f:
        f.write(svg)
    print(f"Generated profile_card.svg  (repos={user.get('public_repos')}, "
          f"stars={stars}, followers={user.get('followers')}, commits={commits})")


if __name__ == "__main__":
    main()