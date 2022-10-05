#!/bin/bash
docker build . -t docker.io/luckysideburn/vaultbot:v1.0.0
docker push docker.io/luckysideburn/vaultbot:v1.0.0
