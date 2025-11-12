# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a blockchain-based traceability system for garment manufacturing. The system tracks garments through their entire production lifecycle using Swarm distributed storage and stores hash references in a database. The system includes:
- **Backend API (Flask)**: REST API for authentication and tickbarr hash retrieval
- **Data Pipeline (Python)**: Scripts to extract, process, and upload garment data to Swarm
- **Frontend (Next.js)**: Modern web interface with authentication, QR/barcode scanning, and multi-language support

## Architecture

The project consists of three main components:

### Backend API (Swarm/backend.py)
Flask REST API that provides:
- **Authentication**: JWT-based login system using Oracle database user verification
- **Hash Retrieval**: `/get_hash` endpoint to query Swarm hashes by tickbarr number from MariaDB
- **CORS Configuration**: Configured to allow requests from frontend (128.0.17.5:3000)

**Key endpoints:**
- `POST /login` → Authenticates user via Oracle `prc_login` procedure, returns JWT token
- `POST /get_hash` → Receives tickbarr, returns corresponding Swarm hash from MariaDB
- `GET /protected` → Protected route example (requires JWT)

**CORS Configuration:**
- Allows origins: `http://128.0.17.5:3000`, `http://localhost:3000`, `http://128.0.17.5`
- Supports credentials and preflight requests
- Runs on port 5000 (0.0.0.0:5000)

### Data Pipeline (Swarm/)
Python scripts for data extraction and Swarm upload:
1. Extracts garment traceability data from Oracle databases (production and inventory systems)
2. Processes and filters relevant fields from multiple database tables
3. Uploads JSON data to Swarm distributed storage
4. Stores Swarm hash references in MariaDB for retrieval

**Key workflow scripts:**
- `get_tickbar_data.py` → Queries Oracle stored procedure `tzprc_traztick` to extract data from 14+ temporary tables
- `uploadFile.py` → Uploads processed JSON to Swarm via Bee API (localhost:1633)
- `saveHashInDb.py` → Main orchestration script that fetches yesterday's tickbarrs from Oracle, uploads to Swarm, and saves hashes to MariaDB
- `oracle_tickbarrs.py` → Queries garments processed yesterday from the inventory database
- `backend.py` → Flask REST API for authentication and hash retrieval

### Frontend (code/)
Next.js 16 application with TypeScript featuring:
- **Authentication System**: JWT-based login with Oracle user verification
- **Multi-language Support**: English and Spanish (i18n)
- **Theme Support**: Dark/Light mode toggle
- **QR/Barcode Scanner**: Camera-based scanning for tickbarr input
- **Traceability Dashboard**: Tabbed interface displaying garment production history

**Component Structure:**
- `app/page.tsx` → Main page with authentication guard and hash submission flow
- `app/layout.tsx` → Root layout with theme and auth providers
- `components/login-form.tsx` → User authentication form
- `components/hash-input.tsx` → Tickbarr input with scanner integration
- `components/traceability-dashboard.tsx` → Main dashboard displaying garment data
- `components/qr-scanner.tsx` → QR code scanner using device camera
- `components/barcode-scanner.tsx` → Barcode scanner component
- `components/scanner-selector.tsx` → Modal to choose between QR/barcode scanner
- `lib/auth-context.tsx` → Authentication state management (JWT, localStorage)
- `lib/theme-context.tsx` → Theme and language state management
- `lib/i18n.tsx` → Translation strings for English/Spanish

**Key Features:**
- JWT token stored in localStorage with auto-restore on page load
- Fetches tickbarr hash from Flask backend (`/get_hash` endpoint)
- Retrieves full traceability data from Ethereum Swarm gateway
- Responsive design with Tailwind CSS
- UI components from Radix UI and shadcn/ui

## Development Commands

### Backend Flask API
```bash
cd Swarm

# Install dependencies
pip install -r requirements.txt

# Run Flask API server (port 5000)
python backend.py
```

### Data Pipeline (Python)
```bash
cd Swarm

# Run the main data pipeline (uploads yesterday's tickbarrs to Swarm)
python saveHashInDb.py

# Test individual functions
python get_tickbar_data.py  # Query single tickbarr data
python uploadFile.py        # Upload single tickbarr to Swarm
python oracle_tickbarrs.py  # Get yesterday's tickbarrs
```

### Frontend (Next.js)
```bash
cd code

# Install dependencies
npm install

# Development server (default port 3000)
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## Environment Configuration

Backend requires `.env` file in `Swarm/` directory with:
- Oracle database credentials (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
- Oracle inventory database credentials (DBIN_USER, DBIN_PASSWORD, DBIN_HOST, DBIN_PORT, DBIN_NAME)
- MariaDB credentials (DB_PRENDAS_USER, DB_PRENDAS_PASSWORD, DB_PRENDAS_HOST, DB_PRENDAS_PORT, DB_PRENDAS_NAME)

Note: The `.env` file is gitignored and contains sensitive database credentials.

## Key Data Flow

### Data Pipeline (Batch Upload)
1. `oracle_tickbarrs.py` queries garments from yesterday: `SELECT ttickbarr FROM apdoprendas WHERE trunc(tfechmovi) = trunc(sysdate - 1)`
2. For each tickbarr, `get_tickbar_data.py` calls Oracle procedure `tzprc_traztick` that populates 14 temporary tables with production history
3. Data is filtered using `relevant_data.json` configuration (defines which fields to extract from each table)
4. JSON is uploaded to Swarm via Bee API (localhost:1633), returns a reference hash
5. Hash is stored in MariaDB table `apdobloctrazhash` (columns: TTICKBARR, TTICKHASH, TNUMEVERS)

### User Query Flow (Frontend → Backend → Swarm)
1. **User Authentication**: User logs in via frontend → `POST /login` to Flask API → Oracle `prc_login` verification → JWT token returned
2. **Tickbarr Input**: User enters/scans tickbarr in frontend (hash-input.tsx)
3. **Hash Retrieval**: Frontend calls `POST /get_hash` with tickbarr → Flask queries MariaDB → Returns Swarm hash
4. **Data Retrieval**: Frontend fetches JSON from Swarm gateway: `https://api.gateway.ethswarm.org/bzz/{hash}`
5. **Display**: Traceability dashboard renders garment production data in tabbed interface

### API Flow Diagram
```
Frontend (Next.js)              Backend (Flask)                 Databases
     |                                |                              |
     |--POST /login----------------->|                              |
     |  {username, password}          |--prc_login----------------->| Oracle
     |                                |<----------------------------|
     |<-JWT token--------------------|                              |
     |                                |                              |
     |--POST /get_hash-------------->|                              |
     |  {tickbarr: "123456"}          |--SELECT TTICKHASH---------->| MariaDB
     |                                |<----------------------------|
     |<-{hash: "abc123..."}----------|                              |
     |                                |                              |
     |--GET Swarm Gateway----------->|                        Ethereum Swarm
     |<-JSON traceability data-------|                              |
```

## Database Tables Used

The system queries these Oracle temporary tables (populated by `tzprc_traztick` procedure):
- `tztotrazwebinfo` - Basic garment and client information
- `tztotrazwebalma` - Warehouse/storage information
- `tztotrazwebacab` - Quality control and auditing
- `tztotrazwebacabmedi` - Measurements
- `tztotrazwebteje` - Weaving details
- `tztotrazwebtint` - Dyeing and finishing
- `tztotrazwebhilo` - Yarn information
- `tztotrazwebhilolote` - Yarn lot details
- `tztotrazwebhiloloteprin` - Primary yarn lot information
- `tztotrazwebcost` - Sewing/assembly information
- `tztotrazwebcostoper` - Sewing operations
- `tztotrazwebcort` - Cutting information
- `tztotrazwebcortoper` - Cutting operations

## Important Notes

### Backend Configuration
- Flask API runs on `0.0.0.0:5000`
- CORS is configured to allow requests from `http://128.0.17.5:3000`, `http://localhost:3000`, and `http://128.0.17.5`
- JWT secret key: `supersecretkey` (should be changed in production)
- JWT token expiration: 48 hours
- The Bee API (Swarm node) must be running on localhost:1633 for data pipeline
- Batch stamp (postage stamp ID) hardcoded in `saveHashInDb.py`: `742bfeab75365749b4a909f1bc384a06ae98a8cb9e9d2850aa4c3209bbdd4a0e`

### Frontend Configuration
- Built with Next.js 16 and TypeScript
- Runs on default Next.js port (3000) in development
- Backend API URL hardcoded in components: `http://128.0.17.5:5000`
- Swarm gateway URL: `https://api.gateway.ethswarm.org/bzz/`
- Authentication tokens stored in browser localStorage
- Supports both QR codes and barcodes via device camera (using jsqr and jsbarcode libraries)

### Database Configuration
- Oracle encoding set to UTF-8 via `NLS_LANG=.AL32UTF8`
- MariaDB table `apdobloctrazhash` stores tickbarr-to-hash mappings with versioning (TNUMEVERS)
- Oracle `prc_login` procedure handles user authentication
- The system processes garments daily in batch mode (yesterday's production)

### Legacy Frontend
- Old React frontend exists in `traza-frontend/` directory (deprecated)
- Current production frontend is in `code/` directory (Next.js)

## Troubleshooting

### CORS Issues
If you encounter CORS preflight errors:
1. Verify Flask backend is running on port 5000
2. Check CORS configuration in `Swarm/backend.py` includes your frontend origin
3. Ensure frontend is making requests to correct endpoint URLs (e.g., `/get_hash` not `/`)
4. Restart both backend and frontend after configuration changes

### Authentication Issues
- JWT tokens expire after 48 hours - users need to re-login
- Tokens are stored in localStorage - clear browser storage if issues persist
- Verify Oracle `prc_login` procedure is accessible and functioning
- Check network connectivity to Oracle database (DB_HOST, DB_PORT)

### Scanner Issues
- Requires HTTPS or localhost for camera access (browser security)
- Ensure camera permissions are granted in browser
- Test with both QR and barcode formats if one fails
