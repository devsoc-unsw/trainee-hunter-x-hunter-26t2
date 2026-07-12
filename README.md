# trainee-hunter-x-hunter-26t2

## Run with Docker

The Docker Compose stack starts:

- the React frontend at <http://localhost:3000>
- the FastAPI backend at <http://localhost:8000>
- PostgreSQL on `localhost:5432`

Start the full application:

```sh
docker compose up --build
```

The frontend proxies requests under `/api` to the backend. For example,
<http://localhost:3000/api/health> checks both the API and its database
connection.

To customize ports or database credentials, copy `.env.example` to `.env`
and edit it before starting the stack. The PostgreSQL data is retained in the
named `postgres_data` volume.

Stop the services with:

```sh
docker compose down
```

To also delete the local database data, run `docker compose down --volumes`.
