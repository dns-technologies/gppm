export interface IVisNode {
  id: number;
  label: any;
}

export interface IVisEdge {
  id: string;
  from: any;
  to: any;
}

export interface IVueDatabaseDetails {
  grantee: string;
  create: boolean;
  temporary: boolean;
  connect: boolean;
  public: boolean;
}

export interface IVueSchemaDetails {
  grantee: string;
  usage: boolean;
  create: boolean;
  public: boolean;
}

export interface IVueTableDetails {
  grantee: string;
  select: boolean;
  insert: boolean;
  update: boolean;
  delete: boolean;
  truncate: boolean;
  references: boolean;
  trigger: boolean;
  public: boolean;
}

export interface IVueAclCommon {
  oid: number;
  name: string;
  owner: string;
  acl: string[];
}

export interface IVueBelongsMembers {
  oid: number;
  rolname: string;
  belongs: string[];
  members: string[];
  parents: string[];
  childs: string[];
}