# Activate the virtual environment
#Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python setup_env.py
} else {
    Write-Host "Activating virtual environment..."
}
& .venv\Scripts\Activate.ps1

# Create a default key.json file if it doesn't exist
if (-not (Test-Path ".\key.json")) {
    $defaultJson = @"
{
    "CLIENT_ID": "<YOUR_CLIENT_ID>",
    "CLIENT_SECRET": "<YOUR_CLIENT_SECRET>"
}
"@
    $defaultJson | Out-File -FilePath ".\key.json" -Encoding utf8
    Write-Host "Default key.json file created. Please update it with your credentials."
    exit 1
}

# Parse the JSON
$config = Get-Content ".\key.json" | ConvertFrom-Json

# Access the values
$CLIENT_ID = $config.CLIENT_ID
$CLIENT_SECRET = $config.CLIENT_SECRET


# Define the subcommand
$SUBCOMMAND = $args[0]


$args = $args[1..$args.Length]



#TODO: Add the option --debug to enable debugging


# Run the main Python script with arguments
switch ($SUBCOMMAND) {
    "rgb" {
        python -m debugpy --wait-for-client --listen 5678 main.py `
            --point1 45.68 10.58 `
            --point2 45.42 10.98 `
            rgb `
            --client_id $CLIENT_ID `
            --client_secret $CLIENT_SECRET `
            --start_date "2023-01-01" `
            --end_date "2023-12-31" `
            --cloud_coverage 20 `
            $args
    }
    "stype" {
        python -m debugpy --listen 5678 main.py `
            --point1 45.68 10.58 `
            --point2 45.42 10.98 `
            stype `
            --client_id $CLIENT_ID `
            --client_secret $CLIENT_SECRET `
            --start_date "2023-01-01" `
            --end_date "2023-12-31" `
            --cloud_coverage 20 `
            $args
    }
    "gprox" {
        python -m debugpy --listen 5678 main.py `
            --point1 45.68 10.58 `
            --point2 45.42 10.98 `
            gprox `
            --client_id $CLIENT_ID `
            --client_secret $CLIENT_SECRET `
            --start_date "2023-01-01" `
            --end_date "2023-12-31" `
            --cloud_coverage 20 `
            --meter_radius 1000 `
            $args
    }
    "stemp" {
        python -m debugpy --listen 5678 main.py `
            --point1 45.68 10.58 `
            --point2 45.42 10.98 `
            stemp `
            --client_id $CLIENT_ID `
            --client_secret $CLIENT_SECRET `
            --start_date "2023-01-01" `
            --end_date "2023-12-31" `
            --cloud_coverage 20 `
            $args
    }
    "vis" {
        python -m debugpy  --listen 5678 main.py `
            --point1 45.68 10.58 `
            --point2 45.42 10.98 `
            vis `
            --client_id $CLIENT_ID `
            --client_secret $CLIENT_SECRET `
            --start_date "2023-01-01" `
            --end_date "2023-12-31" `
            --cloud_coverage 20 `
            $args
    }
    "s3_esaworldcover" {
        python -m debugpy --listen 5678 main.py `
            --point1 45.68 10.58 `
            --point2 45.42 10.98 `
            s3_esaworldcover `
            --version 2
            $args
    }
    "s3_gprox" {
        python -m debugpy --listen 5678 main.py `
            --point1 45.68 10.58 `
            --point2 45.42 10.98 `
            s3_gprox `
            --version 2 `
            --meter_radius $args
    }
    "clean" {
        Remove-Item output\* -Recurse -Force
    }
    Default {
        Write-Host "Unknown subcommand: $SUBCOMMAND"
        exit 1
    }
}
