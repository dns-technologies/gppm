from sqlalchemy import column, table


gp_resgroup_config = table(
    'gp_resgroup_config',
    column('groupid'),
    column('groupname'),
    column('concurrency'),
    column('cpu_rate_limit'),
    column('memory_limit'),
    column('memory_shared_quota'),
    column('memory_spill_ratio'),
    column('memory_auditor'),
    column('cpuset'),
    schema='gp_toolkit'
)
