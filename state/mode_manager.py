import streamlit as st

# Application Mode Constants
MODE_USER = "user"
MODE_DEVELOPER = "developer"


def init_mode_state():
    """
    Initializes the application mode in Streamlit session state.
    Defaults to 'user' mode on initial startup.
    """
    if "mode" not in st.session_state:
        st.session_state["mode"] = MODE_USER


def get_mode() -> str:
    """
    Gets the currently active application mode ('user' or 'developer').

    Returns:
        str: Current mode string.
    """
    init_mode_state()
    return st.session_state.get("mode", MODE_USER)


def set_mode(new_mode: str):
    """
    Sets the active application mode in Streamlit session state.

    Parameters:
        new_mode (str): 'user' or 'developer'.
    """
    if new_mode in [MODE_USER, MODE_DEVELOPER]:
        st.session_state["mode"] = new_mode


def is_user_mode() -> bool:
    """
    Checks if the active application mode is User Mode.

    Returns:
        bool: True if in user mode, False otherwise.
    """
    return get_mode() == MODE_USER


def is_developer_mode() -> bool:
    """
    Checks if the active application mode is Developer Mode.

    Returns:
        bool: True if in developer mode, False otherwise.
    """
    return get_mode() == MODE_DEVELOPER


def toggle_mode():
    """
    Toggles the active mode between User and Developer.
    """
    current = get_mode()
    new_mode = MODE_DEVELOPER if current == MODE_USER else MODE_USER
    set_mode(new_mode)
