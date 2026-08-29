# Implementa JobRhythm Assistant — Nivel 1

Usa el subagente `jobrhythm-assistant-lead` como coordinador.

Desarrolla el primer vertical de JobRhythm Assistant para `Transactions / Documents`, comenzando por descubrimiento y planificación antes de editar.

Casos de aceptación iniciales:

1. “Show me Harbor Freight transactions over $1,500 this month.”
2. “How much did we spend with Harbor Freight this month?”
3. “Show purchases by vendor this month.”
4. “Compare purchases by supplier for the last six months.”
5. “Show the five vendors with the highest spending.”
6. “Graph spending for the last three months.”

Restricciones:

- JobRhythm es la única fuente de verdad.
- Toda recuperación pasa por Django y servicios controlados.
- Ninguna herramienta obtiene acceso SQL libre.
- Toda consulta se restringe por usuario, tenant y permisos antes de aplicar filtros funcionales.
- El Nivel 1 es exclusivamente read-only.
- El LLM no genera HTML, SQL, nombres de rutas ni cálculos financieros que el backend pueda producir.
- El backend devuelve bloques estructurados; Vue decide cómo renderizarlos.
- No introducir embeddings, pgvector, búsqueda semántica, RAG ni workflows de escritura.
- Reutilizar patrones, servicios, componentes y convenciones existentes.
- No hacer cambios destructivos de Git ni modificar migraciones existentes.

Proceso:

1. Lee las instrucciones y documentos de contexto del repositorio.
2. Inspecciona modelos, endpoints, tenant isolation, permisos, auditoría, frontend y pruebas existentes.
3. Produce un plan con archivos concretos, decisiones abiertas, riesgos y pruebas.
4. Espera mi aprobación antes de implementar si el plan requiere cambios de modelos, migraciones, dependencias, configuración de producción o decisiones de producto no resueltas.
5. Implementa por incrementos pequeños.
6. Ejecuta al verificador al terminar cada incremento importante.
7. Entrega evidencia: archivos cambiados, pruebas ejecutadas, resultados, riesgos pendientes y siguiente incremento recomendado.

