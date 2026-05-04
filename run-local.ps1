Write-Host "Starting AI Manager..."
Start-Process powershell -ArgumentList "cd ai-manager; npm install; npm run start"

Start-Sleep -Seconds 3

Write-Host "Starting Dashboard..."
Start-Process powershell -ArgumentList "cd dashboard-web; npm install; npm run dev"

Start-Sleep -Seconds 3

Write-Host "Starting Worker Bot..."
Start-Process powershell -ArgumentList "cd worker-bot; pip install -r requirements.txt; python main.py"
