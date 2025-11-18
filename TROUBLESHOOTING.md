# Troubleshooting Guide

## Frontend Connection Reset Errors

If you're seeing `ERR_CONNECTION_RESET` errors when loading the frontend:

### Issue
The frontend API service was using absolute URLs which bypassed Vite's proxy configuration.

### Solution Applied
The API service now uses relative paths by default, which allows Vite's proxy to forward requests to the backend.

### Steps to Fix

1. **Restart the Docker containers**:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

2. **Check container logs**:
   ```bash
   # Frontend logs
   docker-compose logs frontend -f
   
   # Backend logs
   docker-compose logs backend -f
   ```

3. **Verify services are running**:
   ```bash
   docker-compose ps
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### WebSocket/HMR Issues

If you see WebSocket connection errors in the browser console:
- This is related to Vite's Hot Module Replacement (HMR)
- The app will still work, but live reloading might not function
- The configuration has been updated to fix this
- Restart the frontend container: `docker-compose restart frontend`

### Backend Memory Error (WatchfilesRustInternalError)

If you see "Cannot allocate memory (os error 12)" in backend logs:
- This is caused by uvicorn's file watcher running out of memory
- **Solution**: The `--reload` flag has been removed from the Docker configuration
- To apply code changes, restart manually: `docker-compose restart backend`
- If you need auto-reload, increase Docker Desktop memory allocation (Settings → Resources → Memory)
- The backend will work without auto-reload - just restart when you make code changes

### Common Issues

#### Frontend not loading
- Check if port 5173 is already in use
- Verify the frontend container is running: `docker ps | grep skillboard-frontend`
- Check frontend logs for errors: `docker-compose logs frontend`

#### Backend not responding
- Verify backend is running: `docker ps | grep skillboard-backend`
- Check backend logs: `docker-compose logs backend`
- Test backend directly: `curl http://localhost:8000/health`

#### Database connection issues
- Ensure PostgreSQL container is healthy: `docker ps | grep skillboard-postgres`
- Check database logs: `docker-compose logs postgres`
- Verify DATABASE_URL in docker-compose.yml

#### CORS errors
- Backend CORS is configured for `http://localhost:5173`
- If using a different port, update `backend/app/main.py` CORS settings

### Manual Testing

Test the backend API directly:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/skills/
```

Test the frontend proxy:
```bash
# This should work from the browser console or via curl
curl http://localhost:5173/api/skills/
```

### Rebuilding from Scratch

If issues persist:
```bash
# Stop and remove all containers
docker-compose down -v

# Rebuild everything
docker-compose build --no-cache

# Start services
docker-compose up -d

# Watch logs
docker-compose logs -f
```

