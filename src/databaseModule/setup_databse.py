"""
Synapse - Smart Journal Database Setup
======================================
This script initializes the SQLite database for the Synapse application.

Run this once to create the database file and tables.
Usage: python setup_database.py

Team: Jesse, Nicolas, Naomi, Sonia, Alex
Date: February 2026
"""

import sqlite3
import os
from datetime import datetime, timedelta

DATABASE_NAME = "synapse.db"


def connect_db(db_name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    # Ensure foreign key constraints are enforced in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_database()->None:
    """Initialize the Synapse database with all required tables"""

    # Remove old database if it exists (for fresh setup)
    if os.path.exists(DATABASE_NAME):
        print(f"Found existing database '{DATABASE_NAME}'")
        response = input("Delete and recreate? (y/n): ")
        if response.lower() != "y":
            print("Aborting setup.")
            return
        os.remove(DATABASE_NAME)
        print("Deleted old database")

    conn = connect_db(DATABASE_NAME)
    cursor = conn.cursor()

    print(f"\nCreating database: {DATABASE_NAME}\n")

    # ==================== NOTES TABLE ====================
    print("Creating 'notes' table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT DEFAULT 'manual',              -- manual, import, webclip, etc.
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    print("'notes' table created")

    # ==================== TAGS TABLE ====================
    print("Creating 'tags' table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    print("'tags' table created")

    # ==================== NOTE_TAGS RELATIONSHIP ====================
    print("Creating 'note_tags' junction table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS note_tags (
            note_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (note_id, tag_id)
        )
        """
    )
    print("'note_tags' junction table created")

    # ==================== INSIGHTS TABLE (lightweight) ====================
    print("Creating 'insights' table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            topic TEXT,
            key_insight TEXT,
            sentiment TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
        """
    )
    print("'insights' table created")

    # ==================== NOTE_ANALYSES TABLE (LLM pipeline) ====================
    # Stores richer LLM outputs per note (versioned/rerunnable).
    print("Creating 'note_analyses' table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS note_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            analysis_type TEXT NOT NULL,               -- summary, themes, entities, action_items, etc.
            model_name TEXT,                           -- local model id/name
            prompt_version TEXT,                       -- helps reproducibility
            output_text TEXT NOT NULL,
            output_json TEXT,                          -- optional: JSON string
            input_hash TEXT,                           -- hash of note content when analyzed
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
        """
    )
    print("'note_analyses' table created")

    # ==================== REMINDERS TABLE ====================
    print("Creating 'reminders' table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER,
            reminder_text TEXT NOT NULL,
            due_date TEXT,                             -- ISO datetime string recommended
            priority TEXT DEFAULT 'medium',            -- low/medium/high
            completed INTEGER DEFAULT 0,               -- 0/1
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE SET NULL
        )
        """
    )
    print("'reminders' table created")

    # ==================== TTS QUEUE TABLE (optional GUI module) ====================
    # A simple queue for "read this note aloud" features.
    print("Creating 'tts_queue' table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tts_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER,
            text TEXT NOT NULL,
            voice TEXT,                                -- optional voice id/name
            rate REAL,                                 -- optional speech rate
            status TEXT DEFAULT 'queued',              -- queued/running/done/error
            error_message TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            started_at TEXT,
            finished_at TEXT,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE SET NULL
        )
        """
    )
    print("'tts_queue' table created")

    # ==================== INDEXES FOR PERFORMANCE ====================
    print("\nCreating indexes for better performance...")

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_notes_created
        ON notes(created_at DESC)
        """
    )
    print("Index on notes.created_at")

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tags_name
        ON tags(tag_name)
        """
    )
    print("Index on tags.tag_name")

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reminders_due
        ON reminders(due_date, completed)
        """
    )
    print("Index on reminders(due_date, completed)")

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_note_analyses_note
        ON note_analyses(note_id, created_at DESC)
        """
    )
    print("Index on note_analyses(note_id, created_at)")

    # ==================== FULL-TEXT SEARCH ====================
    print("\nSetting up full-text search (FTS5)...")
    cursor.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts
        USING fts5(title, content, content=notes, content_rowid=id)
        """
    )
    print("Full-text search enabled")

    # ==================== TRIGGERS FOR AUTO-UPDATE ====================
    print("\nCreating triggers...")

    # Update updated_at on notes changes
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS update_note_timestamp
        AFTER UPDATE ON notes
        BEGIN
            UPDATE notes SET updated_at = datetime('now')
            WHERE id = NEW.id;
        END
        """
    )
    print("Auto-update timestamp trigger created")

    # Keep FTS index in sync
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS notes_fts_insert
        AFTER INSERT ON notes
        BEGIN
            INSERT INTO notes_fts(rowid, title, content)
            VALUES (NEW.id, NEW.title, NEW.content);
        END
        """
    )

    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS notes_fts_update
        AFTER UPDATE ON notes
        BEGIN
            UPDATE notes_fts SET title = NEW.title, content = NEW.content
            WHERE rowid = NEW.id;
        END
        """
    )

    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS notes_fts_delete
        AFTER DELETE ON notes
        BEGIN
            DELETE FROM notes_fts WHERE rowid = OLD.id;
        END
        """
    )
    print("FTS sync triggers created")

    conn.commit()

    # ==================== SEED DATA ====================
    print("\nInserting seed data for testing...\n")

    sample_notes = [
        {
            "title": "Welcome to Synapse",
            "content": """This is your first note in Synapse - your AI-powered personal assistant!

Synapse helps you organize your thoughts, extract insights, and stay on top of your tasks. Try creating more notes and watch the AI suggest tags automatically.

Features:
- Smart tag suggestions
- Automatic insight generation
- Reminder extraction
- Pattern recognition across your notes
- Full-text search

Happy note-taking!""",
        },
        {
            "title": "Project Meeting - Q1 Planning",
            "content": """Met with the team today to discuss Q1 goals. Need to finalize the budget by Friday and present to stakeholders next Monday at 2pm.

Action items:
- Review last quarter's expenses
- Draft budget proposal
- Schedule follow-up meeting with Sarah

Feeling confident about the presentation but need to prepare slides.""",
        },
        {
            "title": "Python Learning Notes",
            "content": """Learned about list comprehensions today. They're much more concise than traditional for loops.

Example: squares = [x**2 for x in range(10)]

Also explored decorators - still a bit confusing but starting to make sense. Will practice more tomorrow.""",
        },
        {
            "title": "Morning Workout - January 28",
            "content": """Morning workout: 30 min cardio, feeling energized
Breakfast: Oatmeal with berries
Water intake: 6 glasses so far

Need to schedule doctor appointment for annual checkup.""",
        },
        {
            "title": "Today's Thoughts",
            "content": """Feeling grateful today. The project is coming together nicely and the team is working well together.

Sometimes it's important to pause and appreciate the progress we've made rather than always focusing on what's left to do.

Reminder to self: Take breaks and celebrate small wins.""",
        },
    ]

    note_ids = []
    for note in sample_notes:
        cursor.execute(
            """
            INSERT INTO notes (title, content)
            VALUES (?, ?)
            """,
            (note["title"], note["content"]),
        )
        note_ids.append(cursor.lastrowid)
        print(f"Added note: '{note['title']}'")

    sample_tags = [
        "journal-entry",
        "health-log",
        "learning-note",
        "work-note",
        "work",
        "personal",
        "health",
        "learning",
        "python",
        "meeting",
        "budget",
        "fitness",
        "todo",
        "ideas",
        "gratitude",
    ]

    tag_ids = {}
    for tag_name in sample_tags:
        cursor.execute("INSERT INTO tags (tag_name) VALUES (?)", (tag_name,))
        tag_ids[tag_name] = cursor.lastrowid
        print(f"Added tag: {tag_name}")

    tag_associations = [
        (note_ids[0], tag_ids["personal"]),
        (note_ids[0], tag_ids["ideas"]),
        (note_ids[1], tag_ids["work"]),
        (note_ids[1], tag_ids["meeting"]),
        (note_ids[1], tag_ids["budget"]),
        (note_ids[1], tag_ids["todo"]),
        (note_ids[1], tag_ids["journal-entry"]),
        (note_ids[1], tag_ids["work-note"]),
        (note_ids[2], tag_ids["learning"]),
        (note_ids[2], tag_ids["python"]),
        (note_ids[2], tag_ids["learning-note"]),
        (note_ids[3], tag_ids["health"]),
        (note_ids[3], tag_ids["fitness"]),
        (note_ids[3], tag_ids["health-log"]),
        (note_ids[3], tag_ids["todo"]),
        (note_ids[4], tag_ids["personal"]),
        (note_ids[4], tag_ids["journal-entry"]),
        (note_ids[4], tag_ids["gratitude"]),
    ]

    for note_id, tag_id in tag_associations:
        cursor.execute(
            """
            INSERT INTO note_tags (note_id, tag_id)
            VALUES (?, ?)
            """,
            (note_id, tag_id),
        )

    print("Linked tags to notes")

    # Seed reminders: store as ISO datetime strings for easy sorting/querying
    now = datetime.now()
    friday = (now + timedelta(days=(4 - now.weekday()) % 7)).replace(hour=17, minute=0, second=0, microsecond=0)
    monday = (now + timedelta(days=(7 - now.weekday()) % 7)).replace(hour=14, minute=0, second=0, microsecond=0)

    cursor.execute(
        """
        INSERT INTO reminders (note_id, reminder_text, due_date, priority)
        VALUES (?, ?, ?, ?)
        """,
        (note_ids[1], "Finalize budget proposal", friday.isoformat(sep=" "), "high"),
    )

    cursor.execute(
        """
        INSERT INTO reminders (note_id, reminder_text, due_date, priority)
        VALUES (?, ?, ?, ?)
        """,
        (note_ids[1], "Present to stakeholders", monday.isoformat(sep=" "), "high"),
    )

    print("Added sample reminders")

    conn.commit()

    # ==================== VERIFICATION ====================
    print("\nDatabase Statistics:\n")

    cursor.execute("SELECT COUNT(*) FROM notes")
    note_count = cursor.fetchone()[0]
    print(f"  Notes: {note_count}")

    cursor.execute("SELECT COUNT(*) FROM tags")
    tag_count = cursor.fetchone()[0]
    print(f"  Tags: {tag_count}")

    cursor.execute("SELECT COUNT(*) FROM note_tags")
    link_count = cursor.fetchone()[0]
    print(f"  Note-Tag Links: {link_count}")

    cursor.execute("SELECT COUNT(*) FROM reminders")
    reminder_count = cursor.fetchone()[0]
    print(f"  Reminders: {reminder_count}")

    cursor.execute("SELECT COUNT(*) FROM note_analyses")
    analyses_count = cursor.fetchone()[0]
    print(f"  Note Analyses: {analyses_count}")

    cursor.execute("SELECT COUNT(*) FROM tts_queue")
    tts_count = cursor.fetchone()[0]
    print(f"  TTS Queue Items: {tts_count}")

    conn.close()

    print(f"\nDatabase setup complete! File created: {DATABASE_NAME}")
    print("\nNext steps:")
    print(f"  1. Open '{DATABASE_NAME}' with DB Browser for SQLite")
    print("  2. Explore the tables and sample data")
    print(f"  3. Commit '{DATABASE_NAME}' and this script to GitHub")
    print("\nReady to start building Synapse!\n")


def verify_database()->None:
    """Verify database structure and display sample data"""

    if not os.path.exists(DATABASE_NAME):
        print(f"Database '{DATABASE_NAME}' not found. Run setup first.")
        return

    conn = connect_db(DATABASE_NAME)
    cursor = conn.cursor()

    print(f"\nVerifying database: {DATABASE_NAME}\n")

    # List all tables (excluding internal sqlite_*)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [t[0] for t in cursor.fetchall() if not t[0].startswith("sqlite_")]

    print("Tables:")
    for table_name in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count} rows")

    # Show sample note with tags
    print("\nSample Note with Tags:\n")
    cursor.execute(
        """
        SELECT
            n.title,
            n.content,
            COALESCE(GROUP_CONCAT(t.tag_name, ', '), '') AS tags
        FROM notes n
        LEFT JOIN note_tags nt ON n.id = nt.note_id
        LEFT JOIN tags t ON nt.tag_id = t.id
        WHERE n.id = 2
        GROUP BY n.id
        """
    )

    result = cursor.fetchone()
    if result:
        title, content, tags = result
        print(f"Title: {title}")
        print(f"Tags: {tags}")
        print("\nContent (preview):")
        print(content[:200] + ("..." if len(content) > 200 else ""))

    conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("SYNAPSE - DATABASE SETUP")
    print("=" * 60)

    create_database()
    verify_database()

    print("\n" + "=" * 60)
