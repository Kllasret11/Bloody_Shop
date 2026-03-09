Railway quick setup

1. Push this project to GitHub.
2. In Railway create New Project -> Deploy from GitHub Repo.
3. Add Variables:
   BOT_TOKEN=...
   ADMINS=1160081337
   DB_PATH=/app/data/database.db
   LOGS_DIR=/app/data/logs
4. Add a Volume and mount it to /app/data
5. Redeploy the service.
