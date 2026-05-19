import subprocess
import sys

# Force install groq if not available
try:
    from groq import Groq
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq

import streamlit as st
import random
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hangman AI",
    page_icon="🎮",
    layout="centered"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&display=swap');

body, .stApp {
    background-color: #0d0d0f !important;
    color: #f0f0f0 !important;
    font-family: 'Space Mono', monospace !important;
}
h1 {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 3.5rem !important;
    color: #e8ff47 !important;
    text-shadow: 3px 3px 0 #5a6200, 6px 6px 0 #2a2e00;
    letter-spacing: 0.08em;
    margin-bottom: 0 !important;
}
.category-tag {
    background: #2a2a35; border: 1px solid #6b6b80;
    color: #47c8ff; padding: 4px 14px; border-radius: 3px;
    font-size: 0.7rem; letter-spacing: 0.2em;
    text-transform: uppercase; display: inline-block; margin-bottom: 20px;
}
.word-display {
    display: flex; flex-wrap: wrap; gap: 10px;
    justify-content: center; padding: 24px;
    background: #141418; border: 1px solid #2a2a35;
    border-radius: 4px; margin: 16px 0;
}
.letter-char { font-family: 'Bebas Neue', sans-serif; font-size: 2.2rem; color: #e8ff47; min-width: 28px; text-align: center; }
.letter-blank { font-family: 'Bebas Neue', sans-serif; font-size: 2.2rem; color: #3a3a4a; min-width: 28px; text-align: center; }
.letter-wrong { font-family: 'Bebas Neue', sans-serif; font-size: 2.2rem; color: #ff4757; min-width: 28px; text-align: center; }
.letter-line { width: 28px; height: 2px; background: #2a2a35; border-radius: 1px; }
.hint-box { background: #141418; border: 1px solid #2a2a35; border-radius: 4px; padding: 16px 20px; font-style: italic; color: #f0f0f0; font-size: 0.9rem; line-height: 1.7; margin: 10px 0; }
.wrong-letters-box { background: #1a0a0d; border: 1px solid #ff4757; border-radius: 4px; padding: 10px 16px; color: #ff4757; font-size: 0.85rem; letter-spacing: 0.15em; margin: 8px 0; }
.win-box { background: #0a1f14; border: 2px solid #47ff8a; border-radius: 4px; padding: 20px; text-align: center; color: #47ff8a; font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; letter-spacing: 0.1em; }
.lose-box { background: #1a0508; border: 2px solid #ff4757; border-radius: 4px; padding: 20px; text-align: center; color: #ff4757; font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; letter-spacing: 0.1em; }
.fact-box { background: #141418; border: 1px solid #2a2a35; border-radius: 4px; padding: 16px 20px; font-style: italic; color: #6b6b80; font-size: 0.85rem; line-height: 1.7; margin: 10px 0; text-align: center; }
hr { border-color: #2a2a35 !important; }
</style>
""", unsafe_allow_html=True)

# ── Word bank ────────────────────────────────────────────────────────────────
WORD_BANK = {
    "animals": ["elephant","giraffe","penguin","dolphin","crocodile","chameleon","platypus","armadillo","rhinoceros","hippopotamus"],
    "countries": ["australia","zimbabwe","portugal","bangladesh","switzerland","mozambique","kazakhstan","india","azerbaijan","liechtenstein"],
    "science": ["photosynthesis","mitochondria","chromosome","electrolysis","thermodynamics","hypothesis","ecosystem","gravitational","bioluminescence","electromagnetic"],
    "food": ["biryani","noodles","friedrice","croissant","momos","gulabjamun","butternaan","jalebi","ratatouille","spaghetti"],
    "technology": ["algorithm","blockchain","encryption","kubernetes","javascript","cybersecurity","bandwidth","semiconductor","repository","virtualization"]
}

MAX_WRONG = 6
MODEL = "llama-3.3-70b-versatile"

# ── Groq client ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    api_key = ""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        api_key = os.environ.get("GROQ_API_KEY", "")
    return Groq(api_key=api_key)

# ── Game state ────────────────────────────────────────────────────────────────
def init_game():
    category = random.choice(list(WORD_BANK.keys()))
    word = random.choice(WORD_BANK[category])
    st.session_state.word = word
    st.session_state.category = category
    st.session_state.guessed = set()
    st.session_state.wrong = []
    st.session_state.hint_count = 0
    st.session_state.hints = []
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.fun_fact = ""

if "word" not in st.session_state:
    init_game()

# ── AI functions ──────────────────────────────────────────────────────────────
def get_hint(hint_number):
    client = get_groq_client()
    word = st.session_state.word
    category = st.session_state.category
    guessed = list(st.session_state.guessed)
    wrong = st.session_state.wrong
    revealed = " ".join([ch if ch in st.session_state.guessed else "_" for ch in word])
    hint_levels = {
        1: "Give a vague, creative, poetic clue about the word. Do NOT mention the word or any of its letters directly.",
        2: "Give a more specific clue — mention the category, a key property, or an interesting fact. Still do not reveal the word.",
        3: f"Give a strong hint. You may confirm correct letters ({', '.join(guessed) or 'none'}) and hint at structure. Still don't say the word."
    }
    prompt = f"""You are the hint-giver in a Hangman game.
Word: "{word}", Category: {category}
Correct letters: {', '.join([l for l in guessed if l in word]) or 'none'}
Wrong guesses: {', '.join(wrong) or 'none'}
Revealed: "{revealed}"
Hint level: {hint_number}/3
Instructions: {hint_levels[hint_number]}
Respond with ONLY the hint — 1-2 sentences. No preamble."""
    try:
        response = client.chat.completions.create(
            model=MODEL, max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Hint unavailable: {e}"

def get_fun_fact(word, category, won):
    client = get_groq_client()
    outcome = "won and correctly guessed" if won else "lost and failed to guess"
    prompt = f"""The player just {outcome} the word "{word}" (category: {category}) in Hangman.
Write a single fun, surprising sentence about "{word}". Be enthusiastic but brief. No "Did you know" openers."""
    try:
        response = client.chat.completions.create(
            model=MODEL, max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except:
        return "Great game!"

# ── Hangman drawing ───────────────────────────────────────────────────────────
def draw_hangman(n):
    stages = [
"""
  +---+
  |   |
      |
      |
      |
      |
=========""","""
  +---+
  |   |
  O   |
      |
      |
      |
=========""","""
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""","""
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""","""
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========""","""
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========""","""
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
========="""
    ]
    return stages[min(n, 6)]

# ── Word display ──────────────────────────────────────────────────────────────
def render_word():
    word = st.session_state.word
    guessed = st.session_state.guessed
    game_over = st.session_state.game_over
    won = st.session_state.won
    html = '<div class="word-display">'
    for ch in word:
        if ch in guessed:
            html += f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px"><div class="letter-char">{ch.upper()}</div><div class="letter-line"></div></div>'
        elif game_over and not won:
            html += f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px"><div class="letter-wrong">{ch.upper()}</div><div class="letter-line"></div></div>'
        else:
            html += f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px"><div class="letter-blank">_</div><div class="letter-line"></div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ── Check win/lose ────────────────────────────────────────────────────────────
def check_game():
    word = st.session_state.word
    if all(ch in st.session_state.guessed for ch in word):
        st.session_state.game_over = True
        st.session_state.won = True
        st.session_state.fun_fact = get_fun_fact(word, st.session_state.category, True)
    elif len(st.session_state.wrong) >= MAX_WRONG:
        st.session_state.game_over = True
        st.session_state.won = False
        st.session_state.fun_fact = get_fun_fact(word, st.session_state.category, False)

# ── UI ────────────────────────────────────────────────────────────────────────
col_title, col_cat = st.columns([3, 1])
with col_title:
    st.markdown("<h1>HANG<span style='color:#f0f0f0'>MAN</span></h1>", unsafe_allow_html=True)
with col_cat:
    st.markdown(f'<div class="category-tag">📂 {st.session_state.category.upper()}</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

left, right = st.columns([1, 1.5])

with left:
    st.code(draw_hangman(len(st.session_state.wrong)), language=None)
    st.markdown(f"**WRONG: {len(st.session_state.wrong)}/{MAX_WRONG}**")
    if st.session_state.wrong:
        wrong_str = "  ".join([l.upper() for l in st.session_state.wrong])
        st.markdown(f'<div class="wrong-letters-box">✗  {wrong_str}</div>', unsafe_allow_html=True)

with right:
    render_word()
    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.game_over:
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        rows = [alphabet[:13], alphabet[13:]]
        for row in rows:
            cols = st.columns(len(row))
            for i, letter in enumerate(row):
                with cols[i]:
                    already_guessed = letter in st.session_state.guessed
                    if st.button(letter.upper(), key=f"key_{letter}", disabled=already_guessed):
                        st.session_state.guessed.add(letter)
                        if letter not in st.session_state.word:
                            st.session_state.wrong.append(letter)
                        check_game()
                        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**🤖 AI Hints**")
    hint_count = st.session_state.hint_count
    st.markdown("🔵" * hint_count + "⚪" * (3 - hint_count))

    for h in st.session_state.hints:
        st.markdown(f'<div class="hint-box">"{h}"</div>', unsafe_allow_html=True)

    if not st.session_state.game_over and hint_count < 3:
        if st.button(f"💡 Get Hint {hint_count + 1}/3", key="hint_btn"):
            with st.spinner("Thinking..."):
                hint = get_hint(hint_count + 1)
                st.session_state.hint_count += 1
                st.session_state.hints.append(hint)
                st.rerun()
    elif hint_count >= 3:
        st.markdown("*No hints left!*")

# ── Game Over ─────────────────────────────────────────────────────────────────
if st.session_state.game_over:
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.session_state.won:
        st.markdown('<div class="win-box">🎉 YOU WIN!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="lose-box">💀 GAME OVER<br><span style="font-size:1.2rem;color:#f0f0f0">The word was: {st.session_state.word.upper()}</span></div>', unsafe_allow_html=True)
    if st.session_state.fun_fact:
        st.markdown(f'<div class="fact-box">💡 {st.session_state.fun_fact}</div>', unsafe_allow_html=True)
    if st.button("↺ Play Again", key="play_again"):
        init_game()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
if st.button("↺ New Game", key="new_game"):
    init_game()
    st.rerun()
