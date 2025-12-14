# Quick Setup Guide

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Installation Steps

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the backend server
cd backend
python app.py
```

The backend will start on `http://127.0.0.1:8000`

### 2. Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:3000
```

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure you're running `python app.py` from the `backend` directory
- **Port already in use**: Change the port in `backend/app.py` (line 12)
- **CORS errors**: Ensure `flask-cors` is installed: `pip install flask-cors`

### Frontend Issues

- **Module not found**: Run `npm install` again
- **Proxy errors**: Ensure the backend is running on port 8000
- **Build errors**: Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`

## Development

- Backend auto-reloads on file changes (Flask debug mode)
- Frontend hot-reloads on file changes (Vite HMR)
- Both servers need to be running simultaneously


