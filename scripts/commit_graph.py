
import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone

USERNAME = "sivaraman1612"
TOKEN = os.getenv("GH_TOKEN")

headers = {"Accept": "application/vnd.github+json"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

end = datetime.now(timezone.utc).date()
start = end - timedelta(days=29)

dates = [start + timedelta(days=i) for i in range(30)]
counts = {d: 0 for d in dates}

page = 1
while True:
    response = requests.get(
        f"https://api.github.com/users/{USERNAME}/events",
        headers=headers,
        params={"per_page": 100, "page": page},
        timeout=30,
    )
    response.raise_for_status()
    events = response.json()

    if not events:
        break

    stop = False
    for event in events:
        event_date = datetime.fromisoformat(
            event["created_at"].replace("Z", "+00:00")
        ).date()

        if event_date < start:
            stop = True
            continue

        if event_date > end:
            continue

        if event["type"] == "PushEvent":
            counts[event_date] += len(
                event.get("payload", {}).get("commits", [])
            )

    if stop or len(events) < 100:
        break
    page += 1

plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(12, 4))
fig.patch.set_facecolor("#080D19")
ax.set_facecolor("#080D19")

x = list(range(30))
y = [counts[d] for d in dates]

ax.plot(x, y, color="#22D3EE", linewidth=2.5, marker="o",
        markersize=3, markerfacecolor="#A78BFA")
ax.fill_between(x, y, color="#22D3EE", alpha=0.15)

ax.set_title("30-Day GitHub Commit Performance",
             color="white", pad=15)
ax.set_ylabel("Commits", color="#94A3B8")
ax.set_xticks([0, 7, 14, 21, 29])
ax.set_xticklabels(
    [dates[i].strftime("%d %b") for i in [0, 7, 14, 21, 29]],
    color="#94A3B8"
)
ax.tick_params(axis="y", colors="#94A3B8")
ax.grid(alpha=0.15)
for spine in ax.spines.values():
    spine.set_color("#24314A")

plt.tight_layout()
os.makedirs("dist", exist_ok=True)
plt.savefig("dist/commit-activity.svg",
            format="svg", facecolor=fig.get_facecolor())
