#!/usr/bin/env python3
"""
Test script for the Data Query Server MCP
"""

import asyncio

from data_query_server.server import DataQueryServer


async def test_mcp_tools():
    """Test the MCP server tools"""
    server = DataQueryServer()
    await server.initialize()

    print("=== Testing Data Query Server ===\n")

    # Test 1: List tables
    print("1. Testing list_tables tool:")
    result = server.get_table_info()
    print(f"Available tables: {result['tables']}")
    print()

    # Test 2: Describe table
    print("2. Testing describe_table tool:")
    sales_info = server.get_table_info('sales')
    print(f"Sales table columns: {[col['column'] for col in sales_info['schema']]}")
    print()

    # Test 3: SQL query
    print("3. Testing sql_query tool:")

    # Top products by revenue
    query = """
    SELECT product,
           COUNT(*) as order_count,
           SUM(quantity * price) as total_revenue
    FROM sales
    GROUP BY product
    ORDER BY total_revenue DESC
    """

    result = server.execute_sql(query)
    if result['success']:
        print("Top products by revenue:")
        for row in result['data']:
            print(f"  {row['product']}: ${row['total_revenue']:.2f} ({row['order_count']} orders)")
    else:
        print(f"Query failed: {result['error']}")

    print()

    # Test 4: Customer analysis
    print("4. Customer analysis:")
    customer_query = """
    SELECT city,
           COUNT(*) as customer_count,
           AVG(julianday('now') - julianday(registration_date)) as avg_days_since_registration
    FROM customers
    GROUP BY city
    ORDER BY customer_count DESC
    """

    result = server.execute_sql(customer_query)
    if result['success']:
        print("Customers by city:")
        for row in result['data']:
            print(f"  {row['city']}: {row['customer_count']} customers (avg {row['avg_days_since_registration']:.0f} days since registration)")

    server.cleanup()
    print("\n=== Test completed successfully! ===")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
