import subprocess, sys
try:
    from groq import Groq
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "groq"])
    from groq import Groq

import streamlit as st
import random, os
from collections import defaultdict

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Hangman AI — BAD402", page_icon="🧠", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');
*, *::before, *::after { box-sizing: border-box; }
body, .stApp { background-color: #0a0a0f !important; color: #e8e8f0 !important; font-family: 'Space Mono', monospace !important; }
#MainMenu, footer, header { visibility: hidden; }
h1 { font-family:'Bebas Neue',sans-serif !important; font-size:3.5rem !important; color:#e8ff47 !important;
     text-shadow:3px 3px 0 #5a6200,6px 6px 0 #2a2e00; letter-spacing:0.08em; margin:0 !important; line-height:1 !important; }
h2,h3 { font-family:'Bebas Neue',sans-serif !important; color:#e8e8f0 !important; letter-spacing:0.06em; }
.subtitle { font-size:0.62rem; letter-spacing:0.25em; color:#47c8ff; text-transform:uppercase; margin-bottom:2px; }
.badge { display:inline-block; background:#1a1a2e; border:1px solid #47c8ff; color:#47c8ff;
         padding:3px 12px; border-radius:2px; font-size:0.62rem; letter-spacing:0.2em; text-transform:uppercase; }
.badge-yellow { border-color:#e8ff47 !important; color:#e8ff47 !important; }
.badge-red    { border-color:#ff4757 !important; color:#ff4757 !important; }
.badge-green  { border-color:#47ff8a !important; color:#47ff8a !important; }
.badge-purple { border-color:#c084fc !important; color:#c084fc !important; }
hr { border:none; border-top:1px solid #1e1e2e !important; margin:10px 0 !important; }

/* Word display */
.word-wrap { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; padding:22px 16px;
             background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; min-height:90px; align-items:flex-end; margin:10px 0; }
.lslot { display:flex; flex-direction:column; align-items:center; gap:4px; }
.lchar { font-family:'Bebas Neue',sans-serif; font-size:2.6rem; min-width:28px; text-align:center; line-height:1; }
.lchar.found  { color:#e8ff47; }
.lchar.blank  { color:#2a2a3a; }
.lline { width:28px; height:2px; background:#2a2a3a; border-radius:1px; }

/* AI Thinking box */
.think-box { background:#0a1020; border:1px solid #1e3a5a; border-left:4px solid #47c8ff;
             border-radius:0 6px 6px 0; padding:14px 18px; margin:8px 0; }
.think-title { font-size:0.6rem; letter-spacing:0.2em; color:#47c8ff; text-transform:uppercase; margin-bottom:6px; }
.think-text  { font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#c8d8f0; line-height:1.7; }

/* Prob bars */
.bayes-panel { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; padding:14px; margin:8px 0; }
.bayes-title { font-size:0.6rem; letter-spacing:0.2em; text-transform:uppercase; color:#c084fc; margin-bottom:10px; }
.prob-row { display:flex; align-items:center; gap:8px; margin:5px 0; }
.prob-letter { font-family:'Bebas Neue',sans-serif; font-size:1.1rem; width:20px; }
.prob-bar-bg { flex:1; background:#1a1a2e; border-radius:2px; height:10px; overflow:hidden; }
.prob-bar    { height:10px; border-radius:2px; transition:width .5s ease; }
.prob-val    { font-size:0.62rem; color:#6b6b80; width:42px; text-align:right; }

/* Log */
.log-panel { background:#060610; border:1px solid #1e1e2e; border-radius:6px; padding:14px;
             font-family:'JetBrains Mono',monospace; font-size:0.7rem; max-height:350px; overflow-y:auto; }
.log-entry { padding:4px 0; border-bottom:1px solid #0f0f1a; line-height:1.5; }
.log-time  { color:#3a3a5a; margin-right:8px; }
.c-info { color:#47c8ff; } .c-good { color:#47ff8a; } .c-bad { color:#ff4757; }
.c-warn { color:#e8ff47; } .c-math { color:#c084fc; } .c-ai { color:#ff9f43; }

/* Gallows */
.gallows-wrap { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; padding:16px; text-align:center; }

/* Score */
.score-box { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; padding:14px; text-align:center; margin:6px 0; }
.score-num { font-family:'Bebas Neue',sans-serif; font-size:2.8rem; line-height:1; }

/* Position grid */
.pos-grid { display:flex; flex-wrap:wrap; gap:6px; justify-content:center; padding:10px; background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; margin:8px 0; }
.pos-cell { width:38px; height:38px; border:1px solid #2a2a3a; border-radius:3px; display:flex; align-items:center; justify-content:center;
            font-family:'Bebas Neue',sans-serif; font-size:1.2rem; cursor:pointer; transition:all .15s; }
.pos-cell.selected { background:#1a3a1a; border-color:#47ff8a; color:#47ff8a; }
.pos-cell.unselected { color:#4a4a6a; }

/* Win/Lose */
.win-box  { background:#0a1f14; border:2px solid #47ff8a; border-radius:6px; padding:24px; text-align:center; margin:10px 0; }
.lose-box { background:#1a0508; border:2px solid #ff4757; border-radius:6px; padding:24px; text-align:center; margin:10px 0; }
.result-big { font-family:'Bebas Neue',sans-serif; font-size:3rem; letter-spacing:0.1em; line-height:1.1; }

/* Setup screen */
.setup-box { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:8px; padding:24px; margin:10px 0; }

.stButton > button {
    font-family:'Space Mono',monospace !important; font-size:0.68rem !important; font-weight:700 !important;
    letter-spacing:0.08em !important; text-transform:uppercase !important; border-radius:3px !important;
    background:#0f0f1a !important; border:1px solid #2a2a3a !important; color:#e8e8f0 !important;
    padding:8px 10px !important; transition:all .15s !important;
}
.stButton > button:hover:not(:disabled) { background:#e8ff47 !important; color:#0a0a0f !important; border-color:#e8ff47 !important; }
.stButton > button:disabled { opacity:0.2 !important; }
</style>
""", unsafe_allow_html=True)

# ── Word bank ─────────────────────────────────────────────────────────────────
WORD_BANK = {
    "animals":    ["elephant","giraffe","penguin","dolphin","crocodile","chameleon","platypus","armadillo","rhinoceros","hippopotamus","cheetah","flamingo","mongoose","porcupine","salamander"],
    "countries":  ["australia","zimbabwe","portugal","bangladesh","switzerland","mozambique","kazakhstan","india","azerbaijan","liechtenstein","argentina","cambodia","ethiopia","guatemala","indonesia"],
    "science":    ["photosynthesis","mitochondria","chromosome","electrolysis","thermodynamics","hypothesis","ecosystem","gravitational","bioluminescence","electromagnetic","catalysis","osmosis","neuroscience","radioactive","atmosphere"],
    "food":       ["biryani","noodles","croissant","momos","gulabjamun","jalebi","ratatouille","spaghetti","quesadilla","bruschetta","dumplings","enchilada","risotto","tiramisu","gazpacho"],
    "technology": ["algorithm","blockchain","encryption","kubernetes","javascript","cybersecurity","bandwidth","semiconductor","repository","virtualization","recursion","microprocessor","hyperparameter","defragmentation","authentication"]
}
ALL_WORDS = [w for words in WORD_BANK.values() for w in words]
MAX_WRONG = 6
MODEL = "llama-3.3-70b-versatile"

# ── English letter frequency prior ───────────────────────────────────────────
LETTER_FREQ = {
    'e':12.7,'t':9.1,'a':8.2,'o':7.5,'i':7.0,'n':6.7,'s':6.3,'h':6.1,
    'r':6.0,'d':4.3,'l':4.0,'c':2.8,'u':2.8,'m':2.4,'w':2.4,'f':2.2,
    'g':2.0,'y':2.0,'p':1.9,'b':1.5,'v':1.0,'k':0.8,'j':0.2,'x':0.2,
    'q':0.1,'z':0.1
}

# ── Bayesian Engine ───────────────────────────────────────────────────────────
def get_possible_words(length, correct_positions, wrong_letters, correct_letters):
    """Filter word pool based on all constraints."""
    possible = []
    for w in ALL_WORDS:
        if len(w) != length:
            continue
        if any(ch in w for ch in wrong_letters):
            continue
        match = True
        for i, ch in correct_positions.items():
            if i >= len(w) or w[i] != ch:
                match = False
                break
        if not match:
            continue
        if any(ch not in w for ch in correct_letters):
            continue
        possible.append(w)
    return possible if possible else []

def bayesian_probabilities(length, correct_positions, wrong_letters, correct_letters, guessed_letters):
    possible = get_possible_words(length, correct_positions, wrong_letters, correct_letters)
    unguessed = [ch for ch in 'abcdefghijklmnopqrstuvwxyz' if ch not in guessed_letters]

    letter_counts = defaultdict(int)
    for w in possible:
        for ch in set(w):
            if ch in unguessed:
                letter_counts[ch] += 1

    total = len(possible)
    raw = {}
    for ch in unguessed:
        likelihood = letter_counts[ch] / total if total > 0 else 0
        prior = LETTER_FREQ.get(ch, 0.1) / 100
        raw[ch] = likelihood * prior

    s = sum(raw.values()) or 1
    probs = {ch: v/s for ch, v in raw.items()}
    return probs, possible, letter_counts, total

# ── Logging ───────────────────────────────────────────────────────────────────
def add_log(msg, level="info"):
    if "logs" not in st.session_state:
        st.session_state.logs = []
    css_map = {"info":"c-info","good":"c-good","bad":"c-bad","warn":"c-warn","math":"c-math","ai":"c-ai"}
    icon_map = {"info":"ℹ","good":"✓","bad":"✗","warn":"▲","math":"∑","ai":"🤖"}
    st.session_state.logs.append({
        "msg": msg, "css": css_map.get(level,"c-info"),
        "icon": icon_map.get(level,"ℹ"),
        "turn": st.session_state.get("turn",0)
    })

# ── Groq AI reasoning ────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        api_key = os.environ.get("GROQ_API_KEY","")
    return Groq(api_key=api_key)

def ai_reasoning(letter, prob, possible_count, wrong_letters, correct_positions, pattern):
    prompt = f"""You are an AI playing Hangman using Bayesian strategy (BAD402 AI course).
You just decided to guess the letter '{letter.upper()}'.
- Bayesian probability for this letter: {prob*100:.1f}%
- Possible words remaining: {possible_count}
- Wrong guesses so far: {', '.join(wrong_letters) if wrong_letters else 'none'}
- Current pattern: {pattern}

In 2 sentences max, explain your Bayesian reasoning for choosing '{letter.upper()}'. 
Mention probability, prior (letter frequency), and likelihood (word corpus). Be concise and technical."""
    try:
        r = get_groq_client().chat.completions.create(
            model=MODEL, max_tokens=100,
            messages=[{"role":"user","content":prompt}]
        )
        return r.choices[0].message.content.strip()
    except:
        return f"Chose '{letter.upper()}' with {prob*100:.1f}% posterior probability based on Bayesian update."

def ai_win_message(word, guesses_taken):
    prompt = f"""You are an AI that just won Hangman by guessing the word "{word}" in {guesses_taken} wrong guesses.
Write one triumphant sentence about your Bayesian strategy success. Be brief and fun."""
    try:
        r = get_groq_client().chat.completions.create(
            model=MODEL, max_tokens=60,
            messages=[{"role":"user","content":prompt}]
        )
        return r.choices[0].message.content.strip()
    except:
        return f"Bayesian strategy succeeded! Cracked '{word.upper()}' with {guesses_taken} wrong guesses."

def ai_lose_message(word):
    prompt = f"""You are an AI that just lost Hangman. The word was "{word}" and you couldn't guess it in 6 tries.
Write one humble sentence admitting defeat and mentioning what went wrong statistically. Be brief."""
    try:
        r = get_groq_client().chat.completions.create(
            model=MODEL, max_tokens=60,
            messages=[{"role":"user","content":prompt}]
        )
        return r.choices[0].message.content.strip()
    except:
        return f"The word '{word.upper()}' defeated my Bayesian model this time!"

# ── Hangman SVG ───────────────────────────────────────────────────────────────
def hangman_svg(n):
    parts = [
        '<circle cx="140" cy="62" r="16" stroke="#ff4757" stroke-width="3" fill="none"/>',
        '<line x1="140" y1="78" x2="140" y2="138" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
        '<line x1="140" y1="98" x2="114" y2="122" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
        '<line x1="140" y1="98" x2="166" y2="122" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
        '<line x1="140" y1="138" x2="114" y2="170" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
        '<line x1="140" y1="138" x2="166" y2="170" stroke="#ff4757" stroke-width="3" stroke-linecap="round"/>',
    ]
    scaffold = '''<line x1="30" y1="210" x2="190" y2="210" stroke="#2a2a3a" stroke-width="4" stroke-linecap="round"/>
        <line x1="68" y1="210" x2="68" y2="18" stroke="#2a2a3a" stroke-width="4" stroke-linecap="round"/>
        <line x1="68" y1="18" x2="140" y2="18" stroke="#2a2a3a" stroke-width="4" stroke-linecap="round"/>
        <line x1="140" y1="18" x2="140" y2="46" stroke="#2a2a3a" stroke-width="4" stroke-linecap="round"/>'''
    return f'<svg viewBox="0 0 220 225" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:190px">{"".join([scaffold]+parts[:n])}</svg>'

# ── Word display ──────────────────────────────────────────────────────────────
def word_html(length, correct_positions):
    html = '<div class="word-wrap">'
    for i in range(length):
        ch = correct_positions.get(i, None)
        if ch:
            html += f'<div class="lslot"><div class="lchar found">{ch.upper()}</div><div class="lline"></div></div>'
        else:
            html += f'<div class="lslot"><div class="lchar blank">_</div><div class="lline"></div></div>'
    html += '</div>'
    return html

def pattern_str(length, correct_positions):
    return " ".join([correct_positions.get(i,"_") for i in range(length)])

# ── Probability bars ──────────────────────────────────────────────────────────
def prob_bars_html(probs, top_n=10):
    if not probs:
        return "<p style='color:#3a3a5a;font-size:0.75rem;padding:10px'>Waiting for first guess...</p>"
    top = sorted(probs.items(), key=lambda x: -x[1])[:top_n]
    mx = top[0][1] if top and top[0][1] > 0 else 1
    html = '<div class="bayes-panel"><div class="bayes-title">∑ Posterior Probabilities P(L|Evidence)</div>'
    for letter, prob in top:
        pct = (prob/mx)*100 if mx > 0 else 0
        val = f"{prob*100:.1f}%"
        color = "#47ff8a" if pct>70 else "#47c8ff" if pct>40 else "#e8ff47" if pct>20 else "#ff9f43"
        is_best = letter == top[0][0]
        style = "font-weight:bold;" if is_best else ""
        html += f'''<div class="prob-row">
            <div class="prob-letter" style="color:{color};{style}">{letter.upper()}</div>
            <div class="prob-bar-bg"><div class="prob-bar" style="width:{pct:.1f}%;background:{color}"></div></div>
            <div class="prob-val">{val}</div>
        </div>'''
    html += '</div>'
    return html

# ── Log HTML ──────────────────────────────────────────────────────────────────
def log_html():
    logs = st.session_state.get("logs",[])
    if not logs:
        return '<div class="log-panel"><span style="color:#3a3a5a">Waiting for game to start...</span></div>'
    html = '<div class="log-panel">'
    for entry in reversed(logs[-50:]):
        html += f'<div class="log-entry"><span class="log-time">[T{entry["turn"]:02d}]</span><span class="{entry["css"]}">{entry["icon"]} {entry["msg"]}</span></div>'
    html += '</div>'
    return html

# ── Init / Reset ──────────────────────────────────────────────────────────────
def init_setup():
    st.session_state.update({
        "phase": "setup",          # setup → playing → result
        "secret_word": "",
        "word_length": 0,
        "correct_positions": {},   # {index: letter}
        "correct_letters": set(),  # letters confirmed in word
        "wrong_letters": [],
        "guessed_letters": set(),
        "turn": 0,
        "logs": [],
        "probs": {},
        "possible_count": len(ALL_WORDS),
        "current_guess": None,
        "ai_reasoning_text": "",
        "game_result": None,       # "ai_win" | "ai_lose" | "human_win"
        "result_message": "",
        "score_ai": st.session_state.get("score_ai", 0),
        "score_you": st.session_state.get("score_you", 0),
        "total_games": st.session_state.get("total_games", 0),
        "waiting_response": False,
    })

def start_playing(word_length):
    st.session_state.phase = "playing"
    st.session_state.word_length = word_length
    add_log(f"Game started! Secret word has {word_length} letters", "info")
    add_log(f"Prior: English letter frequency distribution loaded", "math")
    add_log(f"Word corpus: {len(ALL_WORDS)} candidate words available", "math")
    add_log(f"Bayesian model initialised. AI begins guessing...", "ai")
    run_bayes_and_guess()

def run_bayes_and_guess():
    length = st.session_state.word_length
    cp = st.session_state.correct_positions
    wl = st.session_state.wrong_letters
    cl = st.session_state.correct_letters
    gl = st.session_state.guessed_letters

    probs, possible, letter_counts, total = bayesian_probabilities(length, cp, wl, cl, gl)
    st.session_state.probs = probs
    st.session_state.possible_count = total

    if not probs:
        st.session_state.current_guess = None
        return

    best = max(probs, key=probs.get)
    best_prob = probs[best]
    st.session_state.current_guess = best

    pat = pattern_str(length, cp)
    add_log(f"Bayesian update complete — {total} possible words remain", "math")
    add_log(f"Top candidate: '{best.upper()}' with P={best_prob*100:.1f}%", "math")

    # Get AI reasoning from Groq
    reasoning = ai_reasoning(best, best_prob, total, wl, cp, pat)
    st.session_state.ai_reasoning_text = reasoning
    add_log(f"AI: {reasoning}", "ai")

    st.session_state.turn += 1
    st.session_state.guessed_letters.add(best)
    st.session_state.waiting_response = True

def process_response(is_correct, positions_with_letter=None):
    letter = st.session_state.current_guess
    if is_correct and positions_with_letter:
        for pos in positions_with_letter:
            st.session_state.correct_positions[pos] = letter
        st.session_state.correct_letters.add(letter)
        add_log(f"Response: '{letter.upper()}' is CORRECT at positions {[p+1 for p in positions_with_letter]}", "good")

        # Check win
        if len(st.session_state.correct_positions) == st.session_state.word_length:
            word = "".join(st.session_state.correct_positions.get(i,"_") for i in range(st.session_state.word_length))
            add_log(f"🎉 AI guessed the word: {word.upper()}!", "good")
            msg = ai_win_message(word, len(st.session_state.wrong_letters))
            st.session_state.result_message = msg
            st.session_state.game_result = "ai_win"
            st.session_state.score_ai += 1
            st.session_state.total_games += 1
            st.session_state.phase = "result"
        else:
            st.session_state.waiting_response = False
            run_bayes_and_guess()
    else:
        st.session_state.wrong_letters.append(letter)
        add_log(f"Response: '{letter.upper()}' is WRONG — not in word", "bad")
        add_log(f"Eliminating all words containing '{letter.upper()}' from pool", "math")

        if len(st.session_state.wrong_letters) >= MAX_WRONG:
            add_log("AI has used all 6 guesses. YOU WIN! 🎉", "warn")
            msg = ai_lose_message(st.session_state.secret_word or "unknown")
            st.session_state.result_message = msg
            st.session_state.game_result = "human_win"
            st.session_state.score_you += 1
            st.session_state.total_games += 1
            st.session_state.phase = "result"
        else:
            st.session_state.waiting_response = False
            run_bayes_and_guess()

# ── Init session ──────────────────────────────────────────────────────────────
if "phase" not in st.session_state:
    st.session_state.score_ai = 0
    st.session_state.score_you = 0
    st.session_state.total_games = 0
    init_setup()

# ══════════════════════════════════════════════════════════════════════════════
# ── HEADER ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns([2.5, 1, 1, 1])
with c1:
    st.markdown("<div class='subtitle'>Bayesian Strategy</div>", unsafe_allow_html=True)
    st.markdown("<h1>AI HANGMAN</h1>", unsafe_allow_html=True)
with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='score-box'><div style='font-size:0.55rem;letter-spacing:0.2em;color:#ff4757;text-transform:uppercase'>🤖 AI Score</div><div class='score-num' style='color:#ff4757'>{st.session_state.score_ai}</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='score-box'><div style='font-size:0.55rem;letter-spacing:0.2em;color:#47ff8a;text-transform:uppercase'>👤 Your Score</div><div class='score-num' style='color:#47ff8a'>{st.session_state.score_you}</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='score-box'><div style='font-size:0.55rem;letter-spacing:0.2em;color:#6b6b80;text-transform:uppercase'>Games</div><div class='score-num' style='color:#6b6b80'>{st.session_state.total_games}</div></div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE: SETUP
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.phase == "setup":
    lc, rc = st.columns([1.2, 1])
    with lc:
        st.markdown("### 🧠 HOW TO PLAY")
        st.markdown("""<div class='setup-box'>
        <p style='color:#47c8ff;font-size:0.8rem;line-height:1.9'>
        <b style='color:#e8ff47'>You</b> are the Word Setter.<br>
        <b style='color:#ff4757'>AI</b> is the Guesser using Bayesian strategy.<br><br>
        <b>Step 1</b> — Think of a secret word and enter its length below<br>
        <b>Step 2</b> — AI guesses letters one by one<br>
        <b>Step 3</b> — You respond ✅ YES or ❌ NO<br>
        <b>Step 4</b> — If YES, mark which positions the letter appears<br>
        <b>Step 5</b> — AI wins in ≤6 wrong guesses, You win if AI fails!<br><br>
        <span style='color:#c084fc'>Watch the Bayesian probabilities update live after every guess!</span>
        </p></div>""", unsafe_allow_html=True)

        st.markdown("### OR — Let the game pick a word")
        cat = st.selectbox("Pick a category (AI won't know which word):", ["— I'll think of my own —"] + list(WORD_BANK.keys()))
        if cat != "— I'll think of my own —":
            if st.button("🎲 Random Word from Category", key="rand_word"):
                word = random.choice(WORD_BANK[cat])
                st.session_state.secret_word = word
                start_playing(len(word))
                st.rerun()

    with rc:
        st.markdown("### 📝 ENTER YOUR WORD LENGTH")
        st.markdown("<div class='setup-box'>", unsafe_allow_html=True)
        word_input = st.text_input("Type your secret word here (only you can see it):", type="password", key="word_input_field")
        if word_input:
            word_input = word_input.lower().strip()
            if word_input.isalpha() and len(word_input) >= 3:
                st.markdown(f"<span class='badge badge-green'>✓ Word accepted — {len(word_input)} letters</span>", unsafe_allow_html=True)
                if st.button("🚀 START — Let AI Guess!", key="start_btn"):
                    st.session_state.secret_word = word_input
                    start_playing(len(word_input))
                    st.rerun()
            else:
                st.markdown("<span class='badge badge-red'>⚠ Min 3 letters, alphabets only</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 🎓Strategy Used")
        st.markdown("""<div style='background:#0f0f1a;border:1px solid #2a1a4a;border-radius:4px;padding:14px;font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#c084fc;line-height:1.9'>
            P(L | E) ∝ P(E | L) × P(L)<br>
            <span style='color:#6b6b80'>L = Letter being considered</span><br>
            <span style='color:#6b6b80'>E = Revealed pattern evidence</span><br>
            <span style='color:#6b6b80'>P(L) = English letter frequency prior</span><br>
            <span style='color:#6b6b80'>P(E|L) = Likelihood from word corpus</span>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE: PLAYING
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "playing":
    left, mid, right = st.columns([1, 1.5, 1.2])

    with left:
        # Gallows
        st.markdown("<div class='gallows-wrap'>" + hangman_svg(len(st.session_state.wrong_letters)) + "</div>", unsafe_allow_html=True)
        wrong_count = len(st.session_state.wrong_letters)
        color = "green" if wrong_count < 2 else "yellow" if wrong_count < 4 else "red"
        st.markdown(f"<div style='text-align:center;margin-top:6px'><span class='badge badge-{color}'>WRONG: {wrong_count}/{MAX_WRONG}</span></div>", unsafe_allow_html=True)

        if st.session_state.wrong_letters:
            wl = "  ".join(l.upper() for l in st.session_state.wrong_letters)
            st.markdown(f"<div style='background:#1a0508;border:1px solid #ff4757;border-radius:4px;padding:8px 12px;color:#ff4757;font-size:0.8rem;margin-top:8px;letter-spacing:0.15em;text-align:center'>✗  {wl}</div>", unsafe_allow_html=True)

        st.markdown(f"""<div style='background:#0f0f1a;border:1px solid #1e1e2e;border-radius:4px;padding:10px;margin-top:8px;text-align:center'>
            <div style='font-size:0.58rem;letter-spacing:0.2em;color:#6b6b80;text-transform:uppercase'>Possible Words</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:2.2rem;color:#47c8ff'>{st.session_state.possible_count}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↺ New Game", key="new_game"):
            init_setup()
            st.rerun()

    with mid:
        st.markdown(word_html(st.session_state.word_length, st.session_state.correct_positions), unsafe_allow_html=True)

        # AI guess display + response buttons
        if st.session_state.current_guess and st.session_state.waiting_response:
            letter = st.session_state.current_guess
            prob = st.session_state.probs.get(letter, 0)

            st.markdown(f"""<div style='background:#0a1020;border:2px solid #47c8ff;border-radius:6px;padding:18px;text-align:center;margin:12px 0'>
                <div style='font-size:0.6rem;letter-spacing:0.2em;color:#47c8ff;text-transform:uppercase'>🤖 AI Guesses</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:5rem;color:#e8ff47;line-height:1'>{letter.upper()}</div>
                <div style='font-size:0.72rem;color:#c084fc'>Bayesian Probability: <b>{prob*100:.1f}%</b></div>
            </div>""", unsafe_allow_html=True)

            # AI reasoning
            if st.session_state.ai_reasoning_text:
                st.markdown(f'<div class="think-box"><div class="think-title">🧠 AI Reasoning</div><div class="think-text">{st.session_state.ai_reasoning_text}</div></div>', unsafe_allow_html=True)

            st.markdown("**Is the letter present in your word?**")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button(f"✅ YES — '{letter.upper()}' is in my word", key="yes_btn"):
                    st.session_state._pending_yes = True
                    st.rerun()
            with col_no:
                if st.button(f"❌ NO — '{letter.upper()}' is NOT in my word", key="no_btn"):
                    process_response(False)
                    st.rerun()

            # Position selector (shown after YES)
            if st.session_state.get("_pending_yes"):
                length = st.session_state.word_length
                st.markdown(f"**Select positions where '{letter.upper()}' appears (position 1 = first letter):**")

                if "selected_positions" not in st.session_state:
                    st.session_state.selected_positions = []

                pos_cols = st.columns(min(length, 10))
                for i in range(length):
                    with pos_cols[i % min(length, 10)]:
                        already = i in st.session_state.correct_positions
                        sel = i in st.session_state.selected_positions
                        label = f"[{i+1}]" if sel else f"{i+1}"
                        if st.button(label, key=f"pos_{i}", disabled=already):
                            if i in st.session_state.selected_positions:
                                st.session_state.selected_positions.remove(i)
                            else:
                                st.session_state.selected_positions.append(i)
                            st.rerun()

                if st.session_state.selected_positions:
                    sel_str = ", ".join(str(p+1) for p in sorted(st.session_state.selected_positions))
                    st.markdown(f"<span class='badge badge-green'>Selected positions: {sel_str}</span>", unsafe_allow_html=True)
                    if st.button("✅ Confirm Positions", key="confirm_pos"):
                        positions = st.session_state.selected_positions[:]
                        del st.session_state.selected_positions
                        del st.session_state._pending_yes
                        process_response(True, positions)
                        st.rerun()

        elif not st.session_state.waiting_response and not st.session_state.game_result:
            st.markdown("<div style='text-align:center;padding:20px;color:#6b6b80'>⏳ AI is thinking...</div>", unsafe_allow_html=True)

        # Guessed letters
        if st.session_state.guessed_letters:
            st.markdown("<hr>", unsafe_allow_html=True)
            guessed_str = "  ".join(sorted(l.upper() for l in st.session_state.guessed_letters))
            st.markdown(f"<div style='font-size:0.62rem;letter-spacing:0.15em;color:#6b6b80'>ALL GUESSES: {guessed_str}</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div style='font-size:0.62rem;letter-spacing:0.2em;color:#c084fc;text-transform:uppercase;margin-bottom:8px'>∑ Bayesian Analysis</div>", unsafe_allow_html=True)
        st.markdown("""<div style='background:#0f0f1a;border:1px solid #2a1a4a;border-radius:4px;padding:10px 12px;margin-bottom:8px;font-family:JetBrains Mono,monospace;font-size:0.68rem;color:#c084fc;line-height:1.8'>
            P(L|E) ∝ P(E|L) × P(L)<br>
            <span style='color:#6b6b80'>Prior: letter frequency</span><br>
            <span style='color:#6b6b80'>Likelihood: word corpus match</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(prob_bars_html(st.session_state.probs), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.62rem;letter-spacing:0.2em;color:#47c8ff;text-transform:uppercase;margin-bottom:6px'>📋 Strategy Log</div>", unsafe_allow_html=True)
        st.markdown(log_html(), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE: RESULT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "result":
    lc, rc = st.columns([1.5, 1])
    with lc:
        if st.session_state.game_result == "ai_win":
            word = "".join(st.session_state.correct_positions.get(i,"?") for i in range(st.session_state.word_length))
            st.markdown(f"""<div class='lose-box'>
                <div class='result-big' style='color:#ff4757'>🤖 AI WINS!</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:1.6rem;color:#e8ff47;letter-spacing:0.2em'>{word.upper()}</div>
                <div style='font-size:0.8rem;color:#ff9f43;margin-top:8px'>{st.session_state.result_message}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='win-box'>
                <div class='result-big' style='color:#47ff8a'>🎉 YOU WIN!</div>
                <div style='font-size:0.8rem;color:#47ff8a;margin-top:8px'>AI failed to guess your word in {MAX_WRONG} tries!</div>
                <div style='font-size:0.78rem;color:#6b6b80;margin-top:6px'>{st.session_state.result_message}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Play Again", key="play_again"):
                init_setup()
                st.rerun()
        with c2:
            if st.button("📊 See Full Log", key="see_log"):
                st.session_state.show_log = True

    with rc:
        st.markdown("<div style='font-size:0.62rem;letter-spacing:0.2em;color:#47c8ff;text-transform:uppercase;margin-bottom:6px'>📋 Strategy Log</div>", unsafe_allow_html=True)
        st.markdown(log_html(), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(prob_bars_html(st.session_state.probs), unsafe_allow_html=True)
