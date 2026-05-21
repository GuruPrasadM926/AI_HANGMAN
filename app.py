import subprocess, sys
try:
    from groq import Groq
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "groq"])
    from groq import Groq

import streamlit as st
import random, os, math
from collections import defaultdict

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Hangman AI — BAD402", page_icon="🧠", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

body, .stApp { background-color: #0a0a0f !important; color: #e8e8f0 !important; font-family: 'Space Mono', monospace !important; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

h1 { font-family:'Bebas Neue',sans-serif !important; font-size:3.8rem !important; color:#e8ff47 !important;
     text-shadow:3px 3px 0 #5a6200,6px 6px 0 #2a2e00; letter-spacing:0.08em; margin:0 !important; line-height:1 !important; }

.subtitle { font-size:0.65rem; letter-spacing:0.25em; color:#47c8ff; text-transform:uppercase; margin-bottom:4px; }

.badge { display:inline-block; background:#1a1a2e; border:1px solid #47c8ff; color:#47c8ff;
         padding:3px 12px; border-radius:2px; font-size:0.62rem; letter-spacing:0.2em; text-transform:uppercase; }

.badge-yellow { border-color:#e8ff47; color:#e8ff47; }
.badge-red    { border-color:#ff4757; color:#ff4757; }
.badge-green  { border-color:#47ff8a; color:#47ff8a; }

hr { border:none; border-top:1px solid #1e1e2e !important; margin:12px 0 !important; }

/* Word display */
.word-wrap { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; padding:20px 16px;
             background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; min-height:80px; align-items:flex-end; }
.lslot { display:flex; flex-direction:column; align-items:center; gap:3px; }
.lchar { font-family:'Bebas Neue',sans-serif; font-size:2.4rem; min-width:26px; text-align:center; line-height:1; }
.lchar.found  { color:#e8ff47; animation:popIn .3s ease; }
.lchar.blank  { color:#2a2a3a; }
.lchar.reveal { color:#ff4757; }
.lline { width:26px; height:2px; background:#2a2a3a; border-radius:1px; }

/* Keyboard */
.kb-row { display:flex; gap:4px; justify-content:center; margin:3px 0; }

/* Bayesian panel */
.bayes-panel { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; padding:14px; margin:8px 0; }
.bayes-title { font-size:0.62rem; letter-spacing:0.2em; text-transform:uppercase; color:#47c8ff; margin-bottom:10px; }
.prob-row { display:flex; align-items:center; gap:8px; margin:4px 0; }
.prob-letter { font-family:'Bebas Neue',sans-serif; font-size:1.1rem; color:#e8e8f0; width:18px; }
.prob-bar-wrap { flex:1; background:#1a1a2e; border-radius:2px; height:8px; overflow:hidden; }
.prob-bar { height:8px; border-radius:2px; transition:width .4s ease; }
.prob-val { font-size:0.62rem; color:#6b6b80; width:38px; text-align:right; }

/* Log panel */
.log-panel { background:#080810; border:1px solid #1e1e2e; border-radius:6px; padding:14px;
             font-family:'JetBrains Mono',monospace; font-size:0.72rem; max-height:320px; overflow-y:auto; }
.log-entry { padding:3px 0; border-bottom:1px solid #0f0f1a; line-height:1.5; }
.log-time  { color:#3a3a5a; margin-right:8px; }
.log-info  { color:#47c8ff; }
.log-good  { color:#47ff8a; }
.log-bad   { color:#ff4757; }
.log-warn  { color:#e8ff47; }
.log-math  { color:#c084fc; }

/* Hint box */
.hint-box { background:#0f0f1a; border-left:3px solid #47c8ff; padding:12px 16px;
            font-style:italic; color:#c8c8e0; font-size:0.82rem; line-height:1.7; margin:6px 0; border-radius:0 4px 4px 0; }

/* Game over */
.win-box  { background:#0a1f14; border:2px solid #47ff8a; border-radius:6px; padding:24px; text-align:center; }
.lose-box { background:#1a0508; border:2px solid #ff4757; border-radius:6px; padding:24px; text-align:center; }
.result-text { font-family:'Bebas Neue',sans-serif; font-size:3.5rem; letter-spacing:0.1em; line-height:1; }
.fact-box { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:4px; padding:14px 18px;
            font-style:italic; color:#6b6b80; font-size:0.8rem; line-height:1.7; text-align:center; margin:10px 0; }

/* Gallows */
.gallows-wrap { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; padding:16px; text-align:center; }

@keyframes popIn { from{transform:scale(.5);opacity:0} to{transform:scale(1);opacity:1} }

/* Button overrides */
.stButton > button {
    font-family:'Space Mono',monospace !important; font-size:0.68rem !important;
    font-weight:700 !important; letter-spacing:0.08em !important; text-transform:uppercase !important;
    border-radius:3px !important; transition:all .15s ease !important;
    background:#0f0f1a !important; border:1px solid #2a2a3a !important; color:#e8e8f0 !important;
    padding:6px 4px !important;
}
.stButton > button:hover { background:#e8ff47 !important; color:#0a0a0f !important; border-color:#e8ff47 !important; transform:translateY(-1px) !important; }
.stButton > button:disabled { opacity:0.2 !important; transform:none !important; }
</style>
""", unsafe_allow_html=True)

# ── Word bank ─────────────────────────────────────────────────────────────────
WORD_BANK = {
    "animals":    ["elephant","giraffe","penguin","dolphin","crocodile","chameleon","platypus","armadillo","rhinoceros","hippopotamus"],
    "countries":  ["australia","zimbabwe","portugal","bangladesh","switzerland","mozambique","kazakhstan","india","azerbaijan","liechtenstein"],
    "science":    ["photosynthesis","mitochondria","chromosome","electrolysis","thermodynamics","hypothesis","ecosystem","gravitational","bioluminescence","electromagnetic"],
    "food":       ["biryani","noodles","friedrice","croissant","momos","gulabjamun","butternaan","jalebi","ratatouille","spaghetti"],
    "technology": ["algorithm","blockchain","encryption","kubernetes","javascript","cybersecurity","bandwidth","semiconductor","repository","virtualization"]
}
ALL_WORDS = [w for words in WORD_BANK.values() for w in words]
MAX_WRONG = 6
MODEL = "llama-3.3-70b-versatile"

# ── English letter frequency prior (Bayesian prior P(letter)) ─────────────────
LETTER_FREQ = {
    'e':12.7,'t':9.1,'a':8.2,'o':7.5,'i':7.0,'n':6.7,'s':6.3,'h':6.1,
    'r':6.0,'d':4.3,'l':4.0,'c':2.8,'u':2.8,'m':2.4,'w':2.4,'f':2.2,
    'g':2.0,'y':2.0,'p':1.9,'b':1.5,'v':1.0,'k':0.8,'j':0.2,'x':0.2,
    'q':0.1,'z':0.1
}

# ── Bayesian Engine ───────────────────────────────────────────────────────────
def get_possible_words(word, guessed):
    """Return all words consistent with current revealed pattern."""
    target_len = len(word)
    revealed = {i: ch for i, ch in enumerate(word) if ch in guessed}
    wrong = [ch for ch in guessed if ch not in word]
    possible = []
    for w in ALL_WORDS:
        if len(w) != target_len:
            continue
        if any(ch in w for ch in wrong):
            continue
        if any(w[i] != ch for i, ch in revealed.items()):
            continue
        possible.append(w)
    return possible if possible else ALL_WORDS

def bayesian_letter_probabilities(word, guessed):
    """
    Bayesian update:
    P(letter | evidence) ∝ P(evidence | letter) × P(letter)
    Evidence = current pattern of revealed/hidden letters
    Returns dict of letter -> probability (only unguessed letters)
    """
    possible_words = get_possible_words(word, guessed)
    unguessed = [ch for ch in 'abcdefghijklmnopqrstuvwxyz' if ch not in guessed]

    letter_counts = defaultdict(int)
    for w in possible_words:
        for ch in set(w):
            if ch in unguessed:
                letter_counts[ch] += 1

    total_words = len(possible_words)
    raw_probs = {}
    for ch in unguessed:
        likelihood = letter_counts[ch] / total_words if total_words > 0 else 0
        prior = LETTER_FREQ.get(ch, 0.1) / 100
        raw_probs[ch] = likelihood * prior

    total = sum(raw_probs.values()) or 1
    return {ch: v / total for ch, v in raw_probs.items()}, possible_words, letter_counts, total_words

def get_best_suggestion(word, guessed):
    probs, _, _, _ = bayesian_letter_probabilities(word, guessed)
    if not probs:
        return None
    return max(probs, key=probs.get)

# ── Bayesian Log ──────────────────────────────────────────────────────────────
def add_log(msg, level="info"):
    if "logs" not in st.session_state:
        st.session_state.logs = []
    icons = {"info":"ℹ️","good":"✅","bad":"❌","warn":"⚠️","math":"∑"}
    css   = {"info":"log-info","good":"log-good","bad":"log-bad","warn":"log-warn","math":"log-math"}
    st.session_state.logs.append({
        "msg": msg, "level": level,
        "icon": icons.get(level,"ℹ️"),
        "css": css.get(level,"log-info"),
        "turn": st.session_state.get("turn", 0)
    })

# ── Groq AI ───────────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        api_key = os.environ.get("GROQ_API_KEY","")
    return Groq(api_key=api_key)

def get_ai_hint(hint_number):
    client = get_groq_client()
    word, category = st.session_state.word, st.session_state.category
    guessed, wrong = list(st.session_state.guessed), st.session_state.wrong
    revealed = " ".join([ch if ch in st.session_state.guessed else "_" for ch in word])
    hint_levels = {
        1: "Give a vague, creative, poetic clue. Do NOT mention the word or its letters.",
        2: "Give a more specific clue — category, key property, or interesting fact. Don't reveal the word.",
        3: f"Give a strong structural hint using confirmed letters ({', '.join(guessed) or 'none'}). Don't say the word."
    }
    prompt = f"""Hangman hint-giver. Word:"{word}", Category:{category}, Pattern:"{revealed}", Hint level:{hint_number}/3.
Instructions: {hint_levels[hint_number]}
Respond with ONLY 1-2 sentences. No preamble."""
    try:
        r = get_groq_client().chat.completions.create(model=MODEL, max_tokens=120,
            messages=[{"role":"user","content":prompt}])
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"Hint unavailable: {e}"

def get_fun_fact(word, category, won):
    outcome = "won and guessed" if won else "lost on"
    prompt = f'Player just {outcome} "{word}" (category:{category}) in Hangman. One fun surprising fact about "{word}". No "Did you know" opener. Be brief.'
    try:
        r = get_groq_client().chat.completions.create(model=MODEL, max_tokens=80,
            messages=[{"role":"user","content":prompt}])
        return r.choices[0].message.content.strip()
    except:
        return ""

# ── Game init ─────────────────────────────────────────────────────────────────
def init_game():
    category = random.choice(list(WORD_BANK.keys()))
    word = random.choice(WORD_BANK[category])
    st.session_state.update({
        "word": word, "category": category,
        "guessed": set(), "wrong": [],
        "hint_count": 0, "hints": [],
        "game_over": False, "won": False,
        "fun_fact": "", "logs": [], "turn": 0,
        "bayes_probs": {}, "possible_count": len(ALL_WORDS),
        "suggestion": None
    })
    add_log(f"New game started — Category: {category.upper()}", "info")
    add_log(f"Word has {len(word)} letters", "info")
    add_log(f"Prior: Using English letter frequency as Bayesian prior P(letter)", "math")
    add_log(f"Possible word pool initialised — {len(ALL_WORDS)} candidates", "math")
    _run_bayes()

def _run_bayes():
    word = st.session_state.word
    guessed = st.session_state.guessed
    probs, possible, letter_counts, total = bayesian_letter_probabilities(word, guessed)
    st.session_state.bayes_probs = probs
    st.session_state.possible_count = total
    best = max(probs, key=probs.get) if probs else None
    st.session_state.suggestion = best
    return probs, possible, letter_counts, total

def check_game():
    word = st.session_state.word
    if all(ch in st.session_state.guessed for ch in word):
        st.session_state.game_over = True
        st.session_state.won = True
        st.session_state.fun_fact = get_fun_fact(word, st.session_state.category, True)
        add_log("🎉 Player guessed the word correctly!", "good")
    elif len(st.session_state.wrong) >= MAX_WRONG:
        st.session_state.game_over = True
        st.session_state.won = False
        st.session_state.fun_fact = get_fun_fact(word, st.session_state.category, False)
        add_log(f"💀 Game over. The word was: {word.upper()}", "bad")

# ── Hangman SVG ───────────────────────────────────────────────────────────────
def hangman_svg(n):
    parts = [
        '<circle cx="140" cy="65" r="18" stroke="#ff4757" stroke-width="3" fill="none"/>',
        '<line x1="140" y1="83" x2="140" y2="145" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
        '<line x1="140" y1="100" x2="112" y2="125" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
        '<line x1="140" y1="100" x2="168" y2="125" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
        '<line x1="140" y1="145" x2="112" y2="178" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
        '<line x1="140" y1="145" x2="168" y2="178" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
    ]
    scaffold = '''
        <line x1="30" y1="220" x2="200" y2="220" stroke="#2a2a3a" stroke-width="4" stroke-linecap="round"/>
        <line x1="70" y1="220" x2="70" y2="20" stroke="#2a2a3a" stroke-width="4" stroke-linecap="round"/>
        <line x1="70" y1="20" x2="140" y2="20" stroke="#2a2a3a" stroke-width="4" stroke-linecap="round"/>
        <line x1="140" y1="20" x2="140" y2="47" stroke="#2a2a3a" stroke-width="4" stroke-linecap="round"/>
    '''
    body = "".join(parts[:n])
    return f'<svg viewBox="0 0 230 240" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:200px">{scaffold}{body}</svg>'

# ── Word HTML ─────────────────────────────────────────────────────────────────
def word_html():
    word, guessed = st.session_state.word, st.session_state.guessed
    game_over, won = st.session_state.game_over, st.session_state.won
    html = '<div class="word-wrap">'
    for ch in word:
        if ch in guessed:
            cls = "found"
        elif game_over and not won:
            cls = "reveal"
        else:
            cls = "blank"
        disp = ch.upper() if (ch in guessed or (game_over and not won)) else "_"
        html += f'<div class="lslot"><div class="lchar {cls}">{disp}</div><div class="lline"></div></div>'
    html += '</div>'
    return html

# ── Probability bar HTML ──────────────────────────────────────────────────────
def prob_bars_html(probs, top_n=8):
    if not probs:
        return "<p style='color:#3a3a5a;font-size:0.75rem'>No data yet</p>"
    top = sorted(probs.items(), key=lambda x: -x[1])[:top_n]
    max_p = top[0][1] if top else 1
    html = '<div class="bayes-panel"><div class="bayes-title">📊 Bayesian Letter Probabilities — Top 8</div>'
    for letter, prob in top:
        pct = (prob / max_p) * 100
        val = f"{prob*100:.1f}%"
        color = "#47ff8a" if pct > 70 else "#47c8ff" if pct > 35 else "#e8ff47"
        html += f'''<div class="prob-row">
            <div class="prob-letter">{letter.upper()}</div>
            <div class="prob-bar-wrap"><div class="prob-bar" style="width:{pct:.1f}%;background:{color}"></div></div>
            <div class="prob-val">{val}</div>
        </div>'''
    html += '</div>'
    return html

# ── Log HTML ──────────────────────────────────────────────────────────────────
def log_html():
    logs = st.session_state.get("logs", [])
    if not logs:
        return '<div class="log-panel"><span style="color:#3a3a5a">No logs yet...</span></div>'
    html = '<div class="log-panel">'
    for i, entry in enumerate(reversed(logs[-40:])):
        html += f'<div class="log-entry"><span class="log-time">[T{entry["turn"]:02d}]</span><span class="{entry["css"]}">{entry["icon"]} {entry["msg"]}</span></div>'
    html += '</div>'
    return html

# ── Init ──────────────────────────────────────────────────────────────────────
if "word" not in st.session_state:
    init_game()

# ── HEADER ────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.markdown("<div class='subtitle'>VTU BAD402 — Artificial Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<h1>HANG<span style='color:#f0f0f0'>MAN</span></h1>", unsafe_allow_html=True)
with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<span class='badge'>📂 {st.session_state.category.upper()}</span>", unsafe_allow_html=True)
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    wrong = len(st.session_state.wrong)
    color = "green" if wrong < 3 else "warn" if wrong < 5 else "red"
    st.markdown(f"<span class='badge badge-{color}'>WRONG: {wrong}/{MAX_WRONG}</span>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── MAIN LAYOUT ───────────────────────────────────────────────────────────────
left_col, mid_col, right_col = st.columns([1, 1.4, 1.2])

# ── LEFT: Gallows + Wrong letters ────────────────────────────────────────────
with left_col:
    st.markdown("<div class='gallows-wrap'>" + hangman_svg(len(st.session_state.wrong)) + "</div>", unsafe_allow_html=True)

    if st.session_state.wrong:
        wrong_str = "  ".join(l.upper() for l in st.session_state.wrong)
        st.markdown(f"<div style='background:#1a0508;border:1px solid #ff4757;border-radius:4px;padding:8px 12px;color:#ff4757;font-size:0.8rem;margin-top:8px;letter-spacing:0.15em'>✗  {wrong_str}</div>", unsafe_allow_html=True)

    # Bayesian suggestion
    if st.session_state.suggestion and not st.session_state.game_over:
        st.markdown(f"""<div style='background:#0a1f14;border:1px solid #47ff8a;border-radius:4px;padding:10px 12px;margin-top:8px'>
            <div style='font-size:0.6rem;letter-spacing:0.2em;color:#47ff8a;text-transform:uppercase'>🧠 Bayesian Best Guess</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:2rem;color:#47ff8a'>{st.session_state.suggestion.upper()}</div>
            <div style='font-size:0.62rem;color:#3a6a4a'>Most probable next letter</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style='background:#0f0f1a;border:1px solid #1e1e2e;border-radius:4px;padding:10px 12px;margin-top:8px'>
        <div style='font-size:0.6rem;letter-spacing:0.2em;color:#6b6b80;text-transform:uppercase'>Possible Words Remaining</div>
        <div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;color:#47c8ff'>{st.session_state.possible_count}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺ New Game", key="new_game"):
        init_game()
        st.rerun()

# ── MIDDLE: Word + Keyboard + Hints ───────────────────────────────────────────
with mid_col:
    st.markdown(word_html(), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Keyboard
    if not st.session_state.game_over:
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for row in [alphabet[:13], alphabet[13:]]:
            cols = st.columns(len(row))
            for i, letter in enumerate(row):
                with cols[i]:
                    disabled = letter in st.session_state.guessed
                    if st.button(letter.upper(), key=f"k_{letter}", disabled=disabled):
                        st.session_state.turn += 1
                        st.session_state.guessed.add(letter)
                        probs, possible, letter_counts, total = _run_bayes()

                        if letter in st.session_state.word:
                            count = st.session_state.word.count(letter)
                            add_log(f"Guessed '{letter.upper()}' — CORRECT! Appears {count}x in word", "good")
                            add_log(f"Bayesian update: P({letter.upper()}|evidence) was {probs.get(letter,0)*100:.1f}% → confirmed", "math")
                        else:
                            st.session_state.wrong.append(letter)
                            add_log(f"Guessed '{letter.upper()}' — WRONG. Not in word.", "bad")
                            add_log(f"Posterior updated: eliminated words containing '{letter.upper()}'", "math")

                        add_log(f"Possible words remaining: {total} | Best next guess: {st.session_state.suggestion.upper() if st.session_state.suggestion else 'N/A'}", "info")
                        check_game()
                        st.rerun()

    # Hints
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.65rem;letter-spacing:0.2em;color:#47c8ff;text-transform:uppercase'>🤖 AI Hints (Groq)</div>", unsafe_allow_html=True)

    hint_count = st.session_state.hint_count
    st.markdown("🔵" * hint_count + "⚪" * (3 - hint_count))

    for h in st.session_state.hints:
        st.markdown(f'<div class="hint-box">"{h}"</div>', unsafe_allow_html=True)

    if not st.session_state.game_over and hint_count < 3:
        if st.button(f"💡 Get AI Hint {hint_count+1}/3", key="hint_btn"):
            with st.spinner("AI thinking..."):
                hint = get_ai_hint(hint_count + 1)
                st.session_state.hint_count += 1
                st.session_state.hints.append(hint)
                add_log(f"AI Hint {st.session_state.hint_count}/3 requested", "info")
                add_log(f"Hint: \"{hint[:60]}...\"" if len(hint) > 60 else f"Hint: \"{hint}\"", "warn")
                st.rerun()
    elif hint_count >= 3:
        st.markdown("<p style='color:#3a3a5a;font-size:0.75rem'>No hints remaining</p>", unsafe_allow_html=True)

    # Game Over
    if st.session_state.game_over:
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.session_state.won:
            st.markdown(f'<div class="win-box"><div class="result-text" style="color:#47ff8a">🎉 YOU WIN!</div><div style="color:#e8ff47;font-family:Bebas Neue,sans-serif;font-size:1.5rem;letter-spacing:0.2em">{st.session_state.word.upper()}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="lose-box"><div class="result-text" style="color:#ff4757">💀 GAME OVER</div><div style="color:#e8e8f0;font-family:Bebas Neue,sans-serif;font-size:1.2rem;letter-spacing:0.15em">WORD: {st.session_state.word.upper()}</div></div>', unsafe_allow_html=True)

        if st.session_state.fun_fact:
            st.markdown(f'<div class="fact-box">💡 {st.session_state.fun_fact}</div>', unsafe_allow_html=True)

        if st.button("↺ Play Again", key="play_again"):
            init_game()
            st.rerun()

# ── RIGHT: Bayesian Probabilities + Log ───────────────────────────────────────
with right_col:
    st.markdown("<div style='font-size:0.62rem;letter-spacing:0.2em;color:#c084fc;text-transform:uppercase;margin-bottom:6px'>∑ Bayesian Analysis — BAD402</div>", unsafe_allow_html=True)

    # Formula
    st.markdown("""<div style='background:#0f0f1a;border:1px solid #2a1a4a;border-radius:4px;padding:10px 12px;margin-bottom:8px;font-family:JetBrains Mono,monospace;font-size:0.68rem;color:#c084fc'>
        P(L|E) ∝ P(E|L) × P(L)<br>
        <span style='color:#6b6b80'>L = letter, E = revealed pattern</span><br>
        <span style='color:#6b6b80'>Prior P(L) = English letter freq</span><br>
        <span style='color:#6b6b80'>Likelihood P(E|L) = word corpus</span>
    </div>""", unsafe_allow_html=True)

    # Probability bars
    st.markdown(prob_bars_html(st.session_state.bayes_probs), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.62rem;letter-spacing:0.2em;color:#47c8ff;text-transform:uppercase;margin-bottom:6px'>📋 Strategy Log</div>", unsafe_allow_html=True)
    st.markdown(log_html(), unsafe_allow_html=True)
