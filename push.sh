#!/bin/bash
docker build . -t docker.io/luckysideburn/vaultbot:v1.0.8
docker push docker.io/luckysideburn/vaultbot:v1.0.8
git add .
git commit -m "fix"
git push origin main
