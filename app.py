import streamlit as st
import random
import json
import os

MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

st.set_page_config(page_title="Английский квиз", layout="wide")
st.title("🧠 Английский квиз по словам")

def parse_md_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        raw = f.read()
    entries = raw.strip().split("\n\n\n")
    words = []

    for entry in entries:
        lines = entry.strip().splitlines()
        if len(lines) < 3:
            continue

        word = lines[0].strip()
        transcription = lines[1].strip()
        pos = lines[2].strip()

        examples_block = ""
        details_block = ""

        current_block = ""
        for line in lines[3:]:
            if line.startswith("### 🧾"):
                current_block = "examples"
                examples_block += line + "\n"
            elif line.startswith("### "):
                current_block = "details"
                details_block += line + "\n"
            else:
                if current_block == "examples":
                    examples_block += line + "\n"
                elif current_block == "details":
                    details_block += line + "\n"

        words.append({
            "word": word.replace("## 🔤 ", "").strip(),
            "transcription": transcription.replace("**", "").strip(),
            "pos": pos.replace("*", "").strip(),
            "examples": examples_block.strip(),
            "details": details_block.strip()
        })

    return words

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

words_all = parse_md_file(MD_FILE)
stats_data = load_stats()

if "page" not in st.session_state:
    st.session_state.page = "start"
    st.session_state.index = 0
    st.session_state.stats = stats_data
    st.session_state.show = False
    st.session_state.mode = "test"

if st.session_state.page == "start":
    st.subheader("Выберите режим и количество слов")

    mode = st.radio("Режим:", ["🧪 Тест", "🧠 Тренировка"], horizontal=True)
    st.session_state.mode = "train" if mode == "🧠 Тренировка" else "test"

    col1, col2, col3, col4 = st.columns(4)
    for count, col in zip([7, 15, 20, 25], [col1, col2, col3, col4]):
        with col:
            if st.button(f"{count} слов"):
                st.session_state.words = random.sample(words_all, count)
                st.session_state.index = 0
                st.session_state.page = "quiz"
                st.session_state.show = (st.session_state.mode == "train")

    st.write("Или:")
    if st.button("📂 Показать весь файл"):
        st.session_state.words = random.sample(words_all, len(words_all))
        st.session_state.index = 0
        st.session_state.page = "quiz"
        st.session_state.show = (st.session_state.mode == "train")

    if st.button("📊 Показать статистику"):
        st.session_state.page = "stats"

elif st.session_state.page == "quiz":
    words = st.session_state.words
    index = st.session_state.index
    word = words[index]

    st.markdown(f"## {word['word']}")
    st.markdown(f"**{word['transcription']}**")
    st.markdown(f"*{word['pos']}*")

    st.markdown("---")
    st.markdown(word["examples"])
    st.markdown("---")

    if st.session_state.show or st.session_state.mode == "train":
        st.markdown(word["details"])

    if st.session_state.mode == "test":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("✅ Правильно"):
                w = word['word']
                st.session_state.stats.setdefault(w, {"right": 0, "wrong": 0})
                st.session_state.stats[w]["right"] += 1
                save_stats(st.session_state.stats)
                if st.session_state.index < len(words) - 1:
                    st.session_state.index += 1
                    st.session_state.show = False

        with col2:
            if st.button("❓ Показать значение"):
                st.session_state.show = True

        with col3:
            if st.button("❌ Неправильно"):
                w = word['word']
                st.session_state.stats.setdefault(w, {"right": 0, "wrong": 0})
                st.session_state.stats[w]["wrong"] += 1
                save_stats(st.session_state.stats)
                if st.session_state.index < len(words) - 1:
                    st.session_state.index += 1
                    st.session_state.show = False
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("◀ Предыдущее") and index > 0:
                st.session_state.index -= 1
        with col2:
            if st.button("Следующее ▶") and index < len(words) - 1:
                st.session_state.index += 1

    st.markdown("---")
    if st.session_state.index == len(words) - 1 and st.button("🏁 Закончить"):
        st.session_state.page = "start"

elif st.session_state.page == "stats":
    st.header("📊 Статистика по словам")
    for word in sorted(st.session_state.stats.keys()):
        right = st.session_state.stats[word]["right"]
        wrong = st.session_state.stats[word]["wrong"]
        st.write(f"**{word}** — ✅ {right} / ❌ {wrong}")
    if st.button("🔙 Назад"):
        st.session_state.page = "start"
