FROM nginx:alpine

COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY flaskr/static /usr/share/nginx/html/static

RUN chmod -R 755 /usr/share/nginx/html/static

EXPOSE 80