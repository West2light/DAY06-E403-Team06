# SPEC — AI Product Hackathon

**Nhóm: 6** \_\_\_
Vương Hoàng Giang - 2A202600349
Dương Quang Đông - 2A202600445
Phạm Anh Dũng - 2A202600251
Nguyễn Lê Trung - 2A202600174

**Track:** ☐ VinFast · ☑ Vinmec · ☐ VinUni-VinSchool · ☐ XanhSM · ☐ Open
**Problem statement (1 câu):** _Mẹ bầu khó tìm và hiểu các chính sách thai sản/phí dịch vụ của Vinmec → hiện phải gọi hotline hoặc đọc tài liệu dài → AI chatbot giúp trả lời nhanh, cá nhân hoá, 24/7._

---

## 1. AI Product Canvas

|             | Value                                                                                                                                                | Trust                                                                                                      | Feasibility                                                                   |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Câu hỏi** | User nào? Pain gì? AI giải gì?                                                                                                                       | Khi AI sai thì sao? User sửa bằng cách nào?                                                                | Cost/latency bao nhiêu? Risk chính?                                           |
| **Trả lời** | Mẹ bầu & gia đình cần hiểu rõ gói thai sản, bảo hiểm, lịch khám — mất nhiều thời gian tìm info → chatbot trả lời tức thì, cá nhân hoá theo tuần thai | AI trả lời sai → user thấy vì thông tin không khớp nhu cầu → có nút "Xem nguồn / hỏi nhân viên" + feedback | ~$0.005–0.02/query, latency <3s, risk: trả lời sai chính sách / outdated info |

**Automation hay Augmentation?** ☑ Augmentation

**Justify:** User vẫn là người quyết định, chatbot chỉ tư vấn; có thể escalate sang nhân viên → giảm rủi ro sai.

**Learning signal:**

- **User correction đi vào đâu?**
  → Feedback button (👍 / 👎), câu hỏi follow-up, click "xem nhân viên" → log vào hệ thống → nhân viên Vinmec review định kỳ 2 tuần/lần → update knowledge base

- **Product thu signal gì để biết tốt lên hay tệ đi?**
  → Tỷ lệ user hỏi lại cùng 1 câu
  → Tỷ lệ escalate sang nhân viên
  → CSAT sau mỗi session
  → Tỷ lệ câu hỏi out-of-scope (theo dõi để mở rộng KB)

- **Data thuộc loại nào?**
  ☑ Domain-specific · ☑ User-specific · ☐ Real-time · ☑ Human-judgment

- **Có marginal value không?**
  → Có. Chính sách Vinmec là dữ liệu proprietary, model không biết sẵn.

- **Data flywheel — vòng khép kín:**
  User questions + feedback + escalation → nhân viên Vinmec label & validate → update KB + cải thiện retrieval prompt → tăng accuracy → giảm escalation rate → lặp lại.
  Tần suất cập nhật KB: **tối thiểu 2 tuần/lần** hoặc ngay khi có thay đổi chính sách.

---

## 2. User Stories — 4 paths

Mỗi feature chính = 1 bảng. AI trả lời xong → chuyện gì xảy ra?

### Feature 1: Tư vấn chính sách thai sản

**Trigger:** User hỏi về gói thai sản/quyền lợi/các chính sách cho mẹ bầu/người thân -> AI truy xuất chính sách và trả lời

| Path                               | Câu hỏi thiết kế                                           | Mô tả                                                                                                                                                                                         |
| ---------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Happy** — AI đúng, tự tin        | User thấy gì? Flow kết thúc ra sao?                        | AI trả lời đúng, rõ giá, quyền lợi, các chính sách → user hiểu được rõ ràng về các quyền lời và chính sách được hưởng                                                                         |
| **Low-confidence** — AI không chắc | System báo "không chắc" bằng cách nào? User quyết thế nào? | Khi hệ thống chưa có đủ dữ liệu về các thông tin. AI sẽ không trả lời ngay mà hỏi lại những thông tin cần thiết. Nếu người dùng hỏi những thông tin ngoài lề, AI sẽ từ chối một cách lịch sự. |
| **Failure** — AI sai               | User biết AI sai bằng cách nào? Recover ra sao?            | AI trả về thông tin của nhầm gói thai sản. User phát hiện khi đọc lại trên website chính thức hoặc brochure. Recover là cho phép user chọn "Thông tin này không đúng"                         |
| **Correction** — user sửa          | User sửa bằng cách nào? Data đó đi vào đâu?                | User chọn "Câu trả lời không đúng" → log → đưa vào queue review của nhân viên Vinmec                                                                                                          |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** [x] Precision · [ ] Recall

**Tại sao?** Trong dịch vụ cao cấp như Vinmec, thông tin về chi phí gói thai sản và quyền lợi bảo hiểm yêu cầu độ chính xác tuyệt đối. Một sai sót nhỏ (ví dụ: báo nhầm gói sinh mổ 40 triệu thành 30 triệu) sẽ gây ra khiếu nại gay gắt, làm tổn hại uy tín thương hiệu và ảnh hưởng đến trải nghiệm của mẹ bầu. Do đó, hệ thống ưu tiên việc thà từ chối trả lời (chuyển cho CSKH thật) còn hơn cung cấp thông tin sai lệch.

**Nếu sai ngược lại thì chuyện gì xảy ra?** \* **Nếu tối ưu Recall (Low Precision):** Chatbot sẽ cố gắng trả lời mọi câu hỏi bằng mọi giá, dẫn đến hiện tượng "ảo giác" (hallucinate). Bot có thể tự bịa ra chính sách bảo hiểm hoặc báo sai giá gói khám → Mẹ bầu chuẩn bị sai tài chính, gây rủi ro khủng hoảng truyền thông cực lớn.

- **Nếu Low Recall (Precision quá cực đoan):** Bot liên tục từ chối trả lời các câu hỏi hơi chệch từ khóa và đẩy sang người thật → Trải nghiệm chat bị đứt gãy, hệ thống AI trở nên vô dụng vì không giúp giảm tải cho tổng đài.

### Bảng Chỉ số Đo lường Quan trọng

| Metric                                                                                                     | Threshold (Mục tiêu) | Red flag (Dừng/Cảnh báo khi)                                                                      |
| :--------------------------------------------------------------------------------------------------------- | :------------------- | :------------------------------------------------------------------------------------------------ |
| **RAG Faithfulness**<br>_(Độ trung thực: Câu trả lời phải bám sát 100% tài liệu gốc của Vinmec)_           | **≥ 95%**            | **< 85%**<br>_(Cảnh báo: Bot bắt đầu tự bịa thông tin ngoài luồng)_                               |
| **Intent Classification Accuracy**<br>_(Tỷ lệ phân loại đúng ý định hỏi: Giá cả, Bảo hiểm, Lịch khám)_     | **≥ 90%**            | **< 75%** trong 3 ngày liên tiếp<br>_(Cảnh báo: Luồng Prompt hoặc Dữ liệu phân loại đang bị lỗi)_ |
| **Human Handoff Rate**<br>_(Tỷ lệ phiên chat phải chuyển giao cho nhân viên CSKH thật)_                    | **≤ 15%**            | **> 30%**<br>_(Cảnh báo: Chatbot không giải quyết được vấn đề của khách hàng)_                    |
| **Hallucination Rate (Dữ liệu Số)**<br>_(Tỷ lệ ảo giác/sai lệch về giá tiền, tuần thai, tỷ lệ % bảo hiểm)_ | **0%**               | **> 2%**<br>_(Dừng khẩn cấp: Rủi ro pháp lý cao, cần review lại luồng Tool-calling)_              |

---

## 4. Top 3 failure modes

| #   | Trigger                                                  | Hậu quả                                        | Mitigation                                                                                     |
| --- | -------------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | Chính sách thay đổi nhưng data chưa update               | AI trả lời sai nhưng tự tin cao                | Versioning KB + hiển thị _"Cập nhật lần cuối: [ngày]"_ trên mỗi câu trả lời                    |
| 2   | Câu hỏi mơ hồ (VD: _"gói nào tốt?"_)                     | Trả lời generic, không hữu ích                 | Hỏi lại bằng clarifying question trước khi trả lời                                             |
| 3   | Hallucination (bịa thông tin không có trong KB)          | User tin sai info quan trọng về phí/chính sách | Chỉ trả lời từ knowledge base (RAG) + bắt buộc show source; nếu không có nguồn → không trả lời |
| 4   | Câu hỏi y tế thuần tuý bị trả lời như câu hỏi chính sách | User nhận lời khuyên y tế sai từ bot           | Classifier phân loại intent trước khi generate → nếu thuộc y tế → từ chối + redirect bác sĩ    |

> 👉 **Nguy hiểm nhất:** Hallucination mà user không biết → hạn chế bằng RAG strict (chỉ trả lời khi có document support) + hiển thị nguồn bắt buộc.

---

## 5. ROI 3 kịch bản (Return on Investment)

| Khía cạnh      | Conservative (Thận trọng)                                                          | Realistic (Thực tế)                                                | Optimistic (Lạc quan)                                             |
| -------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------- |
| **Assumption** | _200 phiên chat/ngày, tỷ lệ tự xử lý (containment rate) 50%_                       | _1.000 phiên chat/ngày, tỷ lệ tự xử lý 75%_                        | _3.000 phiên chat/ngày (Tích hợp đa kênh App/Zalo), tự xử lý 90%_ |
| **Cost**       | _$10/ngày (Chi phí API LLM + Vector DB)_                                           | _$50/ngày_                                                         | _$150/ngày_                                                       |
| **Benefit**    | _Tiết kiệm 8h CSKH/ngày. Xin được thông tin 5 leads chất lượng (có nhu cầu thực)._ | _Tiết kiệm 60h CSKH/ngày. Lọc được 30 leads hẹn lịch khám/tu vấn._ | _Giảm tải 200h CSKH/ngày. Tăng 5% tỷ lệ chốt gói thai sản._       |
| **Net**        | _+ $20/ngày (chưa tính giá trị quy đổi từ Leads)_                                  | _+ $190/ngày (chưa tính giá trị quy đổi từ Leads)_                 | _+ $650/ngày (ROI cực lớn từ doanh thu gói sinh mới)_             |

**Kill criteria (Khi nào nên dừng hoặc đập đi làm lại?):** 1. Tỷ lệ _Human Handoff_ (khách hàng yêu cầu gặp tư vấn viên thật) **> 40%** trong 4 tuần liên tục (Chứng tỏ Bot vô dụng, hỏi gì cũng không biết). 2. Phát sinh **≥ 2 ca khiếu nại gay gắt/tháng** do khách hàng vin vào bằng chứng Chatbot báo sai giá/quyền lợi so với thực tế (Vi phạm Red flag về Hallucination). 3. Chi phí API > Benefit (số giờ CSKH tiết kiệm + Leads) trong 2 tháng liên tục.

---

## 6. Mini AI spec (1 trang)

## 1. Bài toán & Đối tượng người dùng

Tại Vinmec, các gói thai sản và chính sách bảo hiểm rất đa dạng và phức tạp.

- **User (Mẹ bầu):** Thường mang tâm lý lo âu, cẩn thận, có nhu cầu được giải đáp chi tiết, cá nhân hóa và thấu cảm mọi lúc mọi nơi.
- **User (Đội ngũ CSKH):** Đang bị quá tải bởi hàng trăm câu hỏi lặp đi lặp lại về báo giá, quyền lợi bảo hiểm, dẫn đến thiếu thời gian xử lý các ca tư vấn chuyên sâu.
- **Giải pháp AI:** Trợ lý ảo AI đứng ở giữa, giải quyết nút thắt thông tin, cung cấp trải nghiệm tư vấn 24/7 mượt mà và chính xác.

## 2. Vai trò của AI (Automation & Augmentation)

Sản phẩm áp dụng kiến trúc **Hybrid (Lai)**:

- **Automation (Tự động hóa):** Đối với các luồng hỏi đáp về giá gói sinh, danh mục khám, hay thủ tục nhập viện, AI hoạt động tự động 100% dựa trên tài liệu chính thống.
- **Augmentation (Hỗ trợ/Chuyển giao):** Khi mẹ bầu có biểu hiện bức xúc, hỏi chệch sang triệu chứng y tế khẩn cấp (rỉ ối, đau bụng), hoặc hỏi câu AI không có dữ liệu, hệ thống ngay lập tức tóm tắt lịch sử chat và chuyển giao (Human handoff) cho nhân viên CSKH/Bác sĩ tiếp quản.

## 3. Tiêu chuẩn Chất lượng (Tối ưu Precision)

Trong y tế, "sai một ly đi một dặm". Hệ thống được thiết kế để **tối ưu hóa Precision (Độ chính xác) ở mức cực đoan**, chấp nhận hy sinh Recall.

- AI thà dũng cảm thừa nhận: _"Dạ phần này em chưa có thông tin chính thức, xin phép chuyển máy cho chuyên viên hỗ trợ mẹ"_ còn hơn là đoán bừa.
- Ngưỡng chịu đựng Hallucination (ảo giác thông tin) về giá tiền và chính sách y tế là **0%**.

## 4. Rủi ro cốt lõi (Key Risks) & Cách giảm thiểu

- **Rủi ro nguy hiểm nhất:** Bot trả lời sai nhưng với giọng điệu tự tin, khiến khách hàng tin đó là thật (ví dụ: báo giá gói đẻ rẻ hơn 10 triệu, tư vấn sai luồng cấp cứu).
- **Cách giảm thiểu (Mitigation):** Hệ thống cấm LLM tự do sáng tạo nội dung số. Bắt buộc sử dụng **Strict RAG** (chỉ trích xuất từ Knowledge Base được duyệt của Vinmec) và **Tool-calling** (gọi API lấy giá từ Database). Mọi câu trả lời liên quan đến chính sách/giá cả đều phải hiển thị **Nguồn trích dẫn (Citation)**.

## 5. Cỗ máy học tập (Data Flywheel)

Sản phẩm liên tục thông minh hơn thông qua vòng lặp dữ liệu khép kín:

1. **Thu thập tín hiệu (Signals):** Ghi nhận các ca _Human handoff_ (chuyển người thật) hoặc khi người dùng bấm Dislike (👎) câu trả lời của AI.
2. **Phân tích & Cập nhật:** Đội ngũ vận hành phân tích các ca "thất bại" này để xem AI đang thiếu ngữ cảnh, hay Knowledge Base đang thiếu bài viết. Sau đó, tiến hành tinh chỉnh (Fine-tune) Prompt hoặc bổ sung tài liệu.
3. **Mở rộng giá trị:** AI trả lời trơn tru hơn vào ngày hôm sau ➔ Khách hàng hài lòng, nhắn tin nhiều hơn ➔ Thu thập được nhiều câu hỏi ngách (Long-tail intents) ➔ Kho tàng tri thức (Knowledge Base) của Vinmec ngày càng đồ sộ và hoàn thiện.

## Phân công

- Đông: Canvas + failure modes
- Dũng: User stories 4 paths
- Giang: Eval metrics + ROI
- Trung: Prototype research + prompt test
