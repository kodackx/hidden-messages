#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx

DEFAULT_TIMEOUT = 180.0


def read_session_id(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid session_id '{value}'") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Advance a Hidden Messages session by one turn")
    parser.add_argument("session_id", type=read_session_id, help="Existing session UUID")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for the backend API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"HTTP client timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional path to write the response JSON",
    )
    args = parser.parse_args()

    payload: dict[str, Any] = {"session_id": str(args.session_id)}

    with httpx.Client(base_url=args.base_url, timeout=args.timeout) as client:
        response = client.post("/api/next-turn", json=payload)
        response.raise_for_status()

    data = response.json()
    print(json.dumps(data, indent=2))

    if args.save:
        args.save.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Response saved to {args.save}")


if __name__ == "__main__":
    main()
