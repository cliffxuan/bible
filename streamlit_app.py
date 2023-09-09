import streamlit as st

from bible import get_from_esv


def main():
    st.header("ESV Bible")
    query = st.text_input(
        "search", value="Psalm8", placeholder="Psalm8 | Ps8 | Ps8:1-3 | Ps8v1-3"
    )
    st.markdown(f"```\n{get_from_esv(query=query)}\n```")


if __name__ == "__main__":
    main()
