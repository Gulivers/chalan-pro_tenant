# Proyecto Chalan-Pro - Backend Django

¡Bienvenido al backend de **Chalan-Pro**, el cerebro detrás del sistema de contratos.

Aquí tienes toda la info que necesita un nuevo desarrollador.

---

## 🏗️ Estructura General del Proyecto

```
chalan_pro_qa/
│
├── manage.py                 # Comando principal de Django
├── chalan_pro_qa/           # Proyecto raíz con settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── ctrctsapp/               # App de Contratos
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── routing.py
│   ├── consumers.py         # WebSocket consumers
│   ├── urls.py
│   └── templates/
│
├── crewsapp/                # App de Cuadrillas
├── auditapp/                # App de Logs y Auditoría
├── schedule/                # App para cronogramas (proximamente)
│
├── static/                  # Archivos estáticos (admin, css)
└── media/                   # Archivos cargados por usuarios
```

---

## ⚙️ Principales Tecnologías

| Herramienta        | Uso                                                  |
|--------------------|-------------------------------------------------------|
| **Django**         | Framework principal                                   |
| **Django REST Framework** | API RESTful para Vue.js                       |
| **Channels**       | Soporte WebSocket (para chat y tiempo real)          |
| **MySQL**          | Base de datos actual (se puede migrar a PostgreSQL)  |

---

## 🚦 Buenas prácticas para devs nuevos

1. **Cada app hace una sola cosa bien**
   - `ctrctsapp`: lógica de contratos
   - `crewsapp`: cuadrillas
   - `auditapp`: logging
   - `schedule`: eventos y chats (futuro)

2. **Modelos primero, luego Serializers, luego Views**
   - DRY y limpio. Nada de lógica suelta.

3. **Rutas limpias**
   - Todas las URLs van en su `urls.py` por app.
   - Centralizadas en `chalan_pro_qa/urls.py`

4. **WebSockets usando Channels**
   - Define tu `consumer.py` por app
   - Usa `routing.py` y conéctalo al `asgi.py`

5. **Logs y seguridad**
   - Acciones importantes registradas en `auditapp`
   - Autenticación con tokens (JWT opcional)

 6. **Seguridad**
    - LOs usuarios no autenticados no puedan hacer consultas 
      (ni siquiera GET), podrías usar simplemente:

      permission_classes = [IsAuthenticated, DjangoModelPermissions]

---

## 💡 Tips extra

- Usa el comando:
  ```bash
  python manage.py show_urls
  ```
  para ver todas las rutas disponibles si tienes `django-extensions`.

- Siempre usa `venv` y activa antes de correr:
  ```bash
  . venv/Scripts/activate  (Windows)
  ```

- Usa `makemigrations` y `migrate` con control:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

---

## Configuración recomendada para producción

- Base de datos: `PostgreSQL + django-tenant-schemas` (ideal para multi-tenant)
- Seguridad:
  - HTTPS con Let’s Encrypt o AWS Cert Manager
  - CSRF, CORS
- WebSockets: usando Redis como backend para `channels_redis`

---

## 📚 Recursos útiles

- [Django Docs](https://docs.djangoproject.com/es/5.0/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Channels](https://channels.readthedocs.io/en/stable/)
- [Tenants (multiempresa)](https://django-tenant-schemas.readthedocs.io/)

---

## 🧱 En resumen

> Sistemas sólidos con arquitectura limpia y lógica modular! 
