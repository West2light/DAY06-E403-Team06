"""
agent.py
VinmecAgent: Agent loop sử dụng OpenAI function calling để tư vấn gói thai sản.
"""

import json
import os
from openai import OpenAI
from tools import TOOL_DEFINITIONS, execute_tool

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

BASE_SYSTEM_PROMPT = """Bạn là "Trợ lý Thai Sản Vinmec" – AI chatbot tư vấn chính thức về gói thai sản, \
giá dịch vụ, quyền lợi và chính sách bảo hiểm của hệ thống bệnh viện Vinmec Việt Nam.

## NGUYÊN TẮC CỐT LÕI
1. LUÔN gọi tool `search_knowledge_base` trước khi trả lời bất kỳ câu hỏi nào về chính sách/giá.
2. Chỉ trả lời dựa trên kết quả tool. KHÔNG bịa thêm thông tin.
3. Câu hỏi y tế lâm sàng (triệu chứng, điều trị, cấp cứu) → gọi `classify_request_scope`, rồi từ chối lịch sự.
4. Câu hỏi mơ hồ → hỏi làm rõ trước khi search.
5. Xưng "em", gọi khách hàng là "chị". Thân thiện, thấu cảm với mẹ bầu.
6. Ưu tiên Precision hơn Recall — thà không trả lời còn hơn nói sai.

## ĐỊNH DẠNG PHẢN HỒI CUỐI (JSON BẮT BUỘC)
Khi đã có đủ thông tin, trả về JSON object DUY NHẤT với cấu trúc sau:

{
  "type": "<success|warning|redirect|clarify|normal|log>",
  "text": "<nội dung chính, dùng <b>bold</b> và <br> cho xuống dòng>",
  "policy_tags": ["P001"],
  "price_table": {"rows": [{"label": "Tên mục", "val": "Giá trị"}]},
  "extra_text": "<thông tin bổ sung, inline HTML>",
  "quick_replies": ["Câu hỏi gợi ý 1"],
  "cta": {"primary": "📅 Đặt lịch tư vấn", "secondary": "📞 Gọi hotline"},
  "has_feedback": true,
  "clarify_options": ["Lựa chọn 1"],
  "redirect_options": [{"icon": "📞", "label": "...", "sub": "..."}],
  "no_source_options": [{"icon": "👩‍💼", "label": "...", "sub": "..."}],
  "log_details": "..."
}

## LOẠI PHẢN HỒI
- "success": Trả lời được từ KB. Thêm policy_tags, price_table nếu có số liệu, has_feedback=true.
- "clarify": Câu hỏi mơ hồ. Thêm clarify_options (3–4 lựa chọn cụ thể).
- "redirect": Câu hỏi y tế/khẩn cấp. Thêm redirect_options gồm hotline và đặt lịch bác sĩ.
- "warning": Trong phạm vi nhưng không đủ dữ liệu. Thêm no_source_options.
- "normal": Chào hỏi hoặc trả lời đơn giản. Thêm quick_replies gợi ý 4–5 câu hỏi thường gặp.
- "log": Người dùng phản hồi thông tin sai. Thêm log_details và cta.

CHỈ trả về JSON thuần, KHÔNG có markdown wrapper hay giải thích thêm.
"""

DEFAULT_REDIRECT_OPTIONS = [
    {"icon": "📞", "label": "Gọi hotline Vinmec", "sub": "1900 232 389 – 24/7"},
    {"icon": "👨‍⚕️", "label": "Đặt lịch khám bác sĩ", "sub": "Bác sĩ sản khoa tư vấn trực tiếp"},
    {"icon": "🚨", "label": "Khẩn cấp", "sub": "Đến cơ sở Vinmec gần nhất ngay"},
]

DEFAULT_NO_SOURCE_OPTIONS = [
    {"icon": "👩‍💼", "label": "Kết nối tư vấn viên", "sub": "Phản hồi trong vài phút"},
    {"icon": "📞", "label": "Gọi hotline", "sub": "1900 232 389"},
]

WELCOME_QUICK_REPLIES = [
    "💰 Gói 27 tuần giá bao nhiêu?",
    "📦 So sánh gói 27 và 36 tuần",
    "🏥 Chi phí sinh thường bao nhiêu?",
    "🔪 Chi phí sinh mổ lần 2?",
    "🎁 Ưu đãi tháng 4 có gì?",
    "🔒 Bảo hiểm AIA được bảo lãnh không?",
]

# ---------------------------------------------------------------------------
# VinmecAgent class
# ---------------------------------------------------------------------------

class VinmecAgent:
    """
    Agent xử lý hội thoại với người dùng.
    Mỗi session (session_id) có một instance riêng với conversation history.
    """

    MAX_TOOL_ITERATIONS = 4  # tránh vòng lặp vô tận

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation: list[dict] = []

    def reset(self):
        """Xoá lịch sử hội thoại."""
        self.conversation.clear()

    def get_welcome_message(self) -> dict:
        """Trả về tin nhắn chào hỏi khi bắt đầu phiên."""
        return {
            "type": "normal",
            "text": (
                "Xin chào chị! 👋 Em là trợ lý tư vấn gói thai sản của <b>Vinmec</b>.<br><br>"
                "Em có thể hỗ trợ chị về <b>gói thai sản, giá dịch vụ, quyền lợi, "
                "bảo hiểm và thủ tục nhập viện</b>. Chị cần hỏi gì ạ?"
            ),
            "quick_replies": WELCOME_QUICK_REPLIES,
        }

    def chat(self, user_message: str) -> dict:
        """
        Nhận tin nhắn người dùng, chạy agent loop, trả về response dict.
        """
        # Thêm user message vào history
        self.conversation.append({"role": "user", "content": user_message})

        messages = [
            {"role": "system", "content": BASE_SYSTEM_PROMPT},
            *self.conversation,
        ]

        # Agent loop
        for iteration in range(self.MAX_TOOL_ITERATIONS):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=0.2,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )

            choice = response.choices[0]

            # --- Tool calls ---
            if choice.finish_reason == "tool_calls":
                assistant_msg = choice.message
                messages.append(assistant_msg)

                # Thực thi từng tool call
                for tc in assistant_msg.tool_calls:
                    args = json.loads(tc.function.arguments)
                    result = execute_tool(tc.function.name, args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })

                # Tiếp tục loop để GPT xử lý kết quả tool
                continue

            # --- Final answer ---
            content = choice.message.content or "{}"
            try:
                result_dict = json.loads(content)
            except json.JSONDecodeError:
                result_dict = {"type": "normal", "text": content}

            # Lưu assistant response vào history
            self.conversation.append({
                "role": "assistant",
                "content": content,
            })

            # Đảm bảo các field mặc định
            return self._postprocess(result_dict)

        # Nếu hết iterations mà chưa trả lời
        return {
            "type": "warning",
            "text": "⚠️ Em chưa thể xử lý câu hỏi này. Vui lòng thử lại hoặc liên hệ tư vấn viên.",
            "no_source_options": DEFAULT_NO_SOURCE_OPTIONS,
        }

    def _postprocess(self, data: dict) -> dict:
        """Chuẩn hoá và điền giá trị mặc định cho response."""
        msg_type = data.get("type", "normal")

        # Đảm bảo redirect_options có giá trị mặc định
        if msg_type == "redirect" and not data.get("redirect_options"):
            data["redirect_options"] = DEFAULT_REDIRECT_OPTIONS

        # Đảm bảo no_source_options có giá trị mặc định
        if msg_type == "warning" and not data.get("no_source_options"):
            data["no_source_options"] = DEFAULT_NO_SOURCE_OPTIONS

        # Đảm bảo success luôn có has_feedback
        if msg_type == "success":
            data.setdefault("has_feedback", True)
            data.setdefault("cta", {
                "primary": "📅 Đặt lịch tư vấn",
                "secondary": "📞 Gọi hotline",
            })

        return data
