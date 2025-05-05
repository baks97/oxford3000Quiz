# Подготовка финальной версии кода квиза в виде одного файла, с учетом всех требований
quiz_code = """
import streamlit as st
import random
import json
import os

MD_FILE = "quiz.md"
STATS_FILE = "stats.json"

# Чтение и парсинг MD-файла
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

            for j in range(i+3, len(lines)):
                if lines[j].startswith("### 🧾"):
                    examples_start = j
                    break
            else:
                examples_start = None

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

# Статистика: чтение и запись
def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# Начальные значения
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

# Стартовая страница
if st.session_state.page == "start":
    st.title("🧠 Английский квиз по словам")
    st.subheader("Выберите количество слов:")

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

    if st.button("📊 Показать статистику"):
        st.session_state.page = "stats"
        st.experimental_rerun()

# Квиз
elif st.session_state.page == "quiz":
    word = st.session_state.words[st.session_state.index]

    st.markdown(f"## {word['word']}")
    st.markdown(f"**{word['transcription']}**")
    st.markdown(f"*{word['part_of_speech']}*")
    st.markdown("---")
    st.markdown("### 🧾 Примеры (Oxford)")
    st.markdown(word['examples'])

    if st.session_state.show:
        st.markdown(word['extra'])

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("❌ Неправильно"):
            st.session_state.answers.append((word['word'], False))
            st.session_state.stats.setdefault(word['word'], {"right": 0, "wrong": 0})
            st.session_state.stats[word['word']]["wrong"] += 1
            save_stats(st.session_state.stats)
            st.session_state.index += 1
            st.session_state.show = False
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

    if st.session_state.index >= len(st.session_state.words):
        st.session_state.page = "result"
        st.experimental_rerun()

# Результаты
elif st.session_state.page == "result":
    st.title("📋 Результаты")
    for word, correct in st.session_state.answers:
        if correct:
            st.success(word)
        else:
            st.error(word)
            full = next((w for w in st.session_state.words if w['word'] == word), None)
            if full:
                st.markdown(f"**{full['transcription']}**")
                st.markdown(f"*{full['part_of_speech']}*")
                st.markdown("### 🧾 Примеры (Oxford)")
                st.markdown(full['examples'])
                st.markdown(full['extra'])

    if st.button("🔁 Начать заново"):
        st.session_state.page = "start"
        st.experimental_rerun()

# Показ всего файла
elif st.session_state.page == "full":
    st.title("📚 Все слова")
    all_words = parse_md_file(MD_FILE)
    for word in sorted(all_words, key=lambda w: w['word']):
        st.markdown(f"## {word['word']}")
        st.markdown(f"**{word['transcription']}**")
        st.markdown(f"*{word['part_of_speech']}*")
        st.markdown("### 🧾 Примеры (Oxford)")
        st.markdown(word['examples'])
        st.markdown(word['extra'])
        st.markdown("---")
    if st.button("⬅️ Назад"):
        st.session_state.page = "start"
        st.experimental_rerun()

# Статистика
elif st.session_state.page == "stats":
    st.title("📊 Статистика по словам")
    if st.session_state.stats:
        for word, data in st.session_state.stats.items():
            st.write(f"**{word}** — ✅ {data['right']} / ❌ {data['wrong']}")
    else:
        st.info("Статистика пока пуста.")
    if st.button("⬅️ Назад"):
        st.session_state.page = "start"
        st.experimental_rerun()
"""

# Сохраняем этот код в файл
with open("/mnt/data/oxford_quiz_app.py", "w", encoding="utf-8") as f:
    f.write(quiz_code)

"/mnt/data/oxford_quiz_app.py"
