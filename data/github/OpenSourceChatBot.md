# OpenSource MentorBot

A multi-featured AI chatbot that helps learners explore open-source contributions (GSoC + GitHub + live data + 3D visualization).

## Architecture

- **Frontend:** React + TypeScript + Vite + Tailwind CSS + React Query
- **3D Visualization:** Three.js (@react-three/fiber)
- **Backend:** Spring Boot 3 + Java 17 + WebFlux + Caffeine Cache
- **AI Integration:** Gemini API
- **Data Sources:** GitHub API, GSoC Archive (Scraping)

## Prerequisites

- Java 17+
- Node.js 18+
- Maven
- Docker & Docker Compose (Optional)
- Gemini API Key

## Setup & Run

### Environment Variables

1.  **Backend**: Create `backend/.env` (or set env vars):
    ```env
    GEMINI_API_KEY=your_key
    GITHUB_TOKEN=your_token (optional)
    SERVER_PORT=8080
    ```
2.  **Frontend**: Create `frontend/.env`:
    ```env
    VITE_BACKEND_URL=http://localhost:8080
    VITE_ENV=development
    ```

### Docker (Recommended)

Run the entire stack with one command:

```bash
docker-compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8080`

### Manual Setup

#### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Build and run:
   ```bash
   mvn clean install
   mvn spring-boot:run
   ```

#### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Features

- **Live Data**: Real-time GitHub stats and GSoC organization data.
- **AI Chat**: Gemini-powered responses with context awareness.
- **3D Visualization**: Interactive 3D scenes for data exploration.
- **Dark Mode**: Toggle between light and dark themes.
- **Caching**: Optimized performance with backend caching.

## API Endpoints

- `POST /api/chat`: Main chat endpoint.
- `GET /api/orgs`: Fetch GSoC organizations.
- `GET /api/github?owner={owner}&repo={repo}`: Fetch GitHub repository details.

## Project Structure

- `backend/`: Spring Boot application.
- `frontend/`: React application.
