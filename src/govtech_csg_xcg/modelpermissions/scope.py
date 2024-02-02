import threading
from contextlib import contextmanager

# set scope as `SCOPE_RBAC_IGNORE` will disable the permission check
SCOPE_RBAC_IGNORE = "rbac-ignore"


# Code ported from dongtai module
# ref: https://github.com/HXSecurity/DongTai-agent-python/blob/
# 93c56d48d69b0e93892a6cb68e70de05596cb902/dongtai_agent_python/utils/scope.py
class ScopeContext(threading.local):
    """This object is used to set a global flag temporarily"""

    def __init__(self):
        self._active_scopes = []

    @property
    def active_scopes(self):
        """Get all active scopes

        Returns:
            List: A list containing all active scopes
        """
        return self._active_scopes[:]

    @property
    def current_scope(self):
        """Get the current scope

        Returns:
            str : the last set scope
        """
        if len(self._active_scopes) == 0:
            return ""
        return self._active_scopes[-1][:]  # Slice to get copy.

    def enter_scope(self, name):
        """Enters the given scope, updating the list of active scopes.

        Args:
          name (str): scope name
        """
        self._active_scopes = self._active_scopes + [name]

    def exit_scope(self):
        """Exits the most recently entered scope."""
        self._active_scopes = self._active_scopes[:-1]

    def in_scope(self, name):
        """Check whether we are in the specified scope.

        Args:
            name (str): the name of the scope.

        Returns:
            bool: the flag determines whether we are in the scope specified
        """
        return name in self._active_scopes


SCOPE_CONTEXT = ScopeContext()


@contextmanager
def scope(name):
    """Run code with certain scope

    Args:
        name (str): the scope name
    """
    SCOPE_CONTEXT.enter_scope(name)
    try:
        yield
    finally:
        SCOPE_CONTEXT.exit_scope()


def with_scope(name):
    """Mark the decorated function as in the specified scope

    Args:
        name (str): the scope name
    """

    def wrapper(original_func):
        def _wrapper(*args, **kwargs):
            with scope(name):
                return_value = original_func(*args, **kwargs)
            return return_value

        return _wrapper

    return wrapper


def current_scope():
    """Shortcut function to get the current scope

    Returns:
        str: the current scope
    """
    return SCOPE_CONTEXT.current_scope


def enter_scope(name):
    """Shortcut function to set the current scope

    Args:
        name (str): the scope name
    """
    SCOPE_CONTEXT.enter_scope(name)


def exit_scope():
    """Shortcut function to exit the current scope"""
    SCOPE_CONTEXT.exit_scope()


def in_scope(name):
    """Shortcut function to check whether in certain scope

    Args:
        name (str): the scope name

    Returns:
        bool: flag indicating whether we are in specified scope
    """
    return SCOPE_CONTEXT.in_scope(name)


def in_parent_scope(name):
    """Shortcut function to check whether the parent scope in specified scope.

    If active scope is `['a', 'b', 'c']`, then `in_parent_scope('a') == True`,
    `in_parent_scope('b') == True`

    Args:
        name (str): the scope name

    Returns:
        bool: flag indicating whether we are in specified scope
    """
    return name in SCOPE_CONTEXT.active_scopes[:-1]
