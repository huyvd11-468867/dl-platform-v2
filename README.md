# HuyHaha Deep Learning Academy v2 🚀

**Nền tảng học Deep Learning premium** — dành cho khóa học của thầy HuyHaha.

## Tính năng

- **6 module chuyên sâu:** ML Fundamentals, NLP, CV, Applied DL, Server, MLOps
- **30+ bài tập** với starter code chi tiết và SoTA references (2024-2025)
- **Chấm điểm AI** với phân tích 3 chiều: Hiểu khái niệm · Kỹ thuật · Đầy đủ
- **Chatbot AI** context-aware (biết đang học chủ đề nào)
- **UI dark premium** — editorial design, animations mượt
- **Layout split-panel** — lý thuyết bên trái, bài tập bên phải
- **Docker ready** — 1 lệnh là chạy

## Chạy với Docker (1 lệnh)

```bash
# Clone
git clone <repo-url>
cd dl-platform-v2

# Chạy (không cần API key vẫn xem được nội dung)
docker compose up -d

# Frontend: http://localhost:3000
# Backend API docs: http://localhost:8000/docs
```

## Cài API Key (để dùng chấm điểm + chatbot)

**Cách 1:** Qua UI (khuyến nghị)
- Mở http://localhost:3000 → Cài đặt → Nhập key → Lưu

**Cách 2:** Qua .env
```bash
echo "OPENROUTER_API_KEY=sk-or-v1-..." > .env
docker compose up -d
```

Lấy API key miễn phí tại [openrouter.ai](https://openrouter.ai).

## Chạy thủ công (Development)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (terminal khác)  
cd frontend
python -m http.server 3000
# → http://localhost:3000
```

## Cấu trúc

```
dl-platform-v2/
├── backend/
│   ├── main.py              # FastAPI — grading + chatbot API
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html           # Full SPA — curriculum, theory, exercises, chatbot
│   ├── nginx.conf           # Nginx với proxy to backend
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Thêm bài tập / chỉnh nội dung

Tất cả nội dung nằm trong `frontend/index.html` — biến `CURRICULUM` trong `<script>`.
Format mỗi exercise:
```javascript
{
  id: 'unique-id',
  title: 'Tên bài tập',
  difficulty: 'Cơ bản' | 'Trung bình' | 'Khó',
  desc: 'Mô tả yêu cầu...',
  concepts: ['khái niệm 1', 'khái niệm 2'],
  starter: `// Code khởi đầu...`,
  max_score: 10
}
```

## API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | /health | Health check |
| GET | /api/config-status | Kiểm tra API key |
| POST | /api/set-api-key | Cập nhật API key |
| POST | /api/grade | Chấm điểm bài làm |
| POST | /api/chat | Chat với AI assistant |


## Deploying the frontend to Vercel (via GitHub)

This project includes a minimal `frontend/vercel.json` so the static site can be deployed to Vercel as a static project.

Two quick ways to deploy the frontend:

1) Push to GitHub and connect the repo in Vercel (recommended)

  - Create a new GitHub repo and push the current code:

  ```bash
  # from project root
  git init
  git add .
  git commit -m "Initial commit"
  git branch -M main
  git remote add origin git@github.com:<your-username>/<repo-name>.git
  git push -u origin main
  ```

  - Go to https://vercel.com, sign in, choose "Import Project", pick the GitHub repo and follow the prompts. Vercel will detect the static site and deploy it.

2) Deploy directly from your machine with the Vercel CLI

  ```bash
  # install (if needed)
  npm i -g vercel

  # from the frontend directory
  cd frontend
  vercel login     # follow web auth
  vercel --prod    # deploy to production
  ```

Notes
- The `vercel.json` included uses the static builder and rewrites all routes to `index.html` so SPA routing works.
- If your frontend needs to call the backend, host the backend somewhere reachable (Render/Railway/Fly) and set the backend URL as an environment variable in the Vercel project settings.
- Sensitive values (like `OPENROUTER_API_KEY`) should be set in the backend host or in Vercel's Environment Variables only when required by serverless functions. Do NOT commit secrets to the repo.

If you'd like, I can also add a small GitHub Actions workflow that automatically deploys the frontend on push to `main`.

## Automating deploys from GitHub → Vercel

I've included a GitHub Actions workflow (`.github/workflows/deploy-vercel.yml`) that will deploy the `frontend` folder to Vercel whenever you push to the `main` branch.

Quick steps to create the GitHub repo and enable automated deploys:

1. Ensure you have the GitHub CLI (`gh`) installed and you're authenticated: https://cli.github.com/
2. (Optional) Edit `.gitignore` if you need to exclude additional files.
3. Run the helper script to create the remote and push:

```bash
# from project root
chmod +x scripts/create_remote_repo.sh
./scripts/create_remote_repo.sh <your-username-or-org>/<repo-name>
```

4. In your new GitHub repo go to Settings → Secrets → Actions and add a secret named `VERCEL_TOKEN` with a Vercel personal token. Create a token at https://vercel.com/account/tokens.
5. Push to `main` (script will push automatically). The workflow will run and deploy the `frontend` to Vercel.

If you prefer I can walk you through creating the GitHub repo and setting secrets interactively.

