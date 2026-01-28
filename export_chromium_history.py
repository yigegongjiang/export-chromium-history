# /// script
# requires-python = ">=3.9"
# ///
"""
Chromium History Export Script

Example:
    # Export last 7 days (default)
    uv run export_chromium_history.py --path /path/to/History

    # Export last 30 days
    uv run export_chromium_history.py --path /path/to/History --days 30

    # Path formats supported:
    #   ~/Library/...           (home directory)
    #   $HOME/Library/...       (environment variables)
    #   ./relative/path         (relative paths)
    #
    # Paths with spaces - use quotes or backslash escapes:
    #   --path "$HOME/Library/Application Support/.../History"
    #   --path ~/Library/Application\\ Support/.../History
"""

import argparse
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

REQUIRED_FIELDS = {
    "visits": ["visit_time", "transition", "url"],
    "urls": ["id", "url", "title"],
}


def main():
    parser = argparse.ArgumentParser(
        description="Export Chromium browser history"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days of history to export (default: 7)",
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Path to Chromium History database",
    )
    args = parser.parse_args()

    days_ago = args.days

    # Normalize path with comprehensive handling:
    raw_path = str(args.path).replace("\\ ", " ")
    chromium_history = Path(os.path.expandvars(raw_path)).expanduser().resolve()

    cutoff_date = datetime.now() - timedelta(days=days_ago)
    cutoff_unix = int(cutoff_date.timestamp())
    cutoff_chromium = (cutoff_unix + 11644473600) * 1000000

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"./output_{timestamp}").resolve()

    if not chromium_history.exists():
        print("Error: Chromium History database not found")
        print(f"Path: {chromium_history}")
        print()
        print("Hint: If your path contains spaces, use quotes or backslash escapes:")
        print('  --path "/Users/.../Application Support/.../History"')
        print("  --path ~/Library/Application\\ Support/.../History")
        sys.exit(1)

    if chromium_history.is_dir():
        print("Error: Path is a directory, not a file")
        print(f"Path: {chromium_history}")
        print("Hint: Please specify the full path to the History file, e.g.:")
        print(f"  {chromium_history}/History")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    temp_db = Path(tempfile.gettempdir()) / f"chromium_history_export_{os.getpid()}.db"
    shutil.copy2(chromium_history, temp_db)

    print(f"========== Chromium History Export (Last {days_ago} Days) ==========")
    print(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        # Schema validation
        missing_fields = {}
        for table, required in REQUIRED_FIELDS.items():
            cursor.execute(f"PRAGMA table_info({table})")
            cols = {row[1] for row in cursor.fetchall()}
            missing = [f for f in required if f not in cols]
            if missing:
                missing_fields[table] = missing
        if missing_fields:
            print("Error: Database schema not supported for export!")
            for table, fields in missing_fields.items():
                print(f"  Missing in '{table}': {', '.join(fields)}")
            conn.close()
            sys.exit(1)

        cursor.execute(
            f"SELECT COUNT(*) FROM visits WHERE visit_time >= {cutoff_chromium}"
        )
        visit_count = cursor.fetchone()[0]

        print("Exporting history...")

        transition_map = {
            0: "LINK",
            1: "TYPED",
            2: "AUTO_BOOKMARK",
            3: "AUTO_SUBFRAME",
            4: "MANUAL_SUBFRAME",
            5: "GENERATED",
            6: "AUTO_TOPLEVEL",
            7: "FORM_SUBMIT",
            8: "RELOAD",
            9: "KEYWORD",
            10: "KEYWORD_GENERATED",
        }

        cursor.execute(f"""
            SELECT
                u.url,
                COALESCE(u.title, ''),
                v.visit_time - 11644473600000000,
                v.transition & 0xFF
            FROM visits v
            LEFT JOIN urls u ON v.url = u.id
            WHERE v.visit_time >= {cutoff_chromium}
            ORDER BY v.visit_time DESC
        """)

        records = []
        for row in cursor.fetchall():
            url, title, time_usec, transition_code = row
            page_transition = transition_map.get(transition_code, "LINK")
            records.append(
                {
                    "url": url,
                    "title": title,
                    "time_usec": time_usec,
                    "page_transition": page_transition,
                    "favicon_url": "",
                    "client_id": "",
                    "ptoken": {},
                }
            )

        print("Splitting JSON files (max 1000 records per file)...")

        total = len(records)
        max_per_file = 1000
        num_files = (total + max_per_file - 1) // max_per_file if total > 0 else 1

        print(f"  Total records: {total}")
        print(f"  Will be split into {num_files} files")

        if num_files <= 10:
            print_indices = set(range(num_files))
        else:
            step = (num_files - 1) / 9
            print_indices = {round(step * j) for j in range(10)}

        for i in range(num_files):
            start = i * max_per_file
            end = min((i + 1) * max_per_file, total)
            chunk = records[start:end]

            filename = f"BrowserHistory_{i + 1:03d}.json"
            filepath = output_dir / filename

            output_data = {"Browser History": chunk}
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False)

            if i in print_indices:
                print(f"  -> {filename}: {len(chunk)} records")

        print()
        print("========== Export Statistics ==========")
        print()
        print(f"Visit count: {visit_count}")
        print()
        print(f"Time range (filtered to last {days_ago} days):")

        cursor.execute(f"""
            SELECT MIN(visit_time) FROM visits WHERE visit_time >= {cutoff_chromium}
        """)
        min_time = cursor.fetchone()[0]
        if min_time:
            min_unix = (min_time // 1000000) - 11644473600
            min_dt = datetime.fromtimestamp(min_unix)
            print(f"  Earliest visit: {min_dt.strftime('%Y-%m-%d %H:%M:%S')}")

        cursor.execute(f"""
            SELECT MAX(visit_time) FROM visits WHERE visit_time >= {cutoff_chromium}
        """)
        max_time = cursor.fetchone()[0]
        if max_time:
            max_unix = (max_time // 1000000) - 11644473600
            max_dt = datetime.fromtimestamp(max_unix)
            print(f"  Latest visit: {max_dt.strftime('%Y-%m-%d %H:%M:%S')}")

        print()
        print("========== Export Files ==========")
        print()
        print(f"Output directory: {output_dir}")
        print()
        print("========== Safari Import Instructions ==========")
        print()
        print("To import history in Safari:")
        print("  1. Safari → File → Import Browsing Data from File or Folder...")
        print(f"  2. Select {output_dir} Directory")
        print("  3. Wait for Import to Complete")

        conn.close()

    finally:
        if temp_db.exists():
            temp_db.unlink()

    print()
    print("Done!")


if __name__ == "__main__":
    main()
