#!/bin/bash
docker build . -t docker.io/luckysideburn/vaultbot:v1.0.5
docker push docker.io/luckysideburn/vaultbot:v1.0.5
git add .
git commit -m "fix"
git push origin main
