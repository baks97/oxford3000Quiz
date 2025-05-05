import streamlit as st
import random
import json
import os

MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

st.set_page_config(page_title="🧠 Английский квиз", layout="wide")

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def parse_md_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    entries = content.strip().split("## 🔤 ")
    words = []
    for entry in entries[1:]:
        lines = entry.strip().splitlines()
        if len(lines) < 3:
            continue

        word = lines[0].strip()
        transcription = lines[1].strip()
        part_of_speech = lines[2].strip()

        # Находим индекс начала примеров
        example_start = next((i for i, line in enumerate(lines) if line.startswith("### 🧾")), None)
        if example_start is None:
            continue

        examples = "\n".join(lines[example_start:])
        rest_info = "\n".join(lines[3:example_start])

        words.append({
            "word": word,
            "transcription": transcription,
            "pos": part_of_speech,
            "examples": examples,
            "rest": rest_info
        })

    return words

# ---- Загрузка данных ----
words_all = parse_md_file(MD_FILE)
stats = load_stats()

# ---- Начальное состояние ----
if "page" not in st.session_state:
    st.session_state.page = "start"
if "words" not in st.session_state:
    st.session_state.words = []
if "current" not in st.session_state:
    st.session_state.current = 0
if "correct" not in st.session_state:
    st.session_state.correct = []
if "incorrect" not in st.session_state:
    st.session_state.incorrect = []
if "show" not in st.session_state:
    st.session_state.show = False

# ---- Стартовая страница ----
if st.session_state.page == "start":
    st.title("🧠 Английский квиз по словам")
    st.subheader("Выберите количество слов:")

    col1, col2, col3, col4 = st.columns(4)
    for i, n in enumerate([7, 15, 20, 25]):
        with [col1, col2, col3, col4][i]:
            if st.button(f"{n} слов", key=f"btn_{n}"):
                if len(words_all) < n:
                    st.error("Недостаточно слов в базе.")
                else:
                    st.session_state.words = random.sample(words_all, n)
                    st.session_state.page = "quiz"
                    st.session_state.current = 0
                    st.session_state.correct = []
                    st.session_state.incorrect = []
                    st.session_state.show = False
                    st.experimental_rerun()

    st.markdown("### ")
    if st.button("📄 Показать весь файл"):
        st.session_state.words = sorted(words_all, key=lambda x: x["word"].lower())
        st.session_state.page = "quiz"
        st.session_state.current = 0
        st.session_state.correct = []
        st.session_state.incorrect = []
        st.session_state.show = True
        st.experimental_rerun()

    if st.button("📊 Показать статистику"):
        st.session_state.page = "stats"
        st.experimental_rerun()

# ---- Квиз ----
elif st.session_state.page == "quiz":
    word = st.session_state.words[st.session_state.current]

    st.markdown(f"## 🔤 {word['word']}")
    st.markdown(word['transcription'])
    st.markdown(word['pos'])

    # Показываем только примеры — всегда
    st.markdown(word['examples'])

    # Остальная информация — только по кнопке
    if st.session_state.show:
        st.markdown(word['rest'])

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("❌ Неправильно"):
            st.session_state.incorrect.append(word)
            stats[word['word']] = stats.get(word['word'], {"correct": 0, "wrong": 0})
            stats[word['word']]["wrong"] += 1
            save_stats(stats)
            st.session_state.current += 1
            st.session_state.show = False
            st.experimental_rerun()
    with col2:
        if st.button("👁️ Показать значение" if not st.session_state.show else "🙈 Скрыть значение"):
            st.session_state.show = not st.session_state.show
            st.experimental_rerun()
    with col3:
        if st.button("✅ Правильно"):
            st.session_state.correct.append(word)
            stats[word['word']] = stats.get(word['word'], {"correct": 0, "wrong": 0})
            stats[word['word']]["correct"] += 1
            save_stats(stats)
            st.session_state.current += 1
            st.session_state.show = False
            st.experimental_rerun()

    # Переход к результатам
    if st.session_state.current >= len(st.session_state.words):
        st.session_state.page = "result"
        st.experimental_rerun()

# ---- Результаты ----
elif st.session_state.page == "result":
    st.header("✅ Результаты")
    st.write(f"Правильно: {len(st.session_state.correct)}")
    st.write(f"Неправильно: {len(st.session_state.incorrect)}")

    for word in st.session_state.incorrect:
        st.markdown("---")
        st.markdown(f"## 🔤 {word['word']}")
        st.markdown(word['transcription'])
        st.markdown(word['pos'])
        st.markdown(word['examples'])
        st.markdown(word['rest'])

    if st.button("🔄 Начать заново"):
        st.session_state.page = "start"
        st.experimental_rerun()

# ---- Статистика ----
elif st.session_state.page == "stats":
    st.header("📊 Статистика ответов")
    for word in sorted(stats.keys()):
        stat = stats[word]
        st.markdown(f"**{word}** — ✅ {stat['correct']} | ❌ {stat['wrong']}")

    if st.button("🔙 Назад"):
        st.session_state.page = "start"
        st.experimental_rerun()
