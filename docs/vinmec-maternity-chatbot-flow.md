# Vinmec Maternity Policy Chatbot - Flow Sketch

```mermaid
flowchart TD
    A([User mở chatbot Vinmec]) --> B[User gửi câu hỏi<br/>vd: gói thai sản, giá, quyền lợi, điều kiện, bảo hiểm]
    B --> C{Phân loại phạm vi<br/>"Chính sách thai sản Vinmec"?}

    C -- Không --> O[Thông báo ngoài phạm vi chatbot]
    O --> P[Điều hướng sang kênh phù hợp:<br/>Bác sĩ / CSKH / tư vấn viên]
    P --> Z([Kết thúc phiên hoặc chờ câu hỏi mới])

    C -- Có --> D[Truy xuất KB chính thức của Vinmec]
    D --> E{Đủ dữ liệu ngữ cảnh<br/>để trả lời chính xác?}

    E -- Chưa đủ --> F[Hỏi làm rõ:<br/>gói nào, tuần thai, loại bảo hiểm...]
    F --> G[User bổ sung thông tin]
    G --> D

    E -- Đủ --> H{Có nguồn chính thức<br/>và độ tin cậy đủ cao?}

    H -- Không --> I[Thông báo chưa thể xác nhận chính xác]
    I --> J[Đề xuất chuyển sang tư vấn viên thật]
    J --> Z

    H -- Có --> K[Trả lời ngắn gọn, rõ ràng, bám nguồn:<br/>quyền lợi, giá, điều kiện áp dụng]
    K --> L[Đề xuất bước tiếp theo:<br/>xem chi tiết gói / liên hệ tư vấn]

    L --> M{User xác nhận<br/>thông tin đúng?}

    M -- Đúng --> N([Kết thúc flow:<br/>user tiếp tục xem gói hoặc để lại nhu cầu])

    M -- Sai/Chưa đúng --> Q[User phản hồi "thông tin chưa đúng"]
    Q --> R[Ghi log phản hồi + hội thoại + nguồn đã dùng]
    R --> S[Nhân viên Vinmec review]
    S --> T[Cập nhật/hiệu chỉnh KB]
    T --> U[Cải thiện trả lời cho lượt sau]
    U --> Z
```
