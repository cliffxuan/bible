import streamlit as st

from bible import get_from_esv


def main():
    st.header("ESV Bible")
    cols = st.columns([5, 1])
    query = cols[0].text_input(
        "search", value="Psalm8", placeholder="Psalm8 | Ps8 | Ps8:1-3 | Ps8v1-3",
        label_visibility="collapsed"
    )
    if cols[1].toggle(":scroll:"):
        st.markdown(f"```\n{get_from_esv(query=query)}\n```")
    else:
        st.markdown(get_from_esv(query=query))


if __name__ == "__main__":
    main()
