
import sqlite3

DATABASE_NAME = "myai_memory.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'New Chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(messages)")
    columns = [column[1] for column in cursor.fetchall()]

    if "conversation_id" not in columns:
        cursor.execute("""
            ALTER TABLE messages
            ADD COLUMN conversation_id INTEGER
        """)

    cursor.execute("SELECT id FROM conversations LIMIT 1")
    result = cursor.fetchone()

    if result is None:
        cursor.execute("""
            INSERT INTO conversations (title)
            VALUES ('Previous Conversation')
        """)
        default_id = cursor.lastrowid
    else:
        default_id = result[0]

    cursor.execute("""
        UPDATE messages
        SET conversation_id = ?
        WHERE conversation_id IS NULL
    """, (default_id,))

    connection.commit()
    connection.close()


def create_conversation(title="New Chat"):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO conversations (title) VALUES (?)",
        (title,)
    )

    conversation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return conversation_id


def update_conversation_title(conversation_id, title):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE conversations
        SET title = ?
        WHERE id = ?
    """, (title, conversation_id))

    connection.commit()
    connection.close()


def get_conversations():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title
        FROM conversations
        ORDER BY id DESC
    """)

    conversations = cursor.fetchall()

    connection.close()

    return conversations


def save_message(role, message, conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (role, message, conversation_id)
        VALUES (?, ?, ?)
    """, (role, message, conversation_id))

    connection.commit()
    connection.close()


def get_messages(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT role, message
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id
    """, (conversation_id,))

    messages = cursor.fetchall()

    connection.close()

    return messages


def clear_messages(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE conversation_id = ?
    """, (conversation_id,))

    connection.commit()
    connection.close()
def delete_conversation(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM messages
        WHERE conversation_id = ?
    """, (conversation_id,))

    cursor.execute("""
        DELETE FROM conversations
        WHERE id = ?
    """, (conversation_id,))

    connection.commit()
    connection.close()

create_table()


if __name__ == "__main__":

    print("MyAI multi-chat database is ready!")

    for conversation in get_conversations():
        print(conversation)
