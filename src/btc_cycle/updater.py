"""Controllo e download degli aggiornamenti tramite GitHub Releases (senza Qt)."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from . import GITHUB_REPO

API_LATEST = "https://api.github.com/repos/{repo}/releases/latest"
TIMEOUT = 15


@dataclass
class ReleaseInfo:
    version: str
    tag: str
    notes: str
    html_url: str
    assets: List[Dict[str, str]] = field(default_factory=list)


def parse_version(text: str) -> Tuple[int, ...]:
    nums = re.findall(r"\d+", text.strip().lstrip("vV"))
    return tuple(int(n) for n in nums[:3]) + (0,) * (3 - len(nums[:3]))


def is_newer(remote: str, local: str) -> bool:
    return parse_version(remote) > parse_version(local)


def _request(url: str) -> urllib.request.Request:
    return urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                "User-Agent": "BTC-Cycle-Planner"})


def fetch_latest_release(repo: str = GITHUB_REPO) -> ReleaseInfo:
    with urllib.request.urlopen(_request(API_LATEST.format(repo=repo)), timeout=TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    tag = data.get("tag_name", "")
    return ReleaseInfo(
        version=tag.lstrip("vV"),
        tag=tag,
        notes=data.get("body") or "",
        html_url=data.get("html_url", ""),
        assets=[{"name": a["name"], "url": a["browser_download_url"]}
                for a in data.get("assets", [])],
    )


def check_for_update(local_version: str, repo: str = GITHUB_REPO) -> Optional[ReleaseInfo]:
    """Restituisce la release se più recente della versione locale, altrimenti None."""
    release = fetch_latest_release(repo)
    return release if is_newer(release.version, local_version) else None


def select_asset(assets: List[Dict[str, str]], platform: str = sys.platform) -> Optional[Dict]:
    """Sceglie l'asset adatto alla piattaforma (nomi generati dal workflow di build)."""
    patterns = {
        "win32": [r"setup.*\.exe$", r"windows.*\.zip$"],
        "darwin": [r"macos.*\.(dmg|zip)$"],
    }.get(platform, [r"linux.*\.(appimage|tar\.gz)$"])
    for pattern in patterns:
        for asset in assets:
            if re.search(pattern, asset["name"], re.IGNORECASE):
                return asset
    return None


def download(url: str, dest: Path, progress: Optional[Callable[[int], None]] = None) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(_request(url), timeout=TIMEOUT) as resp, tmp.open("wb") as fh:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = resp.read(65536)
            if not chunk:
                break
            fh.write(chunk)
            done += len(chunk)
            if progress and total:
                progress(int(done * 100 / total))
    tmp.replace(dest)
    return dest


def launch_installer(path: Path) -> bool:
    """Avvia l'installer (Windows). Restituisce True se l'app deve chiudersi."""
    if sys.platform == "win32" and path.suffix.lower() == ".exe":
        subprocess.Popen([str(path)], close_fds=True)
        return True
    if sys.platform.startswith("linux") and path.suffix.lower() == ".appimage":
        os.chmod(path, 0o755)
    return False
