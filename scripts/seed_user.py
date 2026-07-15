import os
import random
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from database.db import get_db

FIRST_NAMES = [
    # Indian
    "Rahul", "Priya", "Amit", "Sneha", "Vikram", "Ananya", "Rohan", "Divya",
    "Arjun", "Kavya", "Suresh", "Meera", "Karthik", "Pooja", "Aditya", "Nisha",
    "Vivek", "Shreya", "Manoj", "Ritu", "Sanjay", "Neha", "Deepak", "Anjali",
    "Ravi", "Swati", "Harish", "Isha", "Nikhil", "Preeti", "Gaurav", "Sunita",
    "Abhishek", "Lakshmi", "Rajesh", "Kiran", "Siddharth", "Tanvi", "Varun", "Simran",
    # Nepali
    "Anish", "Sabina", "Bikash", "Sunita", "Prakash", "Anita", "Sujan", "Rekha",
    "Bibek", "Sarita", "Suman", "Mina", "Nabin", "Sabitri", "Rajan", "Puja",
    "Sagar", "Sabnam", "Dipendra", "Sushmita", "Kiran", "Ranjana", "Prashant", "Rupa",
    "Bishnu", "Gita", "Rabin", "Kamala", "Santosh", "Bimala",
]

LAST_NAMES = [
    # Indian
    "Sharma", "Verma", "Iyer", "Nair", "Reddy", "Gupta", "Patel", "Menon",
    "Rao", "Mehta", "Kapoor", "Joshi", "Chatterjee", "Bose", "Pillai", "Naidu",
    "Agarwal", "Bhatt", "Choudhary", "Desai", "Ghosh", "Kulkarni", "Malhotra", "Nambiar",
    "Pandey", "Rastogi", "Saxena", "Trivedi", "Yadav", "Krishnan",
    # Nepali
    "Shrestha", "Gurung", "Tamang", "Rai", "Limbu", "Magar", "Thapa", "Basnet",
    "Karki", "Adhikari", "Poudel", "Khadka", "Bhattarai", "Dahal", "Sunuwar",
    "Maharjan", "Shakya", "Bajracharya", "Lama", "Chhetri",
]


def generate_candidate():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    suffix = random.randint(10, 999)
    email = f"{first.lower()}.{last.lower()}{suffix}@gmail.com"
    return name, email


def main():
    conn = get_db()
    try:
        while True:
            name, email = generate_candidate()
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing is None:
                break

        password_hash = generate_password_hash("password123")
        created_at = datetime.now().isoformat(sep=" ", timespec="seconds")

        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, created_at),
        )
        conn.commit()
        user_id = cur.lastrowid

        print("Seeded new user:")
        print(f"  id:    {user_id}")
        print(f"  name:  {name}")
        print(f"  email: {email}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
