#!/bin/bash
docker build . -t docker.io/luckysideburn/vaultbot:v1.0.3
docker push docker.io/luckysideburn/vaultbot:v1.0.3
git add .
git commit -m "fix"
git push origin main
