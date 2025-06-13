# Excel → PostgreSQL Sync Utility

Automate exporting Excel sheets to CSV and upserting them into PostgreSQL, with audit timestamps and true change detection.

---

## 🔧 Features

* **Config-driven** via `.env`
* **Selective tabs**: process only the sheets you list
* **Auto-create tables** with proper schema
* **Upsert logic**: insert new rows, update changed rows only
* **Audit fields**: `created_at` & `updated_at`
* **CSV backups** in a `CSV/` folder for traceability

---

## 🚀 Quick Start

1. **Clone & enter**

   ```bash
   git clone https://github.com/youruser/your-repo.git
   cd your-repo
   ```

2. **Set up venv**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install deps**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env`** (at project root)

   ```ini
   EXCEL_FILE_PATH=C:/path/to/your/file.xlsx
   SHEET_NAMES=test_data,test_data2
   PK_COLUMN=ID
   DB_USER=postgres
   DB_PASSWORD=secret
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=my_database
   ```

5. **Run the sync**

   ```bash
   python excel_postgres_sync.py
   ```

---

## 📂 File Structure

```
.
├── excel_postgres_sync.py    # Main script
├── requirements.txt
├── .env                      # Your environment settings (git-ignored)
├── .gitignore                # Git ignore rules
├── CSV/                      # Auto-generated CSV exports
└── personal_area/            # Personal workspace (git-ignored)
```

---

## 🔒 Sample `.gitignore`

```gitignore
# Python bytecode
__pycache__/
*.pyc

# Virtual environment
.venv/

# Environment variables and secrets
.env

# Data exports (auto-generated)
CSV/

# IDE/project settings
.vscode/
.idea/

# User-specific or personal work
personal_area/

# OS-specific files
.DS_Store
Thumbs.db
```

---

## 📝 Notes

* **Keep `.env` secret**: it contains your DB creds.
* **CSV folder**: acts as a checkpoint for each run.
* **Change detection**: uses MD5 hashes to update only truly modified rows.

---

## 📜 License

MIT © gitexplorer23
