"""GitHub search helpers for stock-analysis repositories and source code."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from typing import Any

REPO_SEARCH_URL = "https://api.github.com/search/repositories"
CODE_SEARCH_URL = "https://api.github.com/search/code"
USER_AGENT = "stock-repo-search/1.1"

PRESETS: dict[str, dict[str, str]] = {
    "analysis": {
        "label": "General stock analysis",
        "query": "stock analysis",
    },
    "quant": {
        "label": "Quantitative finance / factor research",
        "query": "quantitative finance",
    },
    "backtest": {
        "label": "Strategy backtesting",
        "query": "stock backtesting",
    },
    "technical": {
        "label": "Technical indicators",
        "query": "stock technical analysis",
    },
    "fundamental": {
        "label": "Fundamental / value investing",
        "query": "stock fundamental analysis",
    },
    "sentiment": {
        "label": "News and social sentiment",
        "query": "stock sentiment analysis",
    },
    "ml": {
        "label": "Machine learning / price prediction",
        "query": "stock prediction machine learning",
    },
    "screener": {
        "label": "Stock screeners",
        "query": "stock screener",
    },
    "portfolio": {
        "label": "Portfolio optimization",
        "query": "stock portfolio optimization",
    },
    "us": {
        "label": "US equities",
        "query": "yfinance stock analysis",
    },
    "ashares": {
        "label": "A-shares / China market",
        "query": "akshare stock",
    },
}

CODE_PRESETS: dict[str, dict[str, Any]] = {
    "yfinance-talib": {
        "label": "yfinance + TA-Lib",
        "terms": ["import yfinance", "import talib"],
        "language": "python",
        "notes": "Repos that pull Yahoo prices and compute TA-Lib indicators.",
    },
    "yfinance-pandas-ta": {
        "label": "yfinance + pandas-ta",
        "terms": ["import yfinance", "import pandas_ta"],
        "language": "python",
        "notes": "Same idea as TA-Lib, using the pandas-ta wrapper.",
    },
    "yfinance-backtrader": {
        "label": "yfinance + Backtrader",
        "terms": ["import yfinance", "import backtrader"],
        "language": "python",
        "notes": "Price download plus an event-driven backtester.",
    },
    "yfinance-vectorbt": {
        "label": "yfinance + VectorBT",
        "terms": ["import yfinance", "import vectorbt"],
        "language": "python",
        "notes": "Vectorized backtesting on Yahoo data.",
    },
    "alpaca-trading": {
        "label": "Alpaca trading API",
        "terms": ["import alpaca"],
        "language": "python",
        "notes": "Broker / paper-trading integrations.",
    },
    "ccxt-freqtrade": {
        "label": "CCXT crypto exchanges",
        "terms": ["import ccxt"],
        "language": "python",
        "notes": "Unified crypto exchange clients.",
    },
}


class GitHubError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def resolve_token(explicit: str | None = None) -> str | None:
    if explicit and explicit.strip():
        return explicit.strip()
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def _headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_get(url: str, token: str | None, timeout: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(url, headers=_headers(token))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            if isinstance(payload, dict):
                payload["_rate_limit_remaining"] = resp.headers.get("X-RateLimit-Remaining")
                payload["_rate_limit_limit"] = resp.headers.get("X-RateLimit-Limit")
            return payload
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        hint = ""
        if exc.code == 401:
            hint = " Token is missing or invalid."
        elif exc.code == 403:
            hint = " Rate limit or code-search auth required. Set GITHUB_TOKEN."
        elif exc.code == 422:
            hint = " GitHub rejected the query syntax."
        raise GitHubError(f"GitHub API error {exc.code}: {body}{hint}", status=exc.code) from exc
    except urllib.error.URLError as exc:
        raise GitHubError(f"Network error talking to GitHub: {exc}") from exc


def build_repo_query(
    text: str,
    language: str | None = None,
    min_stars: int = 0,
    include_archived: bool = False,
    include_forks: bool = False,
) -> str:
    parts = [text.strip()]
    if language:
        parts.append(f"language:{language}")
    if min_stars > 0:
        parts.append(f"stars:>={min_stars}")
    if not include_archived:
        parts.append("archived:false")
    if not include_forks:
        parts.append("fork:false")
    return " ".join(p for p in parts if p)


def search_repositories(
    query: str,
    sort: str = "stars",
    order: str = "desc",
    per_page: int = 15,
    token: str | None = None,
) -> dict[str, Any]:
    params = {
        "q": query,
        "order": order,
        "per_page": str(min(max(per_page, 1), 100)),
    }
    if sort and sort != "best-match":
        params["sort"] = sort
    url = f"{REPO_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    return github_get(url, token)


def normalize_repo(item: dict[str, Any]) -> dict[str, Any]:
    license_info = item.get("license") or {}
    return {
        "full_name": item.get("full_name"),
        "url": item.get("html_url"),
        "description": (item.get("description") or "").replace("\n", " ").strip(),
        "language": item.get("language") or "",
        "stars": item.get("stargazers_count") or 0,
        "forks": item.get("forks_count") or 0,
        "issues": item.get("open_issues_count") or 0,
        "updated": (item.get("updated_at") or "")[:10],
        "created": (item.get("created_at") or "")[:10],
        "topics": ",".join(item.get("topics") or []),
        "license": license_info.get("spdx_id") or "",
        "archived": bool(item.get("archived")),
    }


def search_code(
    query: str,
    per_page: int = 30,
    token: str | None = None,
) -> dict[str, Any]:
    params = {
        "q": query,
        "per_page": str(min(max(per_page, 1), 100)),
    }
    url = f"{CODE_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    return github_get(url, token)


def build_code_query(
    term: str,
    language: str | None = None,
    extension: str | None = None,
    include_forks: bool = False,
) -> str:
    parts = [term.strip()]
    if language:
        parts.append(f"language:{language}")
    if extension:
        ext = extension.lstrip(".")
        parts.append(f"extension:{ext}")
    if not include_forks:
        parts.append("fork:false")
    return " ".join(p for p in parts if p)


def normalize_code_hit(item: dict[str, Any]) -> dict[str, Any]:
    repo = item.get("repository") or {}
    return {
        "repo": repo.get("full_name") or "",
        "repo_url": repo.get("html_url") or "",
        "private": bool(repo.get("private")),
        "file": item.get("name") or "",
        "path": item.get("path") or "",
        "file_url": item.get("html_url") or "",
    }


def intersect_code_terms(
    terms: list[str],
    language: str | None = None,
    extension: str | None = None,
    include_forks: bool = False,
    per_page: int = 50,
    token: str | None = None,
) -> dict[str, Any]:
    """Find repositories that mention every term (possibly in different files)."""
    if not terms:
        raise GitHubError("Provide at least one code search term.")

    cleaned = [t.strip() for t in terms if t and t.strip()]
    if len(cleaned) == 1:
        query = build_code_query(cleaned[0], language, extension, include_forks)
        payload = search_code(query, per_page=per_page, token=token)
        hits = [normalize_code_hit(item) for item in payload.get("items", [])]
        return {
            "mode": "single",
            "queries": [query],
            "hits": hits,
            "repos": _group_code_hits(hits),
            "total_count": payload.get("total_count", 0),
            "rate_limit_remaining": payload.get("_rate_limit_remaining"),
        }

    per_term: list[list[dict[str, Any]]] = []
    queries: list[str] = []
    remaining = None
    totals: list[int] = []
    for term in cleaned:
        query = build_code_query(term, language, extension, include_forks)
        queries.append(query)
        payload = search_code(query, per_page=per_page, token=token)
        hits = [normalize_code_hit(item) for item in payload.get("items", [])]
        per_term.append(hits)
        totals.append(int(payload.get("total_count") or 0))
        remaining = payload.get("_rate_limit_remaining")

    repo_sets = [{hit["repo"] for hit in hits if hit["repo"]} for hits in per_term]
    common = set.intersection(*repo_sets) if repo_sets else set()

    combined: list[dict[str, Any]] = []
    seen = set()
    for hits in per_term:
        for hit in hits:
            if hit["repo"] not in common:
                continue
            key = (hit["repo"], hit["path"])
            if key in seen:
                continue
            seen.add(key)
            combined.append(hit)

    return {
        "mode": "intersection",
        "queries": queries,
        "hits": combined,
        "repos": _group_code_hits(combined),
        "matched_repos": sorted(common),
        "term_totals": totals,
        "rate_limit_remaining": remaining,
    }


def _group_code_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"repo": "", "repo_url": "", "files": []}
    )
    for hit in hits:
        name = hit["repo"]
        bucket = grouped[name]
        bucket["repo"] = name
        bucket["repo_url"] = hit["repo_url"]
        bucket["files"].append(
            {
                "file": hit["file"],
                "path": hit["path"],
                "file_url": hit["file_url"],
            }
        )
    return sorted(grouped.values(), key=lambda row: row["repo"].lower())
