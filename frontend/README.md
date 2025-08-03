# GTM Intelligence Frontend

A simple React app that interfaces with the GTM Intelligence API to research fintech companies.

## Features

- 🚀 **Real-time Research**: Send research requests to the API
- 📊 **Live Results**: View companies found with detailed analysis
- 📋 **Research Logs**: See real-time progress and logs
- 🎯 **Search Depth Control**: Choose quick, standard, or comprehensive search
- 📈 **Quality Metrics**: View quality and coverage scores
- 🏢 **Company Details**: See confidence scores, technologies, and evidence

## Quick Start

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the Development Server**:
   ```bash
   npm start
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:3000`

## Prerequisites

Make sure the GTM Intelligence API is running on `http://localhost:8001`:

```bash
# In the gtm-langgraph directory
source openfunnel/bin/activate
python app/simple_api.py
```

## Usage

1. **Enter Research Goal**: Type your research goal (e.g., "Find fintech companies using AI for fraud detection")

2. **Select Search Depth**:
   - **Quick**: 8 strategies, ~50 companies (fastest)
   - **Standard**: 15 strategies, ~100 companies (balanced)
   - **Comprehensive**: 25 strategies, ~200 companies (thorough)

3. **Click "Start Research"**: The app will send the request to the API and display results

4. **View Results**: See companies found, quality metrics, and recommendations

## API Endpoints

The frontend connects to these API endpoints:

- `POST /research` - Start a research request
- `GET /health` - Health check (not used in frontend)

## Technologies Used

- **React 18** - Frontend framework
- **Axios** - HTTP client for API calls
- **CSS3** - Styling with modern gradients and animations
- **Inter Font** - Clean typography

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.js          # Main React component
│   ├── App.css         # Component styles
│   ├── index.js        # React entry point
│   └── index.css       # Global styles
├── package.json
└── README.md
```

## Development

To modify the frontend:

1. Edit `src/App.js` for component logic
2. Edit `src/App.css` for component styles
3. Edit `src/index.css` for global styles
4. The app will hot-reload automatically

## Deployment

To build for production:

```bash
npm run build
```

This creates a `build/` folder with optimized files ready for deployment. 