from enum import Enum


class PgRelKind(Enum):
    TABLE = 'r'
    INDEX = 'i'
    SEQUENCE = 'S'
    VIEW = 'v'
    MATERIALIZED_VIEW = 'm'
    COMPOSITE_TYPE = 'c'
    TOAST_TABLE = 't'
    FOREIGN_TABLE = 'f'
    PARTITIONED_TABLE = 'p'
