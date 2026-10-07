# Serwer czasu (chrony) dla DevKitu Q11 w sieci lokalnej. AMPERE POINT, 2026-09-25.
FROM alpine:3.20
RUN apk add --no-cache chrony
COPY chrony.conf /etc/chrony/chrony.conf
EXPOSE 123/udp
# -d: na pierwszym planie, -x: nie zmieniaj zegara hosta (kontener nie ma do tego uprawnien)
CMD ["chronyd", "-d", "-x", "-f", "/etc/chrony/chrony.conf"]
