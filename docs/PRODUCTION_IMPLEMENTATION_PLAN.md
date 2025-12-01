# MSL-Tender Production Implementation Plan

## Project Overview
Building a production-ready pork tenderness evaluation application using the Tender_v01023 codebase as inspiration, migrating to Supabase + Vercel with enterprise authentication.

---

## 🎯 **Core Requirements (Based on Codebase Review)**

### **User Workflows**
1. **Admin Workflow**:
   - Login with @illinois.edu credentials (SAML SSO or email whitelist)
   - Browse/filter all 1,490 pork samples in sortable table
   - Select samples (multiples of 4) to create experiment
   - Shuffle and generate participant survey
   - View all created experiments
   - Export response data

2. **Participant Workflow**:
   - Access survey via unique link (no login required)
   - Enter name and email
   - View sets of 4 pork chop images
   - Select 1 "most tender" per set
   - Submit responses
   - Responses saved to database

### **Visual Design**
- 4-column responsive grid (2 columns mobile)
- Green (#009879, #4CAF50) primary actions
- Red (#b12426) for selection/highlight
- Smooth hover effects and transitions
- Clean table interface with filters/sorting

---

## 🔐 **Authentication Strategy**

### **Option 1: SAML SSO with UIUC Shibboleth (RECOMMENDED)**

✅ **Supabase supports SAML 2.0** (Pro plan and above, $0.015/SSO MAU)

**Implementation:**
1. Request UIUC Shibboleth SAML metadata from IT
2. Configure Supabase SAML connection:
   ```bash
   supabase sso add --type saml --project-ref <your-project> \
     --metadata-url 'https://shibboleth.illinois.edu/metadata' \
     --domains illinois.edu
   ```
3. Users click "Sign in with Illinois" button
4. Redirected to UIUC authentication
5. Auto-create admin user on first login
6. Use RLS policies to restrict admin functions

**Benefits:**
- Native UIUC authentication (no password management)
- Automatic @illinois.edu validation
- Enterprise-grade security
- Single sign-on experience
- No manual user management

**Limitations:**
- Requires Pro plan ($25/month)
- Need UIUC IT cooperation for SAML setup
- Additional $0.015 per SSO MAU

---

### **Option 2: Email Whitelist with Magic Links (FREE TIER)**

✅ **Fallback if SAML not feasible**

**Implementation:**
1. Store whitelisted @illinois.edu emails in `admin_users` table
2. Email-based passwordless authentication (magic links)
3. Check user email domain on signup:
   ```sql
   CREATE POLICY "Only illinois.edu can sign up"
   ON auth.users FOR INSERT
   WITH CHECK (email LIKE '%@illinois.edu');
   ```
4. RLS policies verify user is in admin_users table

**Benefits:**
- Free tier compatible
- Easy to manage whitelist
- Passwordless (magic link sent to email)
- No external IT dependencies

**Limitations:**
- Manual whitelist management
- Not true SSO experience
- Users need Illinois email access

---

### **Option 3: Hybrid Approach (RECOMMENDED FOR MVP)**

**Phase 1 (Now)**: Email whitelist for MVP/testing
**Phase 2 (Production)**: Migrate to SAML SSO

This allows rapid development without waiting for UIUC IT approval.

---

## 🏗️ **Technology Stack**

### **Frontend**
- **Framework**: Next.js 14 (App Router) with React 18
- **Styling**: Tailwind CSS + custom CSS for existing design patterns
- **State Management**: React Hooks + Zustand (for global state)
- **UI Components**: shadcn/ui (Radix primitives)
- **Data Tables**: TanStack Table (React Table v8)
- **Image Optimization**: Next.js Image component
- **Deployment**: Vercel

### **Backend**
- **Database**: Supabase PostgreSQL (your existing schema)
- **Auth**: Supabase Auth (SAML or email)
- **Storage**: Supabase Storage (1,490 images uploaded)
- **API**: Supabase auto-generated REST API + Edge Functions (if needed)
- **Real-time**: Supabase Realtime (optional for live updates)

### **Development Tools**
- **Type Safety**: TypeScript
- **Linting**: ESLint + Prettier
- **Testing**: Vitest + React Testing Library
- **Git Hooks**: Husky + lint-staged

---

## 📊 **Database Schema (Already Created)**

Using your existing Supabase schema with enhancements:

```sql
-- Core tables (already exist)
- pork_samples (1,490 records) ✅
- experiments (survey configurations)
- participant_sessions (survey takers)
- responses (individual selections)
- sample_images (image metadata/URLs)
- experiment_samples (join table)

-- Add admin management
CREATE TABLE admin_users (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT,
  added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  added_by UUID REFERENCES auth.users(id)
);
```

---

## 🎨 **Component Architecture**

### **Admin Dashboard**
```
/admin
├── /login - Authentication page
├── /dashboard - Admin home
├── /samples - Browse all pork samples (table view)
├── /experiments
│   ├── /create - Select samples, create experiment
│   ├── /[id] - View experiment details
│   └── /[id]/responses - View participant responses
└── /export - Data export tools
```

### **Participant Interface**
```
/survey/[experimentId]
- Public access (no login)
- Image selection interface
- Response submission
```

---

## 🔄 **Key Migrations from Old Codebase**

### **1. Database Migration**
**Old**: SQLite with CSV files
**New**: Supabase PostgreSQL with proper relations

**Changes**:
- `surveys` table → `experiments` table
- CSV response storage → `responses` + `participant_sessions` tables
- Comma-separated chop_ids → `experiment_samples` join table
- Local images → Supabase Storage URLs

### **2. Authentication**
**Old**: Hardcoded `admin/admin`
**New**: SAML SSO or email whitelist with RLS

### **3. Image Handling**
**Old**: Static `/images/` folder
**New**: Supabase Storage with CDN
- URLs: `https://[project].supabase.co/storage/v1/object/public/pork-images/original/[chop_id].jpg`
- Later: ML-cropped versions in `/cropped/` folder

### **4. API Layer**
**Old**: Express backend with custom routes
**New**: Supabase auto-generated REST API + Edge Functions

---

## 📝 **Implementation Phases**

### **Phase 1: Foundation (Week 1)**
- [x] Supabase setup complete
- [x] Database schema deployed
- [x] Data imported (1,490 records)
- [x] Images uploaded to Storage
- [ ] Next.js project setup
- [ ] Authentication implementation
- [ ] Basic routing structure

### **Phase 2: Admin Interface (Week 2)**
- [ ] Sample browser with table (filters/sorting)
- [ ] Experiment creation flow
- [ ] Sample selection UI (4-per-set validation)
- [ ] Experiment management dashboard
- [ ] Admin user management

### **Phase 3: Participant Interface (Week 3)**
- [ ] Survey page with image grid
- [ ] Image selection logic (1 per set of 4)
- [ ] Form validation (name/email)
- [ ] Response submission
- [ ] Thank you/completion page

### **Phase 4: Data & Export (Week 4)**
- [ ] Response viewing/analytics
- [ ] CSV export functionality
- [ ] Experiment statistics
- [ ] Data visualization

### **Phase 5: ML Image Processing (Future)**
- [ ] ML cropping algorithm
- [ ] Batch processing pipeline
- [ ] Cropped image storage
- [ ] UI toggle between original/cropped

---

## 🔒 **Security Implementation**

### **Row Level Security Policies**

```sql
-- Admin-only access to experiments table
CREATE POLICY "Admins can manage experiments"
ON experiments FOR ALL
USING (
  auth.uid() IN (SELECT id FROM admin_users)
);

-- Public can read active experiments (for surveys)
CREATE POLICY "Public can view active experiments"
ON experiments FOR SELECT
USING (status = 'active');

-- Participants can insert their own responses
CREATE POLICY "Anyone can submit responses"
ON responses FOR INSERT
WITH CHECK (true);

-- Admin can view all responses
CREATE POLICY "Admins can view responses"
ON responses FOR SELECT
USING (
  auth.uid() IN (SELECT id FROM admin_users)
);
```

---

## 🚀 **Deployment Strategy**

### **Vercel Setup**
1. Connect GitHub repo to Vercel
2. Configure environment variables:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=https://[project].supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=[anon-key]
   ```
3. Enable automatic deployments from main branch
4. Set up preview deployments for PRs

### **Custom Domain**
- **Production**: `tender.msl.illinois.edu` or similar
- **Staging**: `tender-staging.vercel.app`

---

## 📋 **Next Immediate Actions**

1. **Choose Authentication Strategy**:
   - [ ] Contact UIUC IT about Shibboleth SAML metadata
   - [ ] OR implement email whitelist for MVP
   - [ ] Decision needed before proceeding

2. **Initialize Next.js Project**:
   ```bash
   npx create-next-app@latest msl-tender-app --typescript --tailwind --app
   ```

3. **Install Dependencies**:
   ```bash
   npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
   npm install @tanstack/react-table zustand
   npm install shadcn-ui
   ```

4. **Setup Project Structure**:
   - Create app routes
   - Configure Supabase client
   - Implement auth providers

---

## 💰 **Cost Estimate**

**Supabase (Pro Plan for SAML)**:
- Base: $25/month
- SSO MAU: $0.015 per user
- Storage: Included (25 GB)
- Bandwidth: Included (250 GB)
- **Estimated**: ~$30/month for small team

**Vercel (Pro)**:
- Base: $20/month
- Serverless functions: Included
- **Estimated**: $20/month

**Total**: ~$50/month for production-ready infrastructure

**Free Tier Option**: $0/month with email whitelist (no SAML)

---

## ✅ **Selected Authentication Strategy**

**Email Whitelist (Free Tier)** - Secure, passwordless magic link authentication

- ✅ **Cost**: $0/month (Supabase free tier)
- ✅ **Security**: Enterprise-grade via RLS policies + magic links
- ✅ **Setup Time**: Immediate (no external dependencies)
- ✅ **Admin Management**: Whitelist table with active/inactive status
- ✅ **User Experience**: Passwordless (magic link sent to @illinois.edu)
- ✅ **Migration Path**: Can upgrade to SAML SSO later without data loss

**Implementation Details**: See `docs/AUTH_IMPLEMENTATION_EMAIL_WHITELIST.md`

---

## 📋 **Next Immediate Actions**

**1. Deploy Authentication Schema**
```bash
# Run in Supabase SQL Editor
cat database/auth_schema.sql
```

**2. Initialize Next.js Project**
```bash
npx create-next-app@latest msl-tender-app --typescript --tailwind --app
cd msl-tender-app
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
npm install @tanstack/react-table zustand
```

**3. Create First Super Admin**
- Sign up with magic link at `/admin/login`
- Copy UUID from Supabase Dashboard → Auth → Users
- Insert into `admin_users` table with `super_admin` role

**4. Build Core Features**
- Admin login/dashboard
- Sample browser
- Experiment creation
- Survey interface

---

**Ready to proceed with Next.js setup?**
