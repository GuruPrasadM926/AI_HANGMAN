"""
Hangman AI Backend — using Groq (free)
Path: hangman/app.py
Run: python app.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from groq import Groq
import random
"""
Hangman AI Backend — using Groq (free)
Path: hangman/app.py
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from groq import Groq
import random
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── Word bank by category ────────────────────────────────────────────────────
WORD_BANK = {
    "animals": [
        "elephant", "giraffe", "penguin", "dolphin", "crocodile",
        "chameleon", "platypus", "armadillo", "rhinoceros", "hippopotamus"
    ],
    "countries": [
        "australia", "zimbabwe", "portugal", "bangladesh", "switzerland",
        "mozambique", "kazakhstan", "india", "azerbaijan", "liechtenstein"
    ],
    "science": [
        "photosynthesis", "mitochondria", "chromosome", "electrolysis",
        "thermodynamics", "hypothesis", "ecosystem", "gravitational",
        "bioluminescence", "electromagnetic"
    ],
    "food": [
        "biryani", "noodles", "friedrice", "croissant", "momos",
        "gulabjamun", "butternaan", "jalebi", "ratatouille", "spaghetti"
    ],
    "technology": [
        "algorithm", "blockchain", "encryption", "kubernetes", "javascript",
        "cybersecurity", "bandwidth", "semiconductor", "repository", "virtualization"
    ]
}

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def pick_word():
    category = random.choice(list(WORD_BANK.keys()))
    word = random.choice(WORD_BANK[category])
    return word, category


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/new-game", methods=["GET"])
def new_game():
    word, category = pick_word()
    return jsonify({
        "word_length": len(word),
        "category": category,
        "word": word,
        "max_wrong": 6
    })


@app.route("/api/hint", methods=["POST"])
def get_hint():
    data = request.get_json()
    word = data.get("word", "")
    category = data.get("category", "")
    guessed_letters = data.get("guessed_letters", [])
    wrong_guesses = data.get("wrong_guesses", [])
    revealed_pattern = data.get("revealed_pattern", "")
    hint_number = data.get("hint_number", 1)

    hint_levels = {
        1: "Give a vague, creative, poetic clue about the word. Do NOT mention the word or any of its letters directly.",
        2: "Give a more specific clue — mention the category, a key property, or an interesting fact. Still do not reveal the word.",
        3: f"Give a strong hint. You may confirm any correct letters already found ({', '.join(guessed_letters) if guessed_letters else 'none yet'}) and hint at the structure. Still don't say the word outright."
    }

    prompt = f"""You are the hint-giver in a Hangman game.

Word to guess: "{word}"
Category: {category}
Letters already guessed correctly: {', '.join([l for l in guessed_letters if l in word]) or 'none'}
Wrong guesses: {', '.join(wrong_guesses) or 'none'}
Current revealed pattern: "{revealed_pattern}"
Hint level requested: {hint_number}/3

Instructions: {hint_levels.get(hint_number, hint_levels[1])}

Respond with ONLY the hint text — one or two sentences, clever and engaging. No preamble."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        hint_text = response.choices[0].message.content.strip()
        return jsonify({"hint": hint_text})
    except Exception as e:
        print(f"Hint error: {e}")
        return jsonify({"hint": "AI hint unavailable right now."}), 200


@app.route("/api/word-reveal-story", methods=["POST"])
def word_reveal_story():
    data = request.get_json()
    word = data.get("word", "")
    category = data.get("category", "")
    won = data.get("won", False)

    outcome = "won and correctly guessed" if won else "lost and failed to guess"

    prompt = f"""The player just {outcome} the word "{word}" (category: {category}) in Hangman.

Write a single fun, surprising, or fascinating sentence about "{word}" that the player would love to read right now.
Be enthusiastic but brief. Start directly with the fact — no intro phrases like "Did you know"."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        fun_fact = response.choices[0].message.content.strip()
        return jsonify({"fun_fact": fun_fact})
    except Exception as e:
        print(f"Story error: {e}")
        return jsonify({"fun_fact": "A fun fact could not be loaded."}), 200


if __name__ == "__main__":
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        print("WARNING: GROQ_API_KEY not set in .env file!")
    else:
        print(f"Groq API Key loaded: {key[:12]}...")
    print("Hangman AI Backend running on http://localhost:5000")
    app.run(debug=True, port=5000)
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── Word bank by category ────────────────────────────────────────────────────
WORD_BANK = {
    "animals": [
        "elephant", "giraffe", "penguin", "dolphin", "crocodile",
        "chameleon", "platypus", "armadillo", "rhinoceros", "hippopotamus"
    ],
    "countries": [
        "australia", "zimbabwe", "portugal", "bangladesh", "switzerland",
        "mozambique", "kazakhstan", "india", "azerbaijan", "liechtenstein"
    ],
    "science": [
        "photosynthesis", "mitochondria", "chromosome", "electrolysis",
        "thermodynamics", "hypothesis", "ecosystem", "gravitational",
        "bioluminescence", "electromagnetic"
    ],
    "food": [
        "biryani", "noodles", "friedrice", "croissant", "momos",
        "gulabjamun", "butternaan", "jalebi", "ratatouille", "spaghetti"
    ],
    "technology": [
        "algorithm", "blockchain", "encryption", "kubernetes", "javascript",
        "cybersecurity", "bandwidth", "semiconductor", "repository", "virtualization"
    ]
}

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"  # free model on Groq


def pick_word():
    category = random.choice(list(WORD_BANK.keys()))
    word = random.choice(WORD_BANK[category])
    return word, category


@app.route("/api/new-game", methods=["GET"])
def new_game():
    word, category = pick_word()
    return jsonify({
        "word_length": len(word),
        "category": category,
        "word": word,
        "max_wrong": 6
    })


@app.route("/api/hint", methods=["POST"])
def get_hint():
    data = request.get_json()
    word = data.get("word", "")
    category = data.get("category", "")
    guessed_letters = data.get("guessed_letters", [])
    wrong_guesses = data.get("wrong_guesses", [])
    revealed_pattern = data.get("revealed_pattern", "")
    hint_number = data.get("hint_number", 1)

    hint_levels = {
        1: "Give a vague, creative, poetic clue about the word. Do NOT mention the word or any of its letters directly.",
        2: "Give a more specific clue — mention the category, a key property, or an interesting fact. Still do not reveal the word.",
        3: f"Give a strong hint. You may confirm any correct letters already found ({', '.join(guessed_letters) if guessed_letters else 'none yet'}) and hint at the structure. Still don't say the word outright."
    }

    prompt = f"""You are the hint-giver in a Hangman game.

Word to guess: "{word}"
Category: {category}
Letters already guessed correctly: {', '.join([l for l in guessed_letters if l in word]) or 'none'}
Wrong guesses: {', '.join(wrong_guesses) or 'none'}
Current revealed pattern: "{revealed_pattern}"
Hint level requested: {hint_number}/3

Instructions: {hint_levels.get(hint_number, hint_levels[1])}

Respond with ONLY the hint text — one or two sentences, clever and engaging. No preamble."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        hint_text = response.choices[0].message.content.strip()
        return jsonify({"hint": hint_text})
    except Exception as e:
        print(f"Hint error: {e}")
        return jsonify({"hint": "AI hint unavailable right now."}), 200


@app.route("/api/word-reveal-story", methods=["POST"])
def word_reveal_story():
    data = request.get_json()
    word = data.get("word", "")
    category = data.get("category", "")
    won = data.get("won", False)

    outcome = "won and correctly guessed" if won else "lost and failed to guess"

    prompt = f"""The player just {outcome} the word "{word}" (category: {category}) in Hangman.

Write a single fun, surprising, or fascinating sentence about "{word}" that the player would love to read right now.
Be enthusiastic but brief. Start directly with the fact — no intro phrases like "Did you know"."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        fun_fact = response.choices[0].message.content.strip()
        return jsonify({"fun_fact": fun_fact})
    except Exception as e:
        print(f"Story error: {e}")
        return jsonify({"fun_fact": "A fun fact could not be loaded."}), 200


if __name__ == "__main__":
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        print("WARNING: GROQ_API_KEY not set in .env file!")
    else:
        print(f"Groq API Key loaded: {key[:12]}...")
    print("Hangman AI Backend running on http://localhost:5000")
    app.run(debug=True, port=5000)