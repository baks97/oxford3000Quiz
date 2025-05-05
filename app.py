import streamlit as st
import random
import json
import os

MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

# --- ФУНКЦИИ ---

def parse_md_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    words = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("## 🔤 "):
            word = lines[i][5:].strip()
            transcription = lines[i+1] if i+1 < len(lines) else ""
            part_of_speech = lines[i+2] if i+2 < len(lines) else ""

            # Найти блок с примерами
            for j in range(i+3, len(lines)):
                if lines[j].startswith("### 🧾"):
                    examples_start = j
                    break
            else:
                examples_start = None

            # Найти конец блока
            for j in range(i+1, len(lines)):
                if lines[j].startswith("## 🔤 ") and j > i:
                    next_entry = j
                    break
            else:
                next_entry = len(lines)

            if examples_start is not None:
                extra = "\n".join(lines[i+3:examples_start])
                examples = "\n".join(lines[examples_start:next_entry])
            else:
                extra = "\n".join(lines[i+3:next_entry])
                examples = ""

            words.append({
                "word": word,
                "transcription": transcription,
                "part_of_speech": part_of_speech,
                "extra": extra,
                "examples": examples
            })
            i = next_entry
        else:
            i += 1
    return words

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# --- СОСТОЯНИЕ СЕССИИ ---

if "page" not in st.session_state:
    st.session_state.page = "start"
if "words" not in st.session_state:
    st.session_state.words = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "show" not in st.session_state:
    st.session_state.show = False
if "answers" not in st.session_state:
    st.session_state.answers = []
if "stats" not in st.session_state:
    st.session_state.stats = load_stats()
if "seed" not in st.session_state:
    st.session_state.seed = None

# --- НАЧАЛЬНЫЙ ЭКРАН ---

if st.session_state.page == "start":
    st.title("🧠 Английский квиз по словам")

    st.subheader("Выберите количество слов:")
    col1, col2, col3, col4 = st.columns(4)
    for col, n in zip([col1, col2, col3, col4], [7, 15, 20, 25]):
        with col:
            if st.button(f"{n} слов"):
                all_words = parse_md_file(MD_FILE)
                st.session_state.seed = random.randint(1, 1_000_000)
                random.seed(st.session_state.seed)
                st.session_state.words = random.sample(all_words, n)
                st.session_state.index = 0
                st.session_state.answers = []
                st.session_state.show = False
                st.session_state.page = "quiz"
                st.experimental_rerun()

    st.write("📂 Или показать весь файл")
    if st.button("Показать весь файл"):
        st.session_state.page = "full"
        st.experimental_rerun()

    if st.button("📊 Показать статистику"):
        st.session_state.page = "stats"
        st.experimental_rerun()

# --- КВИЗ ---

elif st.session_state.page == "quiz":
    words = st.session_state.words
    index = st.session_state.index
    word = words[index]

    st.markdown(f"## 🔤 {word['word']}")
    st.markdown(word['transcription'])
    st.markdown(word['part_of_speech'])

    if st.session_state.show:
        if word["extra"]:
            st.markdown(word["extra"])
        st.markdown(word["examples"])
    else:
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("👁 Показать значение"):
                st.session_state.show = True
                st.experimental_rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("❌ Неправильно"):
            st.session_state.answers.append((word["word"], False))
            st.session_state.stats.setdefault(word["word"], {"right": 0, "wrong": 0})
            st.session_state.stats[word["word"]]["wrong"] += 1
            st.session_state.index += 1
            st.session_state.show = False
            if st.session_state.index >= len(st.session_state.words):
                st.session_state.page = "result"
            st.experimental_rerun()
    with col2:
        if st.button("✅ Правильно"):
            st.session_state.answers.append((word["word"], True))
            st.session_state.stats.setdefault(word["word"], {"right": 0, "wrong": 0})
            st.session_state.stats[word["word"]]["right"] += 1
            st.session_state.index += 1
            st.session_state.show = False
            if st.session_state.index >= len(st.session_state.words):
                st.session_state.page = "result"
            st.experimental_rerun()

# --- РЕЗУЛЬТАТЫ ---

elif st.session_state.page == "result":
    st.title("🏁 Результаты")

    correct = [w for w, r in st.session_state.answers if r]
    wrong = [w for w, r in st.session_state.answers if not r]

    st.success(f"✅ Правильно: {len(correct)}")
    st.error(f"❌ Неправильно: {len(wrong)}")

    if wrong:
        st.subheader("Ошибки:")
        all_words = {w["word"]: w for w in parse_md_file(MD_FILE)}
        for w in wrong:
            word = all_words.get(w)
            if word:
                st.markdown(f"**{word['word']}**")
                st.markdown(word["transcription"])
                st.markdown(word["part_of_speech"])
                if word["extra"]:
                    st.markdown(word["extra"])
                st.markdown(word["examples"])
                st.markdown("---")

    save_stats(st.session_state.stats)

    st.button("🔁 Начать заново", on_click=lambda: st.session_state.update({
        "page": "start", "words": [], "index": 0, "answers": [], "show": False
    }))

# --- ПОЛНЫЙ СПИСОК ---

elif st.session_state.page == "full":
    st.title("📂 Полный список слов")
    all_words = parse_md_file(MD_FILE)
    for word in sorted(all_words, key=lambda w: w['word'].lower()):
        st.markdown(f"## 🔤 {word['word']}")
        st.markdown(word['transcription'])
        st.markdown(word['part_of_speech'])
        if word['extra']:
            st.markdown(word['extra'])
        st.markdown(word['examples'])
        st.markdown("---")

    st.button("🔙 Назад", on_click=lambda: st.session_state.update({"page": "start"}))

# --- СТАТИСТИКА ---

elif st.session_state.page == "stats":
    st.title("📊 Общая статистика")
    stats = load_stats()
    if stats:
        for word, data in sorted(stats.items()):
            total = data["right"] + data["wrong"]
            acc = (data["right"] / total) * 100 if total else 0
            st.markdown(f"**{word}** — ✅ {data['right']} / ❌ {data['wrong']} ({acc:.1f}%)")
    else:
        st.info("Нет сохранённой статистики.")
    st.button("🔙 Назад", on_click=lambda: st.session_state.update({"page": "start"}))
