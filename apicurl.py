$headers = @{
    "Content-Type" = "application/json"
    "x-goog-api-key" = $env:GOOGLE_API_KEY
}

$body = @{
    contents = @(
        @{
            parts = @(
                @{ text = "Explain how AI works in a few words" }
            )
        }
    )
} | ConvertTo-Json -Depth 10

# Note the updated model name in the URL: gemini-2.5-flash
Invoke-RestMethod -Uri "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" `
                  -Method Post `
                  -Headers $headers `
                  -Body $body