# AI智慧客服問答系統

本專案是「基於 RAG 的 AI 智慧客服與課程報名輔助平台」展示版，知識庫來源為：

- `AI智慧應用產業人才培訓班_整合知識庫.txt`
- `Skill.md`

系統目標是讓使用者查詢課程資訊、報名資格、補助費用、甄試資訊、聯絡方式、職前訓練與在職訓練，並在回答中提供來源依據與注意事項。

- 建立 FastAPI 後端 API
- 建立 TXT 知識庫讀取、切割與檢索流程
- 建立前端最小問答頁
- 加入職前/在職訓練分流
- 回答格式包含簡短回答、詳細說明、來源依據與注意事項

### 第三階段：後台管理

- 問答紀錄寫入 `data/chat_logs.json`
- 使用者回饋寫入 `data/feedback.json`
- 無法回答問題追蹤
- 新增管理後台頁

### 第四階段：本機 Hybrid RAG

- 使用關鍵字檢索搭配 TF-IDF cosine similarity
- 依 114/115 期別與職前/在職分類過濾資料
- 後續可替換為 OpenAI Embedding 與 Supabase pgvector

### 第五階段：專題展示版前端

- AI 問答頁

## 測試紀錄（自動化）

- 測試時間：2026-05-20
- 後端啟動：使用 `uvicorn app.main:app --reload --port 8000`（以工作區 `.venv` 執行）
- 健康檢查：`GET /api/health` → {"status":"ok"}
- 知識庫狀態：`GET /api/knowledge/status` → `chunk_count=14`, `retriever=local-hybrid-tfidf`, `llm_enabled=false`
- 聊天測試：`POST /api/chat` 問題："在職勞工進修補助要去哪裡查？" → 回傳 `matched=false`，`llm_used=false`，並產生 conversation_id（範例：`b5007f03-bb39-47c1-8b87-704fcbd9c004`）。
- 前端啟動：在 `frontend-react` 執行 `npm run dev`（已於本機啟動開發伺服器）。

註記：部分回應包含由知識庫文字編碼造成的字元顯示問題，建議確認檔案編碼（UTF-8-sig/Big5）與前端顯示邏輯。
- 課程資訊頁
- FAQ 頁
- 報名流程導覽頁
- 聯絡資訊頁
- 管理後台頁

### 第六階段：React 前端骨架

- 新增 `frontend-react/`
- 使用 Vite + React
- 使用 hash route 建立 AI 問答、課程資訊、FAQ、流程、聯絡與後台頁面
- 保留 FastAPI API 串接
- 可部署到 Vercel 或其他前端平台

## 執行方式

後端：

```bash
cd backend
pip install -r requirements.txt
set ADMIN_TOKEN=dev-admin-token
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

前端可直接用瀏覽器開啟：

```text
frontend/index.html
```

React 前端需先安裝 Node.js：

```bash
cd frontend-react
npm install
npm run dev
```

## 頁面入口

- `frontend/index.html`：AI 問答頁
- `frontend/courses.html`：課程資訊頁
- `frontend/faq.html`：FAQ 頁
- `frontend/process.html`：報名流程導覽頁
- `frontend/contact.html`：聯絡資訊頁
- `frontend/admin.html`：管理後台頁
- `frontend-react/`：React/Vite 前端版本

## API

- `GET /api/health`
- `GET /api/knowledge/status`
- `POST /api/chat`
- `POST /api/feedback`
- `GET /api/admin/stats`
- `GET /api/admin/chat-logs`
- `GET /api/admin/feedback`
- `GET /api/admin/unanswered`
- `POST /api/admin/knowledge/reload`
- `POST /api/admin/knowledge/upload`

管理 API 需在 header 帶入：

```text
X-Admin-Token: dev-admin-token
```

正式部署時請將 `ADMIN_TOKEN` 換成更安全的值。

## 知識庫管理

管理後台可上傳新的 `.txt` 知識庫。上傳後系統會：

- 將原本知識庫備份到 `data/knowledge_versions/`
- 覆蓋目前使用中的知識庫 TXT
- 重新切割 chunk
- 重新建立本機 hybrid retriever
- 將上傳紀錄寫入 `data/knowledge_versions.json`

## 回答規則

- 必須根據知識庫回答
- 必須提供來源依據
- 不可保證補助、錄取或最新梯次資訊
- 若知識庫沒有明確資料，必須回答「目前知識庫沒有明確資料」
- 涉及最新公告、資格認定、補助核定或錄取結果時，提醒查詢官方平台或洽詢承辦單位

## 可選 LLM 回答生成

系統預設可不使用 LLM，會使用本機 RAG 模板回答。

若要啟用 OpenAI Responses API，請設定：

```text
OPENAI_API_KEY=你的金鑰
LLM_MODEL=gpt-5-mini
```

啟用後 `/api/chat` 會在 RAG 檢索後，將檢索段落交給 LLM 生成較自然的客服回答。若 API 呼叫失敗，系統會自動退回本機模板回答。

可透過 `/api/knowledge/status` 查看：

```text
llm_enabled: true / false
```
