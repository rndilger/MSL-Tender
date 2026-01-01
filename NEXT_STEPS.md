# Next Steps - MSL Tender Application

**Last Updated:** December 31, 2025

## High Priority Tasks

### 1. Computer Vision - Automatic Chop Detection
**Status:** Not Started  
**Priority:** HIGH  
**Description:** Implement computer vision to automatically detect and crop pork chops from images, eliminating manual background/tags/scales.

**Implementation Options:**
- **Option A: Python ML Service**
  - Use OpenCV + YOLOv8 or Detectron2 for object detection
  - Deploy as separate Python service or AWS Lambda
  - Store bounding box coordinates in `sample_images` table
  - Add columns: `crop_x1`, `crop_y1`, `crop_x2`, `crop_y2`

- **Option B: Edge Function with TensorFlow.js**
  - Use pre-trained model for image segmentation
  - Run in Supabase Edge Function or Vercel Edge
  - More limited but fully serverless

- **Option C: Pre-processing Script**
  - Batch process all images locally with Python
  - Generate cropped versions and upload to R2 `/cropped/` folder
  - Store URLs in database

**Recommended Approach:** Option A - Python ML Service
- Most accurate detection
- Can fine-tune model on pork chop images
- Reusable for future image processing
- Store coordinates for flexibility (can adjust crops later)

**Database Schema Changes:**
```sql
ALTER TABLE sample_images 
ADD COLUMN crop_x1 INTEGER,
ADD COLUMN crop_y1 INTEGER,
ADD COLUMN crop_x2 INTEGER,
ADD COLUMN crop_y2 INTEGER,
ADD COLUMN auto_cropped BOOLEAN DEFAULT FALSE,
ADD COLUMN crop_confidence DECIMAL(3,2);
```

**Implementation Steps:**
1. Research and select object detection model
2. Create training/validation dataset (annotate ~50-100 sample chops)
3. Fine-tune model on pork chop images
4. Build Python service to process images
5. Update database schema
6. Batch process existing images
7. Update frontend to use bounding box coordinates
8. Add fallback to center-crop if no coordinates exist

---

### 2. Dynamic Image Cropping in Frontend
**Status:** Not Started  
**Priority:** HIGH  
**Depends On:** Task #1  
**Description:** Update image display to use bounding box coordinates from database instead of static center-crop.

**Implementation:**
- Read `crop_x1`, `crop_y1`, `crop_x2`, `crop_y2` from `sample_images`
- Use Next.js Image component with custom loader
- Apply CSS transforms to display only cropped region
- Fallback to current center-crop if no coordinates

**Files to Update:**
- `app/app/admin/experiments/[id]/preview/page.tsx`
- `app/app/admin/experiments/[id]/page.tsx` (sample display)
- `app/app/admin/samples/page.tsx` (if showing images)

---

### 3. Experiment Activation & Survey Flow
**Status:** Not Started  
**Priority:** HIGH  
**Description:** Build participant-facing survey interface for active experiments.

**Components Needed:**
- `/survey/[experimentId]` route for participants
- Session tracking (anonymous or with optional demographics)
- Image selection interface (similar to preview but records responses)
- Response submission to `responses` and `participant_sessions` tables
- Thank you page with completion confirmation

**Features:**
- Randomize image order if `experiments.randomize_order = true`
- Collect timing data if `experiments.collect_timing = true`
- Collect click positions if `experiments.collect_click_data = true`
- Progress persistence (allow participants to resume)
- Mobile-responsive design

---

### 4. Results & Analytics Dashboard
**Status:** Not Started  
**Priority:** MEDIUM  
**Description:** Admin interface to view experiment results and export data.

**Features:**
- View all responses for an experiment
- Aggregate statistics (most selected samples, selection frequencies)
- Timing analysis (average time per set, per selection)
- Click heatmaps (if click data collected)
- CSV export of raw data
- Filter by date range, session characteristics

**Visualizations:**
- Bar charts of selection frequencies
- Box plots of timing data
- Heatmaps of click positions overlaid on images
- Response rate over time

---

## Medium Priority Tasks

### 5. Dark Mode Fixes
**Status:** Partially Complete  
**Priority:** MEDIUM  
**Description:** Fix dark mode toggle functionality and apply consistently across all pages.

**Issues:**
- Toggle doesn't switch themes
- Not applied to all pages
- Visual design needs improvement

**Files to Fix:**
- `app/app/components/DarkModeToggle.tsx`
- `app/app/layout.tsx` (DarkModeProvider)
- Update all page components to respect dark mode classes

---

### 6. Experiment Status Management
**Status:** Not Started  
**Priority:** MEDIUM  
**Description:** Add controls to change experiment status (draft → active → completed → archived).

**Features:**
- "Activate" button on experiment details page (draft → active)
- Validation before activation (must have samples, images loaded)
- "Complete" button to stop accepting responses
- Archive functionality
- Prevent deletion of completed/active experiments
- Show status history/timeline

---

### 7. Sample Management Enhancements
**Status:** Not Started  
**Priority:** MEDIUM  
**Description:** Improve sample browsing and filtering interface.

**Features:**
- Advanced filters (multiple studies, color ranges, marbling ranges)
- Sort by any column
- Bulk operations (tag multiple samples, export subset)
- Image gallery view (not just table)
- Quick view modal for sample details
- Link to related experiments

---

### 8. Image Upload Pipeline
**Status:** Not Started  
**Priority:** LOW  
**Description:** Build admin interface to upload new sample images.

**Features:**
- Drag-and-drop image upload
- Automatic matching to `pork_samples` by filename/ID
- Batch upload with progress indicator
- Image validation (format, size, quality)
- Automatic triggering of CV processing
- Preview before saving

---

## Low Priority / Future Enhancements

### 9. User Management
**Status:** Not Started  
**Priority:** LOW  
**Description:** Manage admin users and permissions.

**Features:**
- Add/remove admin users
- Role-based access (super admin, researcher, viewer)
- Activity logging
- Email invitations

---

### 10. Experiment Templates
**Status:** Not Started  
**Priority:** LOW  
**Description:** Create reusable templates for common experiment types.

**Features:**
- Save experiment configuration as template
- Apply template when creating new experiment
- Share templates between users
- Template library

---

### 11. API for External Access
**Status:** Not Started  
**Priority:** LOW  
**Description:** Build REST API for programmatic access to data.

**Features:**
- API keys for authentication
- Endpoints for samples, experiments, responses
- Rate limiting
- Documentation (OpenAPI/Swagger)

---

## Completed Tasks ✅

- [x] Authentication system with email whitelist
- [x] Admin dashboard with statistics
- [x] Sample browsing with filters
- [x] Experiment creation (3-step filter-based workflow)
- [x] Experiment list with CRUD operations
- [x] Experiment details view
- [x] Delete experiments with confirmation
- [x] Preview experiments before activation
- [x] Image storage on Cloudflare R2
- [x] Database schema and RLS policies
- [x] Deployment to Vercel + Supabase

---

## Technical Debt

### Database Optimization
- Add indexes on frequently queried columns
- Optimize sample filtering queries
- Consider materialized views for statistics

### Performance
- Implement image lazy loading
- Add caching for sample lists
- Optimize bundle size

### Testing
- Unit tests for utility functions
- Integration tests for experiment creation
- E2E tests for critical user flows

### Documentation
- API documentation
- Admin user guide
- Developer setup guide
- Architecture decision records

---

## Notes

**Computer Vision Implementation Priority:**
The automatic chop detection should be the next major feature, as it's critical for the user experience. The current center-crop is a temporary solution that won't work for all images. 

**Recommended Timeline:**
1. Week 1: Computer vision prototype and model selection
2. Week 2: Database schema updates and batch processing
3. Week 3: Frontend integration with dynamic cropping
4. Week 4: Survey interface for participants
5. Week 5: Results dashboard and analytics

**Resources Needed:**
- Annotated training data (50-100 images with chop bounding boxes)
- Python environment for ML training
- GPU access for model training (can use Google Colab free tier)
- Storage for cropped images or bounding box coordinates
