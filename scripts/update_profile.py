#!/usr/bin/env python3
"""Refresh public profile data and self-hosted SVG cards using Python's standard library."""
import collections
import datetime as dt
import html
import json
import math
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USERNAME = os.environ.get("PROFILE_USERNAME", "D4rkpt")
PROFILE_REPO = os.environ.get("GITHUB_REPOSITORY", f"{USERNAME}/{USERNAME}")
TOKEN = os.environ.get("GH_TOKEN", "")
PALETTE = ["#67e8f9", "#a78bfa", "#60a5fa", "#34d399", "#fbbf24", "#fb7185", "#f472b6", "#94a3b8"]


def api(path, data=None):
    url = path if path.startswith("https://") else "https://api.github.com" + path
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-mission-control", "X-GitHub-Api-Version": "2022-11-28"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    body = None if data is None else json.dumps(data).encode()
    if body is not None:
        headers["Content-Type"] = "application/json"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))


def e(value):
    return html.escape(str(value), quote=True)


def short(value, n):
    value = " ".join(str(value or "").split())
    return value if len(value) <= n else value[:n-1] + "…"


def md(value):
    value = " ".join(str(value or "").split())
    return re.sub(r"([\\`*_{}\[\]()<>|])", r"\\\1", value)


def svg_start(width, height, dark):
    bg, panel, ink, muted, line = ("#0b1120", "#121c2e", "#e6edf7", "#94a3b8", "#27354b") if dark else ("#f8fafc", "#ffffff", "#172033", "#53647a", "#d9e2ef")
    style = f'<style>text{{font-family:Arial,sans-serif;fill:{ink}}}.muted{{fill:{muted}}}.label{{font-family:monospace;letter-spacing:1px;fill:{muted}}}</style>'
    start = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">{style}<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="18" fill="{bg}" stroke="{line}"/>'
    return start, (bg, panel, ink, muted, line)


def save(name, content, dark):
    ASSETS.mkdir(exist_ok=True)
    suffix = "-dark" if dark else ""
    (ASSETS / f"{name}{suffix}.svg").write_text(content + "</svg>", encoding="utf-8")


def render_dashboard(user, repos, calendar, dark):
    s, colors = svg_start(1000, 190, dark)
    s += '<text x="28" y="37" font-size="12" class="label">PROFILE TELEMETRY / PUBLIC SIGNALS</text>'
    metrics = [("CALENDAR CONTRIBUTIONS", calendar.get("totalContributions")), ("PUBLIC ORIGINAL REPOS", len(repos)), ("STARS / ELIGIBLE REPOS", sum(r.get("stargazers_count", 0) for r in repos)), ("FOLLOWERS", user.get("followers", 0))]
    for i, (label, value) in enumerate(metrics):
        x = 28 + i * 246
        s += f'<rect x="{x}" y="57" width="230" height="107" rx="12" fill="{colors[1]}" stroke="{colors[4]}"/>'
        s += f'<text x="{x+15}" y="85" font-size="9" class="label">{e(label)}</text><text x="{x+15}" y="138" font-size="38" font-weight="700" style="fill:{PALETTE[i] if dark else ["#0e7490", "#7c3aed", "#2563eb", "#047857"][i]}">{e("—" if value is None else f"{value:,}")}</text>'
    save("dashboard", s, dark)


def render_calendar(calendar, dark):
    s, colors = svg_start(1000, 235, dark)
    s += '<text x="28" y="36" font-size="12" class="label">CONTRIBUTION MAP / GITHUB CALENDAR</text>'
    weeks = calendar.get("weeks", [])
    if not weeks:
        s += '<text x="28" y="112" font-size="17" class="muted">Awaiting first sync — no contribution numbers have been invented.</text>'
    else:
        scale = ["#172337", "#164e63", "#0e7490", "#0891b2", "#67e8f9"] if dark else ["#e2e8f0", "#cffafe", "#67e8f9", "#06b6d4", "#0e7490"]
        levels = {"NONE":0, "FIRST_QUARTILE":1, "SECOND_QUARTILE":2, "THIRD_QUARTILE":3, "FOURTH_QUARTILE":4}
        for row, label in [(1,"Mon"),(3,"Wed"),(5,"Fri")]:
            s += f'<text x="28" y="{75+row*17}" font-size="10" class="muted">{label}</text>'
        for i, week in enumerate(weeks):
            for day in week.get("contributionDays", []):
                x, y = 72+i*16.5, 64+day["weekday"]*17
                fill = scale[levels.get(day.get("contributionLevel", "NONE"), 0)]
                s += f'<rect x="{x}" y="{y}" width="13" height="13" rx="3" fill="{fill}"><title>{e(day["date"])}: {day["contributionCount"]} contributions</title></rect>'
        s += '<text x="28" y="213" font-size="11" class="muted">Contribution counts are not commit counts.</text>'
        s += '<text x="784" y="213" font-size="10" class="muted">Less</text>'
        for i, fill in enumerate(scale):
            s += f'<rect x="817" y="{202}" width="12" height="12" rx="2" fill="{fill}" transform="translate({i*17} 0)"/>'
        s += '<text x="910" y="213" font-size="10" class="muted">More</text>'
    save("contributions", s, dark)


def render_languages(languages, sample_count, dark):
    s, colors = svg_start(1000, 290, dark)
    s += '<text x="28" y="36" font-size="12" class="label">LANGUAGE ORBIT / DETECTED SOURCE BYTES</text>'
    ranked = sorted(languages.items(), key=lambda p:p[1], reverse=True)
    total = sum(languages.values())
    if not total:
        s += '<text x="28" y="116" font-size="17" class="muted">Language data will appear after the first successful sync.</text>'
    else:
        shown = ranked[:7]
        other = sum(n for _, n in ranked[7:])
        if other:
            shown.append(("Other", other))
        circumference = 2*math.pi*74
        offset = 0
        s += f'<circle cx="154" cy="154" r="74" fill="none" stroke="{colors[4]}" stroke-width="21"/>'
        for i, (name, size) in enumerate(shown):
            length = size/total*circumference
            s += f'<circle cx="154" cy="154" r="74" fill="none" stroke="{PALETTE[i]}" stroke-width="21" stroke-dasharray="{length:.3f} {circumference-length:.3f}" stroke-dashoffset="{-offset:.3f}" transform="rotate(-90 154 154)"/>'
            offset += length
            col, row = i//4, i%4
            x, y = 292+col*336, 88+row*42
            s += f'<circle cx="{x}" cy="{y-4}" r="5" fill="{PALETTE[i]}"/><text x="{x+17}" y="{y}" font-size="14">{e(short(name, 23))}</text><text x="{x+262}" y="{y}" text-anchor="end" font-size="14" class="muted">{size/total*100:.1f}%</text>'
        s += f'<text x="154" y="151" text-anchor="middle" font-size="29" font-weight="700">{len(ranked)}</text><text x="154" y="172" text-anchor="middle" font-size="10" class="label">LANGUAGES</text>'
    s += f'<text x="28" y="267" font-size="11" class="muted">Sample: {sample_count} public original repos · Source bytes, not proficiency or coding time.</text>'
    save("languages", s, dark)


def wrap(value, width, lines):
    words, result, line = str(value).split(), [], ""
    for word in words:
        if line and len(line)+len(word)+1 > width:
            result.append(line)
            line = word
        else:
            line = (line+" "+word).strip()
    if line:
        result.append(line)
    if len(result) > lines:
        result = result[:lines]
        result[-1] = short(result[-1], width-1)+"…"
    return [short(t, width) for t in result]


def render_project(repo, index, dark):
    s, colors = svg_start(480, 224, dark)
    accent = "#67e8f9" if dark else "#0e7490"
    s += f'<text x="24" y="33" font-size="10" class="label">PROJECT / {index:02d}</text><circle cx="448" cy="28" r="5" fill="{accent}"/>'
    s += f'<text x="24" y="69" font-size="19" font-weight="700">{e(short(repo["name"], 35))}</text>'
    description = repo.get("description") or "Explore the repository, source files and project history."
    for i, line in enumerate(wrap(description, 56, 3)):
        s += f'<text x="24" y="{99+i*20}" font-size="13" class="muted">{e(line)}</text>'
    language = repo.get("language") or "Source repository"
    pushed = (repo.get("pushed_at") or "")[:10] or "—"
    s += f'<text x="24" y="177" font-size="11" style="fill:{accent}">{e(language)} · {repo.get("stargazers_count",0)} stars · {repo.get("forks_count",0)} forks</text>'
    s += f'<text x="24" y="204" font-size="10" class="muted">Latest push: {e(pushed)}</text><text x="455" y="204" text-anchor="end" font-size="11" style="fill:{accent}">VIEW SOURCE →</text>'
    save(f"project-{index}", s, dark)


def project_markup(repos):
    selected = repos[:4]
    if not selected:
        return "No eligible public projects yet — new public repositories will appear automatically."
    rows = ["<table>"]
    for i, repo in enumerate(selected, 1):
        if i % 2:
            rows.append("<tr>")
        name, url = e(repo["name"]), e(repo["html_url"])
        rows.append(f'<td width="50%"><a href="{url}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/project-{i}-dark.svg" /><source media="(prefers-color-scheme: light)" srcset="assets/project-{i}.svg" /><img src="assets/project-{i}-dark.svg" width="100%" alt="{name} — open source repository" /></picture></a></td>')
        if i % 2 == 0:
            rows.append("</tr>")
    if len(selected) % 2:
        rows.extend(["<td></td>", "</tr>"])
    rows.append("</table>")
    return "\n".join(rows)


def activity_markup(events):
    lines = []
    for event in events:
        if not event.get("public", False):
            continue
        name = event.get("repo", {}).get("name", "")
        if not name or name.lower() == PROFILE_REPO.lower():
            continue
        url = "https://github.com/" + "/".join(urllib.parse.quote(p, safe="") for p in name.split("/"))
        payload = event.get("payload", {})
        date = event.get("created_at", "")[:10]
        kind = event.get("type")
        label = None
        if kind == "PushEvent":
            label = f'Pushed code to [{md(name)}]({url})'
        elif kind == "PullRequestEvent":
            pr = payload.get("pull_request", {})
            action = "merged" if pr.get("merged") else payload.get("action", "updated")
            label = f'{md(action.capitalize())} pull request [{md(short(pr.get("title", "Pull request"), 75))}]({pr.get("html_url", url)})'
        elif kind == "IssuesEvent":
            issue = payload.get("issue", {})
            label = f'{md(payload.get("action", "updated").capitalize())} issue [{md(short(issue.get("title", "Issue"), 75))}]({issue.get("html_url", url)})'
        elif kind == "ReleaseEvent":
            release = payload.get("release", {})
            label = f'Published release [{md(release.get("tag_name", "Release"))}]({release.get("html_url", url)})'
        elif kind == "CreateEvent":
            ref = payload.get("ref") or "repository"
            label = f'Created {md(payload.get("ref_type", "repository"))} `{md(short(ref, 50))}` in [{md(name)}]({url})'
        if label:
            lines.append(f"- `{date}` · {label}")
        if len(lines) == 6:
            break
    return "\n".join(lines) or "No recent public development events are available in the current feed."


def replace_section(text, key, content):
    pattern = rf"(<!-- {key}:START -->).*?(<!-- {key}:END -->)"
    if not re.search(pattern, text, flags=re.S):
        raise ValueError(f"Missing README markers: {key}")
    return re.sub(pattern, lambda m:m[1]+"\n"+content.strip()+"\n"+m[2], text, count=1, flags=re.S)


def main():
    if not TOKEN:
        raise RuntimeError("GH_TOKEN is required. The workflow supplies secrets.GITHUB_TOKEN.")
    encoded = urllib.parse.quote(USERNAME, safe="")
    user = api(f"/users/{encoded}")
    repos = []
    for page in range(1, 101):
        batch = api(f"/users/{encoded}/repos?type=owner&sort=pushed&per_page=100&page={page}")
        repos.extend(r for r in batch if not r.get("private", True) and not r.get("fork") and not r.get("archived") and r["full_name"].lower()!=PROFILE_REPO.lower())
        if len(batch) < 100:
            break
    else:
        raise RuntimeError("Repository pagination limit exceeded; refusing to publish partial totals.")
    repos.sort(key=lambda r:r.get("pushed_at") or "", reverse=True)
    query = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date weekday contributionCount contributionLevel } } } } } }"""
    response = api("/graphql", {"query":query, "variables":{"login":USERNAME}})
    if response.get("errors"):
        raise RuntimeError(json.dumps(response["errors"]))
    calendar = response["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    languages = collections.Counter()
    sample = repos[:40]
    for repo in sample:
        detected = api(f'/repos/{repo["full_name"]}/languages')
        languages.update(detected)
    events = api(f"/users/{encoded}/events/public?per_page=100")
    text = (ROOT/"README.md").read_text(encoding="utf-8")
    days = [d for w in calendar["weeks"] for d in w["contributionDays"]]
    period = f'{days[0]["date"]} → {days[-1]["date"]}' if days else "GitHub calendar period"
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    snapshot = f"<sub>Last successful sync: {today} UTC · Contribution period: {period} · Projects ordered by latest push.</sub>"
    for key, content in [("PROJECTS",project_markup(repos)), ("ACTIVITY",activity_markup(events)), ("SNAPSHOT",snapshot)]:
        text = replace_section(text, key, content)
    for dark in (False, True):
        render_dashboard(user,repos,calendar,dark)
        render_calendar(calendar,dark)
        render_languages(languages,len(sample),dark)
        for i, repo in enumerate(repos[:4], 1):
            render_project(repo,i,dark)
    for path in ASSETS.glob("project-*.svg"):
        match = re.match(r"project-(\d+)(?:-dark)?\.svg$", path.name)
        if match and int(match[1]) > min(len(repos),4):
            path.unlink()
    (ROOT/"README.md").write_text(text, encoding="utf-8")
    print(f"Updated {USERNAME}: {len(repos)} eligible public repos, {len(sample)} language samples, {calendar['totalContributions']} calendar contributions.")


if __name__ == "__main__":
    main()
