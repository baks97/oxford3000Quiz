# Подготовка полного кода квиза на Streamlit в виде строки
full_code = '''
import streamlit as st
import random
import json

MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

def parse_md_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    words = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("## 🔤 "):
            word_entry = {
                "word": lines[i][5:].strip(),
                "transcription": lines[i+1] if i+1 < len(lines) else "",
                "part_of_speech": lines[i+2] if i+2 < len(lines) else "",
                "examples": "",
                "extra": "",
            }

            # Поиск блока ### 🧾
            for j in range(i+3, len(lines)):
                if lines[j].startswith("### 🧾"):
                    examples_start = j
                    break
            else:
                examples_start = None

            # Поиск следующего слова
            for j in range(i+1, len(lines)):
                if lines[j].startswith("## 🔤 "):
                    next_word_start = j
                    break
            else:
                next_word_start = len(lines)

            if examples_start is not None:
                word_entry["examples"] = "\\n".join(lines[examples_start:next_word_start])
                word_entry["extra"] = "\\n".join(lines[i+3:examples_start])
            else:
                word_entry["examples"] = ""
                word_entry["extra"] = "\\n".join(lines[i+3:next_word_start])

            words.append(word_entry)
            i = next_word_start
        else:
            i += 1
    return words

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def load_stats():
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

st.set_page_config(page_title="🧠 Английский квиз", layout="wide")

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

if st.session_state.page == "start":
    st.title("🧠 Английский квиз по словам")
    st.subheader("Выберите количество слов для квиза:")

    col1, col2, col3, col4 = st.columns(4)
    for col, n in zip([col1, col2, col3, col4], [7, 15, 20, 25]):
        with col:
            if st.button(f"{n} слов"):
                st.session_state.seed = random.randint(1, 999999)
                random.seed(st.session_state.seed)
                all_words = parse_md_file(MD_FILE)
                st.session_state.words = random.sample(all_words, n)
                st.session_state.page = "quiz"
                st.session_state.index = 0
                st.session_state.answers = []
                st.session_state.show = False
                st.experimental_rerun()

    st.write("📂 Или показать весь список слов")
    if st.button("Показать весь файл"):
        st.session_state.page = "full"
        st.experimental_rerun()

elif st.session_state.page == "quiz":
    word = st.session_state.words[st.session_state.index]
    st.markdown(f"## 🔤 {word['word']}")
    st.markdown(word['transcription'])
    st.markdown(word['part_of_speech'])
    st.markdown("### 🧾 Примеры")
    st.markdown(word['examples'])

    if st.session_state.show:
        st.markdown(word['extra'])

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("❌ Неправильно"):
            st.session_state.answers.append((word['word'], False))
            st.session_state.stats.setdefault(word['word'], {"right": 0, "wrong": 0})
            st.session_state.stats[word['word']]["wrong"] += 1
            save_stats(st.session_state.stats)
            st.session_state.index += 1
            st.session_state.show = False
            st.experimental_rerun()
    with col2:
        if st.button("👁 Показать значение" if not st.session_state.show else "🙈 Скрыть значение"):
            st.session_state.show = not st.session_state.show
    with col3:
        if st.button("✅ Правильно"):
            st.session_state.answers.append((word['word'], True))
            st.session_state.stats.setdefault(word['word'], {"right": 0, "wrong": 0})
            st.session_state.stats[word['word']]["right"] += 1
            save_stats(st.session_state.stats)
            st.session_state.index += 1
            st.session_state.show = False
            st.experimental_rerun()

    if st.session_state.index >= len(st.session_state.words):
        st.session_state.page = "result"
        st.experimental_rerun()

elif st.session_state.page == "result":
    st.title("🎉 Результаты квиза")
    for word, correct in st.session_state.answers:
        if correct:
            st.success(word)
        else:
            st.error(word)

    if st.button("🔄 Начать заново"):
        st.session_state.page = "start"
        st.experimental_rerun()

elif st.session_state.page == "full":
    st.title("📖 Полный список слов")
    all_words = parse_md_file(MD_FILE)
    for word in sorted(all_words, key=lambda w: w["word"].lower()):
        st.markdown(f"## 🔤 {word['word']}")
        st.markdown(word['transcription'])
        st.markdown(word['part_of_speech'])
        st.markdown("### 🧾 Примеры")
        st.markdown(word['examples'])
        st.markdown(word['extra'])

    if st.button("🔙 Назад"):
        st.session_state.page = "start"
        st.experimental_rerun()

elif st.session_state.page == "stats":
    st.title("📊 Статистика по словам")
    stats = load_stats()
    for word, data in stats.items():
        total = data["right"] + data["wrong"]
        accuracy = (data["right"] / total * 100) if total else 0
        st.write(f"**{word}** — ✅ {data['right']} / ❌ {data['wrong']} — точность: {accuracy:.1f}%")

    if st.button("🔙 Назад"):
        st.session_state.page = "start"
        st.experimental_rerun()
'''
