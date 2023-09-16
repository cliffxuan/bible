from dataclasses import dataclass

import streamlit as st
from PIL import Image

from bible import get_from_esv, parse_query

st.set_page_config(page_title="ESV Bible", page_icon=Image.open("favicon.png"))


@dataclass(eq=True)
class Props:
    query: str = "Gen1"

    def set_search_query(self, query: str):
        query = query.strip()
        if query:
            self.query = query


props = st.session_state.setdefault("props", Props())


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


def top_bar():
    cols = st.columns([5, 1])
    cols[0].text_input(
        "search",
        value=props.query,
        placeholder="search pattern: Psalm8 | Ps8 | Ps8:1-3 | Ps8v1-3",
        label_visibility="collapsed",
        key="query",
        on_change=lambda: props.set_search_query(st.session_state.query),
    )
    cols[1].toggle(":scroll:", key="show_raw")


def bottom_bar(query: str):
    prev_chapter, next_chapter = get_prev_next_chapters(query)
    cols = st.columns([1, 6, 1])
    cols[0].button(
        ":arrow_backward:", on_click=lambda: props.set_search_query(prev_chapter)
    )
    cols[-1].button(
        ":arrow_forward:", on_click=lambda: props.set_search_query(next_chapter)
    )


def main():
    st.header("ESV Bible")
    top_bar()
    if st.session_state.show_raw:
        text = get_from_esv(query=props.query, strict=False)
        st.markdown(f"```\n{text}\n```")
    else:
        text = get_from_esv(query=props.query, strict=True)
        st.markdown(text, unsafe_allow_html=True)

    bottom_bar(props.query)


if __name__ == "__main__":
    main()
