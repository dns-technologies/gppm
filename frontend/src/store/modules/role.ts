import { api } from "@/api";
import { VuexModule, Module, Mutation, Action } from "vuex-module-decorators";
import { IRoleProfile, IRoleProfileCreate, IRolesGraph, IRoleMember, IRoleProfileUpdate, IRolesGraphEdge, IRolesGraphNode, IRoleRelationship } from "@/interfaces/greenplum";
import { mainStore } from "@/utils/store-accessor";
import _ from "lodash";

@Module({ name: "role" })
export default class RolesModule extends VuexModule {
  roles: IRoleProfile[] = [];
  graph: IRolesGraph = { nodes: [], edges: [] };

  get GraphNodes(): IRolesGraphNode[] {
    return this.graph.nodes;
  }

  get GraphEdges(): IRolesGraphEdge[] {
    return this.graph.edges;
  }

  get adminOneRole() {
    return (roleId: number | null) => {
      const filteredRoles = this.roles.filter((role) => role.oid === roleId);
      if (filteredRoles.length > 0) {
        return { ...filteredRoles[0] };
      } else {
        return null;
      }
    };
  }

  @Mutation
  setRoles(payload: IRoleProfile[]) {
    this.roles = _.sortBy(payload, "rolname");
  }

  @Mutation
  setGraph(payload: IRolesGraph) {
    this.graph = payload;
  }

  @Action
  async getRoles() {
    let data: IRoleProfile[] = [];
    try {
      const response = await api.getRoles(mainStore.token, mainStore.contextId);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      this.setRoles(data);
    }
  }

  @Action
  async deleteRole(payload: string) {
    const loadingNotification = { content: "Deleting role", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.deleteRole(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Role successfully deleted",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Role deleted with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async deleteRoles(payload: string[]) {
    const loadingNotification = { content: "Deleting roles", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      const callTasks = async (tasks: string[]) => {
        for (const task of tasks) {
          await api.deleteRole(
            mainStore.token,
            mainStore.contextId,
            task
          );
        }
      };

      await callTasks(payload);

      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Roles successfully deleted",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Roles deleted with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async createRole(payload: IRoleProfileCreate) {
    const loadingNotification = { content: "Creating role", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.createRole(mainStore.token, mainStore.contextId, payload);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Role successfully created",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Role created with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updateRole(payload: { rolname: string; role: IRoleProfileUpdate }) {
    const loadingNotification = { content: "Updating role", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      await api.updateRole(mainStore.token, mainStore.contextId, payload.rolname, payload.role);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Role successfully updated",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Role updated with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async removeMembersFromRole(payload: IRoleRelationship[]) {
    const loadingNotification = { content: "Removing members from role", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      const callTasks = async (tasks: IRoleRelationship[]) => {
        for (const task of tasks) {
          await api.removeMemberFromRole(
            mainStore.token,
            mainStore.contextId,
            task.rolname,
            task.member
          );
        }
      };

      await callTasks(payload);

      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Members successfully removed from role",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Members removed from role with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async appendMembersToRole(payload: IRoleRelationship[]) {
    const loadingNotification = { content: "Appending members to role", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      const callTasks = async (tasks: IRoleRelationship[]) => {
        for (const task of tasks) {
          await api.appendMemberToRole(
            mainStore.token,
            mainStore.contextId,
            task.rolname,
            task.member
          );
        }
      };

      await callTasks(payload);

      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Members successfully appended to role",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Members appended to role with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async changeLinksOfRole(payload: { remove: IRoleRelationship[], append: IRoleRelationship[] }) {
    const loadingNotification = { content: "Changing links of role", showProgress: true };
    mainStore.addNotification(loadingNotification);

    try {
      const callTasksRemove = async (tasks: IRoleRelationship[]) => {
        for (const task of tasks) {
          await api.removeMemberFromRole(
            mainStore.token,
            mainStore.contextId,
            task.rolname,
            task.member
          );
        }
      };

      await callTasksRemove(payload.remove);

      const callTasksAppend = async (tasks: IRoleRelationship[]) => {
        for (const task of tasks) {
          await api.appendMemberToRole(
            mainStore.token,
            mainStore.contextId,
            task.rolname,
            task.member
          );
        }
      };

      await callTasksAppend(payload.append);

      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Links of role successfully changed",
        color: "success",
      });
    } catch (error) {
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Links of role changed with errors",
        color: "warning",
      });
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async getRolesGraph() {
    let data: IRolesGraph = { nodes: [], edges: [] };
    try {
      const response = await api.getRolesGraph(mainStore.token, mainStore.contextId);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      this.setGraph(data);
    }
  }

  @Action
  async getMembersOfRole(payload: string): Promise<IRoleMember[]> {
    let data: IRoleMember[] = [];
    try {
      const response = await api.getMembersOfRole(mainStore.token, mainStore.contextId, payload);
      if (response) {
        data = response.data;
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    } finally {
      return _.sortBy(data, "rolname");
    }
  }
}
