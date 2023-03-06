from typing import Dict, Iterator, List, Optional, Set

from app.db.orm_types import GreenPlumSession

from app.use_case.role import RoleDTO, get_graph_of_members, get_all_roles
from app.use_case.acl import get_database_acl, get_schema_acl, get_table_acl
from app.use_case.privilege import PrivilegeDTO, compile_one_acl_rule, parce_acl_rules, parce_one_acl_rule
from . import GraphPermissionsDTO


class RoleSearcher():
    _oid2role: Dict[int, str]
    _role2oid: Dict[str, int]

    def __init__(self, roles: List[RoleDTO]):
        self._oid2role = dict()
        self._role2oid = dict()

        for role in roles:
            self._oid2role[role.oid] = role.rolname
            self._role2oid[role.rolname] = role.oid

    def oid2rolname(self, oid: int) -> Optional[str]:
        return self._oid2role.get(oid)

    def rolname2oid(self, rolname: int) -> Optional[int]:
        return self._role2oid.get(rolname)


class Graph:
    _graph: Dict[int, List[int]]

    def __init__(self):
        self._graph = dict()

    def add_vertex(self, v: int):
        if not v in self._graph:
            self._graph[v] = []

    def add_edge(self, u: int, v: int):
        self.add_vertex(u)
        self.add_vertex(v)
        self._graph[u].append(v)

    def topological_sort_util(self, v: int, visited: Set[int], stack: List[int]):
        visited.add(v)

        for n in self._graph[v]:
            if not n in visited:
                self.topological_sort_util(n, visited, stack)

        stack.append(v)

    def childs_list(self) -> Dict[int, List[int]]:
        return self._graph

    def topological_sort(self) -> List[int]:
        vertices = self._graph.keys()
        visited = set()
        stack = list()

        for v in vertices:
            if not v in visited:
                self.topological_sort_util(v, visited, stack)

        return stack

    def all_reachable_nodes(self) -> Dict[int, List[int]]:
        vertices = self.topological_sort()
        deps = dict()

        for v in vertices:
            deps[v] = set()
            for n in self._graph[v]:
                deps[v].add(n)
                deps[v].update(deps[n])
            deps[v] = list(deps[v])

        return deps


def _get_all_acls(conn: GreenPlumSession, payload: GraphPermissionsDTO) -> List[str]:
    acl = {
        (True, False, False): lambda: get_database_acl(conn, payload.database),
        (True, True, False): lambda: get_schema_acl(conn, payload.db_schema),
        (True, True, True): lambda: get_table_acl(conn, payload.db_schema, payload.table),
    }.get((
        bool(payload.database),
        bool(payload.db_schema),
        bool(payload.table)
    ))

    if acl is None:
        return []

    return acl().acl


def _max_acls_for_role(rolname: str, payload: GraphPermissionsDTO) -> str:
    # https://www.postgresql.org/docs/current/ddl-priv.html
    acl = {
        (True, False, False): "CTc",
        (True, True, False): "UC",
        (True, True, True): "arwdDxt",
    }.get((
        bool(payload.database),
        bool(payload.db_schema),
        bool(payload.table)
    ))

    return f"{rolname}={acl}/{rolname}"


def change_privilege_roles(privilege: PrivilegeDTO, grantor: str, grantee: str) -> str:
    new_priv = PrivilegeDTO(
        grantee=grantee,
        grantor=grantor,
        privs=privilege.privs,
        privswgo=privilege.privswgo,
    )

    return compile_one_acl_rule(new_priv)


def _get_reachable_roles(conn: GreenPlumSession) -> Dict[int, List[int]]:
    memebers = get_graph_of_members(conn)
    graph = Graph()

    for role in memebers.edges:
        graph.add_edge(role.from_oid, role.to_oid)

    return graph.all_reachable_nodes()


def _all_rules_with_public_acl(roles: List[RoleDTO], privilege: PrivilegeDTO) -> Iterator[str]:
    for role in roles:
        yield change_privilege_roles(
            privilege=privilege,
            grantor=privilege.grantor,
            grantee=role.rolname,
        )


def _get_rules_from_all_admins(roles: List[RoleDTO], payload: GraphPermissionsDTO) -> Iterator[str]:
    for role in roles:
        if role.rolsuper:
            yield _max_acls_for_role(role.rolname, payload)


def get_all_graph_permissions(conn: GreenPlumSession, payload: GraphPermissionsDTO) -> Iterator[PrivilegeDTO]:
    acls = _get_all_acls(conn, payload)
    roles = get_all_roles(conn)
    reachable = _get_reachable_roles(conn)

    permissions = list(_get_rules_from_all_admins(roles, payload))
    role_finder = RoleSearcher(roles)

    for acl in acls:
        permissions.append(acl)
        privilege = parce_one_acl_rule(acl)
        oid = role_finder.rolname2oid(privilege.grantee)

        if oid is None:  # Это PUBLIC
            public_acls = _all_rules_with_public_acl(roles, privilege)
            permissions.extend(public_acls)

        for child in reachable.get(oid, []):
            child_acl = change_privilege_roles(
                privilege=privilege,
                grantor=privilege.grantee,
                grantee=role_finder.oid2rolname(child),
            )
            permissions.append(child_acl)

    return parce_acl_rules(permissions)
