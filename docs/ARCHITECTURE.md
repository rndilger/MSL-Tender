# Project Architecture - Tender

## Overview

Tender is a full-stack web application for conducting pork sensory evaluation research. The architecture follows a modern JAMstack approach using Supabase (PostgreSQL) and Vercel for hosting.

## Technology Stack

### Frontend (Consumer Interface)
- **Framework**: Next.js / React
- **Styling**: Tailwind CSS
- **State Management**: React Context / Zustand
- **Image Optimization**: Next.js Image component
- **Analytics**: Custom tracking with Supabase

### Admin Dashboard
- **Framework**: Next.js / React
- **UI Components**: Shadcn/ui or similar
- **Data Visualization**: Recharts or Chart.js
- **Forms**: React Hook Form + Zod validation

### Backend
- **Database**: PostgreSQL (via Supabase)
- **API**: Supabase Auto-generated REST API
- **Real-time**: Supabase Realtime subscriptions
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage for images

### Hosting & Deployment
- **Frontend Hosting**: Vercel
- **Database Hosting**: Supabase
- **CI/CD**: GitHub Actions → Vercel
- **Domain**: Custom domain via Vercel

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Repository                       │
│                    rndilger/MSL-Tender                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ├─────────────────────────────────────┐
                      │                                     │
                      ▼                                     ▼
            ┌──────────────────┐                ┌──────────────────┐
            │  Vercel Deploy   │                │  Data Scripts    │
            │   (Auto CI/CD)   │                │  (Local/Manual)  │
            └────────┬─────────┘                └────────┬─────────┘
                     │                                   │
                     ▼                                   ▼
         ┌──────────────────────┐          ┌──────────────────────┐
         │   Consumer Frontend  │          │  Supabase Database   │
         │   (Public Access)    │◄─────────┤   (PostgreSQL)       │
         └──────────────────────┘          │   + Storage          │
                     │                     └──────────┬───────────┘
                     │                                │
                     ▼                                ▼
         ┌──────────────────────┐          ┌──────────────────────┐
         │   Admin Dashboard    │          │  Analytics Data      │
         │  (Auth Required)     │◄─────────┤  (Experiment Results)│
         └──────────────────────┘          └──────────────────────┘
```

## Database Schema Summary

### Core Tables

1. **pork_samples** - Annotated pork chop data
   - Physical measurements (color, marbling, firmness)
   - Chemical composition (pH, moisture, fat)
   - Minolta color values (L*, a*, b*)

2. **experiments** - Research study configurations
   - Experiment metadata and settings
   - Status tracking (draft, active, completed)
   - Creator and timestamp information

3. **experiment_samples** - Sample assignments to experiments
   - Links samples to specific experiments
   - Display order and labeling

4. **participant_sessions** - Anonymous user sessions
   - Session tracking without PII
   - Optional demographic collection
   - Device/browser information

5. **responses** - User selections and interactions
   - Selected samples and rankings
   - Response times
   - Click tracking (heatmap data)
   - Confidence ratings

6. **sample_images** - Image file references
   - Links to Supabase Storage
   - Image metadata (size, dimensions, format)
   - Thumbnail URLs

## Application Structure

```
MSL-Tender/
├── frontend/                    # Consumer-facing app
│   ├── app/                    # Next.js app directory
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Landing page
│   │   └── experiment/
│   │       └── [id]/
│   │           └── page.tsx    # Experiment interface
│   ├── components/             # React components
│   │   ├── ImageComparison.tsx
│   │   ├── RankingInterface.tsx
│   │   └── ThankYou.tsx
│   ├── lib/
│   │   ├── supabase.ts        # Supabase client
│   │   └── tracking.ts        # Analytics utilities
│   └── styles/
│       └── globals.css
│
├── admin-dashboard/            # Researcher interface
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx           # Dashboard home
│   │   ├── experiments/
│   │   │   ├── page.tsx       # List experiments
│   │   │   ├── new/
│   │   │   │   └── page.tsx   # Create experiment
│   │   │   └── [id]/
│   │   │       ├── page.tsx   # View/edit experiment
│   │   │       └── results/
│   │   │           └── page.tsx # Analyze results
│   │   ├── samples/
│   │   │   └── page.tsx       # Browse/manage samples
│   │   └── auth/
│   │       └── login/
│   │           └── page.tsx   # Admin login
│   ├── components/
│   │   ├── ExperimentForm.tsx
│   │   ├── DataTable.tsx
│   │   ├── ResultsChart.tsx
│   │   └── SampleSelector.tsx
│   └── lib/
│       ├── supabase.ts
│       └── api.ts
│
├── backend/                    # Future API extensions (if needed)
│   └── (Currently using Supabase auto-API)
│
├── database/
│   ├── schema.sql             # Main database schema
│   ├── migrations/            # Future schema changes
│   ├── seeds/                 # Test data
│   └── consolidated_data_*.csv # Imported study data
│
├── scripts/
│   ├── consolidate_data.py    # Data consolidation
│   ├── inspect_files.py       # Data exploration
│   └── upload_images.py       # (Future) Batch image upload
│
├── docs/
│   ├── SUPABASE_SETUP.md     # This file
│   ├── ARCHITECTURE.md        # Architecture overview
│   └── API.md                 # API documentation
│
└── study files/               # Original Excel files
    └── *.xlsx
```

## Key Features

### Consumer Interface
- Mobile-first responsive design
- Touch-optimized image comparison
- Drag-and-drop ranking
- Progress tracking
- Session persistence
- Offline capability (PWA)

### Admin Dashboard
- Experiment builder with drag-and-drop
- Sample browser with filters
- Real-time participation monitoring
- Results visualization
- Export capabilities (CSV, JSON)
- User management

### Analytics & Tracking
- Response time measurement (millisecond precision)
- Click position tracking
- Image view duration
- Device/browser analytics
- Demographic correlations (if collected)

## Security Model

### Row Level Security (RLS)
- All tables protected by RLS policies
- Public read access for active experiments
- Authenticated write access for researchers
- Session-based access for participants

### Authentication
- **Admin**: Email-based authentication via Supabase
- **Participants**: Anonymous sessions (no login required)
- **API Keys**: 
  - Anon key for client-side (safe for public)
  - Service role key for admin functions (server-side only)

### Data Privacy
- No PII collected from participants by default
- Optional demographic data (configurable)
- Anonymous session identifiers
- IP addresses hashed (optional)

## Performance Considerations

### Database Optimization
- Indexes on frequently queried columns
- Materialized views for analytics
- Connection pooling via Supabase
- Query optimization with EXPLAIN

### Frontend Optimization
- Image lazy loading
- CDN delivery via Vercel
- Static site generation where possible
- Incremental static regeneration
- Service worker caching

### Storage Optimization
- Image compression (WebP format)
- Multiple resolution variants
- Thumbnail generation
- CDN distribution via Supabase Storage

## Deployment Pipeline

```
1. Developer pushes to GitHub
   ↓
2. GitHub Actions runs tests (future)
   ↓
3. Vercel detects push
   ↓
4. Vercel builds Next.js apps
   ↓
5. Vercel deploys to production
   ↓
6. Supabase Edge Functions update (if used)
   ↓
7. Deployment complete
```

### Environments

- **Development**: Local with Supabase local instance (optional)
- **Staging**: Preview deployments on Vercel
- **Production**: Main branch → Vercel production

## Monitoring & Analytics

### Application Monitoring
- Vercel Analytics for web vitals
- Supabase Dashboard for database metrics
- Custom event tracking for user interactions

### Error Tracking
- Next.js error boundaries
- Supabase error logging
- Vercel deployment logs

### Performance Metrics
- Page load times
- Image load times
- Response submission latency
- Database query performance

## Future Enhancements

### Phase 2 (Planned)
- Advanced filtering in admin dashboard
- A/B testing capabilities
- Machine learning predictions
- Advanced heatmap visualizations
- Mobile native apps (React Native)

### Phase 3 (Future)
- Multi-language support
- Integration with lab equipment
- Automated report generation
- API for external researchers
- Collaborative experiment design

## Development Workflow

1. **Local Development**
   ```bash
   # Frontend
   cd frontend
   npm install
   npm run dev
   
   # Admin Dashboard
   cd admin-dashboard
   npm install
   npm run dev
   ```

2. **Database Changes**
   - Modify `schema.sql`
   - Create migration file in `database/migrations/`
   - Apply to Supabase via Dashboard or CLI

3. **Deployment**
   - Push to GitHub
   - Automatic deployment via Vercel
   - Monitor deployment in Vercel dashboard

## Resources & References

- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [PostgreSQL Best Practices](https://www.postgresql.org/docs/current/index.html)
