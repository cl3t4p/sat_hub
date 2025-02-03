#!/bin/bash

# Activate the virtual environment
# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python setup_env.py
else
    echo "Activating virtual environment..."
fi
source .venv/bin/activate

# Create a default key.json file if it doesn't exist
if [ ! -f "key.json" ]; then
    cat > key.json <<EOL
{
    "CLIENT_ID": "<YOUR_CLIENT_ID>",
    "CLIENT_SECRET": "<YOUR_CLIENT_SECRET>"
}
EOL
    echo "Default key.json file created. Please update it with your credentials."
    exit 1
fi

# Parse the JSON
CLIENT_ID=$(jq -r '.CLIENT_ID' key.json)
CLIENT_SECRET=$(jq -r '.CLIENT_SECRET' key.json)

# Define the subcommand
SUBCOMMAND=$1
shift

# Check if the --debug option is present
DEBUG=false
ARGS=()
for arg in "$@"; do
    if [ "$arg" == "--debug" ]; then
        DEBUG=true
    else
        ARGS+=("$arg")
    fi
done

if [ "$DEBUG" = true ]; then
    START_STRING="python -m debugpy --wait-for-client --listen 5678 main.py"
else
    START_STRING="python main.py"
fi

# Run the main Python script with arguments
case "$SUBCOMMAND" in
    "rgb" | "stype" | "stemp" | "vis")
        $START_STRING \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            "$SUBCOMMAND" \
            --client_id "$CLIENT_ID" \
            --client_secret "$CLIENT_SECRET" \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20 \
            "${ARGS[@]}"
        ;;
    "sentinel_gprox")
        $START_STRING \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            sentinel_gprox \
            --client_id "$CLIENT_ID" \
            --client_secret "$CLIENT_SECRET" \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20 \
            --meter_radius 1000 \
            "${ARGS[@]}"
        ;;
    "s3_esaworldcover")
        $START_STRING \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            s3_esaworldcover \
            --version 2 \
            "${ARGS[@]}"
        ;;
    "corine_landcover")
        $START_STRING \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            corine_landcover \
            "${ARGS[@]}"
        ;;
    "s3_gprox")
        $START_STRING \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            s3_gprox \
            --version 2 \
            --meter_radius "${ARGS[@]}"
        ;;
    "clean")
        rm -rf output/*
        ;;
    *)
        echo "Unknown subcommand: $SUBCOMMAND"
        exit 1
        ;;
esac