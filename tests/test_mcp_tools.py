"""
Integration tests for MCP tools functionality
"""
import mcp.types as types
import pytest
from pydantic import AnyUrl

from data_query_server.server import (
    handle_call_tool,
    handle_list_resources,
    handle_list_tools,
    handle_read_resource,
)


class TestMCPTools:
    """Test cases for MCP tool implementations"""

    async def test_list_tools(self):
        """Test that all expected tools are listed"""
        tools = await handle_list_tools()
        assert len(tools) == 3

        tool_names = [tool.name for tool in tools]
        assert "sql_query" in tool_names
        assert "describe_table" in tool_names
        assert "list_tables" in tool_names

        # Check sql_query tool schema
        sql_tool = next(tool for tool in tools if tool.name == "sql_query")
        assert "query" in sql_tool.inputSchema["properties"]
        assert sql_tool.inputSchema["required"] == ["query"]

    async def test_sql_query_tool(self, initialized_global_server):
        """Test the sql_query tool"""
        # Test successful query
        result = await handle_call_tool("sql_query", {"query": "SELECT COUNT(*) as count FROM sales"})
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "successfully" in result[0].text.lower()
        assert "100" in result[0].text

        # Test query with results
        result = await handle_call_tool(
            "sql_query", {"query": "SELECT product FROM sales GROUP BY product ORDER BY product LIMIT 2"}
        )
        assert len(result) == 1
        assert "Product A" in result[0].text or "Product B" in result[0].text

    async def test_sql_query_tool_error(self, initialized_global_server):
        """Test sql_query tool error handling"""
        result = await handle_call_tool("sql_query", {"query": "SELECT * FROM invalid_table"})
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "failed" in result[0].text.lower()

    async def test_sql_query_tool_missing_args(self, initialized_global_server):
        """Test sql_query tool with missing arguments"""
        with pytest.raises(ValueError, match="Missing SQL query"):
            await handle_call_tool("sql_query", {})

    async def test_describe_table_tool(self, initialized_global_server):
        """Test the describe_table tool"""
        result = await handle_call_tool("describe_table", {"table_name": "sales"})
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "sales" in result[0].text.lower()
        assert "order_id" in result[0].text
        assert "Schema:" in result[0].text

    async def test_describe_table_tool_invalid(self, initialized_global_server):
        """Test describe_table tool with invalid table"""
        result = await handle_call_tool("describe_table", {"table_name": "invalid_table"})
        assert len(result) == 1
        assert "Error" in result[0].text

    async def test_list_tables_tool(self, initialized_global_server):
        """Test the list_tables tool"""
        result = await handle_call_tool("list_tables", {})
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "sales" in result[0].text
        assert "customers" in result[0].text
        assert "Available tables:" in result[0].text

    async def test_unknown_tool(self, initialized_global_server):
        """Test calling an unknown tool"""
        with pytest.raises(ValueError, match="Unknown tool"):
            await handle_call_tool("unknown_tool", {})


class TestMCPResources:
    """Test cases for MCP resource implementations"""

    async def test_list_resources(self, initialized_global_server):
        """Test listing available resources"""
        resources = await handle_list_resources()
        assert len(resources) == 3  # 2 datasets + 1 schema resource

        resource_names = [resource.name for resource in resources]
        assert any("sales" in name for name in resource_names)
        assert any("customers" in name for name in resource_names)
        assert any("Schema" in name for name in resource_names)

    async def test_read_dataset_resource(self, initialized_global_server):
        """Test reading a dataset resource"""
        uri = AnyUrl("dataset://sales")
        content = await handle_read_resource(uri)
        assert "success" in content
        assert "data" in content

    async def test_read_schema_resource(self, initialized_global_server):
        """Test reading the schema resource"""
        uri = AnyUrl("schema://all")
        content = await handle_read_resource(uri)
        assert "tables" in content
        assert "datasets_info" in content

    async def test_read_invalid_resource(self, initialized_global_server):
        """Test reading an invalid resource"""
        with pytest.raises(ValueError):
            await handle_read_resource(AnyUrl("invalid://resource"))

        with pytest.raises(ValueError):
            await handle_read_resource(AnyUrl("dataset://nonexistent"))
