#!/bin/bash
docker build . -t docker.io/luckysideburn/vaultbot:v1.0.7
docker push docker.io/luckysideburn/vaultbot:v1.0.7
git add .
git commit -m "fix"
git push origin main
