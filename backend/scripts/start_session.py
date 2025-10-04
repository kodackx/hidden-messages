#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Any, List, Optional

import httpx

DEFAULT_PARTICIPANTS = [
    {
        "name": "Participant Alpha",
        "provider": "openai",
        "role": "communicator",
        "order": 0,
    },
    {
        "name": "Participant Beta",
        "provider": "anthropic",
        "role": "receiver",
        "order": 1,
    },
    {
        "name": "Participant Gamma",
        "provider": "google-gla",
        "role": "bystander",
        "order": 2,
    },
]


def load_participants(path: Optional[Path]) -> List[dict[str, Any]]:
    if path is None:
        return DEFAULT_PARTICIPANTS

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Participants file must contain a JSON array")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new Hidden Messages session")
    parser.add_argument("topic", help="Discussion topic for the agents")
    parser.add_argument(
        "--secret-word",
        dest="secret_word",
        default=None,
        help="Optional explicit secret word (defaults to random if omitted)",
    )
    parser.add_argument(
        "--participants",
        type=Path,
        default=None,
        help="Path to JSON array describing participants; defaults to built-in set",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for the backend API (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    participants = load_participants(args.participants)
    payload: dict[str, Any] = {
        "topic": args.topic,
        "secret_word": args.secret_word,
        "participants": participants,
    }

    with httpx.Client(base_url=args.base_url, timeout=30.0) as client:
        response = client.post("/api/start-session", json=payload)
        response.raise_for_status()

    data = response.json()
    print("Session created successfully!")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
