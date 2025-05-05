# Импорт необходимых библиотек
import streamlit as st
import random
import json
import os
import time

# Константы
MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

# Функция для парсинга markdown-файла
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

        example_start = next((i for i, line in enumerate(lines) if line.startswith("### 🧾")), None)
        cambridge_start = next((i for i, line in enumerate(lines) if line.startswith("### 🌍")), None)

        if example_start is None:
            continue

        examples = "\n".join(lines[example_start : cambridge_start if cambridge_start else None])
        rest_info = "\n".join(lines[3 : example_start])
        cambridge_info = "\n".join(lines[cambridge_start:]) if cambridge_start else ""

        words.append({
            "word": word,
            "transcription": transcription,
            "pos": part_of_speech,
            "examples": examples,
            "rest": rest_info,
            "cambridge": cambridge_info
        })

    return words

# Загрузка и сохранение статистики
def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# Инициализация session_state
if "page" not in st.session_state:
    st.session_state.page = "start"
if "words" not in st.session_state:
    st.session_state.words = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "show" not in st.session_state:
    st.session_state.show = False
if "stats" not in st.session_state:
    st.session_state.stats = load_stats()
if "view_all" not in st.session_state:
    st.session_state.view_all = False

# Главная страница
if st.session_state.page == "start":
    st.markdown("## 🧠 Английский квиз по словам\n")
    st.write("Выберите количество слов:")
    col1, col2, col3, col4 = st.columns(4)
    for i, num in enumerate([7, 15, 20, 25]):
        with [col1, col2, col3, col4][i]:
            if st.button(str(num)):
                st.session_state.words = random.sample(parse_md_file(MD_FILE), num)
                st.session_state.index = 0
                st.session_state.answers = []
                st.session_state.show = False
                st.session_state.page = "quiz"
                time.sleep(0.01)
                st.experimental_rerun()

    st.write("Или:")
    if st.button("📂 Показать весь файл"):
        st.session_state.words = sorted(parse_md_file(MD_FILE), key=lambda x: x['word'])
        st.session_state.index = 0
        st.session_state.view_all = True
        st.session_state.page = "quiz"
        time.sleep(0.01)
        st.experimental_rerun()

    if st.button("📊 Показать статистику"):
        st.session_state.page = "stats"
        st.experimental_rerun()

# Квиз
elif st.session_state.page == "quiz":
    words = st.session_state.words
    i = st.session_state.index

    word = words[i]
    st.markdown(f"### {word['word']}")
    st.markdown(word['transcription'])
    st.markdown(f"*{word['pos']}*")
    st.markdown(word['examples'])  # всегда показывать 🧾

    # Колонки для кнопок
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("✅ Правильно"):
            st.session_state.answers.append((word['word'], True))
            st.session_state.stats[word['word']] = st.session_state.stats.get(word['word'], {"right": 0, "wrong": 0})
            st.session_state.stats[word['word']]["right"] += 1
            save_stats(st.session_state.stats)
            if i + 1 < len(words):
                st.session_state.index += 1
                st.session_state.show = False
            else:
                st.session_state.page = "result"
            st.experimental_rerun()

    with col2:
        label = "🔽 Показать значение" if not st.session_state.show else "🔼 Скрыть значение"
        if st.button(label):
            st.session_state.show = not st.session_state.show
            st.experimental_rerun()

    with col3:
        if st.button("❌ Неправильно"):
            st.session_state.answers.append((word['word'], False))
            st.session_state.stats[word['word']] = st.session_state.stats.get(word['word'], {"right": 0, "wrong": 0})
            st.session_state.stats[word['word']]["wrong"] += 1
            save_stats(st.session_state.stats)
            if i + 1 < len(words):
                st.session_state.index += 1
                st.session_state.show = False
            else:
                st.session_state.page = "result"
            st.experimental_rerun()

    if st.session_state.show:
        st.markdown(word["rest"])
        st.markdown(word["cambridge"])

# Результаты
elif st.session_state.page == "result":
    st.markdown("## 📝 Результаты")
    correct = [w for w, res in st.session_state.answers if res]
    incorrect = [w for w, res in st.session_state.answers if not res]

    st.success(f"Правильно: {len(correct)}")
    st.error(f"Неправильно: {len(incorrect)}")

    if incorrect:
        with st.expander("❗ Неправильно отвеченные слова"):
            for word in [w for w, res in st.session_state.answers if not res]:
                wdata = next(item for item in st.session_state.words if item['word'] == word)
                st.markdown(f"### {wdata['word']}")
                st.markdown(wdata['transcription'])
                st.markdown(f"*{wdata['pos']}*")
                st.markdown(wdata["examples"])
                st.markdown(wdata["rest"])
                st.markdown(wdata["cambridge"])
                st.markdown("---")

    st.markdown(" ")
    st.markdown(" ")
    if st.button("🔁 Начать заново"):
        st.session_state.page = "start"
        st.session_state.view_all = False
        st.experimental_rerun()

# Статистика
elif st.session_state.page == "stats":
    st.markdown("## 📊 Статистика по словам")
    stats = st.session_state.stats
    if stats:
        for word, data in sorted(stats.items()):
            st.markdown(f"**{word}** — ✅ {data['right']} / ❌ {data['wrong']}")
    else:
        st.write("Нет данных статистики.")

    if st.button("⬅ Назад"):
        st.session_state.page = "start"
        st.experimental_rerun()
