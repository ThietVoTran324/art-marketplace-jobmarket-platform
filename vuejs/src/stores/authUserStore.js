import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const authUserStore = defineStore("authUserStore", () => {
  const authUsername = ref(null);
  const authUserId = ref(null);
  const roles = ref([]);
  const accountKind = ref("personal");
  const companyId = ref(null);
  /** null = resolving, true = logged in, false = guest */
  const sessionKnown = ref(null);

  const isGuest = computed(() => sessionKnown.value === false);
  const isAuthenticated = computed(() => sessionKnown.value === true);

  const setUsername = async (username) => {
    authUsername.value = username;
  };

  const setUserId = (id) => {
    authUserId.value = id ?? null;
  };

  const setRoles = (nextRoles) => {
    roles.value = Array.isArray(nextRoles) ? [...nextRoles] : [];
  };

  const setAccountKind = (kind, nextCompanyId = null) => {
    accountKind.value = kind || "personal";
    companyId.value = nextCompanyId ?? null;
  };

  const markAuthenticated = () => {
    sessionKnown.value = true;
  };

  const markGuest = () => {
    sessionKnown.value = false;
  };

  const hasRole = (role) => roles.value.includes(role);

  const clearAuth = () => {
    authUsername.value = null;
    authUserId.value = null;
    roles.value = [];
    accountKind.value = "personal";
    companyId.value = null;
    sessionKnown.value = false;
  };

  return {
    authUsername,
    authUserId,
    roles,
    accountKind,
    companyId,
    sessionKnown,
    isGuest,
    isAuthenticated,
    setUsername,
    setUserId,
    setRoles,
    setAccountKind,
    markAuthenticated,
    markGuest,
    hasRole,
    clearAuth,
  };
});
