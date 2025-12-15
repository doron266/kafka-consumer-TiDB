# Notices and Potential Issues

- The new `docker-compose-nginxincluded.yml` lives in the `frontend/` directory. Paths to backend assets are relative (e.g., `../app`), so run it from that directory to ensure Docker can find the build context and scripts.
- The nginx container expects static assets in `frontend/dist`. Build the frontend before starting nginx (e.g., `npm install && npm run build`) or mount an existing `dist` directory, otherwise only proxying will work and static assets will 404.
- Application login validation currently runs entirely in the frontend and compares plaintext passwords returned by the API. This approach is insecure and should be replaced with server-side authentication.
- API requests now assume the app is accessed through the same host (base path `/api`). Local development against a standalone API on `localhost:8000` will need a proxy or an updated base URL.
- There is no nginx service in the original `docker-compose.yml`. Running both compose files concurrently will create duplicate service names (e.g., `pd`, `tidb`, `kafka`). Use only one at a time to avoid port and name collisions.
