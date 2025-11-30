# Tender

A database-driven mobile web application for pork product sensory evaluation and consumer preference testing.

## Overview

Tender is a comprehensive platform designed for meat quality assessment research at the University of Illinois. The application leverages annotated image files of pork products with associated metadata (color scores, marbling scores, etc.) to conduct consumer perception studies.

## Project Components

### Frontend (`/frontend`)
Consumer-facing mobile web interface for visual/sensory tests where participants select and rank pork product images based on their preferences.

### Admin Dashboard (`/admin-dashboard`)
Researcher interface for:
- Setting up experiments
- Managing annotated images and metadata
- Configuring consumer comparison tests
- Analyzing collected data (selection time, click patterns, rankings, etc.)

### Backend (`/backend`)
API server handling:
- Image and metadata management
- Experiment configuration
- Data collection and analytics
- User authentication and session management

### Database (`/database`)
Schema, migrations, and seed data for:
- Annotated pork product images
- Color and marbling scores
- Experiment configurations
- Consumer response data

### Scripts (`/scripts`)
Data consolidation and processing utilities for preparing annotated images and metadata.

## Getting Started

*Setup instructions will be added as the project develops.*

## Project Structure

```
MSL-Tender/
├── frontend/              # Consumer-facing mobile web app
├── admin-dashboard/       # Researcher admin interface
├── backend/              # API server
├── database/             # Schema, migrations, seeds
├── scripts/              # Data consolidation & processing
├── docs/                 # Documentation
└── study files/          # Research materials and data files
```

## Research Context

This application supports sensory evaluation research in meat science, enabling researchers to:
- Conduct controlled image-based preference studies
- Collect detailed interaction metrics
- Analyze consumer perception patterns
- Correlate visual preferences with objective quality metrics

## License

*To be determined*

## Contact

Ryan Dilger - University of Illinois
