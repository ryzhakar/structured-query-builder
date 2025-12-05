"""
Tests for advanced schema features.

This module tests schema enhancements including:
- Statistical aggregate functions (STDDEV, VARIANCE, STDDEV_POP, VAR_POP)
- Table alias support in BinaryArithmetic and AggregateExpr
- Temporal queries using updated_at column
"""

import pytest
from structured_query_builder import *
from structured_query_builder.translator import translate_query


class TestStatisticalFunctions:
    """Test statistical aggregate functions."""

    def test_stddev_aggregate(self):
        """Test STDDEV aggregate function."""
        query = Query(
            select=[
                AggregateExpr(
                    function=AggregateFunc.stddev,
                    column=Column.markdown_price,
                    alias="price_stddev",
                ),
            ],
            from_=FromClause(table=Table.product_offers),
        )
        sql = translate_query(query)
        assert "STDDEV(markdown_price) AS price_stddev" in sql

    def test_stddev_pop_aggregate(self):
        """Test STDDEV_POP aggregate function."""
        query = Query(
            select=[
                AggregateExpr(
                    function=AggregateFunc.stddev_pop,
                    column=Column.markdown_price,
                    alias="price_stddev_pop",
                ),
            ],
            from_=FromClause(table=Table.product_offers),
        )
        sql = translate_query(query)
        assert "STDDEV_POP(markdown_price) AS price_stddev_pop" in sql

    def test_variance_aggregate(self):
        """Test VARIANCE aggregate function."""
        query = Query(
            select=[
                AggregateExpr(
                    function=AggregateFunc.variance,
                    column=Column.markdown_price,
                    alias="price_variance",
                ),
            ],
            from_=FromClause(table=Table.product_offers),
        )
        sql = translate_query(query)
        assert "VARIANCE(markdown_price) AS price_variance" in sql

    def test_var_pop_aggregate(self):
        """Test VAR_POP aggregate function."""
        query = Query(
            select=[
                AggregateExpr(
                    function=AggregateFunc.var_pop,
                    column=Column.markdown_price,
                    alias="price_var_pop",
                ),
            ],
            from_=FromClause(table=Table.product_offers),
        )
        sql = translate_query(query)
        assert "VAR_POP(markdown_price) AS price_var_pop" in sql


class TestTableAliasSupport:
    """Test table alias support in arithmetic and aggregate expressions."""

    def test_binary_arithmetic_with_table_aliases(self):
        """Test BinaryArithmetic with table aliases on both sides."""
        expr = BinaryArithmetic(
            left_column=Column.markdown_price,
            left_table_alias="my",
            operator=ArithmeticOp.subtract,
            right_column=Column.markdown_price,
            right_table_alias="comp",
            alias="price_gap",
        )

        query = Query(
            select=[expr],
            from_=FromClause(table=Table.product_offers),
        )
        sql = translate_query(query)
        assert "(my.markdown_price - comp.markdown_price) AS price_gap" in sql

    def test_aggregate_with_table_alias(self):
        """Test AggregateExpr with table alias."""
        expr = AggregateExpr(
            function=AggregateFunc.avg,
            column=Column.markdown_price,
            table_alias="my",
            alias="avg_price",
        )

        query = Query(
            select=[expr],
            from_=FromClause(table=Table.product_offers, table_alias="my"),
        )
        sql = translate_query(query)
        assert "AVG(my.markdown_price) AS avg_price" in sql

    def test_mixed_table_aliases_in_query(self):
        """Test query with multiple table aliases."""
        query = Query(
            select=[
                AggregateExpr(
                    function=AggregateFunc.avg,
                    column=Column.markdown_price,
                    table_alias="my",
                    alias="my_avg",
                ),
                AggregateExpr(
                    function=AggregateFunc.avg,
                    column=Column.markdown_price,
                    table_alias="comp",
                    alias="comp_avg",
                ),
            ],
            from_=FromClause(
                table=Table.product_offers,
                table_alias="my",
                joins=[
                    JoinSpec(
                        join_type=JoinType.inner,
                        table=Table.product_offers,
                        table_alias="comp",
                        on_conditions=[
                            ConditionGroup(
                                conditions=[
                                    ColumnComparison(
                                        left_column=QualifiedColumn(
                                            column=Column.id, table_alias="my"
                                        ),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(
                                            column=Column.id, table_alias="comp"
                                        ),
                                    )
                                ],
                                logic=LogicOp.and_,
                            )
                        ],
                    ),
                ],
            ),
        )
        sql = translate_query(query)
        assert "AVG(my.markdown_price) AS my_avg" in sql
        assert "AVG(comp.markdown_price) AS comp_avg" in sql


class TestTemporalQueries:
    """Test temporal queries using updated_at column."""

    def test_updated_at_column_exists(self):
        """Test that updated_at column is available."""
        assert hasattr(Column, "updated_at")
        assert Column.updated_at.value == "updated_at"

    def test_between_condition_with_updated_at(self):
        """Test BETWEEN condition with updated_at for temporal filtering."""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.category)),
                AggregateExpr(function=AggregateFunc.count, column=None, alias="count"),
            ],
            from_=FromClause(table=Table.product_offers),
            where=WhereL1(
                groups=[
                    ConditionGroup(
                        conditions=[
                            BetweenCondition(
                                column=QualifiedColumn(column=Column.updated_at),
                                low="2025-11-22",
                                high="2025-11-29",
                            ),
                        ],
                        logic=LogicOp.and_,
                    )
                ],
                group_logic=LogicOp.and_,
            ),
            group_by=GroupByClause(columns=[Column.category]),
        )
        sql = translate_query(query)
        assert "updated_at BETWEEN '2025-11-22' AND '2025-11-29'" in sql

    def test_temporal_window_with_updated_at(self):
        """Test window function ordered by updated_at."""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
                ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
                WindowExpr(
                    function=WindowFunc.lag,
                    column=Column.markdown_price,
                    partition_by=[Column.vendor],
                    order_by=[OrderByItem(column=Column.updated_at, direction=Direction.asc)],
                    offset=1,
                    alias="previous_price"
                ),
            ],
            from_=FromClause(table=Table.product_offers),
        )
        sql = translate_query(query)
        assert "LAG(markdown_price) OVER (PARTITION BY vendor ORDER BY updated_at ASC)" in sql
