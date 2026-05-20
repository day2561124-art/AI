# React 前端

此資料夾是第六階段建立的 React/Vite 前端，保留原本 FastAPI 後端 API。

## 執行方式

需先安裝 Node.js。

```bash
cd frontend-react
npm install
npm run dev
```

預設 API：

```text
http://127.0.0.1:8000
```

如需調整 API 位址，建立 `.env`：

```text
VITE_API_BASE=http://127.0.0.1:8000
```

管理後台預設開發 token：

```text
dev-admin-token
```

正式部署時請同步調整後端 `ADMIN_TOKEN`。

## 頁面

- `#/chat`：AI 問答
- `#/courses`：課程資訊
- `#/faq`：FAQ
- `#/process`：報名流程
- `#/contact`：聯絡資訊
- `#/admin`：管理後台

## 程式結構

- `src/main.jsx`：React 入口與 hash route 對應
- `src/components/`：共用版面元件
- `src/pages/`：各頁面元件
- `src/services/api.js`：FastAPI 串接
- `src/data/content.js`：前端靜態展示資料
- `src/hooks/useHashRoute.js`：hash route 狀態管理
- `src/styles.css`：全站樣式

## 後台知識庫管理

登入 `#/admin` 後可：

- 查看問答紀錄
- 查看使用者回饋
- 查看無法回答問題
- 上傳新的 `.txt` 知識庫
- 重新載入目前知識庫

上傳知識庫需要後端管理 API token。
