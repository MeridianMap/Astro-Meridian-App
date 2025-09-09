$payload = @{
    "subject" = @{
        "name" = "Test Person - 1987-07-15 09:01"
        "datetime" = @{ "iso_string" = "1987-07-15T09:01:00" }
        "latitude" = @{ "decimal" = 32.7833333333 }
        "longitude" = @{ "decimal" = -96.8 }
        "timezone" = @{ "name" = "America/Chicago" }
    }
    "configuration" = @{
        "house_system" = "P"
        "include_asteroids" = $true
        "include_nodes" = $true  
        "include_lilith" = $true
    }
    "include_aspects" = $true
    "aspect_orb_preset" = "traditional"
    "metadata_level" = "audit"
}

$json = $payload | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/ephemeris/natal" -Method POST -Body $json -ContentType "application/json"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$filename = "api_output_$timestamp.json"

$output = @{
    "test_info" = @{
        "endpoint" = "http://127.0.0.1:8000/ephemeris/natal"
        "timestamp" = (Get-Date).ToString("o")
        "status" = "success"
    }
    "request" = $payload
    "response" = $response
}

$output | ConvertTo-Json -Depth 20 | Out-File -FilePath $filename -Encoding UTF8

Write-Host "✅ SUCCESS! API response saved to: $filename"
Write-Host ""
Write-Host "=== CHART SUMMARY ==="
Write-Host "Planets found: $($response.planets.Count)"
Write-Host "Aspects found: $($response.aspects.Count)" 
Write-Host ""
Write-Host "Sample planets:"
$response.planets.GetEnumerator() | Select-Object -First 5 | ForEach-Object {
    $planet = $_.Key
    $data = $_.Value
    Write-Host "  $planet`: $([math]::Round($data.longitude, 2))° in $($data.sign), House $($data.house)"
}

if ($response.calculation_metadata) {
    Write-Host ""
    Write-Host "Calculation time: $($response.calculation_metadata.calculation_time)s"
}
