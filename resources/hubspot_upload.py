#!/usr/bin/env python3
"""
Upload release notes images to the HubSpot Files API.

Usage:
  python3 resources/hubspot_upload.py output/2026-05-release/images/raw/
  python3 resources/hubspot_upload.py output/_smoke-test/images/raw/ --folder /release-notes/_smoke-test-extraction/

Reads all .png/.jpg/.jpeg files in the input folder (alphabetical order, which
matches the order they were extracted from Loop) and uploads each to HubSpot.
Writes a JSON map to <input_folder>/../hubspot_urls.json mapping the original
local filename to the public HubSpot CDN URL:

  {
    "01_MovePoliciesAccounts.png": "https://NNNNNN.fs1.hubspotusercontent-na1.net/hubfs/NNNNNN/release-notes/2026-05/release-2026-05-01.png",
    ...
  }

Auth: HubSpot Service Key (Bearer token), set as HUBSPOT_SERVICE_KEY in the
environment. Source ~/.zshrc or export the var before running.

Default HubSpot folder layout: /release-notes/YYYY-MM/release-YYYY-MM-NN.<ext>
With --folder: uploads to that folder using the original filenames unchanged.
This is the smoke-test / one-off path; the default release flow keeps the
auto-derived layout for consistency across cycles.

Notes:
- access=PUBLIC_INDEXABLE so URLs render in customer-facing emails and articles
- overwrite=False; if a re-run hits a filename collision the API returns 409
  and the script logs the failure and continues
- Single retry on network error; hard fail on second attempt
- Exits 0 on full success, 2 if any upload failed (caller can decide what to do)
"""

import argparse
import json
import os
import re
import secrets
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.hubapi.com/files/v3/files"
MAX_RETRIES = 1


def derive_release_month(folder_path: Path) -> str:
    """Pull YYYY-MM from a folder path like 'output/2026-05-release/images/raw/'."""
    match = re.search(r"(\d{4})-(\d{2})-release", str(folder_path))
    if not match:
        raise SystemExit(
            f"Could not derive release month from folder path: {folder_path}\n"
            "Expected something like output/YYYY-MM-release/images/raw/"
        )
    return f"{match.group(1)}-{match.group(2)}"


def upload_one(image_path: Path, target_name: str, folder_path: str, token: str) -> dict:
    """Upload one image to HubSpot. Returns the parsed JSON response on success."""
    boundary = "----HubSpotUpload" + secrets.token_hex(16)

    content_type = (
        "image/png" if target_name.lower().endswith(".png") else "image/jpeg"
    )

    with open(image_path, "rb") as f:
        file_content = f.read()

    options = json.dumps(
        {
            "access": "PUBLIC_INDEXABLE",
            "overwrite": False,
        }
    )

    parts = []
    parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{target_name}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'.encode()
    )
    parts.append(file_content)
    parts.append(b"\r\n")
    parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="folderPath"\r\n\r\n'
        f'{folder_path}\r\n'.encode()
    )
    parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="options"\r\n\r\n'
        f'{options}\r\n'.encode()
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "maximizer-release-automation/1.0",
    }

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(API_URL, data=body, method="POST", headers=headers)
        try:
            resp = urllib.request.urlopen(req, timeout=60)
            return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            last_error = f"HTTP {e.code}: {error_body[:300]}"
            # Don't retry 4xx (client errors won't fix themselves)
            if 400 <= e.code < 500:
                break
        except (urllib.error.URLError, TimeoutError) as e:
            last_error = f"Network error: {e}"

        if attempt < MAX_RETRIES:
            print(f"    Retrying after error: {last_error}", file=sys.stderr)

    raise RuntimeError(last_error or "Unknown upload failure")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_folder", help="Local folder containing images to upload")
    parser.add_argument(
        "--folder",
        dest="folder_override",
        default=None,
        help="HubSpot folder path override (e.g. /release-notes/_smoke-test-extraction/). "
             "When set, files keep their original names and the YYYY-MM regex is skipped.",
    )
    args = parser.parse_args()

    token = os.environ.get("HUBSPOT_SERVICE_KEY")
    if not token:
        raise SystemExit(
            "HUBSPOT_SERVICE_KEY not set. Source ~/.zshrc or export it before running."
        )

    input_folder = Path(args.input_folder).resolve()
    if not input_folder.is_dir():
        raise SystemExit(f"Not a directory: {input_folder}")

    if args.folder_override:
        hs_folder = args.folder_override.rstrip("/")
        release_month = None  # signals: keep original filenames
    else:
        release_month = derive_release_month(input_folder)
        hs_folder = f"/release-notes/{release_month}"

    images = sorted(
        p
        for p in input_folder.iterdir()
        if p.suffix.lower() in (".png", ".jpg", ".jpeg")
    )
    if not images:
        print("No images found in folder.", file=sys.stderr)
        sys.exit(0)

    print(f"Uploading {len(images)} image(s) to HubSpot folder {hs_folder}...")
    url_map: dict[str, str] = {}
    failures: list[str] = []

    for i, img in enumerate(images, start=1):
        suffix = img.suffix.lower()
        if release_month is None:
            target = img.name
        else:
            target = f"release-{release_month}-{i:02d}{suffix}"
        print(f"  [{i}/{len(images)}] {img.name} -> {target}")
        try:
            result = upload_one(img, target, hs_folder, token)
            url = result.get("url", "")
            url_map[img.name] = url
            print(f"    {url}")
        except RuntimeError as e:
            print(f"    FAILED: {e}", file=sys.stderr)
            url_map[img.name] = ""
            failures.append(img.name)

    output_path = input_folder.parent.parent / "hubspot_urls.json"
    output_path.write_text(json.dumps(url_map, indent=2))
    print(f"\nWrote URL map to: {output_path}")

    if failures:
        print(
            f"\n{len(failures)} upload(s) failed: {', '.join(failures)}",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
