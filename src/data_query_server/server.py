import os
from typing import Any

import duckdb
import mcp.server.stdio
import mcp.types as types
import numpy as np
import pandas as pd
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import AnyUrl


class DataQueryServer:
    def __init__(self):
        self.db_path = "data/datasets.db"
        self.conn = None
        self.available_datasets = {}

    async def initialize(self):
        """Initialize the DuckDB connection and load sample datasets"""
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Close any existing connection
        if self.conn:
            self.conn.close()

        # Initialize DuckDB connection (use memory if file is locked)
        try:
            self.conn = duckdb.connect(self.db_path)
        except Exception as e:
            print(f"Warning: Could not connect to file database ({e}), using in-memory database")
            self.conn = duckdb.connect(":memory:")

        # Load sample datasets
        await self.load_sample_datasets()

    async def load_sample_datasets(self):
        """Load sample datasets into DuckDB"""
        try:
            # Sample sales data
            sales_data = pd.DataFrame(
                {
                    "order_id": range(1, 101),
                    "customer_id": [f"CUST_{i:03d}" for i in range(1, 101)],
                    "product": ["Product A", "Product B", "Product C"] * 33 + ["Product A"],
                    "quantity": np.random.randint(1, 10, 100),
                    "price": np.random.uniform(10, 100, 100).round(2),
                    "order_date": pd.date_range("2024-01-01", periods=100, freq="D"),
                }
            )

            # Sample customer data
            customer_data = pd.DataFrame(
                {
                    "customer_id": [f"CUST_{i:03d}" for i in range(1, 51)],
                    "name": [f"Customer {i}" for i in range(1, 51)],
                    "email": [f"customer{i}@example.com" for i in range(1, 51)],
                    "city": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"] * 10,
                    "registration_date": pd.date_range("2023-01-01", periods=50, freq="W"),
                }
            )

            # Load into DuckDB
            self.conn.execute("CREATE OR REPLACE TABLE sales AS SELECT * FROM sales_data")
            self.conn.execute("CREATE OR REPLACE TABLE customers AS SELECT * FROM customer_data")

            # Store dataset metadata
            self.available_datasets = {
                "sales": {
                    "description": "Sales transaction data with order details",
                    "columns": [
                        "order_id",
                        "customer_id",
                        "product",
                        "quantity",
                        "price",
                        "order_date",
                    ],
                    "row_count": len(sales_data),
                },
                "customers": {
                    "description": "Customer information and registration data",
                    "columns": ["customer_id", "name", "email", "city", "registration_date"],
                    "row_count": len(customer_data),
                },
            }

            print(f"Loaded {len(self.available_datasets)} datasets successfully")

        except Exception as e:
            print(f"Error loading sample datasets: {e}")

    def execute_sql(self, query: str) -> dict[str, Any]:
        """Execute SQL query and return results"""
        try:
            # Execute query
            result = self.conn.execute(query).fetchall()
            columns = [desc[0] for desc in self.conn.description]

            # Convert to list of dictionaries for better JSON serialization
            rows = []
            for row in result:
                rows.append(dict(zip(columns, row, strict=False)))

            return {"success": True, "data": rows, "columns": columns, "row_count": len(rows)}

        except Exception as e:
            return {"success": False, "error": str(e), "data": [], "columns": [], "row_count": 0}

    def get_table_info(self, table_name: str = None) -> dict[str, Any]:
        """Get information about tables in the database"""
        try:
            if table_name:
                # Get specific table info
                schema_query = f"DESCRIBE {table_name}"
                schema_result = self.conn.execute(schema_query).fetchall()

                return {
                    "table": table_name,
                    "schema": [{"column": row[0], "type": row[1]} for row in schema_result],
                    "metadata": self.available_datasets.get(table_name, {}),
                }
            else:
                # Get all tables
                tables_query = "SHOW TABLES"
                tables_result = self.conn.execute(tables_query).fetchall()

                return {
                    "tables": [row[0] for row in tables_result],
                    "datasets_info": self.available_datasets,
                }

        except Exception as e:
            return {"error": str(e)}

    def cleanup(self):
        """Clean up database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


# Initialize the data server
data_server = DataQueryServer()
server = Server("data-query-server")


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available dataset resources"""
    resources = []

    for dataset_name, info in data_server.available_datasets.items():
        resources.append(
            types.Resource(
                uri=AnyUrl(f"dataset://{dataset_name}"),
                name=f"Dataset: {dataset_name}",
                description=info["description"],
                mimeType="application/json",
            )
        )

    # Add schema resource
    resources.append(
        types.Resource(
            uri=AnyUrl("schema://all"),
            name="Database Schema",
            description="Complete schema information for all datasets",
            mimeType="application/json",
        )
    )

    return resources


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read dataset or schema information"""
    if uri.scheme == "dataset":
        dataset_name = uri.host
        if dataset_name in data_server.available_datasets:
            # Return sample of the dataset
            query = f"SELECT * FROM {dataset_name} LIMIT 10"
            result = data_server.execute_sql(query)
            return str(result)
        else:
            raise ValueError(f"Dataset not found: {dataset_name}")

    elif uri.scheme == "schema":
        # Return complete schema information
        schema_info = data_server.get_table_info()
        return str(schema_info)

    else:
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available SQL query tools"""
    return [
        types.Tool(
            name="sql_query",
            description="Execute a SQL query against the available datasets",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The SQL query to execute"}
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="describe_table",
            description="Get schema and metadata information for a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Name of the table to describe"}
                },
                "required": ["table_name"],
            },
        ),
        types.Tool(
            name="list_tables",
            description="List all available tables and their basic information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests"""

    if name == "sql_query":
        if not arguments or "query" not in arguments:
            raise ValueError("Missing SQL query")

        query = arguments["query"]
        result = data_server.execute_sql(query)

        if result["success"]:
            response_text = "Query executed successfully!\n\n"
            response_text += f"Columns: {', '.join(result['columns'])}\n"
            response_text += f"Rows returned: {result['row_count']}\n\n"

            if result["data"]:
                response_text += "Results:\n"
                # Show first few rows
                for i, row in enumerate(result["data"][:10]):
                    response_text += f"Row {i + 1}: {row}\n"

                if len(result["data"]) > 10:
                    response_text += f"... and {len(result['data']) - 10} more rows\n"
        else:
            response_text = f"Query failed: {result['error']}"

        return [types.TextContent(type="text", text=response_text)]

    elif name == "describe_table":
        if not arguments or "table_name" not in arguments:
            raise ValueError("Missing table name")

        table_name = arguments["table_name"]
        table_info = data_server.get_table_info(table_name)

        if "error" in table_info:
            response_text = f"Error describing table: {table_info['error']}"
        else:
            response_text = f"Table: {table_info['table']}\n\n"
            response_text += "Schema:\n"
            for col in table_info["schema"]:
                response_text += f"  - {col['column']}: {col['type']}\n"

            if "metadata" in table_info and table_info["metadata"]:
                metadata = table_info["metadata"]
                response_text += "\nMetadata:\n"
                response_text += f"  - Description: {metadata.get('description', 'N/A')}\n"
                response_text += f"  - Row count: {metadata.get('row_count', 'N/A')}\n"

        return [types.TextContent(type="text", text=response_text)]

    elif name == "list_tables":
        table_info = data_server.get_table_info()

        if "error" in table_info:
            response_text = f"Error listing tables: {table_info['error']}"
        else:
            response_text = "Available tables:\n\n"
            for table in table_info["tables"]:
                info = table_info["datasets_info"].get(table, {})
                response_text += f"• {table}\n"
                response_text += f"  Description: {info.get('description', 'N/A')}\n"
                response_text += f"  Columns: {', '.join(info.get('columns', []))}\n"
                response_text += f"  Rows: {info.get('row_count', 'N/A')}\n\n"

        return [types.TextContent(type="text", text=response_text)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the server"""
    # Initialize the data server
    await data_server.initialize()

    # Run the MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="data-query-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
