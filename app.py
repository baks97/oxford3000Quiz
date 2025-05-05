import streamlit as st
import random
import json
import os
import re

MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

# Чтение и парсинг .md файла
def parse_md_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = content.split("## 🔤 ")
    words = []
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        word = lines[0].strip()
        transcription = lines[1].strip() if len(lines) > 1 else ""
        part_of_speech = lines[2].strip() if len(lines) > 2 else ""

        examples_oxford = []
        cambridge_block = []
        loading = False

        for i, line in enumerate(lines):
            if line.startswith("### 🧾"):
                loading = "examples"
            elif line.startswith("### 🌍"):
                loading = "cambridge"
            elif line.startswith("###"):
                loading = False
            elif loading == "examples":
                examples_oxford.append(line)
            elif loading == "cambridge":
                cambridge_block.append(line)

        words.append({
            "word": word,
            "transcription": transcription,
            "part_of_speech": part_of_speech,
            "examples": "\n".join(examples_oxford).strip(),
            "cambridge": "\n".join(cambridge_block).strip()
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

# Инициализация состояний
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

# Начальный экран
if st.session_state.page == "start":
    st.title("🧠 Английский квиз по словам")
    st.subheader("Выберите количество слов:")

    cols = st.columns(4)
    for i, count in enumerate([7, 15, 20, 25]):
        if cols[i].button(str(count)):
            all_words = parse_md_file(MD_FILE)
            random.shuffle(all_words)
            st.session_state.words = all_words[:count]
            st.session_state.index = 0
            st.session_state.answers = []
            st.session_state.show = False
            st.session_state.page = "quiz"

    st.write("Или:")
    if st.button("📂 Показать весь файл"):
        st.session_state.words = sorted(parse_md_file(MD_FILE), key=lambda x: x["word"].lower())
        st.session_state.page = "all"

    if st.button("📈 Показать статистику"):
        st.session_state.page = "stats"

# Экран статистики
elif st.session_state.page == "stats":
    st.title("📊 Статистика")
    stats = st.session_state.stats
    for word, record in stats.items():
        st.markdown(f"**{word}** — ✅ {record.get('right', 0)}, ❌ {record.get('wrong', 0)}")

    if st.button("🔙 Назад"):
        st.session_state.page = "start"

# Экран всего файла
elif st.session_state.page == "all":
    st.title("📚 Все слова")
    for word in st.session_state.words:
        st.markdown(f"### {word['word']}")
        st.markdown(word['transcription'])
        st.markdown(word['part_of_speech'])
        st.markdown(word['examples'])
        st.markdown(word['cambridge'])

    if st.button("🔙 Назад"):
        st.session_state.page = "start"

# Основной квиз
elif st.session_state.page == "quiz":
    if st.session_state.index >= len(st.session_state.words):
        st.title("✅ Результаты")
        for word, correct in st.session_state.answers:
            color = "green" if correct else "red"
            st.markdown(f"<span style='color:{color}'>{word}</span>", unsafe_allow_html=True)
        if st.button("🔁 Начать заново"):
            st.session_state.page = "start"
    else:
        word = st.session_state.words[st.session_state.index]
        st.markdown(f"### {word['word']}")
        st.markdown(word["transcription"])
        st.markdown(word["part_of_speech"])

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("❌ Неправильно"):
                st.session_state.answers.append((word['word'], False))
                if word['word'] not in st.session_state.stats:
                    st.session_state.stats[word['word']] = {"right": 0, "wrong": 0}
                st.session_state.stats[word['word']]["wrong"] += 1
                save_stats(st.session_state.stats)
                st.session_state.index += 1
                st.session_state.show = False

        with col2:
            if st.button("👁 Показать значение"):
                st.session_state.show = not st.session_state.show

        with col3:
            if st.button("✅ Правильно"):
                st.session_state.answers.append((word['word'], True))
                if word['word'] not in st.session_state.stats:
                    st.session_state.stats[word['word']] = {"right": 0, "wrong": 0}
                st.session_state.stats[word['word']]["right"] += 1
                save_stats(st.session_state.stats)
                st.session_state.index += 1
                st.session_state.show = False

        if st.session_state.show:
            st.markdown(word["examples"])
            st.markdown(word["cambridge"])
