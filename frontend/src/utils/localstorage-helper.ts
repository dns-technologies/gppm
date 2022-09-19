export const getLocalToken = () => localStorage.getItem("token");

export const saveLocalToken = (token: string) => localStorage.setItem("token", token);

export const removeLocalToken = () => localStorage.removeItem("token");

export const getLocalContextId = () => localStorage.getItem("context");

export const saveLocalContextId = (context_id: string) => localStorage.setItem("context", context_id);

export const removeLocalContextId = () => localStorage.removeItem("context");