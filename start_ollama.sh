#!/bin/bash

until [ "$(docker inspect -f '{{.State.Health.Status}}' ollama)" == "healthy" ]; do
    echo "Waiting for ollama to be healthy..."
    sleep 5
done

docker exec -it ollama ollama run llama3
