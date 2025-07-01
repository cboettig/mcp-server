<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Data Query Server - MCP Project

This is an MCP (Model Context Protocol) server project that provides SQL query capabilities over datasets using DuckDB.

## Project Structure
- `src/data_query_server/server.py` - Main MCP server implementation with DuckDB integration
- `data/` - Directory containing DuckDB database files
- `datasets/` - Directory for additional dataset files

## Key Features
- SQL query execution via MCP tools
- Pre-loaded sample datasets (sales, customers)
- Schema inspection and table listing
- Docker deployment support

## Development Guidelines
- Follow MCP protocol specifications
- Use DuckDB for all database operations
- Maintain type hints for better code quality
- Test SQL queries for security and performance

You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt
