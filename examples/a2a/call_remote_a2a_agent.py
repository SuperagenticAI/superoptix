"""Call a remote A2A agent through the SuperOptiX A2A client wrapper."""

from __future__ import annotations

import argparse
import json

from superoptix.protocols.a2a import A2AClient


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        required=True,
        help="Base URL of the remote A2A agent, for example http://127.0.0.1:8101",
    )
    parser.add_argument(
        "--message",
        default="What can you do for a product research task?",
        help="Message to send to the remote A2A agent.",
    )
    args = parser.parse_args()

    client = A2AClient(agent_url=args.url)
    if not client.connect():
        raise SystemExit(f"Failed to connect to remote A2A agent at {args.url}")

    print("Connected to remote agent")
    print(json.dumps(client.get_capabilities(), indent=2))

    result = client._handle_request(query=args.message)
    print("\nAgent response:\n")
    print(getattr(result, "response", str(result)))


if __name__ == "__main__":
    main()

