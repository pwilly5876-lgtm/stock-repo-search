"""Streamlit UI for searching GitHub stock-analysis repos and source code."""

from __future__ import annotations

import pandas as pd
import streamlit as st

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

st.set_page_config(
    page_title="Stock Repo Search",
    page_icon="📈",
    layout="wide",
)

st.title("Stock Repo Search")
st.caption(
    "Find GitHub repositories that analyze stocks, then drill into source code "
    "that actually calls libraries like yfinance and TA-Lib."
)

with st.sidebar:
    st.header("GitHub access")
    token_input = st.text_input(
        "Personal access token",
        type="password",
        help="Optional but strongly recommended. Code search usually requires a token.",
        placeholder="ghp_…",
    )
    token = resolve_token(token_input)
    if token:
        st.success("Token loaded for this session.")
    else:
        st.warning("No token. Repo search works at a low rate; code search may fail.")

    st.markdown(
        "Create a classic token with **public_repo** scope at "
        "[GitHub settings](https://github.com/settings/tokens)."
    )
    st.divider()
    st.markdown(
        "Not financial advice. Stars measure popularity, not a trading edge."
    )

tab_repos, tab_code, tab_curated = st.tabs(
    ["Repository search", "Code search", "Curated starter list"]
)


def repo_dataframe(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    cols = [
        "stars",
        "forks",
        "language",
        "updated",
        "full_name",
        "url",
        "description",
        "topics",
        "license",
    ]
    return frame[[c for c in cols if c in frame.columns]]


with tab_repos:
    st.subheader("Search repositories")
    preset_keys = list(PRESETS.keys())
    left, right = st.columns([2, 1])
    with left:
        preset = st.selectbox(
            "Preset",
            preset_keys,
            format_func=lambda key: f"{key} — {PRESETS[key]['label']}",
        )
        custom = st.text_input(
            "Extra keywords (optional)",
            placeholder="pairs trading, earnings, options…",
        )
    with right:
        language = st.selectbox(
            "Language",
            ["python", "jupyter notebook", "go", "r", "any"],
            index=0,
        )
        min_stars = st.slider("Minimum stars", 0, 5000, 50, step=10)
        limit = st.slider("Results", 5, 50, 20)
        sort = st.selectbox("Sort", ["stars", "updated", "forks", "best-match"])

    include_archived = st.checkbox("Include archived", value=False)
    include_forks = st.checkbox("Include forks", value=False)

    text = custom.strip() or PRESETS[preset]["query"]
    lang = None if language == "any" else language
    query = build_repo_query(text, lang, min_stars, include_archived, include_forks)
    st.code(query, language="text")

    if st.button("Search repositories", type="primary"):
        try:
            with st.spinner("Talking to GitHub…"):
                payload = search_repositories(
                    query, sort=sort, per_page=limit, token=token
                )
            rows = [normalize_repo(item) for item in payload.get("items", [])]
            total = payload.get("total_count", 0)
            remaining = payload.get("_rate_limit_remaining")
            st.session_state["repo_rows"] = rows
            st.session_state["repo_meta"] = {
                "total": total,
                "remaining": remaining,
                "query": query,
            }
        except GitHubError as exc:
            st.error(str(exc))

    meta = st.session_state.get("repo_meta")
    rows = st.session_state.get("repo_rows")
    if meta:
        st.write(
            f"Showing {len(rows or [])} of {meta['total']} matches. "
            f"Rate limit remaining: {meta['remaining']}"
        )
    if rows:
        frame = repo_dataframe(rows)
        st.dataframe(
            frame,
            use_container_width=True,
            hide_index=True,
            column_config={
                "url": st.column_config.LinkColumn("GitHub"),
                "stars": st.column_config.NumberColumn(format="%d"),
                "forks": st.column_config.NumberColumn(format="%d"),
            },
        )
        st.download_button(
            "Download CSV",
            frame.to_csv(index=False).encode("utf-8"),
            file_name="stock_repos.csv",
            mime="text/csv",
        )


with tab_code:
    st.subheader("Find repos by the libraries they import")
    st.write(
        "This is the useful filter: not “repos *about* stocks”, but repos whose "
        "source actually calls **yfinance** and **TA-Lib** (or another pair)."
    )

    preset_name = st.selectbox(
        "Library combo",
        list(CODE_PRESETS.keys()) + ["custom"],
        format_func=lambda key: (
            "Custom terms"
            if key == "custom"
            else f"{CODE_PRESETS[key]['label']} — {CODE_PRESETS[key]['notes']}"
        ),
    )

    if preset_name == "custom":
        term_a = st.text_input("First snippet", value="import yfinance")
        term_b = st.text_input("Second snippet (optional)", value="import talib")
        language = st.selectbox("Language", ["python", "any"], index=0, key="code_lang")
        terms = [term_a] + ([term_b] if term_b.strip() else [])
        lang = None if language == "any" else language
    else:
        spec = CODE_PRESETS[preset_name]
        terms = list(spec["terms"])
        lang = spec.get("language")
        st.info(" + ".join(f"`{term}`" for term in terms))

    same_file = st.checkbox(
        "Require both terms in the same file",
        value=False,
        help="Off = same repository is enough (recommended for yfinance + TA-Lib).",
    )
    limit = st.slider("Hits per term", 10, 100, 40, key="code_limit")

    if st.button("Search source code", type="primary"):
        try:
            with st.spinner("Searching GitHub code…"):
                if same_file and len(terms) > 1:
                    joined = " ".join(f'"{term}"' for term in terms)
                    result = intersect_code_terms(
                        [joined],
                        language=lang,
                        per_page=limit,
                        token=token,
                    )
                else:
                    result = intersect_code_terms(
                        terms,
                        language=lang,
                        per_page=limit,
                        token=token,
                    )
            st.session_state["code_result"] = result
        except GitHubError as exc:
            st.error(str(exc))
            if not token:
                st.info("Add a GitHub token in the sidebar. Code search almost always needs one.")

    result = st.session_state.get("code_result")
    if result:
        st.caption("Queries used")
        for query in result.get("queries", []):
            st.code(query, language="text")
        if result.get("rate_limit_remaining") is not None:
            st.write(f"Rate limit remaining: {result['rate_limit_remaining']}")

        repos = result.get("repos") or []
        if result.get("mode") == "intersection":
            st.success(
                f"{len(result.get('matched_repos') or [])} repositories mention every term "
                f"(from the top {limit} hits per term)."
            )
        if not repos:
            st.warning("No overlapping repositories in this page of results. Try a token and a larger hit count.")
        else:
            summary_rows = [
                {
                    "repo": row["repo"],
                    "url": row["repo_url"],
                    "matching_files": len(row["files"]),
                    "sample_path": row["files"][0]["path"] if row["files"] else "",
                }
                for row in repos
            ]
            summary = pd.DataFrame(summary_rows)
            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True,
                column_config={"url": st.column_config.LinkColumn("GitHub")},
            )

            file_rows = []
            for row in repos:
                for file_hit in row["files"]:
                    file_rows.append(
                        {
                            "repo": row["repo"],
                            "path": file_hit["path"],
                            "file_url": file_hit["file_url"],
                        }
                    )
            files = pd.DataFrame(file_rows)
            with st.expander("Matching files"):
                st.dataframe(
                    files,
                    use_container_width=True,
                    hide_index=True,
                    column_config={"file_url": st.column_config.LinkColumn("File")},
                )
            st.download_button(
                "Download matching repos CSV",
                summary.to_csv(index=False).encode("utf-8"),
                file_name="code_search_repos.csv",
                mime="text/csv",
            )


with tab_curated:
    st.subheader("Hand-picked starting points")
    st.write("A short list of well-known projects so you are not starting from a blank search.")
    try:
        curated = pd.read_csv("curated_stock_analysis_repos.csv")
        st.dataframe(
            curated,
            use_container_width=True,
            hide_index=True,
            column_config={"url": st.column_config.LinkColumn("GitHub")},
        )
    except FileNotFoundError:
        st.info("curated_stock_analysis_repos.csv is missing from the working directory.")
