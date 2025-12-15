# Frontend login client additions

- `frontend/` contains a Vite + React application for a simple login experience that talks to the existing Django API.
- `frontend/src/App.jsx` renders the login form (username, email, password), validates input locally, fetches the user by email via `GET /api/users`, compares credentials, and on success posts to `/api/logins/add` to record the login.
- `frontend/src/api.js` centralizes API calls with basic error handling and the base URL `http://localhost:8000/api`.
- `frontend/src/main.jsx`, `frontend/src/main.css`, and `frontend/src/App.css` bootstrap the React app and provide minimal styling for the card layout and status alerts.
- `frontend/index.html` is the Vite entry HTML, while `frontend/vite.config.js` configures the dev server.
- `frontend/.gitignore` ignores build artifacts such as `node_modules` and `dist`.

> Note: Installing npm dependencies may require access to the npm registry; if blocked, rerun `npm install` inside `frontend/` once network access is available to generate `package-lock.json`.
