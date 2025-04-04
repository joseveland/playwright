FROM mcr.microsoft.com/playwright:v1.51.1-noble

LABEL authors="joseveland@gmail.com"

USER "pwuser"

ENTRYPOINT ["/bin/sh", "-c", "npx -y playwright@1.51.1 run-server --port 8080 --host 0.0.0.0"]
