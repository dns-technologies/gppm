from fastapi import APIRouter

from app.api.api_v1.gui import login, users, utils, contexts, accesses
from app.api.api_v1.gp import acl, privilege, resource, role, owner

api_router = APIRouter()

# GUI Routes
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contexts.router, prefix="/contexts", tags=["contexts"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(accesses.router, prefix="/accesses", tags=["accesses"])

# GreenPlum Routes
api_router.include_router(acl.router, prefix="/acls", tags=["acls"])
api_router.include_router(role.router, prefix="/roles", tags=["roles"])
api_router.include_router(privilege.router, prefix="/privileges", tags=["privileges"])
api_router.include_router(resource.router, prefix="/resource-groups", tags=["resource-groups"])
api_router.include_router(owner.router, prefix="/owners", tags=["owners"])
