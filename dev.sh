#!/bin/bash

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating a new one..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    exit 1
else
    echo "Activating the virtual environment..."
    source .venv/bin/activate
fi


# Define the client ID and secret
config_file="key.json"

# Check if the key.json file exists
if [ ! -f "$config_file" ]; then
    echo "Creating key.json file..."
    cat <<EOL > "$config_file"
{
    "CLIENT_ID": "your_client_id_here",
    "CLIENT_SECRET": "your_client_secret_here"
}
EOL
else
    echo "key.json file already exists."
fi


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
            --point1 45.68 10.59 \
            --point2 45.42 10.98 \
            stype \
            --client_id $CLIENT_ID \
            --client_secret $CLIENT_SECRET \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20
        ;;
    gprox)
        python main.py \
            --point1 45.68 10.59 \
            --point2 45.42 10.98 \
            gprox \
            --client_id $CLIENT_ID \
            --client_secret $CLIENT_SECRET \
            --start_date "2023-01-01" \
            --end_date "2023-12-31" \
            --cloud_coverage 20 \
            --meter_radius 1000
        ;;
    s3_esaworldcover)
        python main.py \
            --point1 45.68 10.59 \
            --point2 45.42 10.98 \
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