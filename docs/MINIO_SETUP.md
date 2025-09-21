# MinIO 檔案儲存整合說明

本專案已整合 MinIO 作為檔案儲存解決方案，支援 ticket 系統的附件上傳和富文本編輯器的圖片上傳功能。

## 🚀 功能特色

- ✅ 支援一般檔案附件上傳
- ✅ 支援富文本編輯器內嵌圖片上傳
- ✅ 檔案類型和大小驗證
- ✅ 圖片自動尺寸檢測
- ✅ 預簽名 URL 安全存取
- ✅ CDN 支援 (production 環境)
- ✅ 檔案軟刪除和硬刪除
- ✅ 孤立檔案自動清理
- ✅ Production 環境最佳實踐

## 📋 環境需求

1. **MinIO 伺服器** (或 S3 相容服務)
2. **Python 套件依賴**:
   - `minio>=7.2.0`
   - `python-magic>=0.4.27`
   - `pillow>=10.0.0`

## 🔧 環境設定

### 1. 複製環境變數範例

```bash
cp .env.example .env
```

### 2. 設定 MinIO 相關環境變數

編輯 `.env` 檔案：

```bash
# MinIO 基本設定
MINIO_ENDPOINT="localhost:9000"
MINIO_ACCESS_KEY="minioadmin"
MINIO_SECRET_KEY="minioadmin"
MINIO_SECURE=true
MINIO_REGION="us-east-1"

# 儲存桶名稱
MINIO_BUCKET_ATTACHMENTS="ticket-attachments"
MINIO_BUCKET_IMAGES="ticket-images"

# 檔案大小限制
MAX_FILE_SIZE=52428800  # 50MB
MAX_IMAGE_SIZE=10485760  # 10MB

# 檔案 URL 有效期限
FILE_URL_EXPIRY=3600  # 1 小時

# CDN 設定 (Production 環境)
# CDN_DOMAIN="https://cdn.yourdomain.com"
```

### 3. Production 環境設定範例

```bash
# AWS S3
MINIO_ENDPOINT="s3.amazonaws.com"
MINIO_ACCESS_KEY="your-aws-access-key"
MINIO_SECRET_KEY="your-aws-secret-key"
MINIO_SECURE=true
MINIO_REGION="ap-northeast-1"

# 其他 S3 相容服務
MINIO_ENDPOINT="your-s3-service.com"
MINIO_ACCESS_KEY="your-access-key"
MINIO_SECRET_KEY="your-secret-key"
```

## 🛠️ 安裝和部署

### 1. 安裝依賴

```bash
uv sync
```

### 2. 執行資料庫遷移

```bash
uv run alembic upgrade head
```

### 3. 啟動 MinIO (本地開發)

```bash
# 使用 Docker
docker run -p 9000:9000 -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  -v /mnt/data:/data \
  minio/minio server /data --console-address ":9001"
```

### 4. 啟動應用程式

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API 使用說明

### 上傳檔案附件

```bash
curl -X POST "http://localhost:8000/api/v1/attachments/upload" \
  -H "Authorization: Bearer your-jwt-token" \
  -F "file=@document.pdf" \
  -F "ticket_id=1" \
  -F "usage_type=attachment" \
  -F "description=重要文件"
```

### 上傳圖片 (富文本編輯器)

```bash
curl -X POST "http://localhost:8000/api/v1/attachments/upload/image" \
  -H "Authorization: Bearer your-jwt-token" \
  -F "file=@image.jpg" \
  -F "ticket_id=1" \
  -F "description=內嵌圖片"
```

### 獲取附件資訊

```bash
curl -X GET "http://localhost:8000/api/v1/attachments/1" \
  -H "Authorization: Bearer your-jwt-token"
```

### 下載檔案

```bash
curl -X GET "http://localhost:8000/api/v1/attachments/1/download" \
  -H "Authorization: Bearer your-jwt-token" \
  -o downloaded_file.pdf
```

### 獲取 Ticket 附件列表

```bash
# 所有附件
curl -X GET "http://localhost:8000/api/v1/attachments/ticket/1/attachments" \
  -H "Authorization: Bearer your-jwt-token"

# 只獲取一般附件
curl -X GET "http://localhost:8000/api/v1/attachments/ticket/1/attachments?usage_type=attachment" \
  -H "Authorization: Bearer your-jwt-token"

# 只獲取圖片
curl -X GET "http://localhost:8000/api/v1/attachments/ticket/1/images" \
  -H "Authorization: Bearer your-jwt-token"
```

## 🎯 前端整合範例

### JavaScript 檔案上傳

```javascript
// 一般檔案上傳
async function uploadFile(file, ticketId, description) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('ticket_id', ticketId);
    formData.append('usage_type', 'attachment');
    formData.append('description', description);

    const response = await fetch('/api/v1/attachments/upload', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${yourJwtToken}`
        },
        body: formData
    });

    return await response.json();
}

// 富文本編輯器圖片上傳
async function uploadImage(imageFile, ticketId) {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('ticket_id', ticketId);

    const response = await fetch('/api/v1/attachments/upload/image', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${yourJwtToken}`
        },
        body: formData
    });

    const result = await response.json();
    return result.image_url; // 返回圖片 URL 供編輯器使用
}
```

### Vue.js 整合範例

```vue
<template>
  <div>
    <!-- 檔案上傳 -->
    <input type="file" @change="handleFileUpload" />
    
    <!-- 圖片上傳 (富文本編輯器) -->
    <input type="file" accept="image/*" @change="handleImageUpload" />
    
    <!-- 附件列表 -->
    <div v-for="attachment in attachments" :key="attachment.id">
      <a :href="attachment.file_url" target="_blank">
        {{ attachment.file_name }}
      </a>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      attachments: []
    }
  },
  methods: {
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const result = await this.uploadFile(file);
        if (result.success) {
          this.attachments.push(result.attachment);
        }
      }
    },
    
    async handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const result = await this.uploadImage(file);
        if (result.success) {
          // 插入圖片到富文本編輯器
          this.insertImageToEditor(result.image_url);
        }
      }
    },
    
    async uploadFile(file) {
      // 實作上傳邏輯
    },
    
    async uploadImage(file) {
      // 實作圖片上傳邏輯
    }
  }
}
</script>
```

## 🔒 安全設定

### 1. 檔案類型限制

支援的檔案類型在 `app/config.py` 中設定：

```python
allowed_file_types = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    # ... 更多類型
]

allowed_image_types = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    # ... 更多類型
]
```

### 2. 檔案大小限制

```python
max_file_size = 50 * 1024 * 1024  # 50MB
max_image_size = 10 * 1024 * 1024  # 10MB
```

### 3. URL 安全性

- 使用預簽名 URL，有時效性限制
- 支援 CDN 整合，提升存取速度
- 檔案存取需要適當的身份驗證

## 🔧 維護和監控

### 清理孤立檔案

```python
# 在背景任務中執行
from app.services.attachment_service import AttachmentService

async def cleanup_orphaned_files():
    service = AttachmentService(attachment_repository)
    deleted_count = await service.cleanup_orphaned_attachments(hours=24)
    print(f"清理了 {deleted_count} 個孤立檔案")
```

### 更新過期 URL

系統會自動檢查和更新過期的檔案 URL，確保檔案始終可存取。

## 📊 監控指標

建議監控以下指標：

1. **檔案上傳成功率**
2. **檔案存取延遲**
3. **儲存空間使用量**
4. **CDN 命中率** (如果使用)
5. **錯誤率和類型**

## 🐛 常見問題排解

### Q: 檔案上傳失敗，提示連接錯誤

A: 檢查 MinIO 伺服器是否正常運行，確認 `MINIO_ENDPOINT` 設定正確。

### Q: 圖片上傳成功但無法顯示

A: 檢查 `MINIO_SECURE` 設定是否與 MinIO 伺服器的 HTTPS 設定一致。

### Q: 檔案 URL 經常過期

A: 調整 `FILE_URL_EXPIRY` 設定，或實作自動更新 URL 的機制。

### Q: Production 環境效能問題

A: 考慮啟用 CDN，並設定適當的快取策略。

## 📞 技術支援

如需技術支援，請查閱：

1. [MinIO 官方文檔](https://docs.min.io/)
2. [FastAPI 文檔](https://fastapi.tiangolo.com/)
3. 專案 `example_minio_usage.py` 檔案中的範例程式碼

---

**注意事項**: 在 Production 環境中，請確保：
- 使用 HTTPS 連線
- 設定適當的防火牆規則
- 定期備份重要檔案
- 監控系統效能和安全性