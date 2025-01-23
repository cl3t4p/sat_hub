#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate


# Define the client ID and secret
config_file="key.json"

# Parse the JSON using jq
CLIENT_ID=$(jq -r '.CLIENT_ID' "$config_file")
CLIENT_SECRET=$(jq -r '.CLIENT_SECRET' "$config_file")

# Define the subcommand
SUBCOMMAND=$1
shift

# Run the main Python script with arguments
case $SUBCOMMAND in
    stype)
        python main.py \
            --point1 45.68685219444238 10.588434725123092 \
            --point2 45.42337178868138 10.981196017485841 \
            stype \
            --client_id $CLIENT_ID \
            --client_secret $CLIENT_SECRET \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20
        ;;
    gprox)
        python main.py \
            --point1 45.68685219444238 10.588434725123092 \
            --point2 45.42337178868138 10.981196017485841 \
            gprox \
            --client_id $CLIENT_ID \
            --client_secret $CLIENT_SECRET \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20 \
            --meterRadius 1000
        ;;
    s3_esaworldcover)
        python main.py \
            --point1 45.68685219444238 10.588434725123092 \
            --point2 45.42337178868138 10.981196017485841 \
            s3_esaworldcover \
            --version 2
        ;;
    clean)
        rm output/* -r
        ;;
    *)
        echo "Unknown subcommand: $SUBCOMMAND"
        exit 1
        ;;

esac