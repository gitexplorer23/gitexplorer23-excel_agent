# Excel → PostgreSQL Sync Utility

Automate the export of Excel sheets to CSV and upsert them into PostgreSQL with audit timestamps and true change detection—no manual table prep or setup needed.

Simply download the repo, install the requirements, and run the script. It will:
- Automatically create the sample_test_data schema in PostgreSQL
- Generate tables based on Excel tab names
- Infer column types (e.g., varchar, int, etc.) from the original data
- Include audit columns for tracking insert/update timestamps

Fast, clean, and ready to use for data pipelines or analytics.

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
   git clone https://github.com/gitexplorer23/gitexplorer23-excel_agent.git
   cd your-repo
   ```

2. **Set up venv**

   ```bash
   python -m venv .venv
   # Windows
   .venv/Scripts/Activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install deps**

   ```
   pip install -r requirements.txt
   ```

4. **Create `.env`** (at project root)

   ```
   EXCEL_FILE_PATH=C:/path/to/your/file.xlsx
   SHEET_NAMES=test_data,test_data2
   PK_COLUMN=ID
   DB_USER=YourUserName
   DB_PASSWORD=Secret
   DB_HOST=localhost
   DB_PORT=YourPort
   DB_NAME=my_database
   ```

5. **Run the sync**

   ```
   python excel_postgress_integrationV1.2_baseline.py
   ```

---

## 📂 File Structure

```
.
├── excel_postgress_integrationV1.2_baseline.py    # Main script
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
