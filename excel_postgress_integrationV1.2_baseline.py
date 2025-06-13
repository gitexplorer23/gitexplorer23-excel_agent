import os
import hashlib
from dotenv import load_dotenv
import pandas as pd
import sqlalchemy
from sqlalchemy import text, MetaData, Table, inspect
from sqlalchemy.dialects.postgresql import insert

def calculate_row_hash(row, data_cols):
    """Concatenate and hash all relevant fields for change detection."""
    concat = '|'.join(str(row[col]) for col in data_cols)
    return hashlib.md5(concat.encode('utf-8')).hexdigest()

def process_sheet(engine, sheet_name, df, pk_col):
    # Normalize columns
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    # Data columns for hash (excluding pk and timestamps)
    data_cols = [col for col in df.columns if col not in (pk_col, 'created_at', 'updated_at')]
    # Calculate row hash
    df['row_hash'] = df.apply(lambda row: calculate_row_hash(row, data_cols), axis=1)

    inspector = inspect(engine)
    table_exists = inspector.has_table(sheet_name, schema='public')

    with engine.begin() as conn:
        # 1. Create table if missing
        if not table_exists:
            df.head(0).to_sql(
                name=sheet_name,
                con=conn,
                schema='public',
                if_exists='replace',
                index=False
            )
            print(f"✓ Created table '{sheet_name}'.")

        # 2. Ensure timestamp and row_hash columns
        conn.execute(text(f"""
            ALTER TABLE public.{sheet_name}
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                ADD COLUMN IF NOT EXISTS row_hash TEXT;
        """))

        # 3. Ensure unique constraint on PK
        constraint = f"uq_{sheet_name}_{pk_col}"
        conn.execute(text(f"""
            DO $$
            BEGIN
              IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE lower(conname) = lower('{constraint}')
              ) THEN
                ALTER TABLE public.{sheet_name}
                  ADD CONSTRAINT {constraint} UNIQUE ("{pk_col}");
              END IF;
            END $$;
        """))

        # 4. Build and execute upsert
        metadata = MetaData()
        table = Table(sheet_name, metadata,
                      autoload_with=conn, schema='public')

        records = df.to_dict(orient='records')
        stmt = insert(table).values(records)

        # Exclude PK and created_at from updates; update updated_at & row_hash
        update_cols = {
            c.name: stmt.excluded[c.name]
            for c in table.columns
            if c.name not in (pk_col, 'created_at')
        }
        update_cols['updated_at'] = text('now()')

        # Only update if the row_hash has changed
        upsert = stmt.on_conflict_do_update(
            index_elements=[pk_col],
            set_=update_cols,
            where=(table.c.row_hash != stmt.excluded.row_hash)
        )
        conn.execute(upsert)
        print(f"↺ Upsert complete for '{sheet_name}' on PK='{pk_col}' (updated only if data changed).")

def main():
    load_dotenv()
    excel_file = os.getenv('EXCEL_FILE_PATH')
    pk_col     = os.getenv('PK_COLUMN', 'ID').split('#')[0].strip()
    # Parse SHEET_NAMES as a list, removing empty/extra spaces
    sheet_list = [s.strip() for s in os.getenv('SHEET_NAMES', '').split(',') if s.strip()]

    required = ['EXCEL_FILE_PATH', 'SHEET_NAMES', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME']
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

    conn_str = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT','5432')}/{os.getenv('DB_NAME')}"
    )
    engine = sqlalchemy.create_engine(conn_str)

    # Prepare CSV folder
    base_dir = os.path.dirname(excel_file)
    csv_dir  = os.path.join(base_dir, 'CSV')
    os.makedirs(csv_dir, exist_ok=True)

    # Load Excel once, get all available sheet names
    excel = pd.ExcelFile(excel_file)
    available_sheets = set(excel.sheet_names)
    missing_sheets = [s for s in sheet_list if s not in available_sheets]
    if missing_sheets:
        print(f"⚠️ Warning: These sheets are in SHEET_NAMES but not found in workbook: {missing_sheets}")

    # Only process requested sheets that exist
    for name in sheet_list:
        if name not in available_sheets:
            continue
        df = excel.parse(name)
        print(f"\n▶ Processing sheet '{name}' …")
        out_csv = os.path.join(csv_dir, f"{name}.csv")
        df.to_csv(out_csv, index=False)
        print(f"  • Exported to {out_csv}")
        process_sheet(engine, name, df, pk_col)

if __name__ == "__main__":
    main()
