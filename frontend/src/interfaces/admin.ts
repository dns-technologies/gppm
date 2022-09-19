export interface IUserProfile {
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  full_name: string;
  id: number;
}

export interface IUserProfileUpdate {
  email?: string;
  full_name?: string;
  password?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface IUserProfileCreate {
  email: string;
  full_name: string;
  password: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface IAppNotification {
  content: string;
  color?: string;
  showProgress?: boolean;
}

export interface IContext {
  alias: string;
  server: string;
  port: number;
  role: string;
  database: string;
  is_active: boolean;
  id: number;
}

export interface IContextMini {
  alias?: string;
  server: string;
  port: number;
  role: string;
  database: string;
  password?: string;
}

export interface IContextCreate {
  alias: string;
  server: string;
  port: number;
  role: string;
  password: string;
  database: string;
  is_active: boolean;
}

export interface IContextUpdate {
  alias?: string;
  server?: string;
  port?: number;
  role?: string;
  password?: string;
  database?: string;
  is_active?: boolean;
}

export interface IPublicAppInfo {
  project_name: string;
  api_version: string;
  auth_type: string;
}

export interface IAccess {
  user_id: number;
  role: string | null;
  database: string | null;
  db_schema: string | null;
  type_of_entity: string;
  is_active: boolean;
  context_id: number;
  id: number;
}

export interface IAccessCreate {
  user_id: number;
  role: string | null;
  database: string | null;
  db_schema: string | null;
  is_active: boolean;
  context_id: number;
}

export interface IAccessUpdate {
  user_id: number;
  role: string | null;
  database: string | null;
  db_schema: string | null;
  is_active?: boolean;
  context_id: number;
}
