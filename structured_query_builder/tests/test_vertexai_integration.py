"""
Integration tests with Google Vertex AI structured outputs.

Tests that the Pydantic models work correctly with Google's Vertex AI
via LangChain adapters, including testing for quirks and limitations
specific to Google's structured output implementation.
"""

import os
import pytest
from structured_query_builder import *
from structured_query_builder.translator import translate_query

# Only run these tests if credentials are available
SKIP_REASON = "GOOGLE_APPLICATION_CREDENTIALS not set or google-cloud-aiplatform not available"

try:
    from langchain_google_vertexai import ChatVertexAI
    from langchain_core.prompts import ChatPromptTemplate
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False


def has_credentials():
    """Check if Google credentials are available."""
    return (
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or
        os.environ.get("GOOGLE_CLOUD_PROJECT")
    )


@pytest.mark.skipif(
    not VERTEXAI_AVAILABLE or not has_credentials(),
    reason=SKIP_REASON
)
class TestVertexAISchemaGeneration:
    """Test JSON schema generation for Vertex AI."""

    def test_query_schema_is_valid(self):
        """Test that Query model generates valid JSON schema."""
        schema = Query.model_json_schema()

        # Basic schema validation
        assert "properties" in schema
        assert "select" in schema["properties"]
        assert "from" in schema["properties"]  # Note: should be 'from' due to alias

        # Check for discriminated unions
        assert "definitions" in schema or "$defs" in schema

    def test_schema_has_no_recursive_refs(self):
        """
        Verify schema doesn't have circular references.

        This is critical for Google Vertex AI compatibility.
        """
        schema = Query.model_json_schema()

        def check_no_recursive_refs(obj, path="", visited=None):
            if visited is None:
                visited = set()

            if isinstance(obj, dict):
                # Check for $ref
                if "$ref" in obj:
                    ref_path = obj["$ref"]
                    if ref_path in visited:
                        pytest.fail(f"Found recursive reference: {ref_path} at {path}")
                    visited.add(ref_path)

                for key, value in obj.items():
                    check_no_recursive_refs(value, f"{path}.{key}", visited)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_no_recursive_refs(item, f"{path}[{i}]", visited)

        check_no_recursive_refs(schema)

    def test_discriminated_unions_present(self):
        """Test that discriminated unions are properly configured."""
        schema = Query.model_json_schema()

        # SelectExpr should be a union with discriminator
        defs = schema.get("$defs", schema.get("definitions", {}))

        # Check that expression types have discriminators
        assert "ColumnExpr" in defs
        assert "BinaryArithmetic" in defs
        assert "AggregateExpr" in defs
        assert "WindowExpr" in defs
        assert "CaseExpr" in defs

        # Each should have expr_type field
        for expr_type in ["ColumnExpr", "BinaryArithmetic", "AggregateExpr", "WindowExpr", "CaseExpr"]:
            if expr_type in defs:
                assert "properties" in defs[expr_type]
                assert "expr_type" in defs[expr_type]["properties"]


@pytest.mark.skipif(
    not VERTEXAI_AVAILABLE or not has_credentials(),
    reason=SKIP_REASON
)
class TestVertexAIBasicGeneration:
    """Test basic query generation with Vertex AI."""

    @pytest.fixture
    def llm(self):
        """Create Vertex AI LLM instance."""
        return ChatVertexAI(
            model="gemini-1.5-pro",
            temperature=0,
        )

    def test_simple_query_generation(self, llm):
        """
        Test generating a simple query with Vertex AI.

        Query: Show me all vendors and categories from product offers
        """
        llm_with_structure = llm.with_structured_output(Query)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL query builder. Generate a query based on the user's request."),
            ("user", "Show me all vendors and categories from the product_offers table")
        ])

        chain = prompt | llm_with_structure

        try:
            query = chain.invoke({})

            # Verify it's a valid Query object
            assert isinstance(query, Query)
            assert len(query.select) >= 2
            assert query.from_.table == Table.product_offers

            # Translate to SQL and verify it's valid
            sql = translate_query(query)
            assert "SELECT" in sql
            assert "vendor" in sql.lower() or "category" in sql.lower()
            assert "FROM product_offers" in sql

            print(f"\nGenerated SQL:\n{sql}")

        except Exception as e:
            pytest.fail(f"Query generation failed: {e}")

    def test_aggregate_query_generation(self, llm):
        """
        Test generating an aggregate query.

        Query: What's the average price by category?
        """
        llm_with_structure = llm.with_structured_output(Query)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL query builder. Generate a query based on the user's request."),
            ("user", "What's the average regular price for each category in product_offers?")
        ])

        chain = prompt | llm_with_structure

        try:
            query = chain.invoke({})

            assert isinstance(query, Query)
            assert query.group_by is not None

            # Should have aggregate expression
            has_aggregate = any(
                isinstance(expr, AggregateExpr)
                for expr in query.select
            )
            assert has_aggregate, "Query should contain aggregate expression"

            sql = translate_query(query)
            assert "AVG" in sql
            assert "GROUP BY" in sql

            print(f"\nGenerated SQL:\n{sql}")

        except Exception as e:
            pytest.fail(f"Aggregate query generation failed: {e}")


@pytest.mark.skipif(
    not VERTEXAI_AVAILABLE or not has_credentials(),
    reason=SKIP_REASON
)
class TestVertexAIComplexQueries:
    """Test complex query patterns with Vertex AI."""

    @pytest.fixture
    def llm(self):
        """Create Vertex AI LLM instance."""
        return ChatVertexAI(
            model="gemini-1.5-pro",
            temperature=0,
        )

    def test_window_function_query(self, llm):
        """
        Test generating query with window functions.

        Query: Rank products by price within each category
        """
        llm_with_structure = llm.with_structured_output(Query)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL query builder. Generate a query based on the user's request."),
            ("user", "Rank products by regular_price (ascending) within each category from product_offers")
        ])

        chain = prompt | llm_with_structure

        try:
            query = chain.invoke({})

            assert isinstance(query, Query)

            # Should have window function
            has_window = any(
                isinstance(expr, WindowExpr)
                for expr in query.select
            )
            assert has_window, "Query should contain window function"

            sql = translate_query(query)
            assert "OVER" in sql
            assert "PARTITION BY" in sql or "ORDER BY" in sql

            print(f"\nGenerated SQL:\n{sql}")

        except Exception as e:
            pytest.fail(f"Window function query generation failed: {e}")

    def test_computed_column_query(self, llm):
        """
        Test generating query with computed columns.

        Query: Calculate discount amount
        """
        llm_with_structure = llm.with_structured_output(Query)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL query builder. Generate a query based on the user's request."),
            ("user", "Show the discount amount (regular_price minus markdown_price) for products in product_offers")
        ])

        chain = prompt | llm_with_structure

        try:
            query = chain.invoke({})

            assert isinstance(query, Query)

            # Should have arithmetic expression
            has_arithmetic = any(
                isinstance(expr, (BinaryArithmetic, CompoundArithmetic))
                for expr in query.select
            )
            assert has_arithmetic, "Query should contain arithmetic expression"

            sql = translate_query(query)
            assert "-" in sql or "+" in sql or "*" in sql or "/" in sql

            print(f"\nGenerated SQL:\n{sql}")

        except Exception as e:
            pytest.fail(f"Computed column query generation failed: {e}")

    def test_complex_where_query(self, llm):
        """
        Test generating query with complex WHERE clause.

        Query: Products from specific vendors in specific categories
        """
        llm_with_structure = llm.with_structured_output(Query)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL query builder. Generate a query based on the user's request."),
            ("user", "Show products from amazon or walmart in the electronics category from product_offers")
        ])

        chain = prompt | llm_with_structure

        try:
            query = chain.invoke({})

            assert isinstance(query, Query)
            assert query.where is not None

            sql = translate_query(query)
            assert "WHERE" in sql

            print(f"\nGenerated SQL:\n{sql}")

        except Exception as e:
            pytest.fail(f"Complex WHERE query generation failed: {e}")


@pytest.mark.skipif(
    not VERTEXAI_AVAILABLE or not has_credentials(),
    reason=SKIP_REASON
)
class TestVertexAIEdgeCases:
    """Test edge cases and potential quirks with Vertex AI."""

    @pytest.fixture
    def llm(self):
        """Create Vertex AI LLM instance."""
        return ChatVertexAI(
            model="gemini-1.5-pro",
            temperature=0,
        )

    def test_optional_fields_handling(self, llm):
        """
        Test that optional fields are properly handled.

        A query without WHERE, GROUP BY, HAVING, ORDER BY, or LIMIT should work.
        """
        llm_with_structure = llm.with_structured_output(Query)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL query builder. Generate a query based on the user's request."),
            ("user", "Show all columns from product_offers")
        ])

        chain = prompt | llm_with_structure

        try:
            query = chain.invoke({})

            assert isinstance(query, Query)
            # Optional fields should be None or empty
            sql = translate_query(query)
            assert "SELECT" in sql
            assert "FROM product_offers" in sql

            print(f"\nGenerated SQL:\n{sql}")

        except Exception as e:
            pytest.fail(f"Optional fields handling failed: {e}")

    def test_enum_value_validation(self, llm):
        """
        Test that enum values are properly validated.

        The LLM should only be able to generate valid enum values.
        """
        llm_with_structure = llm.with_structured_output(Query)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL query builder. Generate a query based on the user's request."),
            ("user", "Show vendor from product_offers")
        ])

        chain = prompt | llm_with_structure

        try:
            query = chain.invoke({})

            assert isinstance(query, Query)
            # Table and columns should be valid enums
            assert query.from_.table in Table

            for expr in query.select:
                if isinstance(expr, ColumnExpr):
                    assert expr.source.column in Column

            print(f"\nGenerated query with valid enums")

        except Exception as e:
            pytest.fail(f"Enum validation failed: {e}")


# Manual test for exploring Vertex AI behavior
def manual_test_vertexai_generation():
    """
    Manual test function for exploring Vertex AI behavior.

    Run this directly to test various prompts and see how Vertex AI handles them.
    """
    if not VERTEXAI_AVAILABLE:
        print("Vertex AI not available")
        return

    if not has_credentials():
        print("Google credentials not available")
        return

    llm = ChatVertexAI(
        model="gemini-1.5-pro",
        temperature=0,
    )

    llm_with_structure = llm.with_structured_output(Query)

    test_prompts = [
        "Show all products from product_offers",
        "What's the average price by category?",
        "Calculate the discount percentage for each product",
        "Rank products by price within each category",
        "Show products from amazon that cost more than $100",
    ]

    for i, prompt_text in enumerate(test_prompts, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {prompt_text}")
        print('='*80)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL query builder. Generate a query based on the user's request."),
            ("user", prompt_text)
        ])

        chain = prompt | llm_with_structure

        try:
            query = chain.invoke({})
            print(f"\nGenerated Query Object:")
            print(query.model_dump_json(indent=2))

            sql = translate_query(query)
            print(f"\nGenerated SQL:")
            print(sql)

        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    manual_test_vertexai_generation()
