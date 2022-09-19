from .auth_base import BaseAuth
from .auth_ldap import LdapAuth
from .auth_database import DatabaseAuth
from app.core.config import settings


def get_auth_class(auth_type: str) -> BaseAuth:
    all_auth = {
        "ldap": lambda: LdapAuth(
            settings.LDAP_HOST,
            settings.LDAP_USER_SEARCH_BASE,
            settings.LDAP_USER_SEARCH_FILTER,
            settings.LDAP_USER_ATTRS,
        ),
        "local": lambda: DatabaseAuth(),
    }

    auth = all_auth.get(auth_type)

    if auth is None:
        raise NotImplementedError("This auth class is not implemented yet")

    return auth()
