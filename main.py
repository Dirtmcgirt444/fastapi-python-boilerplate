from __future__ import annotations

import asyncio
import html
import re
import xml.etree.ElementTree as element_tree
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

app = FastAPI(title="Pacific Line", description="Skate story signal desk", version="1.0.0")

PACIFIC_QUERIES = {
    "all": "skateboarding (drama OR controversy OR beef OR comeback OR interview)",
    "industry": "skateboarding industry controversy OR brand OR team",
    "people": "skateboarder interview controversy OR beef",
    "competition": "skateboarding contest controversy OR Olympics",
}


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def score_story(title: str, age_hours: float) -> tuple[int, str]:
    urgency = max(0, 36 - int(age_hours))
    heat_words = ("controvers", "beef", "respond", "calls out", "split", "fired", "return", "comeback")
    heat = sum(word in title.lower() for word in heat_words) * 12
    score = min(98, 42 + urgency + heat)
    return score, "High" if score >= 76 else "Watch" if score >= 58 else "Developing"


async def search_stories(topic: str) -> list[dict]:
    query = PACIFIC_QUERIES.get(topic, PACIFIC_QUERIES["all"])
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        request = Request(url, headers={"User-Agent": "PacificLineResearch/1.0"})
        response = await asyncio.to_thread(urlopen, request, timeout=8)
        with response:
            content = response.read()
    except (OSError, URLError) as error:
        raise HTTPException(status_code=502, detail="The public news feed is unavailable. Try again shortly.") from error

    try:
        root = element_tree.fromstring(content)
    except element_tree.ParseError as error:
        raise HTTPException(status_code=502, detail="The public news feed returned an invalid response.") from error
    stories = []
    now = datetime.now(UTC)
    for item in root.findall("./channel/item")[:12]:
        title = clean_text(item.findtext("title"))
        published = item.findtext("pubDate")
        try:
            published_at = parsedate_to_datetime(published).astimezone(UTC)
            age_hours = max(0, (now - published_at).total_seconds() / 3600)
        except (TypeError, ValueError):
            published_at, age_hours = now, 48
        score, label = score_story(title, age_hours)
        source = item.find("source")
        stories.append({"title": title, "url": item.findtext("link"), "source": clean_text(source.text if source is not None else "News source"), "published": published_at.strftime("%b %d · %H:%M UTC"), "momentum": score, "label": label, "angle": "Break down what happened, what is confirmed, and why the skate community cares."})
    return stories


@app.get("/api/stories")
async def get_stories(topic: str = Query("all", pattern="^(all|industry|people|competition)$")):
    return {"stories": await search_stories(topic), "searched_at": datetime.now(UTC).isoformat()}


@app.get("/", response_class=HTMLResponse)
def read_root():
    return PAGE


PAGE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pacific Line — Skate signal desk</title><link rel="icon" href="/favicon.ico"><style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');:root{--ink:#14211e;--muted:#63716c;--line:#d9dfd9;--paper:#f6f5ef;--lime:#c8fb4b;--coral:#ff6a4c;--sky:#a6d9ee}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Manrope,Arial,sans-serif}.shell{max-width:1440px;margin:auto;padding:20px 38px 46px}.top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--ink);padding:0 0 18px}.brand{font-weight:800;font-size:22px;letter-spacing:-1.2px}.brand i{display:inline-block;width:11px;height:11px;border-radius:50%;background:var(--coral);margin-right:7px}.edition,.eyebrow,.meta{font:11px 'DM Mono',monospace;letter-spacing:.06em;text-transform:uppercase}.edition{color:var(--muted)}.hero{display:grid;grid-template-columns:1.35fr .65fr;gap:45px;padding:67px 0 38px}.eyebrow{color:#46625a;margin:0 0 16px;font-weight:500}.hero h1{font-size:clamp(44px,6vw,82px);line-height:.98;letter-spacing:-.075em;margin:0;max-width:850px}.hero h1 em{font-style:normal;background:var(--lime);padding:0 6px}.hero p{align-self:end;max-width:345px;color:var(--muted);font-size:15px;line-height:1.65;margin:0 0 8px}.filters{display:flex;gap:9px;border-top:1px solid var(--ink);padding:16px 0}.filter{border:1px solid var(--line);background:transparent;padding:10px 15px;border-radius:100px;text-transform:uppercase;font:11px 'DM Mono',monospace;cursor:pointer;color:var(--ink)}.filter.active,.filter:hover{background:var(--ink);color:#fff;border-color:var(--ink)}.status{margin-left:auto;display:flex;align-items:center;gap:8px;font:11px 'DM Mono',monospace;color:var(--muted)}.pulse{width:8px;height:8px;background:#78c62b;border-radius:50%;box-shadow:0 0 0 4px #e4f4d2}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.card{border:1px solid var(--line);padding:21px;min-height:270px;display:flex;flex-direction:column;background:#fff;transition:.2s}.card:hover{transform:translateY(-3px);border-color:var(--ink)}.card:first-child{background:var(--sky);border-color:var(--sky)}.meta{color:#55726a;display:flex;justify-content:space-between;gap:8px}.card h2{font-size:21px;line-height:1.2;letter-spacing:-.04em;margin:21px 0 13px}.card p{color:var(--muted);font-size:13px;line-height:1.5;margin:0}.card footer{margin-top:auto;padding-top:18px;display:flex;justify-content:space-between;align-items:center}.score{font:12px 'DM Mono',monospace;border:1px solid currentColor;padding:5px 8px;border-radius:3px}.read{font-size:13px;font-weight:700;color:var(--ink);text-decoration:none}.empty{grid-column:1/-1;border:1px dashed var(--line);padding:60px;text-align:center;color:var(--muted)}.guardrail{margin-top:50px;background:var(--ink);color:#f5f7ee;padding:30px;display:grid;grid-template-columns:1fr 2fr;gap:40px}.guardrail h3{font-size:23px;letter-spacing:-.05em;margin:0}.guardrail p{color:#b9c6c0;margin:0;line-height:1.6;font-size:14px}.guardrail strong{color:var(--lime)}@media(max-width:780px){.shell{padding:18px}.edition{display:none}.hero,.guardrail{grid-template-columns:1fr;gap:25px}.hero{padding:45px 0 28px}.grid{grid-template-columns:1fr}.filters{flex-wrap:wrap}.status{margin-left:0;width:100%}}</style></head><body><main class="shell"><header class="top"><div class="brand"><i></i>PACIFIC LINE</div><div class="edition">Signal desk / 01 — Public-source research</div></header><section class="hero"><div><p class="eyebrow">For skate storytellers who move with context</p><h1>Find the <em>spark.</em><br>Keep it grounded.</h1></div><p>A focused research companion for public skateboarding stories with enough momentum to earn a responsible video angle.</p></section><nav class="filters" aria-label="Story filters"><button class="filter active" data-topic="all">All signals</button><button class="filter" data-topic="industry">Industry</button><button class="filter" data-topic="people">People</button><button class="filter" data-topic="competition">Competition</button><span class="status"><span class="pulse"></span><span id="status">Scanning public sources</span></span></nav><section class="grid" id="stories" aria-live="polite"><div class="empty">Pulling today’s skate signals…</div></section><section class="guardrail"><h3>Context over<br><strong>clout.</strong></h3><p>Pacific Line only surfaces reporting already published by public sources. Treat every lead as a starting point: open the source, verify claims with more than one credible outlet, seek a response when a person is criticized, and never turn rumor, private information, or harassment into content.</p></section></main><script>
const box=document.querySelector('#stories'),status=document.querySelector('#status');const esc=s=>String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));async function load(topic='all'){box.innerHTML='<div class="empty">Following the line…</div>';status.textContent='Scanning public sources';try{const res=await fetch('/api/stories?topic='+topic);if(!res.ok)throw Error();const {stories}=await res.json();box.innerHTML=stories.length?stories.map(s=>`<article class="card"><div class="meta"><span>${esc(s.source)}</span><span>${esc(s.published)}</span></div><h2>${esc(s.title)}</h2><p>${esc(s.angle)}</p><footer><span class="score">${s.momentum}/100 · ${esc(s.label)}</span><a class="read" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">Open source ↗</a></footer></article>`).join(''):'<div class="empty">No fresh stories found. Try another signal.</div>';status.textContent='Updated from public sources'}catch(e){box.innerHTML='<div class="empty">Couldn’t reach the public news feed. Please try again.</div>';status.textContent='Feed unavailable'}}document.querySelectorAll('.filter').forEach(b=>b.addEventListener('click',()=>{document.querySelector('.filter.active').classList.remove('active');b.classList.add('active');load(b.dataset.topic)}));load();
</script></body></html>'''
