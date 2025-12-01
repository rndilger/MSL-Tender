# MSL-Tender Next.js Application

Production-ready pork tenderness evaluation application with email whitelist authentication.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Supabase project with credentials
- Access to @illinois.edu email

### Installation

```bash
# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your Supabase credentials from:
# https://supabase.com/dashboard/project/vxqpbohiradglqfxwjco/settings/api

# Start development server
npm run dev
```

Visit http://localhost:3000

## 🔐 Authentication Setup

### 1. Deploy Auth Schema
Run `../database/auth_schema.sql` in Supabase SQL Editor

### 2. Create First Admin
1. Visit `/admin/login` and enter @illinois.edu email
2. Get user UUID from Supabase Dashboard → Authentication → Users
3. Run SQL to whitelist:
```sql
INSERT INTO admin_users (id, email, full_name, role, is_active)
VALUES ('YOUR-UUID', 'your.email@illinois.edu', 'Your Name', 'super_admin', true);
```

### 3. Add More Admins
Once logged in as super_admin, visit `/admin/users` to manage whitelist

## 📁 Project Structure

```
app/
├── app/
│   ├── admin/
│   │   ├── login/           # Admin login page ✅
│   │   ├── dashboard/       # Admin home ✅
│   │   ├── samples/         # Browse samples (TODO)
│   │   ├── experiments/     # Manage experiments (TODO)
│   │   └── users/           # Admin management (TODO)
│   ├── survey/[id]/         # Public survey interface (TODO)
│   └── auth/signout/        # Sign out handler ✅
├── lib/supabase/
│   ├── client.ts           # Browser client ✅
│   ├── server.ts           # Server client ✅
│   └── middleware.ts       # Auth middleware ✅
├── types/
│   └── database.types.ts   # TypeScript types ✅
└── middleware.ts           # Route protection ✅
```

## 🛠️ Scripts

```bash
npm run dev      # Development server (http://localhost:3000)
npm run build    # Production build
npm run start    # Production server
npm run lint     # Lint code
```

## 🔒 Security Features

- ✅ Email whitelist (@illinois.edu only)
- ✅ Passwordless magic link authentication
- ✅ Row Level Security on all database access
- ✅ Middleware route protection
- ✅ Domain validation (client + database)
- ✅ Active/inactive admin status control

## 🌐 Deployment to Vercel

See `../docs/VERCEL_DEPLOYMENT_GUIDE.md` for complete instructions.

### Quick Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from app directory
cd app
vercel

# Add environment variables in Vercel dashboard:
# - NEXT_PUBLIC_SUPABASE_URL
# - NEXT_PUBLIC_SUPABASE_ANON_KEY
# - NEXT_PUBLIC_SITE_URL (your production URL)
```

## 📚 Documentation

- **Authentication**: `../docs/AUTH_IMPLEMENTATION_EMAIL_WHITELIST.md`
- **Database Schema**: `../database/auth_schema.sql`
- **Supabase Setup**: `../docs/SUPABASE_SETUP_WALKTHROUGH.md`
- **Vercel Deployment**: `../docs/VERCEL_DEPLOYMENT_GUIDE.md`

## 🐛 Troubleshooting

### Magic link not arriving
- Check spam folder
- Verify email is in `admin_users` table with `is_active = true`
- Check Supabase email settings (Dashboard → Auth → Email Templates)

### "Not authorized" error after login
- Verify UUID is in `admin_users` table
- Check `is_active` = true
- Clear browser cookies and retry

### Environment variables not loading
- Restart dev server after editing `.env.local`
- Ensure file is named exactly `.env.local` (not `.env`)
- Check variables start with `NEXT_PUBLIC_` for client-side access

### TypeScript errors
- Run `npm install` to ensure all dependencies installed
- Restart TypeScript server in VS Code (Cmd/Ctrl + Shift + P → "Restart TS Server")

### Middleware redirect loop
- Ensure `/admin/login` is NOT protected in middleware
- Check Supabase URL and anon key are correct
- Clear cookies and restart dev server

---

## 🎯 Next Development Steps

### Phase 1: Sample Management ✅ (In Progress)
- [ ] Sample browser with data table
- [ ] Filters by study, enhancement, tenderness
- [ ] Sorting by all columns
- [ ] Multi-select for experiment creation

### Phase 2: Experiment Creation
- [ ] Select samples (multiples of 4)
- [ ] Configure shuffle/display order
- [ ] Set participant instructions
- [ ] Generate unique survey link

### Phase 3: Survey Interface
- [ ] Public survey access (no login)
- [ ] 4-image grid per set
- [ ] Select 1 "most tender" per set
- [ ] Submit responses with name/email

### Phase 4: Response Management
- [ ] View all participant responses
- [ ] Export to CSV
- [ ] Basic statistics/analytics

### Phase 5: ML Integration
- [ ] Image cropping pipeline
- [ ] Toggle between original/cropped
- [ ] Batch processing interface

---

Built with Next.js 16, Supabase, and Tailwind CSS

**University of Illinois Meat Science Laboratory**
