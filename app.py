import streamlit as st
import random
import json
from pathlib import Path

MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

# =================== Парсинг markdown =========================
def parse_md_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    entries = content.strip().split("## 🔤 ")
    words = []
    for entry in entries[1:]:
        lines = entry.strip().splitlines()
        if len(lines) < 3:
            continue  # пропускаем неполный блок

        word = lines[0].strip()
        transcription = lines[1].strip()
        part_of_speech = lines[2].strip()

        example_start = next((i for i, line in enumerate(lines) if line.strip().startswith("### 🧾")), None)
        rest_info = "\n".join(lines[3:example_start]) if example_start else ""
        examples = "\n".join(lines[example_start:]) if example_start else ""

        words.append({
            "word": word,
            "transcription": transcription,
            "pos": part_of_speech,
            "rest": rest_info,
            "examples": examples
        })

    return words

# =================== Загрузка и сохранение статистики =========================
def load_stats():
    if Path(STATS_FILE).exists():
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# =================== Streamlit интерфейс =========================

st.set_page_config(page_title="Английский Квиз", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "menu"
    st.session_state.words = []
    st.session_state.current = 0
    st.session_state.correct = []
    st.session_state.incorrect = []
    st.session_state.show = False

words_all = parse_md_file(MD_FILE)

# ===== Главный экран =====
if st.session_state.page == "menu":
    st.title("🧠 Английский квиз по словам")
    st.write("Выберите количество слов:")

    col1, col2, col3, col4 = st.columns(4)
    for col, n in zip([col1, col2, col3, col4], [7, 15, 20, 25]):
        if col.button(f"{n} слов"):
            selected = random.sample(words_all, n)
            st.session_state.words = selected
            st.session_state.page = "quiz"
            st.session_state.current = 0
            st.session_state.correct = []
            st.session_state.incorrect = []
            st.session_state.show = False
            st.experimental_rerun()

    st.markdown("### 📊 Или посмотрите статистику")
    if st.button("Показать статистику"):
        st.session_state.page = "stats"
        st.experimental_rerun()

    if st.button("Показать весь список слов"):
        st.session_state.page = "all_words"
        st.experimental_rerun()

# ===== Экран квиза =====
elif st.session_state.page == "quiz":
    idx = st.session_state.current
    word = st.session_state.words[idx]

    st.markdown(f"## 🔤 {word['word']}")
    st.markdown(word['transcription'])
    st.markdown(word['pos'])
    st.markdown("### 🧾 Примеры (Oxford)")
    st.markdown(word['examples'])

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("✅ Правильно", key=f"right_{idx}"):
            st.session_state.correct.append(word['word'])
            st.session_state.current += 1
            st.session_state.show = False
            st.experimental_rerun()

    with col2:
        if st.button("❌ Неправильно", key=f"wrong_{idx}"):
            st.session_state.incorrect.append(word['word'])
            st.session_state.current += 1
            st.session_state.show = False
            st.experimental_rerun()

    with col3:
        if st.button("👁 Показать значение" if not st.session_state.show else "🙈 Скрыть значение", key=f"show_{idx}"):
            st.session_state.show = not st.session_state.show
            st.experimental_rerun()

    if st.session_state.show:
        st.markdown(word["rest"])

    # Завершение
    if st.session_state.current >= len(st.session_state.words):
        # обновим статистику
        stats = load_stats()
        for w in st.session_state.correct:
            stats.setdefault(w, {"right": 0, "wrong": 0})
            stats[w]["right"] += 1
        for w in st.session_state.incorrect:
            stats.setdefault(w, {"right": 0, "wrong": 0})
            stats[w]["wrong"] += 1
        save_stats(stats)

        st.session_state.page = "results"
        st.experimental_rerun()

# ===== Результаты =====
elif st.session_state.page == "results":
    st.title("📋 Результаты")

    st.success(f"✅ Правильных: {len(st.session_state.correct)}")
    st.error(f"❌ Неправильных: {len(st.session_state.incorrect)}")

    if st.session_state.incorrect:
        st.markdown("### ❗ Слова с ошибками:")
        for word in st.session_state.words:
            if word["word"] in st.session_state.incorrect:
                st.markdown(f"**{word['word']}** {word['transcription']} {word['pos']}")
                st.markdown(word["examples"])
                st.markdown(word["rest"])

    if st.button("🔁 Начать заново"):
        st.session_state.page = "menu"
        st.experimental_rerun()

# ===== Статистика =====
elif st.session_state.page == "stats":
    st.title("📊 Статистика")
    stats = load_stats()
    for word in sorted(stats.keys()):
        entry = stats[word]
        st.markdown(f"**{word}** — ✅ {entry['right']} / ❌ {entry['wrong']}")
    if st.button("🔙 Назад"):
        st.session_state.page = "menu"
        st.experimental_rerun()

# ===== Весь список =====
elif st.session_state.page == "all_words":
    st.title("📚 Весь список слов")
    for word in sorted(words_all, key=lambda w: w["word"].lower()):
        st.markdown(f"## 🔤 {word['word']}")
        st.markdown(word['transcription'])
        st.markdown(word['pos'])
        st.markdown("### 🧾 Примеры (Oxford)")
        st.markdown(word['examples'])
        st.markdown(word["rest"])
        st.markdown("---")
    if st.button("🔙 Назад"):
        st.session_state.page = "menu"
        st.experimental_rerun()
