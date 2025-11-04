# Utiliza una imagen base de Nginx ligera
FROM nginx:alpine

# Copia los archivos de tu aplicación a la carpeta raíz de Nginx
COPY dist /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf

# Exponer el puerto 80 para el tráfico HTTP
EXPOSE 80

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]