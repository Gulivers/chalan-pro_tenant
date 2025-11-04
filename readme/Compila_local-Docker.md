Recrea los servicios:
docker compose -f docker-compose.local.yml down
docker compose -f docker-compose.local.yml up -d --build
docker compose -f docker-compose.local.yml ps
docker compose -f docker-compose.local.yml logs -f frontend

# Migraciones y usuario admin
docker compose -f docker-compose.local.yml exec backend python manage.py migrate
docker compose -f docker-compose.local.yml exec backend python manage.py createsuperuser


1) Recrear con la nueva config
docker compose -f docker-compose.local.yml down
docker compose -f docker-compose.local.yml up -d --build
2) Ver estado y logs
docker compose -f docker-compose.local.yml ps
docker compose -f docker-compose.local.yml logs -f postgres
docker compose -f docker-compose.local.yml logs -f backend
docker compose -f docker-compose.local.yml logs -f pgadmin
3) Correr migraciones (si el backend ya está arriba)
docker compose -f docker-compose.local.yml exec backend python manage.py migrate
4) Crear superusuario (opcional)
docker compose -f docker-compose.local.yml exec backend python manage.py createsuperuser
5) Accesos
Backend: http://localhost:8000
pgAdmin: http://localhost:5050 (email: admin@chalan.com / pass: la de ${POSTGRES_PASSWORD})

Si backend sigue sin levantar, pégame las últimas 50 líneas:
docker compose -f docker-compose.local.yml logs --tail=50 back