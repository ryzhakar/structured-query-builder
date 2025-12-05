"""
Tests for example files to ensure they execute without errors.

This module validates that all example files (basic_queries.py,
pricing_analyst_queries.py) run successfully and generate valid SQL.
"""

import pytest
import sys
from io import StringIO


class TestBasicExamples:
    """Test basic_queries.py examples."""

    def test_all_basic_examples_run(self):
        """Test that all 7 basic examples execute without error."""
        from examples import basic_queries

        # Capture stdout to suppress print statements during test
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            # Run all examples
            basic_queries.main()
        finally:
            sys.stdout = old_stdout

    def test_basic_example_1_discount_percentage(self):
        """Test example 1: Simple SELECT."""
        from examples import basic_queries
        query = basic_queries.example_1_simple_select()
        assert query is not None
        assert query.from_.table.value == "product_offers"

    def test_basic_example_2_with_filter(self):
        """Test example 2: SELECT with WHERE."""
        from examples import basic_queries
        query = basic_queries.example_2_with_filter()
        assert query is not None
        assert query.where is not None

    def test_basic_example_3_in_operator(self):
        """Test example 3: IN operator."""
        from examples import basic_queries
        query = basic_queries.example_3_in_operator()
        assert query is not None
        assert query.where is not None

    def test_basic_example_4_aggregate(self):
        """Test example 4: Aggregate with GROUP BY."""
        from examples import basic_queries
        query = basic_queries.example_4_aggregate()
        assert query is not None
        assert query.group_by is not None

    def test_basic_example_5_order_limit(self):
        """Test example 5: ORDER BY with LIMIT."""
        from examples import basic_queries
        query = basic_queries.example_5_order_limit()
        assert query is not None
        assert query.order_by is not None
        assert query.limit is not None

    def test_basic_example_6_count_by_category(self):
        """Test example 6: COUNT by category."""
        from examples import basic_queries
        query = basic_queries.example_6_count_by_category()
        assert query is not None
        assert query.group_by is not None

    def test_basic_example_7_between(self):
        """Test example 7: BETWEEN condition."""
        from examples import basic_queries
        query = basic_queries.example_7_between()
        assert query is not None
        assert query.where is not None


class TestPricingAnalystExamples:
    """Test pricing_analyst_queries.py examples."""

    def test_all_pricing_analyst_examples_run(self):
        """Test that all 7 pricing analyst examples execute without error."""
        from examples import pricing_analyst_queries

        # Capture stdout to suppress print statements during test
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            # Run all examples
            pricing_analyst_queries.main()
        finally:
            sys.stdout = old_stdout

    def test_analyst_example_1_discount_percentage(self):
        """Test example 1: Discount percentage calculation."""
        from examples import pricing_analyst_queries
        query = pricing_analyst_queries.example_1_discount_percentage()
        assert query is not None
        # Should have CompoundArithmetic for discount calculation
        assert any(expr.expr_type == "compound_arithmetic" for expr in query.select)

    def test_analyst_example_2_price_ranking(self):
        """Test example 2: Price ranking by category (window function)."""
        from examples import pricing_analyst_queries
        query = pricing_analyst_queries.example_2_price_ranking()
        assert query is not None
        # Should have WindowExpr for RANK
        assert any(expr.expr_type == "window" for expr in query.select)

    def test_analyst_example_3_competitor_comparison(self):
        """Test example 3: Competitor comparison (self-join)."""
        from examples import pricing_analyst_queries
        query = pricing_analyst_queries.example_3_competitor_comparison()
        assert query is not None
        # Should have JOIN
        assert query.from_.joins is not None
        assert len(query.from_.joins) > 0

    def test_analyst_example_4_above_category_average(self):
        """Test example 4: Products above category average (subquery)."""
        from examples import pricing_analyst_queries
        query = pricing_analyst_queries.example_4_above_category_average()
        assert query is not None
        # Should have subquery in WHERE
        assert query.where is not None
        assert query.where.subquery_conditions is not None

    def test_analyst_example_5_price_tier_classification(self):
        """Test example 5: Price tier classification (CASE)."""
        from examples import pricing_analyst_queries
        query = pricing_analyst_queries.example_5_price_tier_classification()
        assert query is not None
        # Should have CaseExpr
        assert any(expr.expr_type == "case" for expr in query.select)

    def test_analyst_example_6_vendor_price_stats(self):
        """Test example 6: Vendor price statistics (aggregates)."""
        from examples import pricing_analyst_queries
        query = pricing_analyst_queries.example_6_vendor_price_stats()
        assert query is not None
        # Should have multiple aggregates
        assert query.group_by is not None
        assert sum(1 for expr in query.select if expr.expr_type == "aggregate") >= 4

    def test_analyst_example_7_week_over_week_changes(self):
        """Test example 7: Week-over-week changes (LAG window function)."""
        from examples import pricing_analyst_queries
        query = pricing_analyst_queries.example_7_week_over_week_changes()
        assert query is not None
        # Should have WindowExpr with LAG
        window_exprs = [expr for expr in query.select if expr.expr_type == "window"]
        assert len(window_exprs) > 0
