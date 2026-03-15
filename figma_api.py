"""
Figma API integration module.

Usage:
    export FIGMA_API_KEY=your_api_key_here
    python3 figma_api.py
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional


FIGMA_BASE_URL = "https://api.figma.com/v1"


def get_api_key() -> str:
    key = os.environ.get("FIGMA_API_KEY")
    if not key:
        raise ValueError("FIGMA_API_KEY environment variable is not set")
    return key


def figma_request(endpoint: str, api_key: Optional[str] = None) -> dict:
    """Make an authenticated GET request to the Figma API."""
    if api_key is None:
        api_key = get_api_key()
    url = f"{FIGMA_BASE_URL}/{endpoint.lstrip('/')}"
    req = urllib.request.Request(url, headers={"X-Figma-Token": api_key})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_me(api_key: Optional[str] = None) -> dict:
    """Fetch the authenticated user's profile."""
    return figma_request("/me", api_key)


def get_file(file_key: str, api_key: Optional[str] = None) -> dict:
    """Fetch a Figma file by its key."""
    return figma_request(f"/files/{file_key}", api_key)


def get_file_images(file_key: str, node_ids: list[str], api_key: Optional[str] = None) -> dict:
    """Fetch rendered images for specific nodes in a Figma file."""
    ids = ",".join(node_ids)
    return figma_request(f"/images/{file_key}?ids={ids}", api_key)


def get_file_components(file_key: str, api_key: Optional[str] = None) -> dict:
    """Fetch all components in a Figma file."""
    return figma_request(f"/files/{file_key}/components", api_key)


if __name__ == "__main__":
    try:
        api_key = get_api_key()
        print(f"Using Figma API key: {api_key[:8]}...")

        user = get_me(api_key)
        print(f"Authenticated as: {user.get('name', 'Unknown')} ({user.get('email', 'N/A')})")
        print("Figma API setup successful.")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except urllib.error.HTTPError as e:
        print(f"HTTP error {e.code}: {e.reason}")
    except Exception as e:
        print(f"Error: {e}")
