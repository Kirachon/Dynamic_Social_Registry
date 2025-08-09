$body = Get-Content test_household.json -Raw
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/households" -Method POST -ContentType "application/json" -Body $body
