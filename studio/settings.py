"""
Studio settings (API keys etc.). Saved to studio/data/settings.json, which is
never put in git or in any zip. Environment variables win over the file.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict

DATA = Path(__file__).resolve().parent / "data"
DEFAULT_PATH = DATA / "settings.json"
ENV_KEYS = {"brave_api_key": "BRAVE_SEARCH_API_KEY", "serpapi_key": "SERPAPI_API_KEY"}
DEFAULTS: Dict[str, Any] = {
    "brave_api_key": "", "serpapi_key": "", "contact_email": "",
    "provider_order": ["brave", "serpapi", "duckduckgo"],
    "max_web_queries": 6, "studio_password_hash": "",
}
_lock = threading.RLock()


def mask(v: str) -> str:
    if not v:
        return ""
    return "••••" + v[-4:] if len(v) > 8 else "••••"


class Settings:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path or os.environ.get("HVT_STUDIO_SETTINGS", DEFAULT_PATH))

    def load(self) -> Dict[str, Any]:
        with _lock:
            d = dict(DEFAULTS)
            if self.path.exists():
                try:
                    d.update(json.loads(self.path.read_text(encoding="utf-8")))
                except ValueError:
                    pass
            for k, env in ENV_KEYS.items():
                if os.environ.get(env):
                    d[k] = os.environ[env]
                    d[k + "_from_env"] = True
            return d

    def save(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        with _lock:
            cur = {}
            if self.path.exists():
                try:
                    cur = json.loads(self.path.read_text(encoding="utf-8"))
                except ValueError:
                    cur = {}
            for k, v in changes.items():
                if k not in DEFAULTS:
                    continue
                if k in ("brave_api_key", "serpapi_key") and isinstance(v, str) and v.startswith("••••"):
                    continue          # masked value sent back unchanged
                cur[k] = v
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(cur, indent=1), encoding="utf-8")
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass
            return self.public()

    def public(self) -> Dict[str, Any]:
        d = self.load()
        return {"brave_api_key": mask(d["brave_api_key"]), "brave_from_env": bool(d.get("brave_api_key_from_env")),
                "serpapi_key": mask(d["serpapi_key"]), "serpapi_from_env": bool(d.get("serpapi_key_from_env")),
                "contact_email": d.get("contact_email", ""), "provider_order": d["provider_order"],
                "max_web_queries": d["max_web_queries"],
                "studio_password_set": bool(d.get("studio_password_hash")),
                "saved_to": str(self.path)}
