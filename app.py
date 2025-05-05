import streamlit as st
import random
import json
import os
import re

MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

st.set_page_config(page_title="🧠 Английский квиз", layout="wide")

# ------------------------- ПАРСЕР -------------------------
@st.cache_data
def parse_md_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    entries = content.split("## 🔤 ")
    words = []

    for entry in entries[1:]:
        lines = entry.strip().split("\n")
        word = lines[0].strip()
        transcription = lines[1].strip().strip("**")
        part_of_speech = lines[2].strip().strip("*")
        examples_block = ""
        meaning_block = ""
        cambridge_block = ""

        # Найдём примеры Oxford
        oxford_start = next((i for i, line in enumerate(lines) if "### 🧾 Примеры (Oxford)" in line), None)
        oxford_end = next((i for i, line in enumerate(lines) if line.startswith("### 🌍")), len(lines))

        if oxford_start is not None:
            examples_block = "\n".join(lines[oxford_start:oxford_end]).strip()

        # Найдём Переводы Cambridge и примеры
        cambridge_start = next((i for i, line in enumerate(lines) if line.startswith("### 🌍")), None)
        if cambridge_start is not None:
            cambridge_block = "\n".join(lines[cambridge_start:]).strip()

        full_meaning = "\n".join(lines[3:]).strip()

        words.append({
            "word": word,
            "transcription": transcription,
            "part": part_of_speech,
            "examples": examples_block,
            "cambridge": cambridge_block,
            "meaning": full_meaning,
        })

    return words

# ------------------------- СТАТИСТИКА -------------------------
def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

# ------------------------- НАЧАЛЬНАЯ СТРАНИЦА -------------------------
if "page" not in st.session_state:
    st.session_state.page = "start"

if st.session_state.page == "start":
    st.title("🧠 Английский квиз по словам")
    st.markdown("### Выберите количество слов:")

    col1, col2, col3, col4 = st.columns(4)
    for col, n in zip([col1, col2, col3, col4], [7, 15, 20, 25]):
        if col.button(f"{n} слов"):
            st.session_state.num_words = n
            st.session_state.index = 0
            st.session_state.show = False
            st.session_state.answers = []
            st.session_state.page = "quiz"
            st.session_state.initialized = False
            st.rerun()

    st.write("— или —")
    if st.button("📂 Показать весь файл"):
        st.session_state.page = "full"

    if st.button("📊 Показать статистику"):
        st.session_state.page = "stats"

# ------------------------- КВИЗ -------------------------
elif st.session_state.page == "quiz":
    if "initialized" not in st.session_state or not st.session_state.initialized:
        all_words = parse_md_file(MD_FILE)
        st.session_state.words = random.sample(all_words, st.session_state.num_words)
        st.session_state.initialized = True

    words = st.session_state.words
    index = st.session_state.index
    word = words[index]

    st.markdown(f"### **{word['word']}**  \n`{word['transcription']}` — *{word['part']}*")
    st.markdown(word["examples"])

    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col1:
        if st.button("❌ Неправильно"):
            st.session_state.answers.append((word["word"], False))
            st.session_state.index += 1
            st.session_state.show = False
            st.rerun()
    with col2:
        label = "🔽 Показать значение" if not st.session_state.show else "🔼 Скрыть значение"
        if st.button(label):
            st.session_state.show = not st.session_state.show
            st.rerun()
    with col3:
        if st.button("✅ Правильно"):
            st.session_state.answers.append((word["word"], True))
            st.session_state.index += 1
            st.session_state.show = False
            st.rerun()

    if st.session_state.show:
        st.markdown("---")
        st.markdown(word["cambridge"])
        st.markdown("---")
        st.markdown(word["meaning"])

    if st.session_state.index >= len(words):
        st.session_state.page = "result"
        st.rerun()

# ------------------------- РЕЗУЛЬТАТ -------------------------
elif st.session_state.page == "result":
    st.title("✅ Результаты")

    stats = load_stats()
    for word, correct in st.session_state.answers:
        if word not in stats:
            stats[word] = {"right": 0, "wrong": 0}
        if correct:
            stats[word]["right"] += 1
        else:
            stats[word]["wrong"] += 1
    save_stats(stats)

    for word, correct in st.session_state.answers:
        color = "green" if correct else "red"
        st.markdown(f"- <span style='color:{color}'>{word}</span>", unsafe_allow_html=True)

    if st.button("🔁 Начать заново"):
        st.session_state.page = "start"
        st.rerun()

# ------------------------- ПОЛНЫЙ ФАЙЛ -------------------------
elif st.session_state.page == "full":
    st.title("📚 Все слова (в алфавитном порядке)")
    words = sorted(parse_md_file(MD_FILE), key=lambda x: x["word"].lower())
    for word in words:
        st.markdown(f"### **{word['word']}**  \n`{word['transcription']}` — *{word['part']}*")
        st.markdown(word["examples"])
        st.markdown(word["cambridge"])
        st.markdown(word["meaning"])
        st.markdown("---")

    if st.button("🔙 Назад"):
        st.session_state.page = "start"
        st.rerun()

# ------------------------- СТАТИСТИКА -------------------------
elif st.session_state.page == "stats":
    st.title("📊 Статистика")
    stats = load_stats()
    if not stats:
        st.write("Пока нет статистики.")
    else:
        for word, data in stats.items():
            st.write(f"**{word}** — ✅ {data['right']} / ❌ {data['wrong']}")

    if st.button("🔙 Назад"):
        st.session_state.page = "start"
        st.rerun()
