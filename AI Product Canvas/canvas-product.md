# AI Product Canvas — Vinmec Maternity Chatbot 🏥

Điền Canvas cho product AI của nhóm. Mỗi ô có câu hỏi guide — trả lời trực tiếp, xóa phần in nghiêng khi điền.

---

## 🎨 Canvas

|                   | **Value**                                                                                                                                                                             | **Trust**                                                                                                                                                                        | **Feasibility**                                                                                                   |
| :---------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------- |
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được?                                                                                                                 | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào?                                                                                | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì?                                                        |
| **Trả lời**       | Mẹ bầu & gia đình mất 20–40 phút/lần tìm thông tin gói thai sản, bảo hiểm, lịch khám — **AI trả lời tức thì, cá nhân hoá theo tuần thai**, thay vì phải gọi hotline hoặc lục website. | AI trả lời sai chính sách → user thấy khi info không khớp nhu cầu thực tế → nút "Xem nguồn" + "Hỏi nhân viên" hiện ngay dưới mỗi câu trả lời; sửa = 1 click escalate hoặc bấm 👎 | ~$0.005–0.02/query, latency <3s; risk chính: trả lời outdated khi Vinmec thay đổi chính sách mà KB chưa cập nhật. |

---

## 🤖 Automation hay augmentation?

- [ ] Automation — AI làm thay, user không can thiệp
- [x] Augmentation — AI gợi ý, user quyết định cuối cùng

**Justify:**

> Chatbot chỉ tư vấn, không thay thế quyết định của mẹ bầu hay nhân viên y tế. Luôn có lối thoát sang nhân viên Vinmec — cost of reject = 0, cost of wrong answer in healthcare = cao.

_Gợi ý: nếu AI sai mà user không biết → automation nguy hiểm, cân nhắc augmentation._

---

## 🧠 Learning signal

| #   | Câu hỏi                                          | Trả lời                                                                                                                                                                                           |
| :-- | :----------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | User correction đi vào đâu?                      | 👍/👎 + click "Hỏi nhân viên" → ghi vào correction log → nhân viên Vinmec review & validate định kỳ 2 tuần/lần → update knowledge base.                                                           |
| 2   | Product thu signal gì để biết tốt lên hay tệ đi? | **Implicit:** tỷ lệ hỏi lại cùng câu, tỷ lệ escalate sang nhân viên. <br>**Explicit:** CSAT sau mỗi session, 👎 per query. <br>**Mở rộng:** tỷ lệ câu hỏi out-of-scope để biết KB cần bổ sung gì. |
| 3   | Data thuộc loại nào?                             | [x] User-specific · [x] Domain-specific · [ ] Real-time · [x] Human-judgment · [ ] Khác                                                                                                           |

**📝 Chi tiết về Data:**

- Domain-specific (chính sách Vinmec — proprietary, model chung không biết)
- Human-judgment (nhân viên Vinmec label & validate)
- User-specific (tuần thai, loại gói dịch vụ)

**📈 Có marginal value không?**

> **Có.** Chính sách gói thai sản, bảo hiểm, lịch khám của Vinmec là dữ liệu proprietary — model nền không biết sẵn, không ai khác thu được cùng data này.
>
> **Data flywheel — vòng khép kín:** user questions + feedback + escalation → nhân viên label → update KB + cải thiện retrieval → tăng accuracy → giảm escalation rate → lặp lại. Cập nhật tối thiểu 2 tuần/lần hoặc ngay khi có thay đổi chính sách.
