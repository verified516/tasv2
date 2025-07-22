# Vercel Deployment Guide

## Serverless Hosting on Vercel

Vercel offers excellent free hosting for serverless applications:
- Unlimited static sites
- 100GB bandwidth per month
- Serverless functions (100GB-hrs execution time)
- Global CDN
- Custom domains
- Automatic SSL

**Note:** This deployment requires modifications for serverless architecture and is best suited for lower-traffic applications due to serverless limitations.

### Prerequisites:
- Install [Vercel CLI](https://vercel.com/cli): `npm i -g vercel`
- Create account at [vercel.com](https://vercel.com)

### Quick Deploy Steps:

1. **Fork this repository** to your GitHub account

2. **Prepare serverless version:**
   ```bash
   cp deployment/vercel/vercel.json ./
   cp deployment/vercel/api/index.py ./api/
   ```

3. **Deploy with GitHub (Recommended):**
   - Connect your GitHub account to Vercel
   - Import your forked repository
   - Vercel will auto-detect the configuration

4. **Or deploy with CLI:**
   ```bash
   vercel login
   vercel --prod
   ```

### Database Configuration:

For Vercel deployment, you'll need an external database since serverless functions don't support persistent local storage:

**Option 1: PlanetScale (Free tier):**
```bash
# Sign up at planetscale.com
# Create database and get connection string
```

**Option 2: Neon (Free tier):**
```bash
# Sign up at neon.tech  
# Create database and get connection string
```

**Option 3: Aiven (Free tier):**
```bash
# Sign up at aiven.io
# Create PostgreSQL service
```

### Environment Variables:

Set in Vercel dashboard or using CLI:
```bash
vercel env add SESSION_SECRET
vercel env add DATABASE_URL
```

### Limitations:

**Serverless Constraints:**
- 15-second execution limit per function
- No persistent file system
- Cold starts on inactivity
- Limited to read-only file system

**Recommendations for Serverless:**
- Use external database (PlanetScale, Neon, Aiven)
- Optimize for quick responses
- Consider Vercel Edge Functions for better performance
- Cache frequently accessed data

### File Structure for Vercel:
```
/
├── api/
│   └── index.py         # Main serverless function
├── static/              # Static assets
├── vercel.json          # Vercel configuration
├── requirements.txt     # Python dependencies
└── ...                  # Your app files
```

### Custom Domain:
1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Configure DNS as instructed

### Alternatives for Full Flask Apps:
If the serverless limitations don't work for your needs, consider:
- Railway.app (better for traditional Flask apps)
- Render.com (supports long-running processes)
- Fly.io (full VM deployment)

### Pro Tips:
- Vercel excels at static sites and simple APIs
- For complex Flask apps, consider other platforms
- Great for frontend + API architecture
- Excellent for demos and prototypes