# Check if the virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python setup_env.py
} else {
    Write-Host "Activating virtual environment..."
}

# Activate the virtual environment (assuming Windows)
$activateScript = ".venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    . $activateScript
} else {
    Write-Host "Warning: Virtual environment activation script not found."
}

# Create a default key.json file if it doesn't exist
if (-not (Test-Path "key.json")) {
    @'
{
    "CLIENT_ID": "<YOUR_CLIENT_ID>",
    "CLIENT_SECRET": "<YOUR_CLIENT_SECRET>"
}
'@ | Out-File -Encoding UTF8 key.json
    Write-Host "Default key.json file created. Please update it with your credentials."
    exit 1
}

# Parse the JSON file to retrieve credentials
$jsonContent = Get-Content key.json | Out-String | ConvertFrom-Json
$CLIENT_ID = $jsonContent.CLIENT_ID
$CLIENT_SECRET = $jsonContent.CLIENT_SECRET

# Ensure a subcommand was provided as the first argument
if ($args.Length -eq 0) {
    Write-Host "No subcommand provided."
    exit 1
}

# Get the subcommand and shift the arguments
$subcommand = $args[0]
$argsList = @()
if ($args.Length -gt 1) {
    $argsList = $args[1..($args.Length - 1)]
}

# Check for the --debug option
$DEBUG = $false
$otherArgs = @()
foreach ($arg in $argsList) {
    if ($arg -eq "--debug") {
        $DEBUG = $true
    } else {
        $otherArgs += $arg
    }
}

# Build the base Python command
$pythonCommand = "python"
if ($DEBUG) {
    # Launch with debugpy waiting for client on port 5678
    $pythonArgs = @("-m", "debugpy", "--wait-for-client", "--listen", "5678", "main.py")
} else {
    $pythonArgs = @("main.py")
}

# Depending on the subcommand, build the appropriate argument list and invoke Python
switch ($subcommand) {
    "rgb" { 
        $fullArgs = $pythonArgs + @(
            "--point1", "45.68", "10.58",
            "--point2", "45.42", "10.98",
            "rgb",
            "--client_id", $CLIENT_ID,
            "--client_secret", $CLIENT_SECRET,
            "--start_date", "2023-01-01",
            "--end_date", "2023-12-31",
            "--cloud_coverage", "20"
        ) + $otherArgs
        & $pythonCommand @fullArgs
    }
    "stemp" { 
        $fullArgs = $pythonArgs + @(
            "--point1", "45.68", "10.58",
            "--point2", "45.42", "10.98",
            "stemp",
            "--client_id", $CLIENT_ID,
            "--client_secret", $CLIENT_SECRET,
            "--start_date", "2023-01-01",
            "--end_date", "2023-12-31",
            "--cloud_coverage", "20"
        ) + $otherArgs
        & $pythonCommand @fullArgs
    }
    "landcover" { 
        $fullArgs = $pythonArgs + @(
            "--point1", "45.68", "10.58",
            "--point2", "45.42", "10.98",
            "landcover",
            "--client_id", $CLIENT_ID,
            "--client_secret", $CLIENT_SECRET,
            "--start_date", "2023-01-01",
            "--end_date", "2023-12-31",
            "--cloud_coverage", "20"
        ) + $otherArgs
        & $pythonCommand @fullArgs
    }
    "sentinel_gprox" {
        $fullArgs = $pythonArgs + @(
            "--point1", "45.68", "10.58",
            "--point2", "45.42", "10.98",
            "sentinel_gprox",
            "--client_id", $CLIENT_ID,
            "--client_secret", $CLIENT_SECRET,
            "--start_date", "2023-01-01",
            "--end_date", "2023-12-31",
            "--cloud_coverage", "20",
            "--meter_radius", "1000"
        ) + $otherArgs
        & $pythonCommand @fullArgs
    }
    "s3_esaworldcover" {
        $fullArgs = $pythonArgs + @(
            "--point1", "45.68", "10.58",
            "--point2", "45.42", "10.98",
            "s3_esaworldcover",
            "--version", "2"
        ) + $otherArgs
        & $pythonCommand @fullArgs
    }
    "s3_gprox" {
        $fullArgs = $pythonArgs + @(
            "--point1", "45.68", "10.58",
            "--point2", "45.42", "10.98",
            "s3_gprox",
            "--version", "2",
            "--meter_radius"
        ) + $otherArgs
        & $pythonCommand @fullArgs
    }
    "file_gprox" {
        $fullArgs = $pythonArgs + @(
            "--point1", "45.68", "10.58",
            "--point2", "45.42", "10.98",
            "file_gprox",
            "--input_file", "test_files/res/esaworldcover.tif",
            "--value_to_map", "10",
            "--meter_radius"
        ) + $otherArgs
        & $pythonCommand @fullArgs
    }
    "clean" {
        Remove-Item -Path "output\*" -Recurse -Force
    }
    Default {
        Write-Host "Unknown subcommand: $subcommand"
        exit 1
    }
}
