"""
Unit tests for the DataQueryServer class
"""
from data_query_server.server import DataQueryServer


class TestDataQueryServer:
    """Test cases for DataQueryServer functionality"""

    async def test_server_initialization(self, data_server_instance):
        """Test that the server initializes correctly"""
        assert data_server_instance.conn is not None
        assert isinstance(data_server_instance.available_datasets, dict)
        assert len(data_server_instance.available_datasets) == 2
        assert "sales" in data_server_instance.available_datasets
        assert "customers" in data_server_instance.available_datasets

    async def test_sample_datasets_loaded(self, data_server_instance):
        """Test that sample datasets are loaded with correct structure"""
        sales_info = data_server_instance.available_datasets["sales"]
        customers_info = data_server_instance.available_datasets["customers"]

        # Check sales dataset
        assert sales_info["row_count"] == 100
        assert "order_id" in sales_info["columns"]
        assert "customer_id" in sales_info["columns"]
        assert "product" in sales_info["columns"]

        # Check customers dataset
        assert customers_info["row_count"] == 50
        assert "customer_id" in customers_info["columns"]
        assert "name" in customers_info["columns"]
        assert "email" in customers_info["columns"]

    async def test_sql_query_execution(self, data_server_instance):
        """Test SQL query execution functionality"""
        # Test successful query
        result = data_server_instance.execute_sql("SELECT COUNT(*) as count FROM sales")
        assert result["success"] is True
        assert result["row_count"] == 1
        assert result["data"][0]["count"] == 100

        # Test query with GROUP BY
        result = data_server_instance.execute_sql(
            "SELECT product, COUNT(*) as count FROM sales GROUP BY product ORDER BY product"
        )
        assert result["success"] is True
        assert result["row_count"] == 3
        assert all("product" in row and "count" in row for row in result["data"])

    async def test_sql_query_error_handling(self, data_server_instance):
        """Test SQL query error handling"""
        # Test invalid query
        result = data_server_instance.execute_sql("SELECT * FROM nonexistent_table")
        assert result["success"] is False
        assert "error" in result
        assert result["row_count"] == 0
        assert result["data"] == []

    async def test_get_table_info_all(self, data_server_instance):
        """Test getting information about all tables"""
        info = data_server_instance.get_table_info()
        assert "tables" in info
        assert "datasets_info" in info
        assert len(info["tables"]) == 2
        assert set(info["tables"]) == {"customers", "sales"}

    async def test_get_table_info_specific(self, data_server_instance):
        """Test getting information about a specific table"""
        info = data_server_instance.get_table_info("sales")
        assert "table" in info
        assert "schema" in info
        assert "metadata" in info
        assert info["table"] == "sales"
        assert len(info["schema"]) == 6  # Expected number of columns

        # Check schema structure
        schema_columns = [col["column"] for col in info["schema"]]
        expected_columns = ["order_id", "customer_id", "product", "quantity", "price", "order_date"]
        assert set(schema_columns) == set(expected_columns)

    async def test_cleanup(self):
        """Test server cleanup functionality"""
        server = DataQueryServer()
        await server.initialize()
        assert server.conn is not None

        server.cleanup()
        assert server.conn is None
