#!/bin/bash

# Activate the virtual environment
# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 setup_venv.py
else
    echo "Activating virtual environment..."
fi

source .venv/bin/activate

# Create a default key.json file if it doesn't exist
if [ ! -f "./key.json" ]; then
    cat > key.json <<EOL
{
    "CLIENT_ID": "<YOUR_CLIENT_ID>",
    "CLIENT_SECRET": "<YOUR_CLIENT_SECRET>"
}
EOL
    echo "Default key.json file created. Please update it with your credentials."
    exit 1
fi

# Parse the JSON (Using jq for simplicity)
CLIENT_ID=$(jq -r '.CLIENT_ID' key.json)
CLIENT_SECRET=$(jq -r '.CLIENT_SECRET' key.json)

# Define the subcommand
SUBCOMMAND=$1
shift

# Run the main Python script with arguments
case "$SUBCOMMAND" in
    "stype")
        python main.py \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            stype \
            --client_id $CLIENT_ID \
            --client_secret $CLIENT_SECRET \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20
        ;;
    "gprox")
        python main.py \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            gprox \
            --client_id $CLIENT_ID \
            --client_secret $CLIENT_SECRET \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20 \
            --meterRadius 1000
        ;;
    "stemp")
        python main.py \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            stemp \
            --client_id $CLIENT_ID \
            --client_secret $CLIENT_SECRET \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20
        ;;
    "vis")
        python main.py \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            vis \
            --client_id $CLIENT_ID \
            --client_secret $CLIENT_SECRET \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20
        ;;
    "s3_esaworldcover")
        python main.py \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            s3_esaworldcover \
            --version 2
        ;;
    "s3_gprox")
        python main.py \
            --point1 45.68 10.58 \
            --point2 45.42 10.98 \
            s3_gprox \
            --version 2 \
            --meter_radius "$@"
        ;;
    "clean")
        rm -rf output/*
        ;;
    *)
        echo "Unknown subcommand: $SUBCOMMAND"
        exit 1
        ;;
esac
