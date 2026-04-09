from __future__ import annotations

import json
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

BASE_DIR = Path(__file__).resolve().parent
FAQ_PATH = BASE_DIR / "faq_demo.jsonl"
POLICY_PATH = BASE_DIR / "policies.jsonl"
FEEDBACK_LOG_PATH = BASE_DIR / "feedback_log.jsonl"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


FAQ_DB = _load_jsonl(FAQ_PATH)
POLICY_DB = _load_jsonl(POLICY_PATH)
TODAY = date.today()


FACILITY_ALIASES = {
    "times city": "times_city",
    "timescity": "times_city",
    "smart city": "smart_city",
    "smartcity": "smart_city",
    "ocean park 2": "ocean_park_2",
    "oceanpark2": "ocean_park_2",
    "hung yen": "hung_yen",
    "hungy en": "hung_yen",
    "hungyên": "hung_yen",
    "hai phong": "hai_phong",
    "haiphong": "hai_phong",
    "sai gon": "sai_gon",
    "saigon": "sai_gon",
}

IN_SCOPE_KEYWORDS = {
    "thai san", "goi sinh", "goi thai san", "sinh thuong", "sinh mo", "de thuong",
    "de mo", "mo lan 2", "bao hiem", "bao lanh", "dong chi tra", "quyen loi",
    "dieu kien dang ky", "dang ky goi", "ho so sinh", "tam ung", "nhap vien",
    "phong nhi", "phong sau sinh", "khuyen mai", "uu dai", "qua tang", "tai kham",
    "sau sinh", "di sinh", "me va be", "goi 27 tuan", "goi 36 tuan", "vac xin rsv",
    "ivf", "bac si", "chi phi sinh", "gia phong", "danh sach do can chuan bi",
}

OUT_OF_SCOPE_MEDICAL_KEYWORDS = {
    "dau bung", "ra mau", "ra huyet", "thai may dap", "sot", "ho", "kho tho",
    "ngat", "phu", "dau dau", "co cung", "con co", "tuc nguc", "ngua", "noi man",
    "dich am dao", "viem", "thuoc", "uong thuoc", "chan doan", "trieu chung",
    "co nguy hiem khong", "co sao khong", "nen an gi", "nen uong gi", "tu van y khoa",
    "mac benh", "benh gi", "dau hieu benh"
}

OFF_TOPIC_KEYWORDS = {
    "viet code", "lam bai tap", "chinh tri", "chung khoan", "crypto", "thue nha",
    "dat ve may bay", "khach san", "du lich", "lap trinh", "sql", "giai toan",
}

AMBIGUOUS_PATTERNS = {
    "goi nay", "gia bao nhieu", "bao hiem co ap dung khong", "co uu dai khong",
    "dieu kien la gi", "quyen loi la gi", "nhu the nao", "co duoc khong",
}


def _strip_accents(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", text)



def _normalize(text: str) -> str:
    text = _strip_accents(text.lower())
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text



def _tokenize(text: str) -> set[str]:
    return set(_normalize(text).split())



def _extract_facility_keys(text: str) -> set[str]:
    normalized = _normalize(text)
    found: set[str] = set()
    for alias, canonical in FACILITY_ALIASES.items():
        if alias in normalized:
            found.add(canonical)
    return found



def _is_active_policy(policy: dict[str, Any]) -> bool:
    try:
        start = date.fromisoformat(policy["effective_from"])
        end = date.fromisoformat(policy["effective_to"])
        return start <= TODAY <= end
    except Exception:
        return True



def _format_price(value: int | float | None) -> str:
    if value is None:
        return "Không có dữ liệu"
    return f"{int(value):,}".replace(",", ".") + "đ"



def _format_price_info(price_info: dict[str, Any] | None) -> str:
    if not price_info:
        return "Không có thông tin giá cụ thể trong dữ liệu."

    pieces: list[str] = []
    for key, value in price_info.items():
        pretty_key = key.replace("_", " ")
        if isinstance(value, (int, float)):
            if "percent" in key:
                pieces.append(f"- {pretty_key}: {value}%")
            else:
                pieces.append(f"- {pretty_key}: {_format_price(int(value))}")
        else:
            pieces.append(f"- {pretty_key}: {value}")
    return "\n".join(pieces)



def _lexical_score(query: str, text: str) -> int:
    q = _tokenize(query)
    t = _tokenize(text)
    overlap = q & t
    return len(overlap)



def _policy_score(query: str, policy: dict[str, Any]) -> int:
    searchable_text = " ".join([
        policy.get("title", ""),
        policy.get("summary", ""),
        policy.get("details", ""),
        policy.get("category", ""),
        " ".join(policy.get("conditions", []) or []),
        " ".join(policy.get("exceptions", []) or []),
        " ".join(policy.get("facility_scope", []) or []),
    ])
    score = _lexical_score(query, searchable_text)

    # Ưu tiên policy còn hiệu lực.
    if _is_active_policy(policy):
        score += 2

    # Ưu tiên policy khớp theo facility nếu người dùng nhắc tới cơ sở cụ thể.
    query_facilities = _extract_facility_keys(query)
    if query_facilities:
        policy_facilities = set(policy.get("facility_scope", []))
        if "all" in policy_facilities or query_facilities & policy_facilities:
            score += 3
        else:
            score -= 2

    # Ưu tiên các policy có từ khóa giá nếu user đang hỏi giá.
    normalized = _normalize(query)
    if any(word in normalized for word in ["gia", "chi phi", "bao nhieu", "tam ung", "phu thu"]):
        if policy.get("price_info"):
            score += 2

    return score



def _faq_score(query: str, faq: dict[str, Any]) -> int:
    searchable_text = " ".join([
        faq.get("user_question", ""),
        faq.get("intent", ""),
        faq.get("answer", ""),
        " ".join(faq.get("linked_policies", []) or []),
    ])
    return _lexical_score(query, searchable_text)

def _contains_phrase(text: str, phrase: str) -> bool:
    text = f" {text} "
    phrase = f" {phrase.strip()} "
    return phrase in text


def _count_phrase_hits(text: str, phrases: set[str]) -> int:
    return sum(1 for phrase in phrases if _contains_phrase(text, phrase))

@tool
def check_maternity_policy_scope(user_query: str) -> str:
    """
    Kiểm tra câu hỏi của user có nằm trong phạm vi chatbot chính sách thai sản Vinmec hay không.

    Trả về một trong ba trạng thái:
    - in_scope: hỏi đúng phạm vi chính sách / quyền lợi / giá / điều kiện / bảo hiểm / quy trình
    - needs_clarification: có vẻ liên quan nhưng còn quá mơ hồ để trả lời chính xác
    - out_of_scope: hỏi ngoài phạm vi chính sách hoặc hỏi chuyên môn y khoa / triệu chứng / chủ đề khác
    """

    normalized = _normalize(user_query)
    token_count = len(normalized.split())

    # 1) Chủ đề ngoài hẳn chatbot
    off_topic_hits = _count_phrase_hits(normalized, OFF_TOPIC_KEYWORDS)
    if off_topic_hits > 0:
        return (
            "scope=out_of_scope\n"
            "reason=Câu hỏi thuộc chủ đề ngoài chatbot chính sách thai sản.\n"
            "recommended_action=Điều hướng sang kênh phù hợp khác hoặc từ chối lịch sự."
        )

    # 2) Tín hiệu y khoa / triệu chứng rõ ràng
    medical_hits = _count_phrase_hits(normalized, OUT_OF_SCOPE_MEDICAL_KEYWORDS)

    # Nếu user hỏi triệu chứng, thuốc, chẩn đoán... thì out_of_scope
    if medical_hits >= 1:
        return (
            "scope=out_of_scope\n"
            "reason=Câu hỏi đang đi vào chuyên môn y khoa hoặc triệu chứng bệnh, không phải policy/giá/quy trình.\n"
            "recommended_action=Khuyên user liên hệ bác sĩ hoặc nhân viên hỗ trợ y tế."
        )

    # 3) Tín hiệu policy thai sản
    in_scope_hits = _count_phrase_hits(normalized, IN_SCOPE_KEYWORDS)
    ambiguous_hits = _count_phrase_hits(normalized, AMBIGUOUS_PATTERNS)

    # Có thể tận dụng thêm tín hiệu từ chính KB
    policy_match_count = 0
    for policy in POLICY_DB:
        searchable_text = " ".join([
            policy.get("title", ""),
            policy.get("summary", ""),
            policy.get("category", ""),
        ])
        if _lexical_score(user_query, searchable_text) >= 2:
            policy_match_count += 1

    faq_match_count = 0
    for faq in FAQ_DB:
        searchable_text = " ".join([
            faq.get("user_question", ""),
            faq.get("intent", ""),
            faq.get("answer", ""),
        ])
        if _lexical_score(user_query, searchable_text) >= 2:
            faq_match_count += 1

    kb_signal = policy_match_count + faq_match_count

    # 4) Nếu có tín hiệu rõ về policy hoặc KB match tốt thì cho qua tra cứu
    if in_scope_hits >= 1 or kb_signal >= 1:
        # Câu quá ngắn / quá mơ hồ thì hỏi lại
        if ambiguous_hits >= 1 or token_count <= 3:
            return (
                "scope=needs_clarification\n"
                "reason=Câu hỏi có liên quan đến chính sách thai sản nhưng còn mơ hồ, chưa rõ gói nào / cơ sở nào / quyền lợi nào.\n"
                "recommended_action=Hỏi lại đúng một câu ngắn để làm rõ trước khi tra cứu tiếp."
            )

        return (
            "scope=in_scope\n"
            "reason=Câu hỏi có tín hiệu rõ về chính sách thai sản / giá / quyền lợi / điều kiện hoặc khớp knowledge base.\n"
            "recommended_action=Tra cứu knowledge base trước khi trả lời."
        )

    # 5) Không rõ có phải policy hay không
    if ambiguous_hits >= 1 or token_count <= 4:
        return (
            "scope=needs_clarification\n"
            "reason=Câu hỏi còn mơ hồ, chưa đủ để xác định đúng policy cần tra cứu.\n"
            "recommended_action=Hỏi lại đúng một câu để làm rõ trước khi tra cứu tiếp."
        )

    return (
        "scope=out_of_scope\n"
        "reason=Không nhận diện được đây là câu hỏi policy thai sản đủ rõ.\n"
        "recommended_action=Điều hướng sang tư vấn viên nếu user vẫn cần hỗ trợ."
    )


@tool
def search_policy_kb(query: str, top_k: int = 5) -> str:
    """
    Tìm policy phù hợp nhất từ knowledge base local policies.jsonl.
    Dùng khi user hỏi về giá, quyền lợi, điều kiện áp dụng, bảo hiểm, quy trình nhập viện,
    tái khám, ưu đãi, phòng, bác sĩ hoặc các chính sách liên quan.
    """

    ranked = sorted(POLICY_DB, key=lambda p: _policy_score(query, p), reverse=True)
    matches = [p for p in ranked if _policy_score(query, p) > 0][:max(1, top_k)]

    if not matches:
        return (
            "Không tìm thấy policy phù hợp trong knowledge base hiện tại.\n"
            "Gợi ý: cần nói rõ hơn gói thai sản, cơ sở, tuần thai hoặc loại bảo hiểm."
        )

    lines = [f"POLICY_MATCHES cho query: {query}"]
    for idx, policy in enumerate(matches, start=1):
        lines.append(f"\n{idx}. [{policy['policy_id']}] {policy['title']}")
        lines.append(f"Category: {policy['category']}")
        lines.append(f"Facility scope: {', '.join(policy.get('facility_scope', []))}")
        lines.append(f"Summary: {policy.get('summary', '')}")
        lines.append(f"Details: {policy.get('details', '')}")

        conditions = policy.get("conditions") or []
        if conditions:
            lines.append("Conditions:")
            for item in conditions:
                lines.append(f"- {item}")

        exceptions = policy.get("exceptions") or []
        if exceptions:
            lines.append("Exceptions:")
            for item in exceptions:
                lines.append(f"- {item}")

        lines.append("Price info:")
        lines.append(_format_price_info(policy.get("price_info")))
        lines.append(
            f"Effective: {policy.get('effective_from')} -> {policy.get('effective_to')} | "
            f"verification_status={policy.get('verification_status')} | "
            f"escalation_required={policy.get('escalation_required')}"
        )

    return "\n".join(lines)


@tool
def search_faq_kb(query: str, top_k: int = 3) -> str:
    """
    Tìm các câu FAQ tương tự trong faq_demo.jsonl để tham khảo cách diễn đạt và intent liên quan.
    Dùng như nguồn phụ trợ; không được ưu tiên hơn policy gốc.
    """

    ranked = sorted(FAQ_DB, key=lambda f: _faq_score(query, f), reverse=True)
    matches = [f for f in ranked if _faq_score(query, f) > 0][:max(1, top_k)]

    if not matches:
        return "Không tìm thấy FAQ tương tự trong bộ demo hiện tại."

    lines = [f"FAQ_MATCHES cho query: {query}"]
    for idx, faq in enumerate(matches, start=1):
        lines.append(f"\n{idx}. [{faq['faq_id']}] intent={faq['intent']}")
        lines.append(f"User question tương tự: {faq['user_question']}")
        lines.append(f"Linked policies: {', '.join(faq.get('linked_policies', []))}")
        lines.append(f"Answer mẫu: {faq['answer']}")

    return "\n".join(lines)


@tool
def log_user_feedback(user_question: str, assistant_answer: str, feedback_text: str) -> str:
    """
    Ghi nhận phản hồi khi user nói câu trả lời chưa đúng / chưa đủ / cần review.
    Tool này append vào feedback_log.jsonl để nhân viên có thể xem lại sau.
    """

    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user_question": user_question,
        "assistant_answer": assistant_answer,
        "feedback_text": feedback_text,
        "status": "pending_review",
    }

    with FEEDBACK_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return (
        "Đã ghi nhận feedback vào feedback_log.jsonl với trạng thái pending_review.\n"
        "Khuyến nghị phản hồi user rằng thông tin sẽ được đội ngũ kiểm tra lại."
    )
