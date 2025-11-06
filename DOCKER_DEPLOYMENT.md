# 🐳 Docker Deployment Guide

## ✅ Complete Docker Setup

এই bot এখন **Docker** দিয়ে deploy করা যাবে - Python runtime setup এর দরকার নেই!

---

## 📋 Files Created

1. ✅ **Dockerfile** - Multi-stage build, optimized
2. ✅ **.dockerignore** - Clean builds
3. ✅ **docker-compose.yml** - Local testing
4. ✅ **DOCKER_DEPLOYMENT.md** - This guide

---

## 🚀 Quick Start

### Local Testing (Docker Compose)

```bash
# 1. Create .env file
cat > .env << EOF
PORT=10000
OPENROUTER_API_KEY=your_key_here
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
EOF

# 2. Build and run
docker-compose up -d

# 3. Check logs
docker-compose logs -f

# 4. Check health
curl http://localhost:10000/health
```

### Manual Docker Build

```bash
# Build image
docker build -t badshah-ai-trading-bot .

# Run container
docker run -d \
  --name trading-bot \
  -p 10000:10000 \
  -e PORT=10000 \
  -e OPENROUTER_API_KEY=your_key \
  -e BINANCE_API_KEY=your_key \
  -e BINANCE_API_SECRET=your_secret \
  badshah-ai-trading-bot

# Check logs
docker logs -f trading-bot
```

---

## ☁️ Deploy to Render.com (Docker)

### Option 1: Render Docker Support

1. **Create New Web Service**:
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repo

2. **Settings**:
   ```
   Name: badshah-ai-trading-bot
   Environment: Docker
   Dockerfile Path: Dockerfile
   Docker Context: . (root)
   ```

3. **Environment Variables**:
   ```
   PORT=10000
   OPENROUTER_API_KEY=your_key
   BINANCE_API_KEY=your_key
   BINANCE_API_SECRET=your_secret
   ```

4. **Deploy**:
   - Render automatically detects Dockerfile
   - Builds and deploys

---

## ☁️ Deploy to Other Platforms

### Railway.app

1. Connect GitHub repo
2. Railway auto-detects Dockerfile
3. Add environment variables
4. Deploy!

### Fly.io

```bash
# Install flyctl
# Then:
fly launch
fly secrets set OPENROUTER_API_KEY=your_key
fly secrets set BINANCE_API_KEY=your_key
fly secrets set BINANCE_API_SECRET=your_secret
fly deploy
```

### DigitalOcean App Platform

1. Create new app
2. Select Docker
3. Point to Dockerfile
4. Add environment variables
5. Deploy

### AWS ECS / Fargate

```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin your-ecr-url
docker build -t badshah-ai-trading-bot .
docker tag badshah-ai-trading-bot:latest your-ecr-url/badshah-ai-trading-bot:latest
docker push your-ecr-url/badshah-ai-trading-bot:latest

# Then create ECS task definition with environment variables
```

---

## 🔧 Docker Features

### Multi-Stage Build
- ✅ Smaller final image
- ✅ Faster builds
- ✅ Security optimized

### Health Checks
- ✅ Automatic health monitoring
- ✅ Auto-restart on failure
- ✅ Status endpoint: `/health`

### Volume Mounts
- ✅ Logs persist
- ✅ Config can be updated

---

## 📊 Monitoring

### Check Container Status

```bash
docker ps
docker logs trading-bot
docker stats trading-bot
```

### Health Check

```bash
curl http://localhost:10000/health
curl http://localhost:10000/status
```

---

## 🛠️ Troubleshooting

### Build Fails

```bash
# Check Dockerfile syntax
docker build --no-cache -t test .

# Check logs
docker-compose logs
```

### Container Exits

```bash
# Check exit code
docker ps -a

# Check logs
docker logs trading-bot

# Run interactively
docker run -it badshah-ai-trading-bot /bin/bash
```

### Port Already in Use

```bash
# Change PORT in .env
PORT=10001

# Or stop existing container
docker stop trading-bot
```

---

## 🔐 Security

### Environment Variables
- ✅ Never commit `.env` file
- ✅ Use secrets management
- ✅ Rotate keys regularly

### Image Security
- ✅ Multi-stage build reduces attack surface
- ✅ Minimal base image (python:3.11-slim)
- ✅ No root user (if needed, add USER directive)

---

## 📝 Environment Variables

Required:
- `OPENROUTER_API_KEY` - OpenRouter API key
- `BINANCE_API_KEY` - Binance API key
- `BINANCE_API_SECRET` - Binance API secret

Optional:
- `PORT` - Server port (default: 10000)

---

## ✅ Benefits of Docker

1. ✅ **No Python Setup** - Everything included
2. ✅ **Consistent Environment** - Same everywhere
3. ✅ **Easy Deployment** - One command
4. ✅ **Isolation** - No conflicts
5. ✅ **Scalability** - Easy to scale

---

## 🎯 Next Steps

1. ✅ Test locally with `docker-compose up`
2. ✅ Push to GitHub
3. ✅ Deploy to Render/Railway/Fly.io
4. ✅ Monitor logs and health

---

**Docker setup complete! Ready to deploy!** 🚀

