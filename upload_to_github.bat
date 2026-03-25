@echo off
SETLOCAL
:: --- INSTRUCTIONS ---
:: 1. Create a repo on GitHub.com
:: 2. Paste the URL below
:: 3. Save and Double-Click this file
:: ---------------------

SET REPO_URL=PASTE_YOUR_GITHUB_URL_HERE

echo 🚀 Initializing Git...
git init

echo 📦 Adding files...
git add .

echo ✍️  Committing...
git commit -m "Initial commit: AI Study Planner Professional Project"

echo 🔗 Connecting to GitHub...
git branch -M main
git remote add origin %REPO_URL%

echo ⬆️  Pushing to GitHub...
git push -u origin main

echo.
echo ✅ ALL DONE! Your project is now on GitHub.
pause
