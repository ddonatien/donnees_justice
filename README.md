# donnees_justice

A modular system for processing and analyzing French administrative court data.

## Overview

This project provides a clean, deterministic pipeline for:
1. **Ingesting** raw XML court decisions
2. **Processing** data into validated Parquet datasets
3. **Analyzing** statistics and generating visualizations
4. **Serving** results through a minimal web interface

## Architecture

```
data/raw/ (XML)
    ↓ ingest (Rust)
data/clean/ (Parquet)
    ↓ analytics (Python)
statistics & plots
    ↓ web (FastAPI)
HTML interface
```

## Quick Start

### Prerequisites
- Rust (for data pipelines)
- Python 3.9+ (for analytics and web)
- Cargo (Rust package manager)
- pip (Python package manager)

### Setup

```bash
# Clone repository
git clone https://github.com/your-repo/donnees_justice.git
cd donnees_justice

# Install Rust dependencies
cargo build --workspace

# Install Python dependencies
pip install -r analytics/requirements.txt
pip install -r web/requirements.txt
```

### Running the Pipeline

```bash
# 1. Ingest raw XML data → clean Parquet
./scripts/run_ingest.sh

# 2. Run optional compute aggregations
./scripts/run_compute.sh

# 3. Start web server
./scripts/run_server.sh
```

## Components

### 🦀 Rust Pipelines

**Ingest Pipeline** (`pipelines/ingest/`)
- Reads XML files from `data/raw/`
- Validates and normalizes data
- Outputs Parquet files to `data/clean/`
- Idempotent and deterministic

**Compute Pipeline** (`pipelines/compute/`)
- Optional heavy aggregations
- Pre-computes complex statistics
- Outputs additional Parquet files

### 🐍 Python Analytics

**Metrics Module** (`analytics/metrics/`)
- Statistical computations
- Pure functions (no I/O)
- Input: DataFrames/Arrow Tables
- Output: Typed results (Pydantic models)

**Plots Module** (`analytics/plots/`)
- Visualization specifications
- Server-side rendering
- SVG/image output

### 🌐 Web Interface

**FastAPI Server** (`web/server/`)
- Server-rendered HTML (Jinja2)
- Progressive enhancement with htmx
- RESTful API endpoints
- No client-side frameworks

## Configuration

Configuration uses layered YAML files:
- `configs/base.yaml` - Base configuration
- `configs/dev.yaml` - Development overrides
- `configs/prod.yaml` - Production overrides
- Environment variables for secrets

Example:
```yaml
# configs/base.yaml
schema:
  type: object
  properties:
    data_dir:
      type: string
      description: Path to data directories
  required:
    - data_dir
```

## Data Structure

### Raw Data
- XML files from French administrative courts
- Located in `data/raw/TA_YYYYMM/` directories
- Contains case metadata and full text decisions
- Example: `DTA_1805012_20251202.xml`

### Clean Data
- Parquet format with Arrow schemas
- Validated and normalized
- Stored in `data/clean/`
- Schema definitions in `shared/schema/`

## Development

### Building

```bash
# Build all Rust components
cargo build --workspace

# Run tests
cargo test
pytest

# Lint code
cargo clippy
black --check
flake8
```

### Testing

```bash
# Run specific test
pytest analytics/tests/test_metrics.py

# Run Rust tests
cargo test --package ingest
```

## Data Sample

The repository includes a sample XML file (`data_sample.xml`) showing the structure of French administrative court decisions:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document>
  <Donnees_Techniques>
    <Identification>ORTA_2520143_20251205.xml</Identification>
    <Date_Mise_Jour>2026-01-27</Date_Mise_Jour>
  </Donnees_Techniques>
  <Dossier>
    <Code_Juridiction>TA95</Code_Juridiction>
    <Nom_Juridiction>Tribunal Administratif de Cergy-Pontoise</Nom_Juridiction>
    <Numero_Dossier>2520143</Numero_Dossier>
    <Date_Lecture>2025-12-05</Date_Lecture>
    <Type_Decision>Ordonnance</Type_Decision>
    <Type_Recours>Excès de pouvoir</Type_Recours>
    <Code_Publication>D</Code_Publication>
    <Solution>Désistement</Solution>
  </Dossier>
  <Decision>
    <Texte_Integral>...</Texte_Integral>
  </Decision>
</Document>
```

## Project Status

✅ **Complete**
- Architecture design and specification
- Project structure and scaffolding
- Configuration system
- Build scripts and tooling

📝 **In Progress**
- Rust ingestion pipeline implementation
- Python analytics functions
- Web interface development
- Schema definitions

🎯 **Future Work**
- Advanced statistical analysis
- Interactive visualizations
- Performance optimization
- Deployment automation

## Contributing

See [PROJECT_SPEC.txt](PROJECT_SPEC.txt) for detailed architecture and design principles.

## License

[MIT License](LICENSE) - Copyright (c) 2024 donnees_justice

## Contact

For questions or support, please open an issue on GitHub.
