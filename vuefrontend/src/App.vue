<script setup>
import * as Layout from '@components/layout';
</script>

<template>
  <div class="app-container">
    <Layout.NavbarComponent v-if="!$route.meta.hideNavbar" />
    <main class="content">
      <router-view />
    </main>
    <Layout.FooterComponent />
  </div>
</template>


<style>
/* Hace que el contenedor principal ocupe toda la pantalla */
.app-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* 100% del viewport height */
  text-align: center;
}

/* Hace que el contenido principal crezca y empuje el footer hacia abajo */
.content {
  flex: 1;
}

label {
    color: rgba(var(--bs-primary-rgb), 1);
    /* Aplica el color primary de Bootstrap */
  }
  
/* Asegura que el footer se mantenga abajo */
.footer {
  background-color: #2c3e50; /* Ajusta el color del fondo */
  color: white;
  padding: 10px 0;
  text-align: center;
}
</style>
