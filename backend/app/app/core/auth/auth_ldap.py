from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import ldap

from app.models.user import User
from .auth_base import BaseAuth


class LdapAuth(BaseAuth):
    def __init__(self, url: str, base_dn: str, search_filter: str, retrieve_attrs: List[str]) -> None:
        super().__init__()
        self.conn = ldap.initialize(url)
        self.base_dn = base_dn
        self.search_filter = search_filter
        self.retrieve_attrs = retrieve_attrs

    def __auth_in_ldap(self, email: str, password: str, *, db: Session) -> bool:
        auth = False
        try:
            self.conn.simple_bind_s(email, password)
            auth = True
        finally:
            return auth

    def __search_attributes(self, search_filter: str, retrieve_attributes: List[str]) -> List[List]:
        search_scope = ldap.SCOPE_SUBTREE
        result_set = []
        try:
            ldap_result = self.conn.search_s(
                self.base_dn, search_scope, search_filter, retrieve_attributes
            )
            result_set = list(
                list(*zip(
                    *[set_of_attrs[key] for key in retrieve_attributes]
                )) for _, set_of_attrs in ldap_result
            )
        finally:
            return result_set

    def __get_info_from_ldap(self, email: str) -> Dict:
        search_filter = self.search_filter.format(email=email)
        ldap_attrs = self.__search_attributes(search_filter, self.retrieve_attrs)

        if not len(ldap_attrs) == 1:
            return {}

        ldap_data = ldap_attrs[0]
        return {
            "full_name": " ".join([line.decode() for line in ldap_data])
        }

    def auth(self, email: str, password: str, *, db: Session) -> Optional[User]:
        is_auth = self.__auth_in_ldap(email, password, db=db)

        if not is_auth:
            return None

        payload = {
            "email": email,
            "password": password,
        }

        ldap_info = self.__get_info_from_ldap(email)
        payload.update(ldap_info)

        return self.update_db(payload, db=db)
