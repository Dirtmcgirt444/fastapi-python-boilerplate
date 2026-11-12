# Pacific Line — Skate signal desk

Pacific Line is a focused, public-source research dashboard for finding skateboarding stories that may deserve a responsible video angle. It queries the Google News RSS feed for industry, people, and competition signals; it does not present rumor as fact.

## Safety and editorial use

Open the primary source and corroborate material claims before publishing. The dashboard keeps its research niche focused on skate culture while encouraging context, response-seeking, and respect for privacy.

## Run locally

```bash
pip install -e .
fastapi dev main.py
```

The app is then available at `http://127.0.0.1:8000`. The dashboard is served at `/` and the data endpoint is `/api/stories?topic=all|industry|people|competition`.
