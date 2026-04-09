"""
knowledge_base.py
Load và tìm kiếm dữ liệu từ policies.jsonl và faq_demo.jsonl
"""

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def _load_jsonl(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


POLICIES: list[dict] = _load_jsonl("policies.jsonl")
FAQS: list[dict] = _load_jsonl("faq_demo.jsonl")

# Index for quick lookup
POLICY_BY_ID: dict[str, dict] = {p["policy_id"]: p for p in POLICIES}


# ---------------------------------------------------------------------------
# Search helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set[str]:
    """Simple Vietnamese tokenizer: lowercase + split on spaces and punctuation."""
    import re
    text = text.lower()
    tokens = re.findall(r"[\wàáâãèéêìíòóôõùúăđĩũơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹý]+", text)
    return set(tokens)


def _score_policy(policy: dict, query_tokens: set[str]) -> float:
    """Score a policy against query tokens based on keyword overlap."""
    text_parts = [
        policy.get("title", ""),
        policy.get("summary", ""),
        policy.get("details", ""),
        policy.get("category", ""),
        " ".join(policy.get("conditions", [])),
    ]
    doc_tokens = _tokenize(" ".join(text_parts))
    if not doc_tokens:
        return 0.0
    overlap = len(query_tokens & doc_tokens)
    # Boost title matches
    title_tokens = _tokenize(policy.get("title", ""))
    title_match = len(query_tokens & title_tokens)
    return overlap + title_match * 1.5


def _score_faq(faq: dict, query_tokens: set[str]) -> float:
    text = faq.get("user_question", "") + " " + faq.get("answer", "") + " " + faq.get("intent", "")
    doc_tokens = _tokenize(text)
    if not doc_tokens:
        return 0.0
    return len(query_tokens & doc_tokens)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search_policies(query: str, top_k: int = 4) -> list[dict]:
    """Return top-k policies relevant to the query."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return POLICIES[:top_k]

    scored = [(p, _score_policy(p, query_tokens)) for p in POLICIES]
    scored.sort(key=lambda x: x[1], reverse=True)
    results = [p for p, score in scored if score > 0][:top_k]
    return results if results else POLICIES[:2]


def search_faqs(query: str, top_k: int = 3) -> list[dict]:
    """Return top-k FAQs relevant to the query."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return FAQS[:top_k]

    scored = [(f, _score_faq(f, query_tokens)) for f in FAQS]
    scored.sort(key=lambda x: x[1], reverse=True)
    results = [f for f, score in scored if score > 0][:top_k]
    return results


def get_policy_by_id(policy_id: str) -> dict | None:
    return POLICY_BY_ID.get(policy_id)


def format_policies_for_prompt(policies: list[dict]) -> str:
    """Format policies into a compact string for the prompt context."""
    lines = []
    for p in policies:
        lines.append(f"[{p['policy_id']}] {p['title']}")
        lines.append(f"  Tóm tắt: {p['summary']}")
        lines.append(f"  Chi tiết: {p['details']}")
        if p.get("price_info"):
            lines.append(f"  Giá: {json.dumps(p['price_info'], ensure_ascii=False)}")
        if p.get("conditions"):
            lines.append(f"  Điều kiện: {'; '.join(p['conditions'])}")
        lines.append("")
    return "\n".join(lines)


def format_faqs_for_prompt(faqs: list[dict]) -> str:
    """Format FAQs into a compact string for the prompt context."""
    if not faqs:
        return ""
    lines = ["Ví dụ câu hỏi tương tự:"]
    for f in faqs:
        lines.append(f"  Q: {f['user_question']}")
        lines.append(f"  A: {f['answer']}")
        lines.append("")
    return "\n".join(lines)
