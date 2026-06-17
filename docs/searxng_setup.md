# SearXNG Setup for Nexus

## What is SearXNG?

SearXNG is an open-source metasearch engine.

Instead of searching a single search provider, SearXNG aggregates results from multiple search engines and returns them through a unified interface.

Example:

```text
Nexus
  ↓
SearXNG
  ├── Google
  ├── Bing
  ├── DuckDuckGo
  └── Brave
```

---

# Why Use SearXNG?

## Advantages

### Privacy

No API keys required.

### Local First

Can run entirely on the developer's machine.

### Cost

No recurring API expenses.

### Unified Interface

One API regardless of search provider.

### Recruiter Value

Demonstrates understanding of:

* Docker
* Self-hosted services
* Tool calling
* External integrations

---

# Why Not Use SerpAPI?

Pros:

* High quality results
* Easy setup

Cons:

* Paid
* External dependency
* Requires API key

---

# Why Not Use Tavily?

Pros:

* Popular for AI agents
* Agent-focused

Cons:

* API key required
* Usage limits

---

# Why SearXNG For Nexus?

Project goals:

* Local-first
* Open-source
* No API costs
* Production-like architecture

SearXNG aligns well with all four goals.

---

# Architecture

```text
Nexus Agent
      │
      ▼
WebSearchTool
      │
      ▼
SearXNG
      │
      ▼
Search Providers
```

---

# Future Extensions

Possible future additions:

* Result caching
* Search reranking
* News search
* Image search
* Domain filtering
* Search analytics

---

# Installation

```
# Install prerequisites
sudo apt update

sudo apt install -y \
    ca-certificates \
    curl \
    gnupg

# Add Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update

sudo apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Run Docker without sudo
sudo usermod -aG docker $USER

newgrp docker

# Verify
docker --version

docker run hello-world
```

## SearXNG config


```
# Inside compose.yaml:
services:
  searxng:
    image: searxng/searxng:latest
    container_name: nexus-searxng

    ports:
      - "8080:8080"

    restart: unless-stopped

    environment:
      - BASE_URL=http://localhost:8080/

    volumes:
      - searxng-data:/etc/searxng

volumes:
  searxng-data:

# Start SearXNG
cd <path>
docker compose up -d

# Check
docker ps

# Verify on localhost:8080
# Verify API
curl "http://localhost:8080/search?q=Qwen3&format=json"

## Issue 403 Forbidden
Check log: docker logs nexus-searxng --tail 50
Check settings.yml: docker exec -it nexus-searxng cat /etc/searxng/settings.yml
= Solved by add:

Search:
  formats:
    - html
    - json

limiter: false

# Verify API structure
curl \
"http://localhost:8080/search?q=Qwen3&format=json" \
| jq '.results[0]'

```

---