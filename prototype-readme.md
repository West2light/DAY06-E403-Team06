# Prototype - Vinmec maternity policy chatbot

## Mô tả

Bản thử nghiệm (prototype) này mô phỏng một chatbot AI hỗ trợ mẹ bầu và gia đình tra cứu nhanh thông tin về các gói thai sản, bảo hiểm, chi phí, điều kiện đăng ký và các chính sách liên quan của Vinmec.

Mục tiêu của bản thử nghiệm này là thể hiện rõ vai trò của AI trong bài toán này:

- Trả lời nhanh các câu hỏi đúng phạm vi chính sách thai sản.
- Hỏi lại khi người dùng cung cấp chưa đủ thông tin.
- Chỉ trả lời khi tìm được nguồn chính thức.
- Cho phép chuyển đổi sang nhân viên thật (handoff) khi không chắc chắn.
- Ghi nhận phản hồi (feedback) để cải thiện cơ sở tri thức (knowledge base) và câu lệnh (prompt) ở các vòng sau.

## Level: Hybrid prototype

- **Mock UI/flow:** Có các tệp HTML để minh họa giao diện và luồng xử lý của chatbot.
- **Working app local:** Có ứng dụng `vinmec-chatbot/` chạy được bằng FastAPI và giao diện người dùng (frontend) tĩnh.
- **AI behavior:** Phần phụ trợ (backend) có tác nhân (agent), câu lệnh (prompt), cơ sở tri thức (knowledge base), gọi công cụ (tool calling) và ghi nhật ký phản hồi (feedback logging).

Bản thử nghiệm này không chỉ dùng để trình bày giao diện (UI), mà đã mô phỏng được logic cốt lõi của sản phẩm theo hướng ưu tiên tính chính xác (precision-first) như đã nêu trong đặc tả (spec).

## Luồng prototype

Luồng chính được thể hiện trong `vinmec_chatbot_flow.html`:

1. Người dùng gửi câu hỏi về chính sách thai sản, giá gói, quyền lợi, bảo hiểm.
2. Hệ thống kiểm tra xem câu hỏi có nằm trong phạm vi của chatbot hay không.
3. Nếu câu hỏi mơ hồ, bot sẽ hỏi lại để làm rõ thêm thông tin.
4. Hệ thống truy xuất cơ sở tri thức (knowledge base) của Vinmec.
5. Nếu không tìm được nguồn đủ tin cậy, bot sẽ thông báo không chắc chắn và chuyển hướng sang nhân viên thật.
6. Nếu tìm được nguồn chính thức, bot sẽ tạo câu trả lời ngắn gọn, rõ ràng và bám sát tài liệu.
7. Người dùng có thể để lại phản hồi; phản hồi này sẽ được lưu lại để nhân viên xem xét và cập nhật hệ thống.

## Links

- Đặc tả tổng hợp: `spec-final.md`
- Luồng prototype: `vinmec_chatbot_flow.html`
- Bản thử nghiệm giao diện (UI prototype): `vinmec_chatbot_prototype.html`
- Bản thử nghiệm giao diện (UI prototype) phiên bản 2: `vinmec_chatbot_prototype_v2.html`
- Ứng dụng chạy cục bộ: `vinmec-chatbot/`
- Tổng quan kho lưu trữ và cài đặt: `README.md`

## Tools

- **Frontend/UI:** HTML, CSS
- **Backend:** FastAPI
- **Điều phối AI (AI orchestration):** OpenAI API + gọi hàm/công cụ (function/tool calling)
- **Cơ sở tri thức (Knowledge base):** Các tệp JSONL cho các chính sách và FAQ demo.
- **Viết câu lệnh (Prompting):** `backend/prompts/system_prompt.txt`
- **Ghi nhật ký phản hồi (Feedback logging):** `backend/tools.py` + `backend/feedback_log.jsonl`

## Phân công

| Thành viên | Phần                                      | Output                                               |
| ---------- | ----------------------------------------- | ---------------------------------------------------- |
| Đông       | Canvas + failure modes + demo slides      | spec/spec-final.md phần 1, 4, demo/slides.pdf        |
| Dũng       | User stories 4 paths + prompt engineering | spec/spec-final.md phần 2, prototype/prompt-tests.md |
| Giang      | Eval metrics + ROI                        | spec/spec-final.md phần 3, 5, demo/slides.pdf        |
| Trung      | UI prototype + demo script                | prototype/, demo/demo-script.md                      |
