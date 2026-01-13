from sqlalchemy import text
from app.core.db import engine

def add_index():
    with engine.connect() as conn:
        try:
            # Check if index exists
            result = conn.execute(text("SHOW INDEX FROM prices WHERE Key_name = 'idx_prices_symbol_timeframe_ts'"))
            if result.fetchone():
                print("Index idx_prices_symbol_timeframe_ts already exists.")
            else:
                print("Adding index idx_prices_symbol_timeframe_ts...")
                conn.execute(text("CREATE INDEX idx_prices_symbol_timeframe_ts ON prices (symbol, timeframe, ts DESC)"))
                print("Index added successfully.")
        except Exception as e:
            print(f"Error adding index: {e}")

if __name__ == "__main__":
    add_index()
