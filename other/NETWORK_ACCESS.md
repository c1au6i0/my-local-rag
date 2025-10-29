# Network Access Guide for Local RAG Server

## Quick Start

1. **Start the server:**
   ```bash
   ./start_server.sh
   # Or with a custom port:
   ./start_server.sh 8080
   ```

2. **Access from the same computer:**
   - Open browser and go to: `http://localhost:5000`

3. **Access from other devices on the same network:**
   - The server will display your network IP when it starts
   - On other devices, open browser and go to: `http://YOUR_IP:5000`
   - Example: `http://10.0.0.242:5000`

## Troubleshooting Network Access

### If other devices cannot connect:

1. **Check firewall on Ubuntu (this computer):**
   ```bash
   # Check if firewall is active
   sudo ufw status
   
   # If active, allow port 5000
   sudo ufw allow 5000
   
   # Or allow from specific network only (safer)
   sudo ufw allow from 10.0.0.0/24 to any port 5000
   ```

2. **Check if server is listening on all interfaces:**
   ```bash
   # While server is running, check in another terminal:
   netstat -tlnp | grep 5000
   # Should show 0.0.0.0:5000 (not 127.0.0.1:5000)
   ```

3. **Test connection from another device:**
   ```bash
   # From another Linux/Mac device:
   curl http://YOUR_SERVER_IP:5000/health
   
   # Or use telnet to test port:
   telnet YOUR_SERVER_IP 5000
   ```

4. **Common Issues:**
   - **Router isolation:** Some routers isolate devices. Check router settings.
   - **VPN:** If using VPN, it might block local network access.
   - **Docker/VM:** If running in container/VM, need proper port forwarding.

## Security Considerations

⚠️ **WARNING:** The server accepts connections from ANY device on your network!

For better security:

1. **Restrict to specific IPs** (edit web_rag.py):
   ```python
   # Instead of host='0.0.0.0', use specific IP:
   app.run(host='10.0.0.242', port=5000)
   ```

2. **Add authentication** (optional - requires code changes)

3. **Use HTTPS** (for production use)

## Finding Your Network IP

The server automatically displays your IP, but you can also find it:

```bash
# Method 1
hostname -I

# Method 2
ip addr show | grep "inet " | grep -v 127.0.0.1

# Method 3
ifconfig | grep "inet " | grep -v 127.0.0.1
```

## Testing the Server

1. **Health check:**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Test query (with curl):**
   ```bash
   curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d '{"question":"What is this about?"}'
   ```

## Running in Background

To keep server running after closing terminal:

```bash
# Using nohup
nohup ./start_server.sh > server.log 2>&1 &

# Check if running
ps aux | grep web_rag

# Stop the server
pkill -f web_rag.py
```

## Using Different Ports

If port 5000 is already in use:

```bash
# Use port 8080 instead
./start_server.sh 8080

# Or set environment variable
PORT=8080 pixi run python web_rag.py
```

## Logs and Debugging

The server prints logs to console. To save logs:

```bash
# Save logs to file
./start_server.sh 2>&1 | tee server.log

# Watch logs in real-time
tail -f server.log
```

---

**Need help?** Check the server output for your network IP address and share it with devices on your network!
