import requests
import os
import html

USERNAME = "CheRongtian"

IGNORED_LANGS = {
    "jupyter notebook",
    "makefile",
    "cmake",
    "html",
    "css"
}

TOKEN = os.getenv("GITHUB_TOKEN", "")

LANG_COLORS = {
    "Python": "#3572A5",
    "C++": "#f34b7d",
    "C": "#555555",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Java": "#b07219",
    "MATLAB": "#e16737",
    "Shell": "#89e051",
    "R": "#198CE7",
    "Rust": "#dea584",
    "Go": "#00ADD8",
}


def headers():
    if TOKEN:
        return {
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
        }
    return {
        "Accept": "application/vnd.github+json"
    }


def get_repos():
    repos = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?per_page=100&type=owner&page={page}"
        )

        response = requests.get(url, headers=headers())
        response.raise_for_status()

        data = response.json()

        if not data:
            break

        repos.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repos


def get_language_stats():
    stats = {}

    repos = get_repos()

    for repo in repos:
        if repo["fork"]:
            continue

        response = requests.get(
            repo["languages_url"],
            headers=headers()
        )
        response.raise_for_status()

        languages = response.json()

        for lang, byte_count in languages.items():
            if lang.lower() in IGNORED_LANGS:
                continue

            stats[lang] = stats.get(lang, 0) + byte_count

    return stats


def make_svg(stats):
    total = sum(stats.values())

    if total == 0:
        return

    languages = sorted(
        stats.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    width = 720
    row_height = 38
    top = 72
    height = top + len(languages) * row_height + 30

    bar_x = 180
    bar_width = 360
    bar_height = 10

    rows = []

    for i, (lang, count) in enumerate(languages):
        percent = count / total * 100

        y = top + i * row_height

        fill_width = max(
            2,
            bar_width * percent / 100
        )

        color = LANG_COLORS.get(
            lang,
            "#8b949e"
        )

        safe_lang = html.escape(lang)

        rows.append(
            f"""
            <text
                x="28"
                y="{y}"
                class="language"
            >
                {safe_lang}
            </text>

            <rect
                x="{bar_x}"
                y="{y - 10}"
                width="{bar_width}"
                height="{bar_height}"
                rx="5"
                fill="#21262d"
            />

            <rect
                x="{bar_x}"
                y="{y - 10}"
                width="{fill_width:.1f}"
                height="{bar_height}"
                rx="5"
                fill="{color}"
            />

            <text
                x="565"
                y="{y}"
                class="percent"
            >
                {percent:5.2f}%
            </text>
            """
        )

    svg = f"""<svg
        xmlns="http://www.w3.org/2000/svg"
        width="{width}"
        height="{height}"
        viewBox="0 0 {width} {height}"
    >

    <style>
        .title {{
            font: 600 18px monospace;
            fill: #c9d1d9;
        }}

        .subtitle {{
            font: 13px monospace;
            fill: #8b949e;
        }}

        .language {{
            font: 14px monospace;
            fill: #c9d1d9;
        }}

        .percent {{
            font: 14px monospace;
            fill: #8b949e;
        }}
    </style>

    <rect
        x="1"
        y="1"
        width="{width - 2}"
        height="{height - 2}"
        rx="12"
        fill="#0d1117"
        stroke="#30363d"
    />

    <text
        x="28"
        y="34"
        class="title"
    >
        rongtian.che — language usage
    </text>

    <text
        x="28"
        y="54"
        class="subtitle"
    >
        public repositories / generated from GitHub API
    </text>

    {''.join(rows)}

    </svg>
    """

    with open(
        "language.svg",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(svg)


def main():
    stats = get_language_stats()
    make_svg(stats)

    print("language.svg generated")


if __name__ == "__main__":
    main()