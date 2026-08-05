import streamlit as st
from config.security import verify_developer_password

# Application Mode Constants
MODE_USER = "user"
MODE_DEVELOPER = "developer"

# Theme Constants
THEME_DARK = "dark"
THEME_LIGHT = "light"


def init_mode_state():
    """
    Initializes mode state, authentication status, and UI theme in Streamlit session state.
    Defaults to 'user' mode, unauthenticated developer status, and 'dark' theme on startup.
    """
    if "current_mode" not in st.session_state:
        st.session_state["current_mode"] = MODE_USER

    if "developer_authenticated" not in st.session_state:
        st.session_state["developer_authenticated"] = False

    # Sync backward-compatible 'mode' key with 'current_mode'
    st.session_state["mode"] = st.session_state["current_mode"]

    if "theme" not in st.session_state:
        st.session_state["theme"] = THEME_DARK


def get_mode() -> str:
    """
    Gets the currently active application mode ('user' or 'developer').

    Returns:
        str: Current mode string.
    """
    init_mode_state()
    return st.session_state.get("current_mode", MODE_USER)


def is_developer_authenticated() -> bool:
    """
    Checks if Developer Mode has been successfully authenticated in the current session.

    Returns:
        bool: True if authenticated, False otherwise.
    """
    init_mode_state()
    return bool(st.session_state.get("developer_authenticated", False))


def is_user_mode() -> bool:
    """
    Checks if the active application mode is User Mode or if developer authentication is cleared.

    Returns:
        bool: True if operating in user mode, False otherwise.
    """
    return get_mode() == MODE_USER or not is_developer_authenticated()


def is_developer_mode() -> bool:
    """
    Checks if Developer Mode is active AND authenticated.

    Returns:
        bool: True if in authenticated developer mode, False otherwise.
    """
    return get_mode() == MODE_DEVELOPER and is_developer_authenticated()


def set_mode(new_mode: str):
    """
    Sets the active mode. Switching to User Mode automatically resets developer authentication.

    Parameters:
        new_mode (str): 'user' or 'developer'.
    """
    init_mode_state()
    if new_mode == MODE_USER:
        reset_to_user_mode()
    elif new_mode == MODE_DEVELOPER:
        if is_developer_authenticated():
            st.session_state["current_mode"] = MODE_DEVELOPER
            st.session_state["mode"] = MODE_DEVELOPER


def authenticate_developer(password: str) -> bool:
    """
    Validates password and unlocks Developer Mode if correct.

    Parameters:
        password (str): Password provided by user.

    Returns:
        bool: True if authentication succeeded, False otherwise.
    """
    init_mode_state()
    if verify_developer_password(password):
        st.session_state["developer_authenticated"] = True
        st.session_state["current_mode"] = MODE_DEVELOPER
        st.session_state["mode"] = MODE_DEVELOPER
        return True
    return False


def reset_to_user_mode():
    """
    Resets the active mode to User Mode and clears developer authentication.
    """
    st.session_state["current_mode"] = MODE_USER
    st.session_state["mode"] = MODE_USER
    st.session_state["developer_authenticated"] = False


def toggle_mode():
    """
    Toggles between User Mode and Developer Mode if authenticated.
    """
    if is_developer_mode():
        reset_to_user_mode()
    else:
        st.session_state["current_mode"] = MODE_DEVELOPER
        st.session_state["mode"] = MODE_DEVELOPER


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
