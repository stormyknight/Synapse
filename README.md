2/8/2026
**Synapse DB is up**
Just put the database up. Take a look at it. It should have all the features we needed...
Core tables: notes, tags, note_tags
Reminders table
note_analyses table for offline LLM outputs (later)
some sample seed data just so we can see it in the DB Browser
tts_queue table (for later text-to-speech feature)

**Setup Instructions**
Run setup_database.py once to generate synapse.db
Read with DB Browser for SQLite (https://sqlitebrowser.org/dl/)
(Open synapse.db)

**Notes on LLM Model**
Our LLM module will use a local model (likely Llama 3.2 1-3B for baseline, possibly 8B later for deeper analysis).
Runs offline and locally.
https://ollama.com/library/llama3.2
(Takes about 1.3-2GB of space for these models, larger models can give better summaries and such, but they take up more space)

**Next Steps**
Update the system model diagram to include TTS and finalized LLM choice
Begin building the Data Access Layer so GUI can load/save/search notes
After the DAL is ready, start connecting GUI screens to real data.
Continue working on the design document

**Notes on Testing**
All test files must start with "test_" or end with "_test" to be recognized as test files.
All test functions must end with"_test" to be recognized as such.
Need to install "install pytest pytest-qt PyQt5" for tests to work.
Must close out graphics window to complete test