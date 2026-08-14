<script setup>
import { onMounted, ref, onBeforeUnmount, onActivated, onDeactivated, watch } from 'vue';
import axios from 'axios';
import PinFeedCard from './PinFeedCard.vue';
import { prefetchFeedMeta } from '@/composables/usePinFeedMeta';

const pins = ref([]);
const offset = ref(0);
const limit = ref(10);
const isPinsLoading = ref(false);
const hasMore = ref(true);

const props = defineProps({
  value: String,
});

const loadPins = async () => {
  if (isPinsLoading.value || !hasMore.value) return;

  isPinsLoading.value = true;
  try {
    const response = await axios.get(`/api/pins/search`, {
      params: { offset: offset.value, limit: limit.value, value: props.value },
      withCredentials: true,
    });
    const batch = response.data || [];
    pins.value.push(...batch);
    if (batch.length) {
      prefetchFeedMeta(batch.map((p) => p.id)).catch((e) => console.error(e));
    }
    offset.value += limit.value;
    if (batch.length < limit.value) {
      hasMore.value = false;
    }
    if (limit.value === 10) {
      limit.value = 5;
    }
  } catch (error) {
    console.log(error);
  } finally {
    isPinsLoading.value = false;
  }
};

const resetAndLoad = () => {
  pins.value = [];
  offset.value = 0;
  limit.value = 10;
  hasMore.value = true;
  isPinsLoading.value = false;
  loadPins();
};

const handleScroll = () => {
  const scrollableHeight = document.documentElement.scrollHeight;
  const currentScrollPosition = window.innerHeight + window.scrollY;
  if (currentScrollPosition + 200 >= scrollableHeight) {
    loadPins();
  }
};

onMounted(() => {
  loadPins();
  window.addEventListener('scroll', handleScroll);
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll);
});

onActivated(() => {
  window.addEventListener('scroll', handleScroll);
});

onDeactivated(() => {
  window.removeEventListener('scroll', handleScroll);
});

watch(() => props.value, resetAndLoad);
</script>

<template>
  <div
    class="ml-20 mt-10 mr-6"
    v-masonry
    transition-duration="0.4s"
    item-selector=".item"
    stagger="0.03s"
  >
    <PinFeedCard v-for="pinem in pins" :key="pinem.id" class="item" :pin="pinem" v-masonry-tile />
  </div>
</template>
