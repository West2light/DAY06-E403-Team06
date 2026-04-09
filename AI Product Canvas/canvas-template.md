# AI Product Canvas — template

Điền Canvas cho product AI của nhóm. Mỗi ô có câu hỏi guide — trả lời trực tiếp, xóa phần in nghiêng khi điền.

---

## Canvas

|                   | Value                                                                                   | Trust                                                                                             | Feasibility                                                                            |
| ----------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được?                   | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì?                             |
| **Trả lời**       | _Nhân viên văn phòng mất 30 phút/ngày phân loại email — AI gợi ý nhãn, giảm còn 5 phút_ | _AI gắn sai nhãn → user thấy ngay khi đọc email, sửa 1 click, hệ thống học từ correction_         | _~$0.01/email, latency <2s, risk: hallucinate nội dung nhạy cảm nếu dùng external API_ |

---

## Automation hay augmentation?

☐ Automation — AI làm thay, user không can thiệp
☐ Augmentation — AI gợi ý, user quyết định cuối cùng

**Justify:** \_\_\_
_VD: Augmentation — user thấy gợi ý và chấp nhận/từ chối, cost of reject = 0_

Gợi ý: nếu AI sai mà user không biết → automation nguy hiểm, cân nhắc augmentation.

---

## Learning signal

| #   | Câu hỏi                                                                                                    | Trả lời                                                                           |
| --- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| 1   | User correction đi vào đâu?                                                                                | _Mỗi lần user sửa → ghi correction log → dùng để cải thiện model_                 |
| 2   | Product thu signal gì để biết tốt lên hay tệ đi?                                                           | _Implicit: acceptance rate. Explicit: thumbs down. Correction: user sửa output_   |
| 3   | Data thuộc loại nào? ☐ User-specific · ☐ Domain-specific · ☐ Real-time · ☐ Human-judgment · ☐ Khác: \_\_\_ | _User-specific + Real-time — model chung không biết pattern riêng của từng người_ |

**Có marginal value không?** (Model đã biết cái này chưa? Ai khác cũng thu được data này không?)

---

---

## Cách dùng

1. Điền Value trước — chưa rõ pain thì chưa điền Trust/Feasibility
2. Trust: trả lời 4 câu UX (đúng → sai → không chắc → user sửa)
3. Feasibility: ước lượng cost, không cần chính xác — order of magnitude đủ
4. Learning signal: nghĩ về vòng lặp dài hạn, không chỉ demo ngày mai
5. Đánh [?] cho chỗ chưa biết — Canvas là hypothesis, không phải đáp án
