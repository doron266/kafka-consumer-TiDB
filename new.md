# New files overview

## Frontend React application (`frontend/`)
- Added a Vite-powered React application that renders a simple login panel asking for username, email, and password. Successful credential matches trigger a confirmation message and record a login audit entry through the existing `/api/logins/add` endpoint.
- Login flow fetches the user with `/api/users?email=` and checks username/email/password locally before logging the attempt, aligning with the Django API shapes in `app/api/views.py`.
- Styling is contained in `src/styles.css` for a centered card experience, with form state handling in `src/App.jsx` and bootstrapping via `src/main.jsx` and `index.html`.
- `vite.config.js` sets a dev proxy to the Django API at port 8000 and exposes an environment override (`VITE_API_BASE_URL`) used by the React code.
- `frontend/Dockerfile` builds the React bundle and serves it via nginx using `frontend/nginx.conf`, which proxies `/api/` requests to the existing backend.

## Docker Compose copy with nginx (`docker-compose.frontend.yml`)
- Duplicates the existing stack and introduces a `frontend` service built from `./frontend`, exposing port `8080` to serve the static React build through nginx while routing `/api/` to the Django service on `8000`.
