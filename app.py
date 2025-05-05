import streamlit as st
import random
import json
import os

MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

st.set_page_config(layout="wide", page_title="🧠 Английский квиз", page_icon="🧠")

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

        example_start = next((i for i, line in enumerate(lines) if line.strip().startswith("### 🧾")), None)
        if example_start is None:
            continue

        rest_info = "\n".join(lines[3:example_start])
        examples = "\n".join(lines[example_start:])

        words.append({
            "word": word,
            "transcription": transcription,
            "pos": part_of_speech,
            "rest": rest_info,
            "examples": examples
        })

    return words

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

words_all = parse_md_file(MD_FILE)
stats = load_stats()

if "page" not in st.session_state:
    st.session_state.page = "start"

if st.session_state.page == "start":
    st.title("🧠 Английский квиз по словам")
    st.subheader("Выберите количество слов:")

    col1, col2, col3, col4 = st.columns(4)
    for col, n in zip([col1, col2, col3, col4], [7, 15, 20, 25]):
        if col.button(f"{n} слов"):
            if len(words_all) < n:
                st.error(f"Недостаточно слов в файле для {n} слов.")
            else:
                selected = random.sample(words_all, n)
                st.session_state.words = selected
                st.session_state.page = "quiz"
                st.session_state.current = 0
                st.session_state.correct = []
                st.session_state.incorrect = []
                st.session_state.show = False
                st.stop()  # завершает выполнение, без перезагрузки

    st.markdown("---")
    if st.button("📂 Показать весь список слов"):
        st.session_state.page = "all"
        st.experimental_rerun()

    if st.button("📊 Показать статистику"):
        st.session_state.page = "stats"
        st.experimental_rerun()

elif st.session_state.page == "quiz":
    idx = st.session_state.current
    word = st.session_state.words[idx]

    st.markdown(f"### 🔤 {word['word']}")
    st.markdown(f"{word['transcription']}")
    st.markdown(f"{word['pos']}")
    st.markdown("---")
    st.markdown(word['examples'])

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("✅ Правильно"):
            st.session_state.correct.append(word)
            stats[word["word"]] = stats.get(word["word"], {"correct": 0, "incorrect": 0})
            stats[word["word"]]["correct"] += 1
            save_stats(stats)
            st.session_state.current += 1
            st.session_state.show = False
            st.experimental_rerun()
    with col2:
        if st.button("❌ Неправильно"):
            st.session_state.incorrect.append(word)
            stats[word["word"]] = stats.get(word["word"], {"correct": 0, "incorrect": 0})
            stats[word["word"]]["incorrect"] += 1
            save_stats(stats)
            st.session_state.current += 1
            st.session_state.show = False
            st.experimental_rerun()
    with col3:
        if st.button("👁 Показать значение" if not st.session_state.show else "🙈 Скрыть значение"):
            st.session_state.show = not st.session_state.show

    if st.session_state.show:
        st.markdown("---")
        st.markdown(word["rest"])

    if st.session_state.current >= len(st.session_state.words):
        st.session_state.page = "result"
        st.experimental_rerun()

elif st.session_state.page == "result":
    st.title("✅ Результаты")
    st.success(f"Правильных: {len(st.session_state.correct)}")
    st.error(f"Неправильных: {len(st.session_state.incorrect)}")

    if st.session_state.incorrect:
        st.markdown("### ❌ Ошибки:")
        for word in st.session_state.incorrect:
            st.markdown(f"**{word['word']}** {word['transcription']} {word['pos']}")
            st.markdown(word["examples"])
            st.markdown("---")

    if st.button("🔁 Начать заново"):
        st.session_state.page = "start"
        st.experimental_rerun()

elif st.session_state.page == "all":
    st.title("📖 Полный список слов")
    for word in sorted(words_all, key=lambda w: w["word"].lower()):
        st.markdown(f"### 🔤 {word['word']}")
        st.markdown(f"{word['transcription']}")
        st.markdown(f"{word['pos']}")
        st.markdown(word["examples"])
        st.markdown("---")

    if st.button("⬅️ Назад"):
        st.session_state.page = "start"
        st.experimental_rerun()

elif st.session_state.page == "stats":
    st.title("📊 Статистика")
    if not stats:
        st.info("Статистика пока пуста.")
    else:
        for word, data in stats.items():
            st.markdown(f"**{word}** — ✅ {data['correct']} / ❌ {data['incorrect']}")
    if st.button("⬅️ Назад"):
        st.session_state.page = "start"
        st.experimental_rerun()
