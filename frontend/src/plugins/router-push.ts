import Router from "vue-router";

// Великий комментарий: https://github.com/vuejs/vue-router/issues/2881#issuecomment-520554378
// https://itecnote.com/tecnote/r-vue-router-uncaught-in-promise-error-redirected-from-login-to-via-a-navigation-guard/
// Для подавлении ошики Redirected from "" to "" via a navigation guard

const originalPush = Router.prototype.push;
Router.prototype.push = function push(location, onResolve?, onReject?): any {
    if (onResolve || onReject) {
        return originalPush.call(this, location, onResolve, onReject);
    }
    let route: any = originalPush.call(this, location);
    return route.catch((err) => {
        if (Router.isNavigationFailure(err)) {
            // resolve err
            return err;
        }
        // rethrow error
        return Promise.reject(err);
    })
}