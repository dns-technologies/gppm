export interface IAclDatabase {
    oid: number;
    name: string;
    owner: string;
    acl: string[];
}

export interface IAclSchema {
    oid: number;
    name: string;
    owner: string;
    acl: string[];
}

export interface IAclTable {
    oid: number;
    name: string;
    owner: string;
    acl: string[];
    schema: string;
}

export interface IRoleProfile {
    oid: number;
    rolname: string;
    rolsuper: boolean;
    rolcreaterole: boolean;
    rolcreatedb: boolean;
    rolinherit: boolean;
    rolcanlogin: boolean;
}

export interface IRoleProfileCreate {
    rolname: string;
    password: string;
    rolsuper: boolean;
    rolcreaterole: boolean;
    rolcreatedb: boolean;
    rolinherit: boolean;
    rolcanlogin: boolean;
}

export interface IRoleProfileUpdate {
    rolname: string;
    password?: string;
    rolsuper: boolean;
    rolcreaterole: boolean;
    rolcreatedb: boolean;
    rolinherit: boolean;
    rolcanlogin: boolean;
}

export interface IRolesGraph {
    nodes: IRolesGraphNode[];
    edges: IRolesGraphEdge[];
}

export interface IRolesGraphNode {
    oid: number,
    rolname: string,
}

export interface IRolesGraphEdge {
    from_oid: number,
    to_oid: number,
}

export interface IPermission {
    grantee: string;
    grantor: string;
    privs: string[];
    privswgo: string[];
}

export interface IDecodeRulesRequest {
    acls: string[]
}

export interface IRoleMember {
    oid: number;
    rolname: string;
}

export interface IRoleRelationship {
    rolname: string;
    member: string;
}

export interface IGrantDatabase {
    name: string;
    role_specification: string;
    with_grant_option: boolean;
    privileges: {
        create: boolean;
        temporary: boolean;
        connect: boolean;
    }
}

export interface IGrantSchemasInDatabase {
    role_specification: string;
    with_grant_option: boolean;
    database: string;
    privileges: {
        create: boolean;
        usage: boolean;
    }
}

export interface IGrantSchema {
    name: string;
    role_specification: string;
    with_grant_option: boolean;
    database: string;
    privileges: {
        create: boolean;
        usage: boolean;
    }
}

export interface IGrantTablesInSchema {
    role_specification: string;
    with_grant_option: boolean;
    database: string;
    schema: string;
    privileges: {
        select: boolean;
        insert: boolean;
        update: boolean;
        delete: boolean;
        truncate: boolean;
        references: boolean;
        trigger: boolean;
    }
}

export interface IGrantTablesInDatabase {
    role_specification: string;
    with_grant_option: boolean;
    database: string;
    privileges: {
        select: boolean;
        insert: boolean;
        update: boolean;
        delete: boolean;
        truncate: boolean;
        references: boolean;
        trigger: boolean;
    }
}

export interface IGrantTable {
    name: string;
    role_specification: string;
    with_grant_option: boolean;
    database: string;
    schema: string;
    privileges: {
        select: boolean;
        insert: boolean;
        update: boolean;
        delete: boolean;
        truncate: boolean;
        references: boolean;
        trigger: boolean;
    }
}

export interface IResourceGroup {
    oid: number;
    name: string;
    concurrency: number;
    cpu_rate_limit: number;
    memory_limit: number;
    group_members: string[];
}

export interface IResourceGroupCreate {
    name: string;
    concurrency: number;
    cpu_rate_limit: number;
    memory_limit: number;
    group_members: string[];
}

export interface IResourceGroupUpdate {
    concurrency: number;
    cpu_rate_limit: number;
    memory_limit: number;
    group_members: string[];
}

export interface IResourceGroupAvailableLimits {
    concurrency_min: number;
    cpu_rate_limit_min: number;
    memory_limit_min: number;
    concurrency_max: number;
    cpu_rate_limit_max: number;
    memory_limit_max: number;
}

export interface IAclDefaultPermission {
    schema: string;
    objtype: string;
    defaclacl: IPermission[];
}

export interface IGraphPermissionParams {
    database: string;
    schema: string;
    table: string;
}

export interface IRevokeAllDefaults {
    database: string;
    schema?: string;
    entrie_type: string;
    target_role: string;
    role_specification: string;
}

export interface IUpdateEntityOwner {
    type_of_entity: string;
    owner: string;
    database: string;
    schema?: string;
    table?: string;
}