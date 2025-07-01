# Data Query Server - MCP

An MCP (Model Context Protocol) server that enables LLMs to query datasets using SQL through DuckDB integration.

## Features

- **SQL Query Execution**: Execute SQL queries against preloaded datasets
- **Schema Inspection**: Explore table structures and metadata
- **Sample Datasets**: Includes sales and customer data for demonstration
- **Docker Support**: Easy deployment with Docker and docker-compose
- **Type Safety**: Full type hints for better code quality

## Quick Start

### 1. Install Dependencies

```bash
uv sync --dev --all-extras
```

### 2. Run the Server

```bash
uv run python -m data_query_server
```

### 3. Using Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build manually
docker build -t data-query-server .
docker run -v ./data:/app/data data-query-server
```

## Available Tools

The MCP server provides these tools for LLMs:

- **`sql_query`**: Execute SQL queries against the datasets
- **`describe_table`**: Get schema and metadata for a specific table
- **`list_tables`**: List all available tables with descriptions

## Sample Datasets

The server comes with two pre-loaded datasets:

### Sales Table
- `order_id`: Unique order identifier
- `customer_id`: Customer reference
- `product`: Product name (Product A, B, C)
- `quantity`: Number of items ordered
- `price`: Price per item
- `order_date`: Date of the order

### Customers Table
- `customer_id`: Unique customer identifier
- `name`: Customer name
- `email`: Customer email address
- `city`: Customer city
- `registration_date`: Date customer registered

## Example Queries

```sql
-- Top selling products
SELECT product, SUM(quantity * price) as revenue 
FROM sales 
GROUP BY product 
ORDER BY revenue DESC;

-- Customer order history
SELECT c.name, COUNT(s.order_id) as order_count, SUM(s.quantity * s.price) as total_spent
FROM customers c
JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;

-- Monthly sales trends
SELECT 
    strftime('%Y-%m', order_date) as month,
    COUNT(*) as orders,
    SUM(quantity * price) as revenue
FROM sales 
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;
```

## Development

### Project Structure

```
src/
├── data_query_server/
│   ├── __init__.py
│   ├── __main__.py
│   └── server.py          # Main MCP server implementation
data/                       # DuckDB database files
datasets/                   # Additional dataset files
.vscode/
├── mcp.json               # MCP server configuration
└── tasks.json             # VS Code tasks
```

### Configuration

The MCP server is configured in `.vscode/mcp.json`:

```json
{
  "servers": {
    "data-query-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "data_query_server"]
    }
  }
}
```

## Adding New Datasets

To add new datasets to the server:

1. Place CSV files in the `datasets/` directory
2. Modify the `load_sample_datasets()` method in `server.py`
3. Update the `available_datasets` metadata

Example:
```python
# Load your CSV data
new_data = pd.read_csv('datasets/your_data.csv')

# Create table in DuckDB
self.conn.execute("CREATE OR REPLACE TABLE your_table AS SELECT * FROM new_data")

# Add metadata
self.available_datasets['your_table'] = {
    'description': 'Description of your dataset',
    'columns': list(new_data.columns),
    'row_count': len(new_data)
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
- Each note resource has a name, description and text/plain mimetype

### Prompts

The server provides a single prompt:
- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools

The server implements one tool:
- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration

[TODO: Add configuration details specific to your implementation]

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "data-query-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/cboettig/Documents/github/schmidtdse/mcp-server",
        "run",
        "data-query-server"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "data-query-server": {
      "command": "uvx",
      "args": [
        "data-query-server"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /home/cboettig/Documents/github/schmidtdse/mcp-server run data-query-server
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.