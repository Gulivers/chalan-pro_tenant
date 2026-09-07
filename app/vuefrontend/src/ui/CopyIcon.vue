<template>
  <svg
    width="14"
    height="14"
    viewBox="0 0 14 14"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    v-bind="pti()">
    <path
      fill="currentColor"
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M4.35 1.1h6.4c.86 0 1.55.69 1.55 1.55v6.85h-1.25V2.75a.3.3 0 0 0-.3-.3H4.35V1.1ZM1.65 3.4h6.75c.72 0 1.3.58 1.3 1.3v7c0 .72-.58 1.3-1.3 1.3H1.65c-.72 0-1.3-.58-1.3-1.3v-7c0-.72.58-1.3 1.3-1.3Zm0 1.25v7h6.75v-7H1.65Z" />
  </svg>
</template>

<script>
import BaseIcon from "@primevue/icons/baseicon";

export default {
  name: "CopyIcon",
  extends: BaseIcon,
};
</script>
