Railway quick setup

1. Push this project to GitHub.
2. In Railway create New Project -> Deploy from GitHub Repo.
3. Add PostgreSQL to the project.
4. In Variables add:
   BOT_TOKEN=...
   ADMINS=1160081337
   LOGS_DIR=/app/logs
5. Railway will automatically provide DATABASE_URL from PostgreSQL.
6. Redeploy the service.

The bot now works only with PostgreSQL. SQLite file storage is no longer used.
