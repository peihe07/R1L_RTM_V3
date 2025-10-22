# R1L Requirement & Test Management System

現代化的需求與測試案例管理系統，支援 CFTS、SYS.2 需求和 TestCase 的整合查詢。

---

## 🚀 快速開始

### 使用 Docker（推薦）

```bash
./start-docker.sh
```

訪問：http://localhost:55688

### 檢查系統狀態

```bash
# 檢查服務健康狀態
./health_check.sh

# 檢查資料完整性
./data_health_check.sh
```

---

## 📚 完整文檔

### 🎓 新手指南

| 文檔 | 說明 | 適合對象 |
|------|------|---------|
| [README.md](README.md) | 本文檔 - 快速開始 | 所有人 |
| [PROJECT_REBUILD_GUIDE.md](PROJECT_REBUILD_GUIDE.md) | 從零重建完整教學 | 想要複製專案的人 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 常用指令速查 | 日常使用者 |

### 🔧 技術文檔

| 文檔 | 說明 | 適合對象 |
|------|------|---------|
| [DATA_MANAGEMENT_GUIDE.md](DATA_MANAGEMENT_GUIDE.md) | 資料管理詳細指南 | 管理員 |
| [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md) | 資料架構說明 | 開發者 |
| [DATABASE_SETUP_GUIDE.md](DATABASE_SETUP_GUIDE.md) | 資料庫設置指南 | 管理員 |
| [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) | 腳本完整參考 | 所有人 |

### 💾 備份相關

| 文檔 | 說明 | 適合對象 |
|------|------|---------|
| [BACKUP_README.md](BACKUP_README.md) | 備份快速參考 | 管理員 |

---

## 🔧 可用腳本

### 啟動與管理

```bash
./start-docker.sh         # 啟動所有服務
./health_check.sh         # 檢查服務健康狀態
./data_health_check.sh    # 檢查資料完整性
```

### 備份與還原

```bash
./full_backup.sh                              # 完整備份
./backup_database.sh                          # 備份資料庫
./backup_data.sh                              # 備份 Excel 資料
./restore_database.sh <backup_file>          # 還原資料庫
```

**詳細說明請參考:** [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md)

---

## 📊 資料導入

### 完整導入流程

```bash
# 1. 啟動服務
./start-docker.sh

# 2. 導入所有資料
docker-compose exec backend bash -c "
  python batch_import_cfts_new.py /data/CFTS && \
  python batch_import_sys2.py /data/R1L_SYS.2.xlsx && \
  python batch_import_testcase.py /data/R1L_TestCase.xlsx
"

# 3. 驗證資料
./data_health_check.sh
```

### 個別導入

```bash
# CFTS 資料
docker-compose exec backend python batch_import_cfts_new.py /data/CFTS

# SYS.2 資料
docker-compose exec backend python batch_import_sys2.py /data/R1L_SYS.2.xlsx

# TestCase 資料
docker-compose exec backend python batch_import_testcase.py /data/R1L_TestCase.xlsx
```

---

## 🎯 功能特色

- ✅ CFTS 搜尋與查看（5,452 筆）
- ✅ 需求 ID 搜尋
- ✅ Melco ID 點擊查看詳細資訊
- ✅ SYS.2 需求資料顯示（14,683 筆）
- ✅ 相關 TestCase 自動關聯（34,457 筆）
- ✅ 現代化響應式 UI 設計
- ✅ RESTful API 接口
- ✅ 完整的備份還原機制

---

## 🛠️ 技術棧

### 後端
- **框架:** FastAPI 0.118.0
- **資料庫:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0.43
- **伺服器:** Uvicorn 0.37.0

### 前端
- **框架:** Vue.js 3.3.8
- **建置工具:** Vite 5.0.0
- **HTTP 客戶端:** Axios 1.6.2
- **字體:** Inter (Google Fonts)

### 基礎設施
- **容器化:** Docker + Docker Compose
- **反向代理:** Nginx (Alpine)
- **網路:** 自訂 Docker bridge network
- **健康檢查:** 所有服務內建檢查

---

## 📁 資料結構

```
R1L_RTM_V2/
├── data/                          # Excel 原始資料（容器外）
│   ├── CFTS/                      # 31 個 CFTS Excel 檔案
│   ├── R1L_SYS.2.xlsx            # SYS.2 需求資料
│   └── R1L_TestCase.xlsx         # TestCase 資料
│
├── backups/                       # 備份目錄（容器外）
│   ├── full_backup_*.tar.gz      # 完整備份
│   ├── db_backup_*.sql.gz        # 資料庫備份
│   └── data_*/                    # Excel 資料備份
│
├── backend/                       # FastAPI 後端
├── frontend/                      # Vue.js 前端
├── reverse-proxy/                 # Nginx 配置
└── docker/                        # Docker 配置
```

**資料存放策略:**
- ✅ Excel 原始資料 → 容器外 (方便編輯)
- ✅ PostgreSQL 資料 → Docker Volume (最佳效能)
- ✅ 備份檔案 → 容器外 (易於管理)

**詳細說明請參考:** [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md)

---

## 🐳 Docker 指令

### 基本操作

```bash
# 啟動所有服務
./start-docker.sh
# 或
docker-compose up -d

# 停止服務（保留資料）
docker-compose down

# 停止並刪除資料（危險！）
docker-compose down -v

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f

# 重建服務
docker-compose up --build -d
```

### 進入容器

```bash
# 進入後端容器
docker-compose exec backend bash

# 進入資料庫容器
docker-compose exec db psql -U postgres requirement_db

# 進入前端容器
docker-compose exec frontend sh
```

---

## 🌐 訪問位址

| 服務 | 位址 | 說明 |
|------|------|------|
| 前端介面 | http://localhost:55688 | 主要使用介面 |
| 後端 API | http://localhost:55688/api | API 端點 |
| API 文檔 | http://localhost:55688/api/docs | Swagger UI |
| 健康檢查 | http://localhost:55688/api/health | 健康狀態 |

---

## 📝 API 端點

### CFTS 需求

- `GET /cfts/search?cfts_id={id}` - 搜尋 CFTS ID
- `GET /req/search?req_id={id}` - 搜尋需求 ID

### SYS.2 需求

- `GET /sys2/requirement/{melco_id}` - 獲取 SYS.2 詳細資料

### TestCase

- `GET /testcases/by-feature-id/{feature_id}` - 獲取相關 TestCase

### 系統

- `GET /health` - API 健康檢查
- `GET /readiness` - 服務準備狀態

**完整 API 文檔:** http://localhost:55688/api/docs

---

## 💾 備份策略

### 自動備份（推薦）

設定 Cron 自動備份：

```bash
# 編輯 crontab
crontab -e

# 加入以下內容
0 2 * * * cd /path/to/R1L_RTM_V2 && ./full_backup.sh >> backups/backup.log 2>&1
0 */6 * * * cd /path/to/R1L_RTM_V2 && ./backup_database.sh >> backups/backup.log 2>&1
```

### 手動備份

```bash
# 完整備份（推薦）
./full_backup.sh

# 僅備份資料庫
./backup_database.sh

# 僅備份 Excel 資料
./backup_data.sh
```

### 還原資料

```bash
# 還原資料庫
./restore_database.sh backups/db_backup_YYYYMMDD_HHMMSS.sql.gz

# 還原完整備份（參考 BACKUP_README.md）
```

**詳細說明請參考:** [BACKUP_README.md](BACKUP_README.md)

---

## 💡 開發

### 開發環境特性

- ✅ **前端熱重載** - 程式碼變更自動更新
- ✅ **後端自動重啟** - 偵測變更自動重載
- ✅ **資料持久化** - Docker Volume 保存資料
- ✅ **程式碼掛載** - 直接編輯主機檔案
- ✅ **健康檢查** - 自動監控服務狀態

### 本地開發（不使用 Docker）

**後端:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🎨 UI 設計

採用現代化、簡潔的設計風格：

- 🎨 **漸層背景** - 紫藍漸層視覺效果
- 🔲 **圓角卡片** - 柔和的卡片設計
- 🎯 **響應式佈局** - 支援各種螢幕尺寸
- ⚡ **流暢動畫** - 過渡效果和互動回饋
- 📱 **移動優先** - 優秀的行動裝置體驗
- 🔤 **Inter 字體** - 現代化的無襯線字體

---

## 🔍 故障排除

### 服務無法啟動

```bash
# 檢查容器狀態
docker-compose ps

# 查看錯誤日誌
docker-compose logs backend
docker-compose logs db
docker-compose logs frontend

# 重啟服務
docker-compose restart
```

### 資料庫連線失敗

```bash
# 檢查資料庫狀態
docker-compose exec db pg_isready -U postgres

# 重啟資料庫
docker-compose restart db

# 查看資料庫日誌
docker-compose logs db
```

### 前端無法連接後端

```bash
# 檢查網路連接
docker-compose exec frontend ping backend

# 檢查 Nginx 配置
docker-compose exec reverse-proxy nginx -t

# 重啟反向代理
docker-compose restart reverse-proxy
```

**更多故障排除請參考:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 📊 資料統計

| 資料類型 | 記錄數 | 說明 |
|---------|--------|------|
| CFTS 需求 | 5,452 筆 | 從 31 個 Excel 檔案導入 |
| SYS.2 需求 | 14,683 筆 | 單一 Excel 檔案 |
| TestCase | 34,457 筆 | 單一 Excel 檔案 |
| **總計** | **54,592 筆** | 完整需求追溯 |

---

## 🤝 如何複製此專案

如果你想要複製這個專案到自己的環境：

1. **閱讀重建指南** - [PROJECT_REBUILD_GUIDE.md](PROJECT_REBUILD_GUIDE.md)
2. **了解資料架構** - [DATA_ARCHITECTURE.md](DATA_ARCHITECTURE.md)
3. **設定資料管理** - [DATA_MANAGEMENT_GUIDE.md](DATA_MANAGEMENT_GUIDE.md)
4. **開始實作** - 跟著文檔一步步操作

---

## 📞 聯絡資訊

**專案狀態:** 生產環境就緒

**最後更新:** 2025-01-22

---

## 📄 授權

本專案為內部使用，請勿外傳。

---

**💡 提示:** 如果你是第一次使用，建議從 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) 開始！
