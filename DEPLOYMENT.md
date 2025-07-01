# MCP Data Query Server - Deployment Guide

## ✅ WORKING SOLUTION: Network-Accessible MCP Server

Your MCP server is now successfully containerized and accessible over HTTP/SSE transport!

## Quick Start

### 1. Build and Run the Container

```bash
# Build the Docker image
docker build -t data-query-server .

# Run the container
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  --restart unless-stopped \
  data-query-server

# Check if it's running
docker ps
```

### 2. Test the Server

```bash
# Test SSE endpoint
curl -i http://localhost:8000/sse

# List available tools
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
  http://localhost:8000/messages | jq

# Execute SQL query
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "sql_query", "arguments": {"query": "SELECT COUNT(*) FROM sales"}}, "id": 2}' \
  http://localhost:8000/messages | jq
```

## Available Endpoints

- **SSE Endpoint**: `http://localhost:8000/sse` - For MCP client connections
- **Message Endpoint**: `http://localhost:8000/messages` - For JSON-RPC MCP requests

## Available Tools

1. **`sql_query`** - Execute SQL queries on the available datasets
   - Parameters: `query` (string) - The SQL query to execute
   
2. **`describe_table`** - Get schema and metadata for a specific table
   - Parameters: `table_name` (string) - Name of the table to describe
   
3. **`list_tables`** - List all available tables and their information
   - Parameters: None

## Sample Datasets

The server includes two pre-loaded datasets:

- **`sales`** - Sales transaction data (100 rows)
  - Columns: order_id, customer_id, product, quantity, price, order_date
  
- **`customers`** - Customer information (50 rows)
  - Columns: customer_id, name, email, city, registration_date

## MCP Client Configuration

### For VSCode MCP Extensions

Add this to your VSCode MCP configuration:

```json
{
  "mcp.servers": {
    "data-query-server": {
      "transport": "sse",
      "url": "http://localhost:8000/sse",
      "messageEndpoint": "http://localhost:8000/messages"
    }
  }
}
```

### For Other MCP Clients

Configure your MCP client to use:
- **Transport**: HTTP/SSE
- **SSE URL**: `http://localhost:8000/sse`
- **Message URL**: `http://localhost:8000/messages`

## Production Deployment

### Using Docker Compose

```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
    environment:
      - LOG_LEVEL=info
    volumes:
      - ./data:/app/data  # Persist database
```

### Environment Variables

- `LOG_LEVEL` - Set logging level (default: info)
- Server binds to `0.0.0.0:8000` by default

### Security Considerations

For production deployment:

1. **Use HTTPS**: Deploy behind a reverse proxy (nginx/traefik) with SSL
2. **Authentication**: Add authentication middleware if needed
3. **Network Security**: Restrict access to trusted networks
4. **Resource Limits**: Set container resource limits

```bash
# Example with resource limits
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  --restart unless-stopped \
  --memory=512m \
  --cpus=1.0 \
  data-query-server
```

## Troubleshooting

### Container Won't Start
```bash
# Check container logs
docker logs mcp-server

# Check if port is in use
netstat -tulpn | grep :8000
```

### Database Issues
The server automatically falls back to in-memory database if the file database is locked.

### Connection Issues
- Ensure port 8000 is accessible
- Check firewall settings
- Verify container is running: `docker ps`

## Example Usage

```bash
# Complex SQL query example
curl -s -X POST -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "sql_query",
      "arguments": {
        "query": "SELECT s.product, COUNT(*) as orders, AVG(s.quantity) as avg_quantity, SUM(s.quantity * s.price) as revenue FROM sales s JOIN customers c ON s.customer_id = c.customer_id WHERE c.city = \"New York\" GROUP BY s.product ORDER BY revenue DESC"
      }
    },
    "id": 4
  }' \
  http://localhost:8000/messages | jq -r '.result.content[0].text'
```

## Success! 🎉

Your MCP server is now running as a standalone network service, providing SQL query capabilities over datasets via the MCP protocol over HTTP/SSE transport. It can be accessed by any MCP-compatible client including VSCode extensions, custom applications, or other AI tools.
