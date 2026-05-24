import csv
import uuid
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert

from app.db.session import SessionLocal
from app.models.hanzi import Hanzi


CSV_PATH = Path("data/hanziDB.csv")
BATCH_SIZE = 1000


def transform_row(row: dict) -> dict:
    return {
        "id": uuid.uuid4(),
        "character": row["charcter"],
        "pinyin": row["pinyin"],

        # roboczo: PL = EN
        "meaning_en": row["definition"],
        "meaning_pl": row["definition"],

        # HSK → difficulty_level
        "difficulty_level": int(row["hsk_levl"] or 1),

        # brak kategorii tematycznej
        "theme_category": None,
    }


def batch_upsert(session, batch: list[dict]):
    if not batch:
        return

    stmt = insert(Hanzi).values(batch)

    # UPSERT po unique character
    stmt = stmt.on_conflict_do_nothing(
        index_elements=["character"]
    )

    session.execute(stmt)


def seed():
    session = SessionLocal()

    batch = []
    total = 0
    inserted = 0
    skipped = 0

    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                batch.append(transform_row(row))

                if len(batch) >= BATCH_SIZE:
                    inserted, skipped = flush(session, batch, inserted, skipped)
                    total += len(batch)
                    batch.clear()

            if batch:
                inserted, skipped = flush(session, batch, inserted, skipped)
                total += len(batch)

        print("\n===== SEED SUMMARY =====")
        print(f"Total processed: {total}")
        print(f"Inserted (attempted): {inserted}")
        print(f"Skipped (duplicates): {skipped}")
        print("========================\n")

    except Exception as e:
        session.rollback()
        print(f"Seed failed: {e}")
        raise

    finally:
        session.close()


def flush(session, batch, inserted, skipped):
    stmt = insert(Hanzi).values(batch)

    result = session.execute(
        stmt.on_conflict_do_nothing(index_elements=["character"])
    )

    session.commit()

    # rowcount bywa None w PostgreSQL + ON CONFLICT
    inserted += len(batch)

    # dokładne skipped nie jest dostępne bez SELECT,
    # więc traktujemy to jako informacyjne
    print(f"Processed batch: {len(batch)} rows")

    return inserted, skipped


if __name__ == "__main__":
    seed()
