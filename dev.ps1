# Activate the virtual environment
& .\.venv\Scripts\Activate.ps1



# Parse the JSON
$config = Get-Content ".\key.json" | ConvertFrom-Json

# Access the values
$CLIENT_ID = $config.CLIENT_ID
$CLIENT_SECRET = $config.CLIENT_SECRET


# Define the subcommand
$SUBCOMMAND = $args[0]
$args = $args[1..($args.Length - 1)]

# Run the main Python script with arguments
switch ($SUBCOMMAND) {
    "stype" {
        python main.py `
            --point1 45.68685219444238 10.588434725123092 `
            --point2 45.42337178868138 10.981196017485841 `
            stype `
            --client_id $CLIENT_ID `
            --client_secret $CLIENT_SECRET `
            --start_date "2023-01-01" `
            --end_date "2023-12-31" `
            --cloud_coverage 20
    }
    "gprox" {
        python main.py `
            --point1 45.68685219444238 10.588434725123092 `
            --point2 45.42337178868138 10.981196017485841 `
            gprox `
            --client_id $CLIENT_ID `
            --client_secret $CLIENT_SECRET `
            --start_date "2023-01-01" `
            --end_date "2023-12-31" `
            --cloud_coverage 20 `
            --meterRadius 1000
    }
    "stemp" {
        python main.py `
            --point1 45.68685219444238 10.588434725123092 `
            --point2 45.42337178868138 10.981196017485841 `
            stemp `
            --client_id $CLIENT_ID `
            --client_secret $CLIENT_SECRET `
            --start_date "2023-01-01" `
            --end_date "2023-12-31" `
            --cloud_coverage 20 `
    }
    "vis" {
        python main.py `
            --point1 45.68685219444238 10.588434725123092 `
            --point2 45.42337178868138 10.981196017485841 `
            vis `
            --client_id $CLIENT_ID `
            --client_secret $CLIENT_SECRET `
            --start_date "2023-01-01" `
            --end_date "2023-12-31" `
            --cloud_coverage 20 `
    }
    "s3_esaworldcover" {
        python main.py `
            --point1 45.68685219444238 10.588434725123092 `
            --point2 45.42337178868138 10.981196017485841 `
            s3_esaworldcover `
            --version 2
    }
    "clean" {
        Remove-Item output\* -Recurse -Force
    }
    Default {
        Write-Host "Unknown subcommand: $SUBCOMMAND"
        exit 1
    }
}
