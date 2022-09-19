import re
from collections import namedtuple
from typing import Dict, List, Iterator

from . import PrivilegeDTO
from app.use_case.exceptions import FailedToParseACLRule, FailedToParseACLSymbols, FailedToParseTextPrivileges

_valid_privileges = {
    'SELECT': 'r',
    'UPDATE': 'w',
    'INSERT': 'a',
    'DELETE': 'd',
    'TRUNCATE': 'D',
    'REFERENCES': 'x',
    'TRIGGER': 't',
    'EXECUTE': 'X',
    'USAGE': 'U',
    'CREATE': 'C',
    'CONNECT': 'c',
    'TEMPORARY': 'T',
    'ALL': '',
}

_valid_privileges_inv = {
    v: k for k, v in _valid_privileges.items()
}


def _decode_acl(acl_symbols: List[str]) -> List[str]:
    try:
        return [_valid_privileges_inv[symbol] for symbol in acl_symbols]
    except KeyError:
        raise FailedToParseACLSymbols(acl_symbols)


def _encode_acl(privileges: List[str]) -> List[str]:
    try:
        return [_valid_privileges[priv] for priv in privileges]
    except KeyError:
        raise FailedToParseTextPrivileges(privileges)


def _parce_acl_rule_light(acl: str) -> PrivilegeDTO:
    re_res = re.findall('[^=/"]+', acl)
    re_res_len = len(re_res)
    no_acl_line = "=/" in acl

    if re_res_len == 3:
        grantee, acl_line, grantor = re_res
    elif re_res_len == 2:
        if no_acl_line:
            acl_line, grantee, grantor = '', *re_res,
        else:
            grantee, acl_line, grantor = '', *re_res
    elif re_res_len == 1 and no_acl_line:
        grantee, acl_line, grantor = '', '', *re_res
    else:
        raise FailedToParseACLRule(acl)

    return PrivilegeDTO(
        grantee,
        grantor,
        privswgo=re.findall('[^*](?=[*])', acl_line),
        privs=re.findall('[^*](?=[^*]|$)', acl_line),
    )


def parce_one_acl_rule(acl: str) -> PrivilegeDTO:
    priv = _parce_acl_rule_light(acl)

    return PrivilegeDTO(
        priv.grantee,
        priv.grantor,
        privswgo=_decode_acl(priv.privswgo),
        privs=_decode_acl(priv.privs),
    )


def compile_one_acl_rule(privilege: PrivilegeDTO) -> str:
    privs = "".join(_encode_acl(privilege.privs))
    privswgo_raw = map(lambda x: f"{x}*", _encode_acl(privilege.privswgo))
    privswgo = "".join(privswgo_raw)

    return f'"{privilege.grantee}"={privs}{privswgo}/"{privilege.grantor}"'


def _parce_batch_acls_final(acls: List[str]) -> Iterator[PrivilegeDTO]:
    PrivilegeFinal = namedtuple('PrivilegeFinal', 'count_acls privswgo privs')
    role_acls: Dict[str, PrivilegeFinal] = {}

    # Объединяем ACL листы по пользователю, к которому применяются права
    for acl in acls:
        current = parce_one_acl_rule(acl)
        prev = role_acls.get(current.grantee)
        if prev is None:
            pf = PrivilegeFinal(
                1,
                current.privswgo,
                current.privs,
            )
        else:
            new_privswgo_set = set(current.privswgo + prev.privswgo)
            new_privs_set = set(current.privs + prev.privs) - new_privswgo_set
            pf = PrivilegeFinal(
                prev.count_acls + 1,
                list(new_privswgo_set),
                list(new_privs_set),
            )
        role_acls.update({current.grantee: pf})

    for key, val in role_acls.items():
        yield PrivilegeDTO(
            grantee=key,
            grantor=val.count_acls,
            privs=val.privs,
            privswgo=val.privswgo,
        )


def _parce_batch_acls(acls: List[str]) -> Iterator[PrivilegeDTO]:
    for acl in acls:
        yield parce_one_acl_rule(acl)


def parce_acl_rules(acls: List[str], *, final=True) -> Iterator[PrivilegeDTO]:
    worker = _parce_batch_acls_final if final else _parce_batch_acls
    for acl in worker(acls):
        yield acl
