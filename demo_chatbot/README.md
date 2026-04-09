# Vinmec Maternity Policy Bot (Demo)

Đây là phiên bản chuyển đổi từ mẫu `agent.py + system_prompt.txt + tools.py` sang chatbot tra cứu **chính sách thai sản Vinmec** dựa trên 2 file database local:

- `policies.jsonl`
- `faq_demo.jsonl`

## 1. Cấu trúc file

- `agent.py`: LangGraph agent loop tương tự mẫu TravelBuddy
- `tools.py`: tool kiểm tra phạm vi, tra cứu policy, tra cứu FAQ, log feedback
- `system_prompt.txt`: prompt điều khiển hành vi bot
- `policies.jsonl`: knowledge base policy
- `faq_demo.jsonl`: câu hỏi mẫu / intent mẫu
- `feedback_log.jsonl`: log phản hồi khi user báo sai

## 2. Cài thư viện

```bash
pip install langgraph langchain-openai langchain-core python-dotenv
```

## 3. Thiết lập API key

Tạo `.env`:

```env
OPENAI_API_KEY=your_key_here
```

## 4. Chạy bot

Đứng trong thư mục `vinmec_chatbot` rồi chạy:

```bash
python agent.py
```

## 5. Flow hoạt động

1. User hỏi.
2. Bot gọi `check_maternity_policy_scope` để xác định đúng phạm vi hay không.
3. Nếu đúng phạm vi, bot gọi `search_policy_kb` để lấy policy liên quan nhất.
4. Nếu cần, bot gọi thêm `search_faq_kb` để tham khảo câu hỏi tương tự.
5. Bot trả lời ngắn gọn, kèm mã policy làm nguồn tham chiếu.
6. Nếu user báo sai / chưa đúng, bot gọi `log_user_feedback` để append vào `feedback_log.jsonl`.

## 6. Ví dụ câu hỏi nên test

- `Gói thai sản 36 tuần gồm những gì?`
- `Sinh mổ lần 2 ở Smart City khoảng bao nhiêu tiền?`
- `Tháng 4 có ưu đãi gì cho gói sinh không?`
- `Nếu không mua gói thì nhập viện có cần tạm ứng bao nhiêu?`
- `Bảo hiểm AIA có chi trả toàn bộ không?`
- `Em đang đau bụng và ra máu thì có sao không?`  ← bot phải từ chối tư vấn y khoa và điều hướng.
- `Thông tin này không đúng rồi` ← bot nên ghi log feedback.

## 7. Lưu ý quan trọng

Dữ liệu bạn cung cấp đang có trường `verification_status = demo_synthetic`, nên bot này là **demo chatbot bám theo database nội bộ bạn gửi**, chưa phải hệ thống xác nhận chính sách chính thức ngoài thực tế.
