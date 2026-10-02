"""
Load test for EADRP's core citizen-report -> AI-triage path.

This is what makes any "handles X req/s" resume claim defensible: it exercises the
real code path (create incident -> ML severity call -> auto-assignment -> read
back) against your own running stack instead of a synthetic endpoint.

Usage
-----
1. Start the stack:      docker compose up --build
2. Get a citizen token:   register + log in once, or use scripts/seed_users.py
3. Run:                   locust -f tests/load/locustfile.py --host http://localhost:8000

Then open http://localhost:8089, set concurrent users / spawn rate, and start the
test. Locust reports p50/p95/p99 latency and requests/sec live, and you can export
a CSV with `--csv=results` for a repeatable, citable number.

Headless one-off run, e.g. 50 users for 3 minutes:
    locust -f tests/load/locustfile.py --host http://localhost:8000 \
        --headless -u 50 -r 5 -t 3m --csv=results
"""

import random

from locust import HttpUser, task, between

DISASTER_TYPES = [
    "FLOOD", "EARTHQUAKE", "CYCLONE", "WILDFIRE", "LANDSLIDE",
    "STORM", "DROUGHT", "INDUSTRIAL_FIRE",
]

LOCATIONS = [
    ("Chennai, Tamil Nadu", 13.0827, 80.2707),
    ("Kochi, Kerala", 9.9312, 76.2673),
    ("Guwahati, Assam", 26.1445, 91.7362),
    ("Bhubaneswar, Odisha", 20.2961, 85.8245),
    ("Bengaluru, Karnataka", 12.9716, 77.5946),
]


class CitizenReporter(HttpUser):
    """Simulates citizens registering an account and submitting incident reports —
    the path that triggers the ML severity call and the auto-assignment rules engine,
    which is the most expensive request in the system."""

    wait_time = between(1, 3)

    def on_start(self):
        email = f"loadtest_{random.randint(1, 10_000_000)}@example.com"
        self.client.post(
            "/api/v1/auth/register",
            json={"full_name": "Load Test Citizen", "email": email, "password": "LoadTest@123"},
        )
        resp = self.client.post(
            "/api/v1/auth/token", json={"email": email, "password": "LoadTest@123"}
        )
        token = resp.json().get("access_token") if resp.status_code == 200 else None
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    @task(3)
    def submit_incident(self):
        location, lat, lng = random.choice(LOCATIONS)
        self.client.post(
            "/api/v1/incidents",
            json={
                "title": f"{random.choice(DISASTER_TYPES).title()} reported near {location}",
                "description": "Load-test generated incident report for performance benchmarking.",
                "disaster_type": random.choice(DISASTER_TYPES),
                "location": location,
                "latitude": lat + random.uniform(-0.05, 0.05),
                "longitude": lng + random.uniform(-0.05, 0.05),
                "people_affected": random.randint(1, 500),
                "injuries": random.randint(0, 40),
            },
            headers=self.headers,
            name="/incidents [POST create+triage]",
        )

    @task(5)
    def list_my_incidents(self):
        self.client.get("/api/v1/incidents", headers=self.headers, name="/incidents [GET list]")
