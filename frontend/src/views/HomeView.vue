<template>
  <div class="home">
    <GroceryCarousel />
    <HelloWorld />
  </div>
</template>

<script>
import HelloWorld from "@/components/HelloWorld.vue";
import GroceryCarousel from "@/components/GroceryCarousel.vue";

export default {
  name: "HomeView",
  components: {
    HelloWorld,
    GroceryCarousel,
  },
};
</script>
