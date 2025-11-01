
# syntax=docker/dockerfile:1


FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# 只複製依賴檔案以加速快取
COPY pyproject.toml uv.lock ./

# 安裝依賴
RUN uv sync

# 複製專案檔案
COPY . .

# 健康檢查（可選，檢查 8000 port）
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 預設啟動指令
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
