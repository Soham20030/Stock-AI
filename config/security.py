import os
import hmac

# Default developer password retrieved from environment variables
DEVELOPER_PASSWORD = os.getenv("DEVELOPER_PASSWORD", "change-me")


def get_developer_password() -> str:
    """
    Retrieves the current developer password from environment variables or fallback default.

    Returns:
        str: Active developer mode password.
    """
    return os.getenv("DEVELOPER_PASSWORD", DEVELOPER_PASSWORD)


def verify_developer_password(input_password: str) -> bool:
    """
    Verifies the provided input password against the configured DEVELOPER_PASSWORD
    using constant-time string comparison to prevent timing side-channel attacks.

    Parameters:
        input_password (str): Password string provided by user.

    Returns:
        bool: True if input matches expected developer password, False otherwise.
    """
    if not input_password:
        return False

    expected_password = get_developer_password()
    return hmac.compare_digest(
        input_password.encode("utf-8"),
        expected_password.encode("utf-8")
    )
