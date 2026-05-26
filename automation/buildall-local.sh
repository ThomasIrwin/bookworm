#!/usr/bin/env bash
set -e # Exit if any command fails

# --- CONFIG ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$SCRIPT_DIR/../server"
FRONTEND_DIR="$SCRIPT_DIR/../frontend"
SERVER_IMG_NAME="bookworm-server"
SERVER_CONTAINER_NAME="bookworm-server"
NETWORK_NAME="bookworm-network"
SERVER_PORT=8080
MAX_WAIT=60 # Seconds

log() { echo -e "\033[1;34m[bookworm]\033[0m $1"; }

# --- Database Startup --- #
start_db() {
    log "Starting PostgreSQL..."
    docker compose up -d postgres

    log "Waiting for database to be healthy..."
    local elapsed=0
    until [ "$(docker inspect --format='{{.State.Health.Status}}' bookworm-db 2>/dev/null)" = "healthy" ]; do
        if [ $elapsed -ge $MAX_WAIT ]; then
            echo "ERROR: Database unhealthy for more than 1 minute. Exiting..." >&2
            exit 1
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done
    log "Database healthy"
}

# --- Server Startup --- #
start_server() {
    log "Running tests..."
    (cd $SERVER_DIR && ./mvnw test)

    log "Building JAR..."
    (cd $SERVER_DIR && docker build -t "$SERVER_IMG_NAME" .)

    log "Starting server container..."
    # Clean up any old containers
    docker rm -f "$SERVER_CONTAINER_NAME" 2>/dev/null || true

    docker run -d \
        --name "$SERVER_CONTAINER_NAME" \
        --network "$NETWORK_NAME" \
        --env-file $SERVER_DIR/.env \
        -p "${SERVER_PORT}:8080" \
        "$SERVER_IMG_NAME"

    log "Waiting for server to be healthy..."
    local elapsed=0
    until curl -sf "http://localhost:${SERVER_PORT}/api/v1/actuator/health" > /dev/null 2>&1; do
        if [ $elapsed -ge $MAX_WAIT ]; then
        echo "ERROR: Server unhealthy for more than 1 minute. Exiting..." >&2
        exit 1
        fi
        sleep 3
        elapsed=$((elapsed + 3))
    done
    log "Server is healthy."
}

# --- Frontend Startup --- #
start_frontend() {
  log "Starting frontend..."
  (cd $FRONTEND_DIR && exec npm run dev)
}

# --- Entry Point --- #
main() {
  start_db
  start_server
  start_frontend  # Blocking (script stays alive watching npm)
}

main
