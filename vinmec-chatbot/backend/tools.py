"""
tools.py
Định nghĩa OpenAI function-calling tools và hàm thực thi tương ứng.
"""

from knowledge_base import (
    search_policies,
    search_faqs,
    get_policy_by_id,
    format_policies_for_prompt,
    format_faqs_for_prompt,
)

# ---------------------------------------------------------------------------
# Tool schemas (OpenAI function definitions)
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Tìm kiếm trong Knowledge Base chính thức của Vinmec để lấy các chính sách "
                "và FAQ liên quan đến câu hỏi của người dùng. "
                "Luôn gọi tool này trước khi trả lời bất kỳ câu hỏi nào về gói thai sản, "
                "giá, quyền lợi, bảo hiểm, thủ tục nhập viện."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Truy vấn tìm kiếm bằng tiếng Việt. "
                            "Ví dụ: 'gói sinh 27 tuần giá bao nhiêu', "
                            "'bảo hiểm AIA đồng chi trả', 'sinh mổ lần 2 chi phí'"
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Số lượng kết quả trả về (mặc định 4, tối đa 6).",
                        "default": 4,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_policy_detail",
            "description": (
                "Lấy chi tiết đầy đủ của một chính sách theo policy_id. "
                "Dùng khi cần thông tin cụ thể hơn về một chính sách đã biết ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "policy_id": {
                        "type": "string",
                        "description": "ID của chính sách, ví dụ: P001, P003, P012",
                    }
                },
                "required": ["policy_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "classify_request_scope",
            "description": (
                "Phân loại câu hỏi có nằm trong phạm vi chatbot không. "
                "Gọi tool này khi không chắc chắn câu hỏi có phải là y tế thuần tuý "
                "hay câu hỏi chính sách/dịch vụ."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Câu hỏi của người dùng cần phân loại.",
                    }
                },
                "required": ["text"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

MEDICAL_KEYWORDS = {
    "đau bụng", "đau lưng", "ra máu", "xuất huyết", "triệu chứng", "bị sao",
    "có nguy hiểm", "chóng mặt", "buồn nôn", "nhức đầu", "khó thở",
    "rỉ ối", "vỡ ối", "cơn co", "thai nhi không động", "cấp cứu",
    "nguy hiểm không", "có sao không", "bình thường không", "nên làm gì",
    "uống thuốc gì", "tiêm gì", "xét nghiệm gì nên làm", "chỉ số bình thường",
    "nhịp tim thai", "siêu âm thấy", "bác sĩ nói", "chẩn đoán",
    "điều trị", "phác đồ", "thuốc uống", "kháng sinh",
}

OUT_OF_SCOPE_KEYWORDS = {
    "thời tiết", "chứng khoán", "tin tức", "thể thao", "nấu ăn",
    "du lịch", "nhà hàng", "khách sạn", "điện thoại", "laptop",
}


def execute_tool(tool_name: str, tool_args: dict) -> str:
    """Dispatch và thực thi tool, trả về string kết quả."""
    if tool_name == "search_knowledge_base":
        return _search_knowledge_base(**tool_args)
    elif tool_name == "get_policy_detail":
        return _get_policy_detail(**tool_args)
    elif tool_name == "classify_request_scope":
        return _classify_request_scope(**tool_args)
    else:
        return f"[ERROR] Tool không tồn tại: {tool_name}"


def _search_knowledge_base(query: str, top_k: int = 4) -> str:
    top_k = min(max(1, top_k), 6)
    policies = search_policies(query, top_k=top_k)
    faqs = search_faqs(query, top_k=2)

    parts = []
    if policies:
        parts.append("=== CHÍNH SÁCH TÌM THẤY ===")
        parts.append(format_policies_for_prompt(policies))
    if faqs:
        parts.append("=== VÍ DỤ FAQ LIÊN QUAN ===")
        parts.append(format_faqs_for_prompt(faqs))

    if not parts:
        return "Không tìm thấy thông tin liên quan trong Knowledge Base."

    return "\n".join(parts)


def _get_policy_detail(policy_id: str) -> str:
    policy = get_policy_by_id(policy_id)
    if not policy:
        return f"Không tìm thấy chính sách với ID: {policy_id}"
    return format_policies_for_prompt([policy])


def _classify_request_scope(text: str) -> str:
    lower = text.lower()
    tokens = set(lower.split())

    # Check medical
    for kw in MEDICAL_KEYWORDS:
        if kw in lower:
            return (
                "SCOPE: out_of_scope_medical\n"
                f"Lý do: Câu hỏi chứa từ khoá y tế: '{kw}'. "
                "Chatbot không tư vấn y tế lâm sàng."
            )

    # Check completely off-topic
    for kw in OUT_OF_SCOPE_KEYWORDS:
        if kw in lower:
            return (
                "SCOPE: out_of_scope_other\n"
                f"Lý do: Câu hỏi '{kw}' không liên quan đến dịch vụ Vinmec."
            )

    # Maternity/hospital keywords → in scope
    maternity_kw = {
        "gói", "sinh", "thai", "bầu", "mang thai", "đẻ", "mổ", "c-section",
        "bảo hiểm", "aia", "giá", "phí", "quyền lợi", "đặt lịch", "bác sĩ",
        "vinmec", "bệnh viện", "nhập viện", "phòng", "tạm ứng", "vaccine",
        "ivf", "thụ tinh", "tuần", "tháng", "ưu đãi", "khuyến mãi",
    }
    for kw in maternity_kw:
        if kw in lower:
            return "SCOPE: in_scope\nLý do: Câu hỏi liên quan đến dịch vụ thai sản/y tế Vinmec."

    return "SCOPE: ambiguous\nLý do: Chưa rõ phạm vi, nên hỏi thêm thông tin."
