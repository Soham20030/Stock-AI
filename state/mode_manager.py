import streamlit as st

# Application Mode Constants
MODE_USER = "user"
MODE_DEVELOPER = "developer"

# Theme Constants
THEME_DARK = "dark"
THEME_LIGHT = "light"


def init_mode_state():
    """
    Initializes the application mode and theme in Streamlit session state.
    Defaults to 'user' mode and 'dark' theme on initial startup.
    """
    if "mode" not in st.session_state:
        st.session_state["mode"] = MODE_USER
    if "theme" not in st.session_state:
        st.session_state["theme"] = THEME_DARK


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


# -----------------------------------------------------------------------------
# THEME STATE HELPERS (DARK / LIGHT MODE)
# -----------------------------------------------------------------------------
def get_theme() -> str:
    """
    Gets the currently active UI theme ('dark' or 'light').

    Returns:
        str: Current theme string.
    """
    init_mode_state()
    return st.session_state.get("theme", THEME_DARK)


def set_theme(new_theme: str):
    """
    Sets the active UI theme in Streamlit session state.

    Parameters:
        new_theme (str): 'dark' or 'light'.
    """
    if new_theme in [THEME_DARK, THEME_LIGHT]:
        st.session_state["theme"] = new_theme


def is_dark_theme() -> bool:
    """
    Checks if the active UI theme is Dark Mode.

    Returns:
        bool: True if dark theme, False otherwise.
    """
    return get_theme() == THEME_DARK


def is_light_theme() -> bool:
    """
    Checks if the active UI theme is Light Mode.

    Returns:
        bool: True if light theme, False otherwise.
    """
    return get_theme() == THEME_LIGHT


def toggle_theme():
    """
    Toggles the active UI theme between Dark and Light Mode.
    """
    current = get_theme()
    new_theme = THEME_LIGHT if current == THEME_DARK else THEME_DARK
    set_theme(new_theme)
