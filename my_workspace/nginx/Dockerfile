FROM nginx:alpine

# ลบ default config
RUN rm /etc/nginx/conf.d/default.conf

# copy config
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/coopform.conf /etc/nginx/conf.d/coopform.conf

# Vue SPA build จะถูก copy มาจาก frontend build stage ในอนาคต
# ตอน dev ใช้ placeholder หน้า nginx default แทน

EXPOSE 80
