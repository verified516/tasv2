# Fly.io Deployment Guide

## Free Hosting on Fly.io

Fly.io offers generous free tier:
- 3 shared-CPU VMs with 256MB RAM each
- 3GB persistent storage per month
- PostgreSQL database (3GB free storage)
- Global edge locations
- No cold starts

### Prerequisites:
- Install [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/)
- Create account: `flyctl auth signup`

### Quick Deploy Steps:

1. **Clone and navigate** to your repository:
   ```bash
   git clone https://github.com/yourusername/tasv2
   cd tasv2
   ```

2. **Copy Fly configuration:**
   ```bash
   cp deployment/fly/fly.toml ./
   cp deployment/fly/Dockerfile ./
   ```

3. **Launch the app:**
   ```bash
   flyctl launch --copy-config --name school-management
   ```

4. **Create PostgreSQL database:**
   ```bash
   flyctl postgres create --name school-management-db --region iad
   flyctl postgres attach school-management-db
   ```

5. **Set environment variables:**
   ```bash
   flyctl secrets set SESSION_SECRET=$(openssl rand -base64 32)
   ```

6. **Deploy:**
   ```bash
   flyctl deploy
   ```

### Manual Configuration:

1. **Initialize Fly app:**
   ```bash
   flyctl launch --no-deploy
   ```

2. **Edit fly.toml** with your app name and preferences

3. **Add PostgreSQL:**
   ```bash
   flyctl postgres create --name your-app-db
   flyctl postgres attach your-app-db -a your-app-name
   ```

4. **Set secrets:**
   ```bash
   flyctl secrets set SESSION_SECRET=your-secret-key
   ```

5. **Deploy:**
   ```bash
   flyctl deploy
   ```

### Database Connection:
Fly automatically sets `DATABASE_URL` when you attach PostgreSQL.

### Custom Domain:
```bash
flyctl certs create yourdomain.com
```

### Scaling:
```bash
# Scale to 0 machines (auto-start on request)
flyctl scale count 0

# Scale to 1 machine always running
flyctl scale count 1
```

### Monitoring:
```bash
# View logs
flyctl logs

# Monitor app
flyctl status
```

### Free Limits:
- 3 shared-CPU VMs (256MB RAM each)
- 160GB outbound data transfer per month
- PostgreSQL: 3GB storage, 10GB outbound transfer
- No sleep mode - apps stay responsive

### Pro Tips:
- Use `auto_stop_machines = true` to minimize resource usage
- Fly automatically handles SSL certificates
- Great for production workloads with low to moderate traffic