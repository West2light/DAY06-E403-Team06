# DAY06-E403-Team06

Repo này hiện có nhiều nhánh làm việc, trong đó app chạy được hoàn chỉnh nhất là `vinmec-chatbot/`.

## Cấu trúc thư mục

```text
DAY06-E403-Team06/
├─ vinmec-chatbot/           # App chatbot chính đang chạy với FastAPI + frontend tĩnh
│  ├─ backend/
│  │  ├─ main.py             # FastAPI app, serve frontend + API routes
│  │  ├─ agent.py            # Agent loop gọi OpenAI function calling
│  │  ├─ tools.py            # Tool definitions + feedback logging
│  │  ├─ knowledge_base.py   # Load/search policies và FAQs
│  │  ├─ data/
│  │  │  ├─ policies.jsonl
│  │  │  └─ faq_demo.jsonl
│  │  ├─ prompts/
│  │  │  └─ system_prompt.txt
│  │  ├─ requirements.txt
│  │  ├─ bookings.json       # Dữ liệu booking sinh ra khi chạy
│  │  └─ feedback_log.jsonl  # Log feedback sinh ra khi chạy
│  ├─ frontend/
│  │  ├─ index.html
│  │  └─ styles.css
│  ├─ .env
│  ├─ .env.example
│  ├─ run.bat
│  └─ run.sh
├─ demo_chatbot/             # Bản demo/tooling cũ để tham chiếu
├─ docs/                     # Tài liệu flow/spec
├─ Data_demo/                # Dữ liệu demo khác
└─ AI Product Canvas/        # Tài liệu sản phẩm
```

## Workflow của `vinmec-chatbot`

### 1. Luồng chạy tổng thể

1. User mở `http://localhost:8000`.
2. FastAPI trong `vinmec-chatbot/backend/main.py` trả về `frontend/index.html`.
3. Frontend gọi các API:
   - `POST /api/welcome`
   - `POST /api/chat`
   - `POST /api/reset`
   - `POST /api/booking`
   - `POST /api/feedback`
4. Backend tạo hoặc lấy `VinmecAgent` theo `session_id`.
5. `VinmecAgent` gửi hội thoại + `TOOL_DEFINITIONS` cho OpenAI.
6. Model có thể gọi các tool trong `backend/tools.py` để:
   - tìm KB
   - phân loại scope
   - lấy chi tiết policy
   - ghi feedback khi user báo sai/thiếu
7. Backend trả JSON response cho frontend để render bubble, CTA, feedback row, booking flow.

### 2. Luồng dữ liệu

- Knowledge base được đọc từ:
  - `vinmec-chatbot/backend/data/policies.jsonl`
  - `vinmec-chatbot/backend/data/faq_demo.jsonl`
- Booking được append vào:
  - `vinmec-chatbot/backend/bookings.json`
- Feedback được append vào:
  - `vinmec-chatbot/backend/feedback_log.jsonl`

### 3. Điểm kiến trúc cần lưu ý

- `frontend/index.html` đang gọi API cố định tới `http://localhost:8000`, nên backend phải chạy ở đúng port này nếu không sửa frontend.
- App không tách frontend dev server riêng; chỉ cần chạy FastAPI là đủ.
- `main.py` vừa serve API vừa serve asset frontend.
- `run.bat` và `run.sh` đều `cd` vào `vinmec-chatbot/backend` trước khi chạy `uvicorn`, nên import hiện tại đang phụ thuộc cách chạy này.

## Cách chạy project

### Yêu cầu

- Python 3.10+
- Có OpenAI API key

### Chuẩn bị biến môi trường

Từ thư mục `vinmec-chatbot/`, tạo file `.env`:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

Có thể copy từ `vinmec-chatbot/.env.example`.

### Cách 1: Chạy nhanh bằng script

Windows:

```powershell
cd vinmec-chatbot
.\run.bat
```

macOS / Linux:

```bash
cd vinmec-chatbot
chmod +x run.sh
./run.sh
```

Sau đó mở:

```text
http://localhost:8000
```

### Cách 2: Chạy thủ công

```powershell
cd vinmec-chatbot\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Nếu dùng macOS / Linux:

```bash
cd vinmec-chatbot/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Health check nhanh

Sau khi server chạy, có thể kiểm tra:

```text
http://localhost:8000/api/health
```

Docs FastAPI:

```text
http://localhost:8000/docs
```

## Những gì README cũ đang thiếu

- Chưa nói repo có nhiều thư mục, nhưng app chính là `vinmec-chatbot/`.
- Chưa nói cần file `.env` và `OPENAI_API_KEY`.
- Chưa nói frontend được serve từ chính FastAPI, không cần mở `index.html` trực tiếp.
- Chưa nói đúng workflow booking/feedback/KB.
- Chưa có cách chạy bằng `run.bat` / `run.sh`.
- Chưa nêu rõ file dữ liệu nào là input và file nào được sinh ra khi chạy.
