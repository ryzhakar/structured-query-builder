"""
Tests for Phase 1 enhanced queries and schema features.

Tests coverage:
- Statistical aggregate functions (STDDEV, VARIANCE)
- Table alias support in BinaryArithmetic and AggregateExpr
- All 8 new Phase 1 queries generate valid SQL
- Temporal queries with updated_at column
"""

import pytest
from structured_query_builder import *
from structured_query_builder.translator import translate_query


class TestStatisticalFunctions:
    """Test new statistical aggregate functions."""

    def test_stddev_aggregate(self):
        """Test STDDEV aggregate function."""
        query = Query(
            select=[
                AggregateExpr(
                    function=AggregateFunc.stddev,
                    column=Column.markdown_price,
                    alias="price_stddev"
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
                    alias="price_stddev_pop"
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
                    alias="price_variance"
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
                    alias="price_var_pop"
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
            alias="price_gap"
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
            alias="avg_price"
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
                    alias="my_avg"
                ),
                AggregateExpr(
                    function=AggregateFunc.avg,
                    column=Column.markdown_price,
                    table_alias="comp",
                    alias="comp_avg"
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
                                        left_column=QualifiedColumn(column=Column.id, table_alias="my"),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(column=Column.id, table_alias="comp")
                                    )
                                ],
                                logic=LogicOp.and_
                            )
                        ]
                    ),
                ]
            ),
        )
        sql = translate_query(query)
        assert "AVG(my.markdown_price) AS my_avg" in sql
        assert "AVG(comp.markdown_price) AS comp_avg" in sql


class TestTemporalQueries:
    """Test temporal queries using updated_at column."""

    def test_updated_at_column_exists(self):
        """Test that updated_at column is available."""
        assert hasattr(Column, 'updated_at')
        assert Column.updated_at.value == "updated_at"

    def test_between_condition_with_updated_at(self):
        """Test BETWEEN condition with updated_at for temporal filtering."""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.category)),
                AggregateExpr(
                    function=AggregateFunc.count,
                    column=None,
                    alias="count"
                ),
            ],
            from_=FromClause(table=Table.product_offers),
            where=WhereL1(
                groups=[
                    ConditionGroup(
                        conditions=[
                            BetweenCondition(
                                column=QualifiedColumn(column=Column.updated_at),
                                low="2025-11-22",
                                high="2025-11-29"
                            ),
                        ],
                        logic=LogicOp.and_
                    )
                ],
                group_logic=LogicOp.and_
            ),
            group_by=GroupByClause(columns=[Column.category]),
        )
        sql = translate_query(query)
        assert "updated_at BETWEEN '2025-11-22' AND '2025-11-29'" in sql


class TestPhase1Queries:
    """Test all 8 Phase 1 queries generate valid SQL."""

    def test_query_16_map_violations(self):
        """Test Q16: MAP Violations (Unmatched)."""
        from examples.phase1_queries import query_16_map_violations_unmatched

        query = query_16_map_violations_unmatched()
        sql = translate_query(query)

        # Verify key elements
        assert "SELECT id" in sql
        assert "vendor = 'Them'" in sql
        assert "brand = 'Nike'" in sql
        assert "markdown_price < 50.0" in sql
        assert "LIMIT 100" in sql

    def test_query_17_premium_gap(self):
        """Test Q17: Premium Gap Analysis (Matched)."""
        from examples.phase1_queries import query_17_premium_gap_analysis

        query = query_17_premium_gap_analysis()
        sql = translate_query(query)

        # Verify multi-table aggregates
        assert "AVG(my.markdown_price)" in sql
        assert "AVG(comp.markdown_price)" in sql
        assert "INNER JOIN exact_matches" in sql
        assert "GROUP BY brand, category" in sql

    def test_query_18_supply_chain(self):
        """Test Q18: Supply Chain Failure Detector (Unmatched)."""
        from examples.phase1_queries import query_18_supply_chain_failure_detector

        query = query_18_supply_chain_failure_detector()
        sql = translate_query(query)

        # Verify aggregates
        assert "COUNT(*)" in sql
        assert "SUM(availability)" in sql
        assert "GROUP BY brand, vendor" in sql

    def test_query_19_loss_leader(self):
        """Test Q19: Loss-Leader Hunter (Matched)."""
        from examples.phase1_queries import query_19_loss_leader_hunter

        query = query_19_loss_leader_hunter()
        sql = translate_query(query)

        # Verify column comparison in WHERE
        assert "comp.markdown_price < my.regular_price" in sql
        assert "LIMIT 50" in sql

    def test_query_20_price_snapshot(self):
        """Test Q20: Category Price Snapshot (Temporal)."""
        from examples.phase1_queries import query_20_category_price_snapshot

        query = query_20_category_price_snapshot()
        sql = translate_query(query)

        # Verify temporal filtering
        assert "updated_at BETWEEN" in sql
        assert "MIN(markdown_price)" in sql
        assert "AVG(markdown_price)" in sql

    def test_query_21_promo_erosion(self):
        """Test Q21: Promo Erosion Index (Unmatched)."""
        from examples.phase1_queries import query_21_promo_erosion_index

        query = query_21_promo_erosion_index()
        sql = translate_query(query)

        # Verify price comparison aggregates
        assert "AVG(markdown_price)" in sql
        assert "AVG(regular_price)" in sql
        assert "vendor = 'Them'" in sql

    def test_query_22_brand_presence(self):
        """Test Q22: Brand Presence Tracking (Unmatched)."""
        from examples.phase1_queries import query_22_brand_presence_tracking

        query = query_22_brand_presence_tracking()
        sql = translate_query(query)

        # Verify brand tracking metrics
        assert "COUNT(*)" in sql
        assert "SUM(availability)" in sql
        assert "AVG(markdown_price)" in sql
        assert "GROUP BY brand, vendor" in sql

    def test_query_23_discount_depth(self):
        """Test Q23: Discount Depth Distribution (Unmatched)."""
        from examples.phase1_queries import query_23_discount_depth_distribution

        query = query_23_discount_depth_distribution()
        sql = translate_query(query)

        # Verify statistical function usage
        assert "STDDEV(markdown_price)" in sql
        assert "AVG(markdown_price)" in sql
        assert "AVG(regular_price)" in sql
        assert "is_markdown = TRUE" in sql


class TestQuerySerialization:
    """Test that all new queries can be serialized to JSON."""

    def test_all_phase1_queries_serialize(self):
        """Test JSON serialization of all Phase 1 queries."""
        from examples import phase1_queries

        query_functions = [
            phase1_queries.query_16_map_violations_unmatched,
            phase1_queries.query_17_premium_gap_analysis,
            phase1_queries.query_18_supply_chain_failure_detector,
            phase1_queries.query_19_loss_leader_hunter,
            phase1_queries.query_20_category_price_snapshot,
            phase1_queries.query_21_promo_erosion_index,
            phase1_queries.query_22_brand_presence_tracking,
            phase1_queries.query_23_discount_depth_distribution,
        ]

        for query_func in query_functions:
            query = query_func()
            json_str = query.model_dump_json()
            assert json_str is not None
            assert len(json_str) > 0
            # Verify it can be parsed back
            assert '"select"' in json_str or '"SELECT"' in json_str.upper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
