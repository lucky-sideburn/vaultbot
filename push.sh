#!/bin/bash
docker build . -t docker.io/luckysideburn/vaultbot:v1.0.4
docker push docker.io/luckysideburn/vaultbot:v1.0.4
git add .
git commit -m "fix"
git push origin main
