from src.logicModule import noteLogic


sample_note = """
Today I worked on Synapse and finally got the offline model connected.
I still feel stressed because school is busy, but I am happy that progress is being made.
"""

result = noteLogic.analyzeNoteContent(sample_note)

print(result)




result2 = noteLogic.analyzeAndStoreNote(
    note_id=1,
    content="Today I worked on Synapse and felt pretty good about my progress.",
    databaseName="synapse.db"
)

print(result2)