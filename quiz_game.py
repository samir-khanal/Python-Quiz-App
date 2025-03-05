import sqlite3
import time

# Database Setup
conn = sqlite3.connect("Quiz_game.db", check_same_thread=False)
cursor = conn.cursor()

# Create Tables if they do not exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        score INTEGER,
        time_taken REAL       
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        options TEXT
    )
""")
conn.commit()

class Quiz:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.questions = self.get_questions()
        self.start_time = time.time()  # Start timing when quiz begins
        self.time_taken = 0  # Initialize time taken

    def get_questions(self):
        """Fetching MCQ questions from database or allow users to add them"""
        cursor.execute("SELECT id, question, answer, options FROM questions")
        rows = cursor.fetchall()

        if not rows:
            return []
        # Return list of dicts with id, question, answer, and options
        return [{"id": row[0], "question": row[1],"answer": row[2], "options": row[3]} for row in rows]

    def add_questions(self, question, answer, options):
        """Add question to database"""
        cursor.execute("INSERT INTO questions (question, answer, options) VALUES (?, ?, ?)", (question, answer, options))
        conn.commit()
        time.sleep(0.5)  # Small delay to indicate success

    def delete_question(self, question_id):
        """Delete a question by its ID"""
        cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        time.sleep(0.5)  # Delay after deletion for smoother UX

    def start_quiz(self):
        """Start the quiz and record the start time"""
        self.start_time = time.time()
        time.sleep(1)  # Pause before starting

    def check_answer(self, user_answers):
        """Check answers and calculate score"""
        self.score = 0
        for i, question in enumerate(self.questions):
            if user_answers[i].strip().lower() == question["answer"].strip().lower():
                self.score += 1
        # Calculate time taken when user submits answers
        self.time_taken = round(time.time() - self.start_time, 2)  # Round to 2 decimal places
   
    def save_score(self):
        """Save score to leaderboard and calculate time taken"""

        try:
            cursor.execute("INSERT INTO leaderboard (name, score, time_taken) VALUES (?, ?, ?)", (self.name, self.score, self.time_taken))
        except sqlite3.IntegrityError:
            cursor.execute("UPDATE leaderboard SET score = ?, time_taken = ? WHERE name = ?", (self.score, self.time_taken, self.name))
        conn.commit()

    def get_leaderboard(self):
        """Retrieve leaderboard data"""
        cursor.execute("SELECT name, score, time_taken FROM leaderboard ORDER BY score DESC, time_taken ASC")
        return cursor.fetchall()
