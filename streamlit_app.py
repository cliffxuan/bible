import streamlit as st
from PIL import Image

from bible import get_from_esv, parse_query

st.set_page_config(page_title="ESV Bible", page_icon=Image.open("favicon.png"))


def get_prev_next_chapters(query: str) -> tuple[str, str]:
    start_verse, end_verse = parse_query(query)
    if start_verse.chapter_number == 1:
        prev_book = start_verse.book.prev()
        prev_chapter = f"{prev_book.name.lower()}{prev_book.chapter_count}"
    else:
        prev_chapter = (
            f"{start_verse.book.name.lower()}{max(start_verse.chapter_number - 1, 1)}"
        )
    cur_verse = end_verse or start_verse
    if cur_verse.chapter_number < cur_verse.book.chapter_count:
        next_chapter = f"{cur_verse.book.name.lower()}{cur_verse.chapter_number + 1}"
    else:
        next_chapter = f"{cur_verse.book.next().name.lower()}1"
    return prev_chapter, next_chapter


def set_search_query(query: str):
    st.session_state.query = query


def get_search_query() -> str:
    return st.session_state.setdefault("query", "Psalm8")


def main():
    st.header("ESV Bible")
    cols = st.columns([5, 1])
    query = cols[0].text_input(
        "search",
        value=get_search_query(),
        placeholder="search pattern: Psalm8 | Ps8 | Ps8:1-3 | Ps8v1-3",
        label_visibility="collapsed",
    )
    if not query.strip():
        return
    prev_chapter, next_chapter = get_prev_next_chapters(query)
    if cols[1].toggle(":scroll:"):
        text = get_from_esv(query=query, strict=False)
        st.markdown(f"```\n{text}\n```")
    else:
        text = get_from_esv(query=query, strict=True)
        st.markdown(text, unsafe_allow_html=True)
    cols = st.columns([1, 6, 1])
    cols[0].button(
        ":arrow_backward:", on_click=set_search_query, kwargs={"query": prev_chapter}
    )
    cols[-1].button(
        ":arrow_forward:", on_click=set_search_query, kwargs={"query": next_chapter}
    )


if __name__ == "__main__":
    main()
