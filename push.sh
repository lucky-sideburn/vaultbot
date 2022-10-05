#!/bin/bash
docker build . -t docker.io/luckysideburn/vaultbot:v1.1.0
docker push docker.io/luckysideburn/vaultbot:v1.1.0
git add .
git commit -m "fix"
git push origin main
