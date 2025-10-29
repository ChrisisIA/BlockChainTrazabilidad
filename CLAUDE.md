# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a blockchain-based traceability system for garment manufacturing. The system tracks garments through their entire production lifecycle using Swarm distributed storage and stores hash references in a database. The frontend provides a web interface to query and display garment traceability information using Swarm hashes.

## Architecture

The project consists of two main components:

### Backend (Swarm/)
Python-based data pipeline that:
1. Extracts garment traceability data from Oracle databases (production and inventory systems)
2. Processes and filters relevant fields from multiple database tables
3. Uploads JSON data to Swarm distributed storage
4. Stores Swarm hash references in MariaDB for retrieval

**Key workflow:**
- `get_tickbar_data.py` → Queries Oracle stored procedure `tzprc_traztick` to extract data from 14+ temporary tables
- `uploadFile.py` → Uploads processed JSON to Swarm via Bee API (localhost:1633)
- `saveHashInDb.py` → Main orchestration script that fetches yesterday's tickbarrs from Oracle, uploads to Swarm, and saves hashes to MariaDB
- `oracle_tickbarrs.py` → Queries garments processed yesterday from the inventory database

### Frontend (traza-frontend/)
React application that:
- Accepts a Swarm hash input (tickbarr hash)
- Fetches JSON data from Swarm gateway
- Displays structured garment information (client, attributes, production history)

## Development Commands

### Backend (Python)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the main data pipeline (uploads yesterday's tickbarrs to Swarm)
cd Swarm
python saveHashInDb.py

# Test individual functions
python get_tickbar_data.py  # Query single tickbarr data
python uploadFile.py        # Upload single tickbarr to Swarm
python oracle_tickbarrs.py  # Get yesterday's tickbarrs
```

### Frontend (React)
```bash
cd traza-frontend

# Install dependencies
npm install

# Development server (runs on 0.0.0.0:3000)
npm start

# Production build
npm run build

# Run tests
npm test
```

## Environment Configuration

Backend requires `.env` file in `Swarm/` directory with:
- Oracle database credentials (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
- Oracle inventory database credentials (DBIN_USER, DBIN_PASSWORD, DBIN_HOST, DBIN_PORT, DBIN_NAME)
- MariaDB credentials (DB_PRENDAS_USER, DB_PRENDAS_PASSWORD, DB_PRENDAS_HOST, DB_PRENDAS_PORT, DB_PRENDAS_NAME)

Note: The `.env` file is gitignored and contains sensitive database credentials.

## Key Data Flow

1. `oracle_tickbarrs.py` queries garments from yesterday: `SELECT ttickbarr FROM apdoprendas WHERE trunc(tfechmovi) = trunc(sysdate - 1)`
2. For each tickbarr, `get_tickbar_data.py` calls Oracle procedure that populates 14 temporary tables with production history
3. Data is filtered using `relevant_data.json` configuration (defines which fields to extract from each table)
4. JSON is uploaded to Swarm via Bee API, returns a reference hash
5. Hash is stored in MariaDB table `apdobloctrazhash` (columns: TTICKBARR, TTICKHASH)
6. Frontend queries Swarm gateway with hash to retrieve and display data

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

- The Bee API (Swarm node) must be running on localhost:1633
- Batch stamp (postage stamp ID) is hardcoded in `saveHashInDb.py`: `742bfeab75365749b4a909f1bc384a06ae98a8cb9e9d2850aa4c3209bbdd4a0e`
- Frontend is configured for deployment at: `/intranet/planeamiento/trazabilidad_blockchain`
- Frontend queries public Swarm gateway: `https://api.gateway.ethswarm.org/bzz/`
- Oracle encoding is set to UTF-8 via `NLS_LANG=.AL32UTF8`
- The system processes garments daily in batch mode (yesterday's production)
