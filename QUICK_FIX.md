# Quick Fix: Frontend Not Loading

If the frontend page is not opening in Docker, try these solutions:

## Solution 1: Run Frontend Locally (Recommended for Development)

Instead of running the frontend in Docker, run it locally:

1. **Stop the frontend container:**
   ```bash
   docker-compose stop frontend
   ```

2. **Install dependencies locally:**
   ```bash
   cd frontend
   npm install
   ```

3. **Run the frontend locally:**
   ```bash
   npm run dev
   ```

4. **Keep backend and database in Docker:**
   ```bash
   # In another terminal, from project root
   docker-compose up -d postgres backend
   ```

The frontend will connect to the backend at `http://localhost:8000` via the Vite proxy.

## Solution 2: Fix Docker Networking

If you must use Docker for frontend:

1. **Check Windows Firewall:**
   - Ensure port 5173 is not blocked
   - Add exception for Docker Desktop

2. **Restart Docker Desktop:**
   - Sometimes Docker networking needs a reset

3. **Use a different port:**
   ```yaml
   # In docker-compose.yml
   ports:
     - "3000:5173"  # Use port 3000 instead
   ```
   Then access at `http://localhost:3000`

## Solution 3: Check for Port Conflicts

```bash
# Check what's using port 5173
netstat -ano | findstr :5173

# Kill the process if needed (replace PID with actual process ID)
taskkill /PID <PID> /F
```

## Why This Happens

Docker networking on Windows can sometimes have issues with port forwarding, especially with development servers that use WebSockets (like Vite HMR). Running the frontend locally while keeping backend in Docker is often the most reliable solution for development.

