from sqlalchemy import column, table


pg_class = table(
    'pg_class',
    column('oid'),
    column('relname'),
    column('relacl'),
    column('relnamespace'),
    column('relkind'),
    column('relowner'),
)

pg_namespace = table(
    'pg_namespace',
    column('oid'),
    column('nspname'),
    column('nspowner'),
    column('nspacl'),
)

pg_roles = table(
    'pg_roles',
    column('oid'),
    column('rolname'),
    column('rolsuper'),
    column('rolinherit'),
    column('rolcreaterole'),
    column('rolcreatedb'),
    column('rolcanlogin'),
    column('rolreplication'),
    column('rolresgroup'),
)

pg_proc = table(
    'pg_proc',
    column('oid'),
    column('proname'),
    column('proargtypes'),
    column('pronamespace'),
    column('proacl'),
    column('proowner'),
)

pg_type = table(
    'pg_type',
    column('oid'),
    column('typname'),
    column('typnamespace'),
    column('typowner'),
    column('typacl'),
)

pg_language = table(
    'pg_language',
    column('oid'),
    column('lanname'),
    column('lanowner'),
    column('lanacl'),
)

pg_database = table(
    'pg_database',
    column('oid'),
    column('datname'),
    column('datdba'),
    column('datacl'),
    column('datistemplate'),
)

pg_tablespace = table(
    'pg_tablespace',
    column('oid'),
    column('spcname'),
    column('spcowner'),
    column('spcacl'),
)

pg_attribute = table(
    'pg_attribute',
    column('attrelid'),
    column('attname'),
    column('attnum'),
    column('attisdropped'),
    column('attacl'),
)

pg_auth_members = table(
    'pg_auth_members',
    column('member'),
    column('roleid'),
)

pg_shdescription = table(
    'pg_shdescription',
    column('objoid'),
    column('classoid'),
    column('description'),
)

pg_default_acl = table(
    'pg_default_acl',
    column('oid'),
    column('defaclrole'),
    column('defaclnamespace'),
    column('defaclobjtype'),
    column('defaclacl'),
)
