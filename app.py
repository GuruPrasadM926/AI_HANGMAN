import subprocess, sys
try:
    from groq import Groq
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "groq"])
    from groq import Groq

import streamlit as st
import random, os
from collections import defaultdict

st.set_page_config(page_title="Hangman AI — BAD402", page_icon="🧠", layout="wide")

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
hr { border:none; border-top:1px solid #1e1e2e !important; margin:10px 0 !important; }
.word-wrap { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; padding:22px 16px;
             background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; min-height:90px; align-items:flex-end; margin:10px 0; }
.lslot { display:flex; flex-direction:column; align-items:center; gap:4px; }
.lchar { font-family:'Bebas Neue',sans-serif; font-size:2.6rem; min-width:28px; text-align:center; line-height:1; }
.lchar.found { color:#e8ff47; }
.lchar.blank { color:#2a2a3a; }
.lline { width:28px; height:2px; background:#2a2a3a; border-radius:1px; }
.think-box { background:#0a1020; border:1px solid #1e3a5a; border-left:4px solid #47c8ff; border-radius:0 6px 6px 0; padding:14px 18px; margin:8px 0; }
.think-title { font-size:0.6rem; letter-spacing:0.2em; color:#47c8ff; text-transform:uppercase; margin-bottom:6px; }
.think-text { font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#c8d8f0; line-height:1.7; }
.bayes-panel { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; padding:14px; margin:8px 0; }
.bayes-title { font-size:0.6rem; letter-spacing:0.2em; text-transform:uppercase; color:#c084fc; margin-bottom:10px; }
.prob-row { display:flex; align-items:center; gap:8px; margin:5px 0; }
.prob-letter { font-family:'Bebas Neue',sans-serif; font-size:1.1rem; width:20px; }
.prob-bar-bg { flex:1; background:#1a1a2e; border-radius:2px; height:10px; overflow:hidden; }
.prob-bar { height:10px; border-radius:2px; transition:width .5s ease; }
.prob-val { font-size:0.62rem; color:#6b6b80; width:42px; text-align:right; }
.log-panel { background:#060610; border:1px solid #1e1e2e; border-radius:6px; padding:14px;
             font-family:'JetBrains Mono',monospace; font-size:0.7rem; max-height:380px; overflow-y:auto; }
.log-entry { padding:4px 0; border-bottom:1px solid #0a0a15; line-height:1.5; }
.log-time { color:#3a3a5a; margin-right:8px; }
.c-info{color:#47c8ff;} .c-good{color:#47ff8a;} .c-bad{color:#ff4757;}
.c-warn{color:#e8ff47;} .c-math{color:#c084fc;} .c-ai{color:#ff9f43;}
.gallows-wrap { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; padding:16px; text-align:center; }
.score-box { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:6px; padding:14px; text-align:center; margin:6px 0; }
.score-num { font-family:'Bebas Neue',sans-serif; font-size:2.8rem; line-height:1; }
.win-box  { background:#0a1f14; border:2px solid #47ff8a; border-radius:6px; padding:24px; text-align:center; margin:10px 0; }
.lose-box { background:#1a0508; border:2px solid #ff4757; border-radius:6px; padding:24px; text-align:center; margin:10px 0; }
.result-big { font-family:'Bebas Neue',sans-serif; font-size:3rem; letter-spacing:0.1em; line-height:1.1; }
.setup-box { background:#0f0f1a; border:1px solid #1e1e2e; border-radius:8px; padding:20px; margin:10px 0; }
.stButton > button { font-family:'Space Mono',monospace !important; font-size:0.68rem !important; font-weight:700 !important;
    letter-spacing:0.08em !important; text-transform:uppercase !important; border-radius:3px !important;
    background:#0f0f1a !important; border:1px solid #2a2a3a !important; color:#e8e8f0 !important;
    padding:8px 10px !important; transition:all .15s !important; }
.stButton > button:hover:not(:disabled) { background:#e8ff47 !important; color:#0a0a0f !important; border-color:#e8ff47 !important; }
.stButton > button:disabled { opacity:0.2 !important; }
</style>
""", unsafe_allow_html=True)

# ── Massive word corpus — 400+ words across categories ───────────────────────
WORD_CORPUS = {
    "animals": [
        "ant","ape","bat","bee","cat","cod","cow","dog","doe","emu","fly","fox","gnu","hen","hog",
        "jay","koi","owl","pig","ram","rat","yak","bear","bird","buck","bull","carp","clam","colt",
        "crab","crow","dart","deer","dodo","dove","duck","fawn","flea","frog","gnat","goat","gull",
        "hare","hawk","ibis","kite","lamb","lark","lion","lynx","mink","mole","moth","mule","newt",
        "pony","puma","slug","snag","swan","toad","vole","wasp","wolf","worm","wren","zebra","bison",
        "cobra","crane","eagle","finch","gecko","goose","horse","hyena","koala","llama","macaw","moose",
        "mouse","otter","panda","parrot","quail","raven","shark","sheep","skunk","sloth","snail","snake",
        "squid","stork","tapir","tiger","trout","viper","whale","zebra","alpaca","badger","beagle",
        "beaver","canary","cheetah","condor","cougar","coyote","donkey","falcon","ferret","gibbon",
        "gopher","iguana","jaguar","lemur","lizard","marmot","monkey","osprey","pelican","pigeon",
        "rabbit","raccoon","salmon","scorpion","seagull","sparrow","spider","squirrel","starfish",
        "swallow","termite","turkey","turtle","vulture","walrus","weasel","buffalo","caribou",
        "chimpanzee","crocodile","elephant","flamingo","giraffe","gorilla","hamster","hedgehog",
        "hippopotamus","kangaroo","leopard","manatee","mongoose","narwhal","pangolin","penguin",
        "platypus","porcupine","rhinoceros","salamander","chameleon","armadillo","chimpanzee",
        "dolphin","lobster","octopus","opossum","peacock","pheasant","piranha","porpoise"
    ],
    "countries": [
        "chad","cuba","fiji","iran","iraq","laos","mali","niue","oman","peru","togo","china","egypt",
        "ghana","india","italy","japan","kenya","libya","malta","nepal","niger","qatar","spain","sudan",
        "syria","tonga","wales","yemen","angola","belize","bhutan","brazil","brunei","canada","cyprus",
        "france","greece","guinea","guyana","israel","jordan","kuwait","latvia","malawi","mexico",
        "monaco","norway","panama","poland","russia","rwanda","serbia","sweden","taiwan","turkey",
        "uganda","ukraine","albania","algeria","andorra","armenia","austria","bahamas","bahrain",
        "belarus","belgium","bolivia","croatia","denmark","ecuador","eritrea","estonia","finland",
        "georgia","germany","grenada","hungary","iceland","ireland","jamaica","lebanon","lesotho",
        "liberia","moldova","myanmar","namibia","nigeria","pakistan","romania","senegal","somalia",
        "tunisia","uruguay","vanuatu","vietnam","zambia","zimbabwe","cambodia","colombia","djibouti",
        "dominica","ethiopia","guatemala","honduras","indonesia","kiribati","malaysia","maldives",
        "mongolia","morocco","mozambique","nicaragua","paraguay","portugal","scotland","singapore",
        "slovakia","slovenia","tanzania","thailand","australia","azerbaijan","bangladesh","costa rica",
        "indonesia","kazakhstan","kyrgyzstan","liechtenstein","luxembourg","madagascar","mauritania",
        "philippines","switzerland","tajikistan","uzbekistan"
    ],
    "science": [
        "acid","atom","base","cell","data","gene","heat","ions","mass","node","volt","wave","alloy",
        "amino","anode","axion","boron","chaos","clone","comet","decay","delta","diode","drone","earth",
        "enyme","epoch","force","fungi","gamma","helix","hertz","joule","laser","light","lipid","liver",
        "logic","meson","metal","molar","nerve","niche","ozone","oxide","phase","plasm","polar","proton",
        "pulse","quark","radar","ratio","relay","solar","solid","sonic","sound","speed","spore","quasar",
        "stimulus","stress","synapse","theory","tissue","toxin","vapor","virus","vision","yield","acetic",
        "aether","alkali","ampere","binary","carbon","charge","climate","cosmos","crystal","dalton",
        "derive","dipole","doppler","dynamo","effect","energy","enzyme","factor","fathom","ferment",
        "filter","fission","fossil","fusion","galaxy","genome","glacial","gravity","habitat","hardness",
        "hormone","hydrate","inertia","isotope","kinetic","lattice","magnet","matter","mineral","mixture",
        "molten","momentum","nebula","neutron","nucleus","optical","organic","osmosis","oxidize","particle",
        "pathogen","photon","physics","pioneer","planet","polymer","pressure","protein","quantum","radiant",
        "reactor","reflect","refract","relativity","resonance","salinity","solution","spectrum","static",
        "stellar","sublimate","symbiosis","thermal","tectonic","velocity","voltage","wavelength","electron",
        "evolution","frequency","potential","radiation","ecosystem","electrolysis","chromosome","hypothesis",
        "mitochondria","bioluminescence","thermodynamics","electromagnetic","photosynthesis","gravitational"
    ],
    "food": [
        "bun","dip","egg","fig","ham","jam","pie","rye","soy","tea","yam","beef","beet","brie","cake",
        "chip","chop","clam","crab","dhal","feta","fish","flan","kale","kiwi","lamb","leek","lime",
        "milk","mint","miso","naan","oats","okra","olive","pear","plum","pork","rice","roti","sage",
        "salt","soup","soya","taco","tofu","tuna","udon","veal","waffles","yogurt","apple","avocado",
        "bacon","basil","berry","bread","broth","candy","carrot","cheese","chicken","chilli","chips",
        "chive","cocoa","coffee","cookie","cream","crepe","curry","dates","donut","dough","feast",
        "flour","fudge","garlic","gelato","ginger","grapes","gravy","guava","honey","hummus","juice",
        "lemon","lentil","lychee","mango","maple","melon","mocha","mochi","muffin","mushroom","noodle",
        "nutmeg","onion","orange","oyster","papaya","pasta","peach","peanut","pepper","pickle","pizza",
        "plum","poppy","potato","pretzel","prune","pudding","radish","raisin","relish","risotto","salad",
        "salmon","salsa","sauce","sesame","shrimp","sorbet","spices","steak","sugar","sushi","sweet",
        "syrup","thyme","toast","tomato","truffle","vanilla","waffle","walnut","wasabi","almond",
        "biryani","brownie","burrito","cashew","chapati","coconut","custard","eclair","enchilada",
        "espresso","fritter","granola","grilled","gulabjamun","jackfruit","jalebi","kebab","lasagna",
        "lobster","macaroon","marmalade","masala","momos","mousse","mustard","omelette","paella",
        "pancake","parsley","pastry","pomelo","popcorn","pumpkin","quiche","quinoa","ravioli","samosa",
        "sandwich","sausage","scallop","sherbet","smoothie","soufle","spinach","sprouts","squash",
        "strudel","tapioca","tiramisu","tortilla","turmeric","tzatziki","croissant","ratatouille",
        "spaghetti","bruschetta","quesadilla","buttermilk","cheesecake","cinnamon","dumplings",
        "edamame","gazpacho","guacamole","lemonade","marinated","minestrone","prosciutto"
    ],
    "technology": [
        "api","app","bit","bug","bus","cpu","css","dns","gpu","gui","hub","ide","lan","led","log",
        "mac","net","ram","rom","sdk","sql","ssh","tcp","url","usb","vpn","wan","web","xml","ajax",
        "atom","bash","beta","bios","blob","boot","byte","call","chip","code","data","disk","file",
        "font","fork","grep","hash","heap","hook","html","http","icon","ipv6","java","json","kern",
        "link","lint","load","lock","loop","mesh","mock","node","null","open","pack","page","pass",
        "path","ping","pipe","plan","plug","poll","port","push","pypi","raid","repo","rest","root",
        "ruby","rust","scan","sort","span","spec","spin","stub","swap","sync","task","test","text",
        "tick","tree","type","unix","void","wiki","yard","agile","agent","alert","alias","array",
        "async","audit","basis","batch","binary","block","build","cache","class","click","cloud",
        "cluster","compile","cookie","cursor","daemon","debug","delay","deploy","digit","docker",
        "domain","driver","encode","error","event","fetch","field","filter","frame","fuzzy","graph",
        "index","input","kafka","kernel","latency","layer","library","linux","logger","memory","method",
        "metric","mobile","model","module","mongo","mutex","mysql","object","output","parser","patch",
        "payload","pipeline","plugin","pointer","polling","process","program","protocol","proxy","python",
        "query","queue","record","render","router","runtime","schema","script","search","server","signal",
        "socket","sprint","stack","state","static","stream","struct","syntax","system","thread","token",
        "trigger","tunnel","update","upload","vector","vertex","virtual","widget","window","workflow",
        "algorithm","bandwidth","blockchain","bootstrap","container","cybersecurity","database","debugging",
        "encryption","framework","frontend","function","hardware","interface","iteration","javascript",
        "kubernetes","microservice","middleware","network","programming","recursion","repository",
        "semiconductor","software","testing","virtualization","authentication","defragmentation",
        "hyperparameter","microprocessor"
    ],
    "general": [
        "ace","age","air","aim","arc","arm","art","ask","awe","bay","bed","box","buy","cap","car",
        "cup","cut","day","dig","dim","dip","dot","dry","dug","ear","end","era","eve","eye","far",
        "fat","few","fit","fix","fly","fun","gap","gem","get","gig","got","gun","gut","gym","had",
        "hat","him","hit","hop","hot","how","hug","hum","ice","ill","ink","inn","joy","key","kid",
        "kin","kit","lag","lap","law","lay","led","leg","let","lid","lip","lit","lot","low","mad",
        "map","mat","met","mix","mud","mug","nap","nod","now","odd","old","opt","orb","our","out",
        "own","pad","pal","pan","pat","pay","pen","pet","pit","pop","pot","pro","pub","put","raw",
        "red","rid","rig","rim","rip","row","rub","rug","run","rut","sad","sap","sat","saw","say",
        "set","sew","she","shy","sip","sit","six","sky","sly","sob","son","spa","spy","sum","sun",
        "tab","tan","tap","tar","tax","tie","tip","toe","ton","too","top","tow","toy","try","tub",
        "tug","two","use","van","vat","vet","via","vie","vow","wax","way","who","why","win","wit",
        "woe","wok","won","wow","yew","zap","zip","zone","able","ache","acre","aged","also","alto",
        "arch","area","army","aunt","auto","away","baby","back","ball","band","bank","barn","base",
        "bath","bell","belt","best","bike","bill","bind","bite","blow","blue","blur","body","bold",
        "bolt","bone","book","bore","both","bowl","busy","call","calm","came","camp","cape","card",
        "care","cart","case","cash","cave","city","clap","clay","clip","club","clue","coal","coat",
        "coin","cold","come","cook","cool","cope","copy","cord","core","corn","cost","coup","crew",
        "crop","curl","dawn","days","dead","deal","dean","debt","deed","deep","deny","desk","diet",
        "dime","dine","dirt","does","done","door","dose","down","draw","drew","drop","drum","dual",
        "dump","dusk","dust","duty","each","earn","ease","edge","else","emit","even","ever","evil",
        "exam","face","fact","fail","fair","fake","fame","farm","fast","fate","feel","feet","fell",
        "felt","fend","fern","fill","find","fire","firm","fish","fist","flag","flat","flaw","flew",
        "flip","flow","foam","foes","fold","folk","fond","food","fool","foot","fore","form","fort",
        "four","free","from","full","gain","gate","gave","gaze","gift","girl","give","glad","glow",
        "goal","gold","golf","gone","good","gown","grab","grew","grid","grin","grip","grow","gust",
        "half","hall","halt","hand","hang","hard","harm","harp","hate","have","head","heal","heap",
        "hear","heel","held","helm","help","herb","here","hero","hide","high","hill","hint","hire",
        "hold","hole","home","hope","horn","host","hour","huge","hung","hunt","hurt","idea","idle",
        "inch","into","iron","isle","item","jobs","join","joke","jump","just","keen","keep","kill",
        "kind","king","knew","know","lack","lake","land","lane","last","late","laud","lead","leaf",
        "leak","lean","leap","left","lend","lens","less","lick","life","like","line","list","live",
        "load","loan","loft","lone","long","look","loom","lose","loss","lost","love","luck","lure",
        "lurk","made","mail","main","make","male","mall","mane","many","mark","mars","mast","mean",
        "meet","melt","menu","mere","mild","mile","mill","mind","mine","miss","mist","mode","mood",
        "moon","more","most","move","much","must","myth","name","near","neck","need","next","nice",
        "nine","none","noon","norm","note","noun","obey","once","open","oral","oven","over","pace",
        "pack","page","pain","pair","palm","park","part","past","peak","peel","peer","pick","pile",
        "pine","pink","pipe","plan","play","plea","plot","plow","ploy","plus","poem","poet","pole",
        "poll","pond","pool","poor","pose","post","pour","prey","pull","pure","race","rage","raid",
        "rail","rain","rake","rang","rank","rare","rate","read","real","reap","reel","rely","rend",
        "rent","rest","rich","ride","ring","riot","rise","risk","road","roam","roar","role","roll",
        "roof","room","rope","rose","ruin","rule","rush","rust","safe","sail","sake","sale","sand",
        "sane","sang","sank","save","seal","seam","seem","seen","self","sell","send","sent","shed",
        "ship","shoe","shop","shot","show","shut","sick","side","sigh","silk","sing","sink","site",
        "size","skin","skip","slam","slap","slim","slip","slow","slum","snap","snow","soak","sock",
        "soil","sold","sole","some","song","soon","sore","sort","soul","span","spur","star","stay",
        "stem","step","stir","stop","store","storm","story","straight","strange","strength","stretch",
        "strike","strip","stroll","strong","study","stuff","style","swam","swap","swear","sweep",
        "swift","swim","swore","table","taken","taste","teach","team","tear","tech","tell","tend",
        "term","than","that","them","then","they","thin","this","thou","thus","tide","till","time",
        "tiny","tire","title","today","told","toll","tome","tone","took","tool","torn","toss","tour",
        "town","trap","trek","trim","trio","trip","true","tube","tune","turn","ugly","undo","unit",
        "upon","used","user","vast","very","view","vote","wade","wage","wake","walk","wall","want",
        "ward","warm","warn","wary","wash","wave","weak","wear","weed","week","well","went","were",
        "what","when","whom","wide","wife","wild","will","wilt","wind","wine","wing","wire","wish",
        "with","woke","word","wore","work","worm","worn","wove","wrap","wrist","wrote","yard","year",
        "your","zero"
    ]
}

# Flat corpus for when category is unknown
ALL_WORDS_FLAT = list(set([w for words in WORD_CORPUS.values() for w in words]))

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
def get_corpus(category):
    if category and category in WORD_CORPUS:
        return WORD_CORPUS[category]
    return ALL_WORDS_FLAT

def get_possible_words(length, correct_positions, wrong_letters, correct_letters, category):
    corpus = get_corpus(category)
    possible = []
    for w in corpus:
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
    # Fallback: if corpus filtered too aggressively, use all words of same length
    if not possible:
        possible = [w for w in ALL_WORDS_FLAT if len(w) == length
                    and not any(ch in w for ch in wrong_letters)
                    and all(w[i]==ch for i,ch in correct_positions.items() if i<len(w))
                    and all(ch in w for ch in correct_letters)]
    return possible

def bayesian_probabilities(length, correct_positions, wrong_letters, correct_letters, guessed_letters, category):
    possible = get_possible_words(length, correct_positions, wrong_letters, correct_letters, category)
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

    # If corpus is exhausted, fall back to pure letter frequency
    if total == 0:
        probs = {ch: LETTER_FREQ.get(ch, 0.1)/100 for ch in unguessed}
        s2 = sum(probs.values()) or 1
        probs = {ch: v/s2 for ch, v in probs.items()}

    return probs, possible, total

# ── Logging ───────────────────────────────────────────────────────────────────
def add_log(msg, level="info"):
    if "logs" not in st.session_state:
        st.session_state.logs = []
    css = {"info":"c-info","good":"c-good","bad":"c-bad","warn":"c-warn","math":"c-math","ai":"c-ai"}
    icon = {"info":"ℹ","good":"✓","bad":"✗","warn":"▲","math":"∑","ai":"🤖"}
    st.session_state.logs.append({
        "msg": msg, "css": css.get(level,"c-info"),
        "icon": icon.get(level,"ℹ"),
        "turn": st.session_state.get("turn", 0)
    })

# ── Groq AI ───────────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        return Groq(api_key=os.environ.get("GROQ_API_KEY",""))

def ai_reasoning(letter, prob, possible_count, wrong_letters, pattern, category):
    prompt = f"""You are an AI playing Hangman using Bayesian strategy (VTU BAD402 AI).
You chose letter '{letter.upper()}' with posterior probability {prob*100:.1f}%.
- Category: {category}
- Possible words remaining: {possible_count}
- Wrong guesses: {', '.join(wrong_letters) if wrong_letters else 'none'}
- Pattern: {pattern}
In exactly 2 short sentences, explain your Bayesian reasoning. Mention prior (letter frequency) and likelihood (word corpus). Be concise."""
    try:
        r = get_groq_client().chat.completions.create(model=MODEL, max_tokens=80,
            messages=[{"role":"user","content":prompt}])
        return r.choices[0].message.content.strip()
    except:
        return f"Chose '{letter.upper()}' — posterior P={prob*100:.1f}%, based on letter frequency prior and word corpus likelihood."

def ai_win_msg(word, wrong_count):
    try:
        r = get_groq_client().chat.completions.create(model=MODEL, max_tokens=50,
            messages=[{"role":"user","content":f"You just won Hangman guessing '{word}' with {wrong_count} wrong guesses using Bayesian strategy. One triumphant sentence."}])
        return r.choices[0].message.content.strip()
    except:
        return f"Bayesian strategy cracked '{word.upper()}' with only {wrong_count} wrong guesses!"

def ai_lose_msg(wrong_count):
    try:
        r = get_groq_client().chat.completions.create(model=MODEL, max_tokens=50,
            messages=[{"role":"user","content":f"You just lost Hangman after {wrong_count} wrong guesses. One humble sentence about Bayesian failure."}])
        return r.choices[0].message.content.strip()
    except:
        return "The word defeated my Bayesian model this time — a rare statistical anomaly!"

# ── SVG Gallows ───────────────────────────────────────────────────────────────
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

# ── Word HTML ─────────────────────────────────────────────────────────────────
def word_html(length, correct_positions):
    html = '<div class="word-wrap">'
    for i in range(length):
        ch = correct_positions.get(i)
        cls = "found" if ch else "blank"
        disp = ch.upper() if ch else "_"
        html += f'<div class="lslot"><div class="lchar {cls}">{disp}</div><div class="lline"></div></div>'
    html += '</div>'
    return html

def pattern_str(length, correct_positions):
    return " ".join([correct_positions.get(i,"_") for i in range(length)])

# ── Probability bars ──────────────────────────────────────────────────────────
def prob_bars_html(probs, top_n=10):
    if not probs:
        return "<p style='color:#3a3a5a;font-size:0.75rem;padding:10px'>Waiting...</p>"
    top = sorted(probs.items(), key=lambda x: -x[1])[:top_n]
    mx = max(v for _,v in top) if top else 1
    if mx <= 0: mx = 1
    html = '<div class="bayes-panel"><div class="bayes-title">∑ Posterior P(L|Evidence) — Top 10</div>'
    for letter, prob in top:
        pct = min((prob/mx)*100, 100)
        val = f"{prob*100:.1f}%"
        color = "#47ff8a" if pct>70 else "#47c8ff" if pct>40 else "#e8ff47" if pct>20 else "#ff9f43"
        bold = "font-weight:bold;" if letter==top[0][0] else ""
        html += f'''<div class="prob-row">
            <div class="prob-letter" style="color:{color};{bold}">{letter.upper()}</div>
            <div class="prob-bar-bg"><div class="prob-bar" style="width:{pct:.1f}%;background:{color}"></div></div>
            <div class="prob-val">{val}</div></div>'''
    html += '</div>'
    return html

# ── Log HTML ──────────────────────────────────────────────────────────────────
def log_html():
    logs = st.session_state.get("logs",[])
    if not logs:
        return '<div class="log-panel"><span style="color:#3a3a5a">No logs yet...</span></div>'
    html = '<div class="log-panel">'
    for e in reversed(logs[-60:]):
        html += f'<div class="log-entry"><span class="log-time">[T{e["turn"]:02d}]</span><span class="{e["css"]}">{e["icon"]} {e["msg"]}</span></div>'
    html += '</div>'
    return html

# ── Game Logic ────────────────────────────────────────────────────────────────
def init_setup():
    st.session_state.update({
        "phase": "setup",
        "secret_word": "", "word_length": 0, "category": None,
        "correct_positions": {}, "correct_letters": set(),
        "wrong_letters": [], "guessed_letters": set(),
        "turn": 0, "logs": [], "probs": {}, "possible_count": 0,
        "current_guess": None, "ai_reasoning_text": "",
        "game_result": None, "result_message": "",
        "waiting_response": False,
        "score_ai":    st.session_state.get("score_ai", 0),
        "score_you":   st.session_state.get("score_you", 0),
        "total_games": st.session_state.get("total_games", 0),
    })

def start_playing(word_length, category):
    st.session_state.phase = "playing"
    st.session_state.word_length = word_length
    st.session_state.category = category
    corpus = get_corpus(category)
    pool = [w for w in corpus if len(w) == word_length]
    add_log(f"Game started! Word length: {word_length}, Category: {category or 'general'}", "info")
    add_log(f"Corpus filtered to {len(pool)} words of length {word_length} in category '{category or 'general'}'", "math")
    add_log(f"Prior P(L): English letter frequency distribution", "math")
    add_log(f"Bayesian model ready. AI begins guessing...", "ai")
    run_bayes_and_guess()

def run_bayes_and_guess():
    length   = st.session_state.word_length
    cp       = st.session_state.correct_positions
    wl       = st.session_state.wrong_letters
    cl       = st.session_state.correct_letters
    gl       = st.session_state.guessed_letters
    category = st.session_state.category

    probs, possible, total = bayesian_probabilities(length, cp, wl, cl, gl, category)
    st.session_state.probs = probs
    st.session_state.possible_count = total

    if not probs:
        add_log("No letters available to guess!", "bad")
        return

    best = max(probs, key=probs.get)
    best_prob = probs[best]
    st.session_state.current_guess = best

    pat = pattern_str(length, cp)
    add_log(f"Bayesian update — {total} possible words remain in corpus", "math")
    add_log(f"Best guess: '{best.upper()}' | Posterior P={best_prob*100:.1f}%", "math")

    reasoning = ai_reasoning(best, best_prob, total, wl, pat, category or "general")
    st.session_state.ai_reasoning_text = reasoning
    add_log(f"{reasoning}", "ai")

    st.session_state.turn += 1
    st.session_state.guessed_letters.add(best)
    st.session_state.waiting_response = True

def process_response(is_correct, positions_with_letter=None):
    letter = st.session_state.current_guess
    if is_correct and positions_with_letter is not None:
        for pos in positions_with_letter:
            st.session_state.correct_positions[pos] = letter
        st.session_state.correct_letters.add(letter)
        add_log(f"'{letter.upper()}' CORRECT at positions {[p+1 for p in positions_with_letter]}", "good")

        if len(st.session_state.correct_positions) == st.session_state.word_length:
            word = "".join(st.session_state.correct_positions.get(i,"?") for i in range(st.session_state.word_length))
            add_log(f"🎉 AI guessed the word: {word.upper()}!", "good")
            st.session_state.result_message = ai_win_msg(word, len(st.session_state.wrong_letters))
            st.session_state.game_result = "ai_win"
            st.session_state.score_ai += 1
            st.session_state.total_games += 1
            st.session_state.phase = "result"
        else:
            st.session_state.waiting_response = False
            run_bayes_and_guess()
    else:
        st.session_state.wrong_letters.append(letter)
        add_log(f"'{letter.upper()}' WRONG — eliminating all words containing it", "bad")
        add_log(f"Posterior updated: words with '{letter.upper()}' removed from pool", "math")

        if len(st.session_state.wrong_letters) >= MAX_WRONG:
            add_log("AI used all 6 guesses. YOU WIN! 🎉", "warn")
            st.session_state.result_message = ai_lose_msg(len(st.session_state.wrong_letters))
            st.session_state.game_result = "human_win"
            st.session_state.score_you += 1
            st.session_state.total_games += 1
            st.session_state.phase = "result"
        else:
            st.session_state.waiting_response = False
            run_bayes_and_guess()

# ── Session init ──────────────────────────────────────────────────────────────
if "phase" not in st.session_state:
    st.session_state.score_ai = 0
    st.session_state.score_you = 0
    st.session_state.total_games = 0
    init_setup()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
c1,c2,c3,c4 = st.columns([2.5,1,1,1])
with c1:
    st.markdown("<div class='subtitle'>VTU BAD402 — Artificial Intelligence | Bayesian Strategy</div>", unsafe_allow_html=True)
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
# SETUP PHASE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.phase == "setup":
    lc, rc = st.columns([1.2, 1])
    with lc:
        st.markdown("### 🧠 HOW TO PLAY")
        st.markdown("""<div class='setup-box'>
        <p style='color:#c8c8e0;font-size:0.82rem;line-height:2.0'>
        <b style='color:#e8ff47'>You</b> = Word Setter &nbsp;|&nbsp; <b style='color:#ff4757'>AI</b> = Guesser (Bayesian)<br><br>
        <b style='color:#47c8ff'>1.</b> Think of a secret word<br>
        <b style='color:#47c8ff'>2.</b> Select its category & enter its length<br>
        <b style='color:#47c8ff'>3.</b> AI guesses letters using Bayesian probability<br>
        <b style='color:#47c8ff'>4.</b> Click ✅ YES or ❌ NO for each guess<br>
        <b style='color:#47c8ff'>5.</b> If YES → mark which positions contain the letter<br>
        <b style='color:#47c8ff'>6.</b> AI wins in ≤6 wrong guesses. You win if AI fails!<br><br>
        <span style='color:#c084fc'>Watch Bayesian probabilities update live! 📊</span>
        </p></div>""", unsafe_allow_html=True)

        st.markdown("### 🎓 BAD402 Formula")
        st.markdown("""<div style='background:#0f0f1a;border:1px solid #2a1a4a;border-radius:4px;padding:14px;font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#c084fc;line-height:2.0'>
            P(L | E) ∝ P(E | L) × P(L)<br>
            <span style='color:#6b6b80'>L = Letter &nbsp;|&nbsp; E = Pattern Evidence</span><br>
            <span style='color:#6b6b80'>P(L)   = English letter frequency (prior)</span><br>
            <span style='color:#6b6b80'>P(E|L) = Word corpus match (likelihood)</span><br>
            <span style='color:#6b6b80'>P(L|E) = Updated belief (posterior)</span>
        </div>""", unsafe_allow_html=True)

    with rc:
        st.markdown("### 📝 SET YOUR WORD")
        st.markdown("<div class='setup-box'>", unsafe_allow_html=True)

        category = st.selectbox("Category of your word:",
            ["general","animals","countries","science","food","technology"],
            help="Tells AI which word corpus to search — makes guessing smarter!")

        word_input = st.text_input("Type your secret word (hidden):", type="password", key="word_field")

        if word_input:
            word_clean = word_input.lower().strip()
            if word_clean.isalpha() and len(word_clean) >= 3:
                st.markdown(f"<div style='background:#0a1f14;border:1px solid #47ff8a;border-radius:4px;padding:8px 12px;color:#47ff8a;font-size:0.75rem;margin:8px 0'>✓ Word accepted — {len(word_clean)} letters | Category: {category}</div>", unsafe_allow_html=True)
                if st.button("🚀 START — Let AI Guess!", key="start_btn"):
                    st.session_state.secret_word = word_clean
                    start_playing(len(word_clean), category)
                    st.rerun()
            else:
                st.markdown("<div style='background:#1a0508;border:1px solid #ff4757;border-radius:4px;padding:8px 12px;color:#ff4757;font-size:0.75rem;margin:8px 0'>⚠ Min 3 letters, alphabets only</div>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**OR — Let the game pick a random word:**")
        rand_cat = st.selectbox("Pick category for random word:", list(WORD_CORPUS.keys()), key="rand_cat")
        if st.button("🎲 Random Word", key="rand_btn"):
            word = random.choice(WORD_CORPUS[rand_cat])
            st.session_state.secret_word = word
            start_playing(len(word), rand_cat)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PLAYING PHASE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "playing":
    left, mid, right = st.columns([1, 1.5, 1.2])

    with left:
        st.markdown("<div class='gallows-wrap'>" + hangman_svg(len(st.session_state.wrong_letters)) + "</div>", unsafe_allow_html=True)
        wc = len(st.session_state.wrong_letters)
        col = "green" if wc < 2 else "yellow" if wc < 4 else "red"
       border_color = "#47ff8a" if col=="green" else "#e8ff47" if col=="yellow" else "#ff4757"
        st.markdown(f"<div style='text-align:center;margin:6px 0'><span style='background:#0f0f1a;border:1px solid;border-radius:2px;padding:3px 12px;font-size:0.62rem;letter-spacing:0.2em;border-color:{border_color};color:{border_color}'>WRONG: {wc}/{MAX_WRONG}</span></div>", unsafe_allow_html=True)

        if st.session_state.wrong_letters:
            wl = "  ".join(l.upper() for l in st.session_state.wrong_letters)
            st.markdown(f"<div style='background:#1a0508;border:1px solid #ff4757;border-radius:4px;padding:8px;color:#ff4757;font-size:0.78rem;text-align:center;margin:4px 0;letter-spacing:0.15em'>✗ {wl}</div>", unsafe_allow_html=True)

        cat_display = st.session_state.category or "general"
        st.markdown(f"<div style='background:#0f0f1a;border:1px solid #1e1e2e;border-radius:4px;padding:8px;text-align:center;margin:4px 0'><div style='font-size:0.55rem;color:#6b6b80;letter-spacing:0.2em;text-transform:uppercase'>Category</div><div style='font-family:Bebas Neue,sans-serif;font-size:1.4rem;color:#47c8ff'>{cat_display.upper()}</div></div>", unsafe_allow_html=True)

        st.markdown(f"<div style='background:#0f0f1a;border:1px solid #1e1e2e;border-radius:4px;padding:8px;text-align:center;margin:4px 0'><div style='font-size:0.55rem;color:#6b6b80;letter-spacing:0.2em;text-transform:uppercase'>Possible Words</div><div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;color:#47c8ff'>{st.session_state.possible_count}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↺ New Game", key="new_game"):
            init_setup()
            st.rerun()

    with mid:
        st.markdown(word_html(st.session_state.word_length, st.session_state.correct_positions), unsafe_allow_html=True)

        if st.session_state.current_guess and st.session_state.waiting_response:
            letter = st.session_state.current_guess
            prob = st.session_state.probs.get(letter, 0)

            st.markdown(f"""<div style='background:#0a1020;border:2px solid #47c8ff;border-radius:6px;padding:18px;text-align:center;margin:10px 0'>
                <div style='font-size:0.58rem;letter-spacing:0.2em;color:#47c8ff;text-transform:uppercase'>🤖 AI Guesses</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:5rem;color:#e8ff47;line-height:1.1'>{letter.upper()}</div>
                <div style='font-size:0.72rem;color:#c084fc'>Posterior Probability: <b>{prob*100:.1f}%</b></div>
                <div style='font-size:0.62rem;color:#3a3a5a;margin-top:4px'>Guess #{st.session_state.turn} | {st.session_state.possible_count} words remain</div>
            </div>""", unsafe_allow_html=True)

            if st.session_state.ai_reasoning_text:
                st.markdown(f'<div class="think-box"><div class="think-title">🧠 AI Bayesian Reasoning</div><div class="think-text">{st.session_state.ai_reasoning_text}</div></div>', unsafe_allow_html=True)

            st.markdown("**Is this letter in your word?**")
            cy, cn = st.columns(2)
            with cy:
                if st.button(f"✅ YES — '{letter.upper()}' is in my word", key="yes_btn"):
                    st.session_state._pending_yes = True
                    st.rerun()
            with cn:
                if st.button(f"❌ NO — '{letter.upper()}' is NOT in my word", key="no_btn"):
                    process_response(False)
                    st.rerun()

            if st.session_state.get("_pending_yes"):
                length = st.session_state.word_length
                st.markdown(f"**Select ALL positions where '{letter.upper()}' appears (1 = first letter):**")
                if "selected_positions" not in st.session_state:
                    st.session_state.selected_positions = []

                cols = st.columns(min(length, 12))
                for i in range(length):
                    with cols[i % min(length, 12)]:
                        already = i in st.session_state.correct_positions
                        sel = i in st.session_state.selected_positions
                        lbl = f"✓{i+1}" if sel else f"{i+1}"
                        if st.button(lbl, key=f"pos_{i}", disabled=already):
                            if i in st.session_state.selected_positions:
                                st.session_state.selected_positions.remove(i)
                            else:
                                st.session_state.selected_positions.append(i)
                            st.rerun()

                if st.session_state.selected_positions:
                    sel_str = ", ".join(str(p+1) for p in sorted(st.session_state.selected_positions))
                    st.markdown(f"<div style='background:#0a1f14;border:1px solid #47ff8a;border-radius:4px;padding:8px;color:#47ff8a;font-size:0.75rem;margin:6px 0'>✓ Selected: Position(s) {sel_str}</div>", unsafe_allow_html=True)
                    if st.button("✅ Confirm & Continue", key="confirm_pos"):
                        positions = st.session_state.selected_positions[:]
                        del st.session_state.selected_positions
                        del st.session_state._pending_yes
                        process_response(True, positions)
                        st.rerun()

        if st.session_state.guessed_letters:
            st.markdown("<hr>", unsafe_allow_html=True)
            g_str = "  ".join(sorted(l.upper() for l in st.session_state.guessed_letters))
            st.markdown(f"<div style='font-size:0.6rem;letter-spacing:0.12em;color:#6b6b80'>ALL GUESSED: {g_str}</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div style='font-size:0.62rem;letter-spacing:0.2em;color:#c084fc;text-transform:uppercase;margin-bottom:8px'>∑ Bayesian Analysis</div>", unsafe_allow_html=True)
        st.markdown("""<div style='background:#0f0f1a;border:1px solid #2a1a4a;border-radius:4px;padding:10px 12px;margin-bottom:8px;font-family:JetBrains Mono,monospace;font-size:0.66rem;color:#c084fc;line-height:1.9'>
            P(L|E) ∝ P(E|L) × P(L)<br>
            <span style='color:#6b6b80'>Prior P(L)   → letter frequency</span><br>
            <span style='color:#6b6b80'>Likeli P(E|L) → corpus word match</span><br>
            <span style='color:#6b6b80'>Posterior     → updated belief</span>
        </div>""", unsafe_allow_html=True)
        st.markdown(prob_bars_html(st.session_state.probs), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.62rem;letter-spacing:0.2em;color:#47c8ff;text-transform:uppercase;margin-bottom:6px'>📋 Strategy Log</div>", unsafe_allow_html=True)
        st.markdown(log_html(), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RESULT PHASE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "result":
    lc, rc = st.columns([1.5, 1])
    with lc:
        if st.session_state.game_result == "ai_win":
            word = "".join(st.session_state.correct_positions.get(i,"?") for i in range(st.session_state.word_length))
            st.markdown(f"""<div class='lose-box'>
                <div class='result-big' style='color:#ff4757'>🤖 AI WINS!</div>
                <div style='font-family:Bebas Neue,sans-serif;font-size:1.8rem;color:#e8ff47;letter-spacing:0.2em;margin:8px 0'>{word.upper()}</div>
                <div style='font-size:0.8rem;color:#ff9f43;margin-top:6px'>{st.session_state.result_message}</div>
                <div style='font-size:0.7rem;color:#6b6b80;margin-top:8px'>Wrong guesses: {len(st.session_state.wrong_letters)}/{MAX_WRONG} | Turns: {st.session_state.turn}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='win-box'>
                <div class='result-big' style='color:#47ff8a'>🎉 YOU WIN!</div>
                <div style='font-size:0.85rem;color:#47ff8a;margin-top:8px'>AI failed to guess your word in {MAX_WRONG} tries!</div>
                <div style='font-size:0.78rem;color:#6b6b80;margin-top:6px'>{st.session_state.result_message}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Play Again", key="play_again"):
            init_setup()
            st.rerun()

    with rc:
        st.markdown("<div style='font-size:0.62rem;letter-spacing:0.2em;color:#47c8ff;text-transform:uppercase;margin-bottom:6px'>📋 Full Strategy Log</div>", unsafe_allow_html=True)
        st.markdown(log_html(), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(prob_bars_html(st.session_state.probs), unsafe_allow_html=True)
