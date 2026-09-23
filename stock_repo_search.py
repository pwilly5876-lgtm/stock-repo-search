#!/usr/bin/env python3
"""Search GitHub for stock-analysis repositories and library usage in code.

Examples:
  python stock_repo_search.py
  python stock_repo_search.py --preset quant --min-stars 200 --limit 20
  python stock_repo_search.py --mode code --code-preset yfinance-talib
  python stock_repo_search.py --mode code --term "import yfinance" --term "import talib"
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from typing import Any

from stock_github import (
    CODE_PRESETS,
    PRESETS,
    GitHubError,
    build_repo_query,
    intersect_code_terms,
    normalize_repo,
    resolve_token,
    search_repositories,
)


def print_repo_table(rows: list[dict[str, Any]]) -> None:
    if not rows:
        print("No repositories found.")
        return
    print(f"{'STARS':>7} {'FORKS':>6} {'LANG':<12} {'UPDATED':<10} {'REPO':<40} DESCRIPTION")
    print("-" * 140)
    for row in rows:
        print(
            f"{row['stars']:>7} {row['forks']:>6} {str(row['language'])[:12]:<12} "
            f"{row['updated']:<10} {str(row['full_name'])[:40]:<40} {row['description'][:70]}"
        )
        print(f"{'':>7} {'':>6} {'':<12} {'':<10} {row['url']}")


def print_code_table(result: dict[str, Any]) -> None:
    repos = result.get("repos") or []
    if not repos:
        print("No matching repositories.")
        return
    print(f"{'REPO':<40} FILES  URL")
    print("-" * 120)
    for row in repos:
        print(f"{row['repo'][:40]:<40} {len(row['files']):>5}  {row['repo_url']}")
        for file_hit in row["files"][:5]:
            print(f"    {file_hit['path']}")


def write_csv(path: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        with open(path, "w", newline="", encoding="utf-8") as fh:
            fh.write("")
        return
    fields = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search GitHub for repositories that analyze stocks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Repo presets: "
        + ", ".join(PRESETS)
        + "\nCode presets: "
        + ", ".join(CODE_PRESETS),
    )
    parser.add_argument("query", nargs="*", help="Free-text repo search")
    parser.add_argument("--mode", choices=["repos", "code"], default="repos")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="analysis")
    parser.add_argument("--code-preset", choices=sorted(CODE_PRESETS))
    parser.add_argument(
        "--term",
        action="append",
        dest="terms",
        help="Code snippet to find. Repeat for intersection (yfinance + talib).",
    )
    parser.add_argument("--language", "-l", help="Language filter, e.g. python")
    parser.add_argument("--min-stars", type=int, default=50)
    parser.add_argument(
        "--sort",
        choices=["stars", "forks", "updated", "best-match"],
        default="stars",
    )
    parser.add_argument("--order", choices=["desc", "asc"], default="desc")
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--include-archived", action="store_true")
    parser.add_argument("--include-forks", action="store_true")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--out", help="Write results to this file")
    parser.add_argument("--list-presets", action="store_true")
    parser.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list_presets:
        print("Repository presets:\n")
        for key, spec in PRESETS.items():
            print(f"  {key:<12} {spec['label']}")
            print(f"               {spec['query']}\n")
        print("Code presets:\n")
        for key, spec in CODE_PRESETS.items():
            print(f"  {key:<22} {spec['label']}")
            print(f"                       {spec['notes']}")
            print(f"                       terms: {spec['terms']}\n")
        return 0

    token = resolve_token(args.token)
    try:
        if args.mode == "code":
            return run_code_search(args, token)
        return run_repo_search(args, token)
    except GitHubError as exc:
        print(str(exc), file=sys.stderr)
        return 1


def run_repo_search(args: argparse.Namespace, token: str | None) -> int:
    preset = PRESETS[args.preset]
    text = " ".join(args.query).strip() or preset["query"]
    query = build_repo_query(
        text,
        args.language,
        args.min_stars,
        args.include_archived,
        args.include_forks,
    )
    print(f"Query : {query}", file=sys.stderr)
    payload = search_repositories(
        query,
        sort=args.sort,
        order=args.order,
        per_page=args.limit,
        token=token,
    )
    items = [normalize_repo(item) for item in payload.get("items", [])]
    print(
        f"Hits  : {len(items)} shown of {payload.get('total_count', 0)} total",
        file=sys.stderr,
    )
    remaining = payload.get("_rate_limit_remaining")
    if remaining is not None:
        print(f"Rate  : {remaining} remaining", file=sys.stderr)
    emit(args, items, {"query": query, "mode": "repos"})
    return 0


def run_code_search(args: argparse.Namespace, token: str | None) -> int:
    if args.code_preset:
        spec = CODE_PRESETS[args.code_preset]
        terms = list(spec["terms"])
        language = args.language or spec.get("language")
    else:
        terms = args.terms or ["import yfinance", "import talib"]
        language = args.language or "python"

    print(f"Terms : {terms}", file=sys.stderr)
    result = intersect_code_terms(
        terms,
        language=language,
        include_forks=args.include_forks,
        per_page=max(args.limit, 20),
        token=token,
    )
    print(f"Mode  : {result['mode']}", file=sys.stderr)
    for query in result.get("queries", []):
        print(f"Query : {query}", file=sys.stderr)
    if result.get("rate_limit_remaining") is not None:
        print(f"Rate  : {result['rate_limit_remaining']} remaining", file=sys.stderr)

    if args.format == "table" and not args.out:
        print_code_table(result)
        return 0

    rows = [
        {
            "repo": row["repo"],
            "url": row["repo_url"],
            "matching_files": len(row["files"]),
            "paths": ";".join(file_hit["path"] for file_hit in row["files"]),
        }
        for row in result.get("repos", [])
    ]
    emit(args, rows, {"mode": "code", "queries": result.get("queries")})
    return 0


def emit(args: argparse.Namespace, rows: list[dict[str, Any]], extra: dict[str, Any]) -> None:
    out_path = args.out
    if args.format == "csv" and not out_path:
        out_path = "stock_repos.csv"
    if args.format == "json" and not out_path:
        out_path = "stock_repos.json"

    if args.format == "table" and not out_path:
        print_repo_table(rows)
        return

    meta = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "returned": len(rows),
        **extra,
    }
    if out_path and out_path.endswith(".json") or args.format == "json":
        path = out_path or "stock_repos.json"
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"meta": meta, "results": rows}, fh, indent=2, ensure_ascii=False)
        print(f"Wrote {len(rows)} rows to {path}")
        return

    path = out_path or "stock_repos.csv"
    write_csv(path, rows)
    print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    raise SystemExit(main())
