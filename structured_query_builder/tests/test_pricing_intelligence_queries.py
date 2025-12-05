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


class TestPhase1Queries:
    """Test all 8 Phase 1 queries generate valid SQL."""

    def test_query_16_map_violations(self):
        """Test Q16: MAP Violations (Unmatched)."""
        from examples.pricing_intelligence_queries import (
            query_16_map_violations_unmatched,
        )

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
        from examples.pricing_intelligence_queries import query_17_premium_gap_analysis

        query = query_17_premium_gap_analysis()
        sql = translate_query(query)

        # Verify nested arithmetic in aggregate: AVG(my.price - comp.price)
        assert "AVG((my.markdown_price - comp.markdown_price))" in sql
        assert "avg_premium_gap" in sql
        assert "INNER JOIN exact_matches" in sql
        assert "GROUP BY brand, category" in sql

    def test_query_18_supply_chain(self):
        """Test Q18: Supply Chain Failure Detector (temporal with LAG)."""
        from examples.pricing_intelligence_queries import (
            query_18_supply_chain_failure_detector,
        )

        query = query_18_supply_chain_failure_detector()
        sql = translate_query(query)

        # Verify temporal pattern with LAG window function
        assert "LAG(weekly.availability_changes)" in sql
        assert "PARTITION BY brand" in sql
        assert "SUM(availability)" in sql
        assert "GROUP BY brand, updated_at" in sql

    def test_query_19_loss_leader(self):
        """Test Q19: Loss-Leader Hunter (Matched)."""
        from examples.pricing_intelligence_queries import query_19_loss_leader_hunter

        query = query_19_loss_leader_hunter()
        sql = translate_query(query)

        # Verify column comparison in WHERE
        assert "comp.markdown_price < my.regular_price" in sql
        assert "LIMIT 50" in sql

    def test_query_20_price_snapshot(self):
        """Test Q20: Category Price Snapshot (temporal comparison with self-join)."""
        from examples.pricing_intelligence_queries import (
            query_20_category_price_snapshot,
        )

        query = query_20_category_price_snapshot()
        sql = translate_query(query)

        # Verify temporal self-join pattern
        assert "current.updated_at BETWEEN" in sql
        assert "historical.updated_at BETWEEN" in sql
        assert "MIN(current.markdown_price)" in sql
        assert "MIN(historical.markdown_price)" in sql
        assert "INNER JOIN product_offers AS historical" in sql
        assert "price_lift_pct" in sql

    def test_query_21_promo_erosion(self):
        """Test Q21: Promo Erosion Index (Unmatched)."""
        from examples.pricing_intelligence_queries import query_21_promo_erosion_index

        query = query_21_promo_erosion_index()
        sql = translate_query(query)

        # Verify price comparison aggregates
        assert "AVG(markdown_price)" in sql
        assert "AVG(regular_price)" in sql
        assert "vendor = 'Them'" in sql

    def test_query_22_brand_presence(self):
        """Test Q22: Brand Presence Tracking with LAG (Unmatched)."""
        from examples.pricing_intelligence_queries import (
            query_22_brand_presence_tracking,
        )

        query = query_22_brand_presence_tracking()
        sql = translate_query(query)

        # Verify temporal tracking with LAG
        assert "COUNT(*)" in sql
        assert "LAG(weekly.offer_count)" in sql
        assert "PARTITION BY brand, vendor" in sql
        assert "GROUP BY brand, vendor, updated_at" in sql
        # Verify week-over-week change calculation
        assert "previous_count" in sql
        assert "count_change_pct" in sql

    def test_query_23_discount_depth(self):
        """Test Q23: Discount Depth Distribution (Unmatched)."""
        from examples.pricing_intelligence_queries import (
            query_23_discount_depth_distribution,
        )

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
        from examples import pricing_intelligence_queries

        query_functions = [
            pricing_intelligence_queries.query_16_map_violations_unmatched,
            pricing_intelligence_queries.query_17_premium_gap_analysis,
            pricing_intelligence_queries.query_18_supply_chain_failure_detector,
            pricing_intelligence_queries.query_19_loss_leader_hunter,
            pricing_intelligence_queries.query_20_category_price_snapshot,
            pricing_intelligence_queries.query_21_promo_erosion_index,
            pricing_intelligence_queries.query_22_brand_presence_tracking,
            pricing_intelligence_queries.query_23_discount_depth_distribution,
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
"""
Tests for Phase 2 and Phase 3 ARCHITECT queries.

Phase 2 Coverage (Q24-Q26):
- ARCHITECT: Range architecture and strategic positioning
- Commoditization coefficient, brand weighting, price ladder analysis

Phase 3 Coverage (Q27-Q29):
- ARCHITECT: Procurement intelligence using competitive pricing proxies
- Vendor fairness audit, safe haven scanner, inventory velocity detection
"""

import pytest
from structured_query_builder import *
from structured_query_builder.translator import translate_query


class TestPhase2Queries:
    """Test all 3 Phase 2 ARCHITECT range queries."""

    def test_query_24_commoditization_coefficient(self):
        """Test Q24: Commoditization Coefficient (Matched)."""
        from examples.pricing_intelligence_queries import (
            query_24_commoditization_coefficient,
        )

        query = query_24_commoditization_coefficient()
        sql = translate_query(query)

        # Verify LEFT JOIN for unmatched products
        assert "LEFT JOIN exact_matches" in sql
        assert "GROUP BY category" in sql

        # Verify counting pattern for coefficient calculation
        assert "COUNT(my.id)" in sql
        assert "COUNT(em.source_id)" in sql

        # Verify vendor filter
        assert "vendor = 'Us'" in sql

    def test_query_25_brand_weighting_fingerprint(self):
        """Test Q25: Brand Weighting Fingerprint (Unmatched)."""
        from examples.pricing_intelligence_queries import (
            query_25_brand_weighting_fingerprint,
        )

        query = query_25_brand_weighting_fingerprint()
        sql = translate_query(query)

        # Verify brand and vendor grouping
        assert "GROUP BY brand, vendor" in sql

        # Verify counting for share-of-shelf calculation
        assert "COUNT(*)" in sql

        # Verify ordering by vendor and brand
        assert "ORDER BY vendor ASC, brand ASC" in sql

    def test_query_26_price_ladder_void_scanner(self):
        """Test Q26: Price Ladder Void Scanner (Unmatched)."""
        from examples.pricing_intelligence_queries import (
            query_26_price_ladder_void_scanner,
        )

        query = query_26_price_ladder_void_scanner()
        sql = translate_query(query)

        # Verify price range aggregates
        assert "MIN(markdown_price)" in sql
        assert "MAX(markdown_price)" in sql
        assert "AVG(markdown_price)" in sql

        # Verify statistical function for gap analysis
        assert "STDDEV(markdown_price)" in sql

        # Verify grouping
        assert "GROUP BY category, vendor" in sql
        assert "ORDER BY category ASC" in sql


class TestPhase3Queries:
    """Test all 3 Phase 3 ARCHITECT procurement queries."""

    def test_query_27_vendor_fairness_audit(self):
        """Test Q27: Vendor Fairness Audit (Matched)."""
        from examples.pricing_intelligence_queries import query_27_vendor_fairness_audit

        query = query_27_vendor_fairness_audit()
        sql = translate_query(query)

        # Verify matched execution pattern
        assert "INNER JOIN exact_matches" in sql
        assert "INNER JOIN product_offers AS comp" in sql

        # Verify competitive pricing comparison (using regular_price as cost proxy)
        assert "comp.regular_price < my.regular_price" in sql

        # Verify vendor filter
        assert "vendor = 'Us'" in sql

        # Verify ordering and limit
        assert "ORDER BY brand ASC" in sql
        assert "LIMIT 100" in sql

    def test_query_28_safe_haven_scanner(self):
        """Test Q28: Safe Haven Scanner with temporal STDDEV (Matched)."""
        from examples.pricing_intelligence_queries import query_28_safe_haven_scanner

        query = query_28_safe_haven_scanner()
        sql = translate_query(query)

        # Verify matched execution
        assert "INNER JOIN exact_matches" in sql

        # Verify price gap calculation
        assert "price_gap" in sql
        assert "(comp.markdown_price - my.markdown_price)" in sql

        # Verify temporal window STDDEV for price volatility
        assert "STDDEV(comp.markdown_price) OVER" in sql
        assert "PARTITION BY id" in sql
        assert "ORDER BY updated_at" in sql
        assert "price_volatility_52w" in sql

    def test_query_29_inventory_velocity_detector(self):
        """Test Q29: Inventory Velocity Detector with LAG state tracking."""
        from examples.pricing_intelligence_queries import (
            query_29_inventory_velocity_detector,
        )

        query = query_29_inventory_velocity_detector()
        sql = translate_query(query)

        # Verify LAG for previous availability state
        assert "LAG(comp.availability)" in sql
        assert "PARTITION BY id" in sql
        assert "ORDER BY updated_at" in sql

        # Verify toggle count window function
        assert "COUNT(comp.id) OVER" in sql
        assert "toggle_count" in sql

        # Verify previous_availability column
        assert "previous_availability" in sql

        # Verify filtering for high-velocity products
        assert "toggle_count > 3" in sql

        # Verify ordering by toggle count (descending)
        assert "ORDER BY toggle_count DESC" in sql


class TestPhase2Phase3Serialization:
    """Test that all Phase 2 and Phase 3 queries serialize correctly."""

    def test_all_phase2_queries_serialize(self):
        """Test JSON serialization of all Phase 2 queries."""
        from examples import pricing_intelligence_queries

        query_functions = [
            pricing_intelligence_queries.query_24_commoditization_coefficient,
            pricing_intelligence_queries.query_25_brand_weighting_fingerprint,
            pricing_intelligence_queries.query_26_price_ladder_void_scanner,
        ]

        for query_func in query_functions:
            query = query_func()
            json_str = query.model_dump_json()
            assert json_str is not None
            assert len(json_str) > 0
            # Verify it contains query structure
            assert '"select"' in json_str or '"SELECT"' in json_str.upper()

    def test_all_phase3_queries_serialize(self):
        """Test JSON serialization of all Phase 3 queries."""
        from examples import pricing_intelligence_queries

        query_functions = [
            pricing_intelligence_queries.query_27_vendor_fairness_audit,
            pricing_intelligence_queries.query_28_safe_haven_scanner,
            pricing_intelligence_queries.query_29_inventory_velocity_detector,
        ]

        for query_func in query_functions:
            query = query_func()
            json_str = query.model_dump_json()
            assert json_str is not None
            assert len(json_str) > 0
            # Verify it contains query structure
            assert '"select"' in json_str or '"SELECT"' in json_str.upper()


class TestArchitectCoverageCompletion:
    """Test that ARCHITECT archetype has complete coverage."""

    def test_all_architect_queries_generate_valid_sql(self):
        """Test that all 6 ARCHITECT queries generate valid SQL."""
        from examples import pricing_intelligence_queries

        architect_queries = [
            # Phase 2: Range Architecture (3 queries)
            pricing_intelligence_queries.query_24_commoditization_coefficient,
            pricing_intelligence_queries.query_25_brand_weighting_fingerprint,
            pricing_intelligence_queries.query_26_price_ladder_void_scanner,
            # Phase 3: Procurement Intelligence (3 queries)
            pricing_intelligence_queries.query_27_vendor_fairness_audit,
            pricing_intelligence_queries.query_28_safe_haven_scanner,
            pricing_intelligence_queries.query_29_inventory_velocity_detector,
        ]

        for query_func in architect_queries:
            query = query_func()
            sql = translate_query(query)

            # All queries should have SELECT and FROM
            assert "SELECT" in sql
            assert "FROM" in sql
            assert len(sql.strip()) > 0

    def test_architect_bimodal_coverage(self):
        """Test that ARCHITECT has both matched and unmatched variants."""
        from examples import pricing_intelligence_queries

        # Matched queries (require exact_matches table)
        matched_queries = [
            pricing_intelligence_queries.query_24_commoditization_coefficient,  # LEFT JOIN for coefficient
            pricing_intelligence_queries.query_27_vendor_fairness_audit,
            pricing_intelligence_queries.query_28_safe_haven_scanner,
            # Q29 now uses unmatched pattern with temporal LAG for velocity detection
        ]

        # Unmatched queries (no exact_matches table)
        unmatched_queries = [
            pricing_intelligence_queries.query_25_brand_weighting_fingerprint,
            pricing_intelligence_queries.query_26_price_ladder_void_scanner,
            pricing_intelligence_queries.query_29_inventory_velocity_detector,  # Enhanced with LAG, no longer matched
        ]

        # Verify matched queries use exact_matches
        for query_func in matched_queries:
            query = query_func()
            sql = translate_query(query)
            assert "exact_matches" in sql

        # Verify unmatched queries don't use exact_matches
        for query_func in unmatched_queries:
            query = query_func()
            sql = translate_query(query)
            assert "exact_matches" not in sql


class TestProcurementIntelligencePatterns:
    """Test Phase 3 procurement intelligence patterns use only competitive data."""

    def test_no_cost_columns_referenced(self):
        """Verify Phase 3 queries use NO internal cost data columns."""
        from examples import pricing_intelligence_queries

        procurement_queries = [
            pricing_intelligence_queries.query_27_vendor_fairness_audit,
            pricing_intelligence_queries.query_28_safe_haven_scanner,
            pricing_intelligence_queries.query_29_inventory_velocity_detector,
        ]

        # These column names should NEVER appear (system is air-gapped from cost data)
        forbidden_columns = ["cost", "wholesale", "cogs", "margin"]

        for query_func in procurement_queries:
            query = query_func()
            sql = translate_query(query).lower()

            for forbidden in forbidden_columns:
                assert forbidden not in sql, (
                    f"Query {query_func.__name__} uses forbidden column '{forbidden}'"
                )

    def test_competitive_pricing_proxies_used(self):
        """Verify Phase 3 uses competitive pricing as cost proxy."""
        from examples import pricing_intelligence_queries

        # Q27: Uses regular_price as cost proxy
        query = pricing_intelligence_queries.query_27_vendor_fairness_audit()
        sql = translate_query(query)
        assert "regular_price" in sql
        assert "comp.regular_price < my.regular_price" in sql

        # Q28: Uses markdown_price for temporal volatility and gap analysis
        query = pricing_intelligence_queries.query_28_safe_haven_scanner()
        sql = translate_query(query)
        assert "my.markdown_price" in sql
        assert "comp.markdown_price" in sql
        assert "price_gap" in sql
        assert "price_volatility_52w" in sql  # Temporal STDDEV window function

        # Q29: Uses availability as velocity proxy with LAG
        query = pricing_intelligence_queries.query_29_inventory_velocity_detector()
        sql = translate_query(query)
        assert "availability" in sql
        assert "previous_availability" in sql  # LAG-based state tracking


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Tests for Q30-Q41 queries (ENFORCER, PREDATOR, MERCENARY, ARCHITECT archetypes).

These queries were implemented to achieve 100% coverage across all intelligence models.
Covers parity maintenance, headroom discovery, optical dominance, and total reconnaissance.
"""

import pytest
from structured_query_builder import *
from structured_query_builder.translator import translate_query


class TestQ30Q35EnforcerPredatorMercenary:
    """Test Q30-Q35: ENFORCER parity, PREDATOR headroom, MERCENARY optical."""

    def test_query_30_index_drift_check(self):
        """Test Q30: Index Drift Check (ENFORCER - Parity Maintenance)."""
        from examples.pricing_intelligence_queries import query_30_index_drift_check

        query = query_30_index_drift_check()
        sql = translate_query(query)

        # Verify matched execution pattern
        assert "INNER JOIN exact_matches" in sql
        assert "INNER JOIN product_offers AS comp" in sql

        # Verify price ratio calculation
        assert "price_ratio" in sql
        assert "my.markdown_price" in sql
        assert "comp.markdown_price" in sql

        # Verify vendor filters
        assert "vendor = 'Us'" in sql

        # Verify ordering and limit
        assert "ORDER BY" in sql
        assert "LIMIT 100" in sql

    def test_query_31_average_selling_price_gap(self):
        """Test Q31: Average Selling Price Gap (ENFORCER - Parity Maintenance)."""
        from examples.pricing_intelligence_queries import (
            query_31_average_selling_price_gap,
        )

        query = query_31_average_selling_price_gap()
        sql = translate_query(query)

        # Verify UNMATCHED execution (no exact_matches)
        assert "exact_matches" not in sql

        # Verify aggregation
        assert "AVG(markdown_price)" in sql

        # Verify grouping by brand, category, vendor
        assert "GROUP BY brand, category, vendor" in sql

    def test_query_32_sku_violation_scan(self):
        """Test Q32: SKU Violation Scan (ENFORCER - MAP Policing)."""
        from examples.pricing_intelligence_queries import query_32_sku_violation_scan

        query = query_32_sku_violation_scan()
        sql = translate_query(query)

        # Verify matched execution
        assert "INNER JOIN exact_matches" in sql

        # Verify MAP violation calculation
        assert "map_violation_amount" in sql
        assert "my.regular_price" in sql
        assert "comp.markdown_price" in sql

        # Verify filtering for violations
        assert "comp.markdown_price < my.regular_price" in sql

        # Verify limit
        assert "LIMIT 100" in sql

    def test_query_33_unnecessary_discount_finder(self):
        """Test Q33: Unnecessary Discount Finder (PREDATOR - Headroom Discovery)."""
        from examples.pricing_intelligence_queries import (
            query_33_unnecessary_discount_finder,
        )

        query = query_33_unnecessary_discount_finder()
        sql = translate_query(query)

        # Verify matched execution
        assert "INNER JOIN exact_matches" in sql

        # Verify headroom calculation
        assert "price_headroom" in sql
        assert "comp.markdown_price" in sql
        assert "my.markdown_price" in sql

        # Verify filtering for over-discounting
        assert "my.markdown_price < comp.markdown_price" in sql
        assert "my.markdown_price < my.regular_price" in sql

        # Verify limit
        assert "LIMIT 100" in sql

    def test_query_34_anchor_check(self):
        """Test Q34: Anchor Check (MERCENARY - Optical Dominance)."""
        from examples.pricing_intelligence_queries import query_34_anchor_check

        query = query_34_anchor_check()
        sql = translate_query(query)

        # Verify matched execution
        assert "INNER JOIN exact_matches" in sql

        # Verify anchor gap calculation
        assert "anchor_gap" in sql
        assert "comp.regular_price" in sql
        assert "my.regular_price" in sql

        # Verify filtering for weaker anchor
        assert "my.regular_price < comp.regular_price" in sql

        # Verify limit
        assert "LIMIT 100" in sql

    def test_query_35_ad_hoc_keyword_scrape(self):
        """Test Q35: Ad Hoc Keyword Scrape (ARCHITECT - Semantic Clustering)."""
        from examples.pricing_intelligence_queries import query_35_ad_hoc_keyword_scrape

        query = query_35_ad_hoc_keyword_scrape()
        sql = translate_query(query)

        # Verify unmatched execution (no exact_matches)
        assert "exact_matches" not in sql

        # Verify aggregations for pricing intelligence
        assert "AVG(markdown_price)" in sql
        assert "MIN(markdown_price)" in sql
        assert "MAX(markdown_price)" in sql
        assert "COUNT(*)" in sql

        # Verify keyword filtering (example uses "laptop" and "gaming")
        assert "ILIKE" in sql


class TestQ36Q37MercenaryHistorian:
    """Test Q36-Q37: MERCENARY optical dominance and HISTORIAN temporal patterns."""

    def test_query_36_discount_depth_alignment(self):
        """Test Q36: Discount Depth Alignment (MERCENARY - Optical Dominance)."""
        from examples.pricing_intelligence_queries import (
            query_36_discount_depth_alignment,
        )

        query = query_36_discount_depth_alignment()
        sql = translate_query(query)

        # Verify matched execution
        assert "INNER JOIN exact_matches" in sql

        # Verify discount amount calculations
        assert "my_discount_amount" in sql
        assert "comp_discount_amount" in sql

        # Verify arithmetic: regular - markdown
        assert "my.regular_price" in sql
        assert "my.markdown_price" in sql
        assert "comp.regular_price" in sql
        assert "comp.markdown_price" in sql

        # Verify vendor filter
        assert "vendor = 'Us'" in sql

        # Verify limit
        assert "LIMIT 100" in sql

    def test_query_37_magic_number_distribution(self):
        """Test Q37: Magic Number Distribution (HISTORIAN - Temporal Patterns)."""
        from examples.pricing_intelligence_queries import (
            query_37_magic_number_distribution,
        )

        query = query_37_magic_number_distribution()
        sql = translate_query(query)

        # Verify unmatched execution
        assert "exact_matches" not in sql

        # Verify psychological price point detection using LIKE/ILIKE
        # (e.g., prices ending in .99, .95, .00)
        assert "markdown_price" in sql

        # Verify aggregation
        assert "COUNT(*)" in sql

        # Verify vendor filter
        assert "vendor != 'Us'" in sql


class TestQ38Q41ArchitectInflationReconnaissance:
    """Test Q38-Q41: ARCHITECT inflation tracking and total reconnaissance."""

    def test_query_38_same_store_inflation_rate(self):
        """Test Q38: Same-Store Inflation Rate (ARCHITECT - Temporal Inflation)."""
        from examples.pricing_intelligence_queries import (
            query_38_same_store_inflation_rate,
        )

        query = query_38_same_store_inflation_rate()
        sql = translate_query(query)

        # Verify matched execution
        assert "INNER JOIN exact_matches" in sql

        # Verify LAG window function for temporal comparison
        assert "LAG(markdown_price" in sql
        assert "PARTITION BY id" in sql
        assert "ORDER BY updated_at" in sql
        assert "previous_price" in sql

        # Verify aggregations for inflation calculation
        assert "AVG(markdown_price)" in sql or "AVG" in sql
        assert "current_avg_price" in sql
        assert "historical_avg_price" in sql

        # Verify grouping by category
        assert "GROUP BY category" in sql

    def test_query_39_entry_level_creep(self):
        """Test Q39: Entry-Level Creep (ARCHITECT - Market Floor Tracking)."""
        from examples.pricing_intelligence_queries import query_39_entry_level_creep

        query = query_39_entry_level_creep()
        sql = translate_query(query)

        # Verify unmatched execution
        assert "exact_matches" not in sql

        # Verify percentile calculation for entry-level threshold
        assert "PERCENTILE_DISC" in sql or "percentile_disc" in sql.lower()
        assert "0.1" in sql  # 10th percentile

        # Verify aggregations
        assert "MIN(markdown_price)" in sql
        assert "COUNT(*)" in sql

        # Verify grouping
        assert "GROUP BY category" in sql

        # Verify vendor filter
        assert "vendor != 'Us'" in sql

    def test_query_40_semantic_keyword_scrape(self):
        """Test Q40: Semantic Keyword Scrape (ARCHITECT - Manual Matching)."""
        from examples.pricing_intelligence_queries import (
            query_40_semantic_keyword_scrape,
        )

        query = query_40_semantic_keyword_scrape()
        sql = translate_query(query)

        # Verify unmatched execution
        assert "exact_matches" not in sql

        # Verify multi-keyword semantic search using ILIKE
        assert "ILIKE" in sql
        assert "title" in sql

        # Verify aggregations for pricing intelligence
        assert "AVG(markdown_price)" in sql
        assert "MIN(markdown_price)" in sql
        assert "MAX(markdown_price)" in sql
        assert "COUNT(*)" in sql

        # Verify vendor filter
        assert "vendor != 'Us'" in sql

    def test_query_41_new_arrival_survival_rate(self):
        """Test Q41: New Arrival Survival Rate (ARCHITECT - Velocity Inference)."""
        from examples.pricing_intelligence_queries import (
            query_41_new_arrival_survival_rate,
        )

        query = query_41_new_arrival_survival_rate()
        sql = translate_query(query)

        # Verify unmatched execution
        assert "exact_matches" not in sql

        # Verify filtering for survivors (TRUE uppercase in SQL)
        assert "availability = TRUE" in sql

        # Verify IS NOT NULL for created_at
        assert "created_at IS NOT NULL" in sql

        # Verify vendor filter
        assert "vendor != 'Us'" in sql

        # Verify ordering and limit
        assert "ORDER BY" in sql
        assert "LIMIT 100" in sql


class TestQ30Q41Serialization:
    """Test that all Q30-Q41 queries serialize correctly."""

    def test_all_q30_q41_serialize(self):
        """Test JSON serialization of all Q30-Q41 queries."""
        from examples import pricing_intelligence_queries

        query_functions = [
            pricing_intelligence_queries.query_30_index_drift_check,
            pricing_intelligence_queries.query_31_average_selling_price_gap,
            pricing_intelligence_queries.query_32_sku_violation_scan,
            pricing_intelligence_queries.query_33_unnecessary_discount_finder,
            pricing_intelligence_queries.query_34_anchor_check,
            pricing_intelligence_queries.query_35_ad_hoc_keyword_scrape,
            pricing_intelligence_queries.query_36_discount_depth_alignment,
            pricing_intelligence_queries.query_37_magic_number_distribution,
            pricing_intelligence_queries.query_38_same_store_inflation_rate,
            pricing_intelligence_queries.query_39_entry_level_creep,
            pricing_intelligence_queries.query_40_semantic_keyword_scrape,
            pricing_intelligence_queries.query_41_new_arrival_survival_rate,
        ]

        for query_func in query_functions:
            query = query_func()
            json_str = query.model_dump_json()
            assert json_str is not None
            assert len(json_str) > 0
            # Verify it contains query structure
            assert '"select"' in json_str or '"SELECT"' in json_str.upper()


class TestQ30Q41Coverage:
    """Test that Q30-Q41 achieve full archetype coverage."""

    def test_all_q30_q41_generate_valid_sql(self):
        """Test that all 12 Q30-Q41 queries generate valid SQL."""
        from examples import pricing_intelligence_queries

        queries = [
            pricing_intelligence_queries.query_30_index_drift_check,
            pricing_intelligence_queries.query_31_average_selling_price_gap,
            pricing_intelligence_queries.query_32_sku_violation_scan,
            pricing_intelligence_queries.query_33_unnecessary_discount_finder,
            pricing_intelligence_queries.query_34_anchor_check,
            pricing_intelligence_queries.query_35_ad_hoc_keyword_scrape,
            pricing_intelligence_queries.query_36_discount_depth_alignment,
            pricing_intelligence_queries.query_37_magic_number_distribution,
            pricing_intelligence_queries.query_38_same_store_inflation_rate,
            pricing_intelligence_queries.query_39_entry_level_creep,
            pricing_intelligence_queries.query_40_semantic_keyword_scrape,
            pricing_intelligence_queries.query_41_new_arrival_survival_rate,
        ]

        for query_func in queries:
            query = query_func()
            sql = translate_query(query)

            # All queries should have SELECT and FROM
            assert "SELECT" in sql
            assert "FROM" in sql
            assert len(sql.strip()) > 0

    def test_matched_vs_unmatched_coverage(self):
        """Test that Q30-Q41 include both matched and unmatched variants."""
        from examples import pricing_intelligence_queries

        # Matched queries (require exact_matches table)
        matched_queries = [
            pricing_intelligence_queries.query_30_index_drift_check,
            pricing_intelligence_queries.query_32_sku_violation_scan,
            pricing_intelligence_queries.query_33_unnecessary_discount_finder,
            pricing_intelligence_queries.query_34_anchor_check,
            pricing_intelligence_queries.query_36_discount_depth_alignment,
            pricing_intelligence_queries.query_38_same_store_inflation_rate,
        ]

        # Unmatched queries (no exact_matches table)
        unmatched_queries = [
            pricing_intelligence_queries.query_31_average_selling_price_gap,
            pricing_intelligence_queries.query_35_ad_hoc_keyword_scrape,
            pricing_intelligence_queries.query_37_magic_number_distribution,
            pricing_intelligence_queries.query_39_entry_level_creep,
            pricing_intelligence_queries.query_40_semantic_keyword_scrape,
            pricing_intelligence_queries.query_41_new_arrival_survival_rate,
        ]

        # Verify matched queries use exact_matches
        for query_func in matched_queries:
            query = query_func()
            sql = translate_query(query)
            assert "exact_matches" in sql

        # Verify unmatched queries don't use exact_matches
        for query_func in unmatched_queries:
            query = query_func()
            sql = translate_query(query)
            assert "exact_matches" not in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
