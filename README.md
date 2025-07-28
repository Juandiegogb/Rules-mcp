```
"mcpServers": {
    "rules": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/server",
        "run",
        "rules.py"
      ],
      "env": {
        "DB_USER": "postgres",
        "DB_HOST": "localhost",
        "DB_PASSWORD": "Admin",
        "DB_PORT": "5500",
        "DB_NAME": "new_db"
      }
    }
  }
```
