import { ref } from 'vue';

const isOpen = ref(false);
const mode = ref('login'); // login | signup | reset

export function useAuthModal() {
  function openAuthModal(nextMode = 'login') {
    mode.value = nextMode;
    isOpen.value = true;
  }

  function closeAuthModal() {
    isOpen.value = false;
  }

  function requireAuth() {
    openAuthModal('login');
    return false;
  }

  return {
    isOpen,
    mode,
    openAuthModal,
    closeAuthModal,
    requireAuth,
  };
}
