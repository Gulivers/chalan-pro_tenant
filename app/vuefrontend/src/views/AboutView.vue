<template>
  <section class="py-5 bg-light">
    <div class="container">
      <!-- Title Section -->
      <div class="row justify-content-center">
        <div class="col-lg-8 text-center">
          <h3 class="display-5 text-primary">About Chalan-Pro</h3>
          <p class="py-2"><strong>Chalan-Pro</strong> is a modern ERP web system built for the construction industry, 
            designed to streamline the management of contracts, 
            communities, work crews, and scheduling in real time. From bid preparation to final approval,
            it automates key processes that traditionally require manual work.</p>
        </div>
      </div>

      <!-- Content Section -->
      <div class="row">
        <div class="col-lg-10 mx-auto text-justify">
          <!-- What is Chalan-Pro for? -->
          <h3 class="text-primary mb-4">What is Chalan-Pro for?</h3>
          <p class="text-muted mb-4">
            <strong>Chalan-Pro</strong> helps construction companies reduce costs by eliminating errors, minimizing downtime, and optimizing resources. It supports the management of materials, work orders, and contract workflows — all in a single, cloud-based platform accessible from any device.
          </p>
          <p class="text-muted mb-4">
            With full traceability of prices, units of measure, schedules, and assigned crews, Chalan-Pro is a powerful solution for general contractors, electricians, supervisors, and administrators. Its dashboards and reporting tools deliver the insights needed to make smarter, faster decisions.
          </p>

          <!-- Key Modules -->
          <h3 class="text-primary mb-4">Main Modules Included</h3>
          <ul class="list-group list-group-flush mb-4 text-muted">
            <li class="list-group-item"><strong>Contract Management:</strong> Create and control contracts and bids with dynamic validations and print-to-PDF functionality.</li>
            <li class="list-group-item"><strong>Work Price Management:</strong> Define and assign trim and rough prices by builder and house model.</li>
            <li class="list-group-item"><strong>Crew Scheduling:</strong> Assign crews and supervisors to communities and generate a visual calendar with drag-and-drop support.</li>
            <li class="list-group-item"><strong>Real-Time Messaging:</strong> Crew supervisors and office staff can chat per scheduled task via WebSockets and receive notifications.</li>
            <li class="list-group-item"><strong>House Notes:</strong> Add house notes with formatted content and embedded images linked to specific scheduled tasks.</li>
            <li class="list-group-item"><strong>Document Folders:</strong> Upload, categorize, and access images, PDFs and blueprints for each event and job.</li>
            <li class="list-group-item"><strong>Permissions System:</strong> Full role-based access control with group-level and individual permissions for each feature.</li>
          </ul>

          <!-- Advantages of Chalan-Pro -->
          <h3 class="text-primary mb-4">Advantages of Being a WebApp</h3>
          <ul class="list-group list-group-flush mb-4 text-muted">
            <li class="list-group-item"><strong>Accessibility:</strong> Accessible from any device with internet access.</li>
            <li class="list-group-item"><strong>Security:</strong> Includes authentication, authorization, and user session controls.</li>
            <li class="list-group-item"><strong>Customizable:</strong> Easily adaptable to company-specific workflows and user roles.</li>
          </ul>

          <!-- Legal Overview Link -->
          <div class="text-center mt-5">
           <!-- <a :href="`${baseUrl}/docs/Chalan-Pro_System_Overview_Declaration.pdf`" target="_blank" 
              class="btn btn-outline-primary btn-lg">
              View Legal Overview
            </a>-->
            <p class="mt-2 text-muted" style="font-size: 14px;">
              Document authored by Oliver Alberto Hernandez Perez (<i>oliverhernandez.p@gmail.com</i>)<br>
              All rights reserved. © 2025 Chalan-Pro.
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>

const baseUrl = window.location.origin;

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap');

section {
  font-family: 'Montserrat', sans-serif;
}

h2, h3 {
  font-weight: 500;
  color: #395ecb;
}

p, ul, li {
  font-weight: 500;
  color: #474f57;
  font-size: 16px;
}

.lead {
  font-weight: 500;
  font-size: 16px;
}

.list-group-item {
  border: 0;
  background: transparent;
  font-size: 16px;
}

.container {
  max-width: 1140px;
}

.text-muted {
  color: #4a4a4a !important;
  font-size: 16px;
}

@media (max-width: 768px) {
  h2 {
    font-size: 2.5rem;
  }
  h3 {
    font-size: 1.75rem;
  }
}
</style>
