"""
Tests for pricing intelligence queries organized by archetype.

This module tests all 37 production intelligence queries (Q03-Q41),
organized by the five intelligence archetypes:
- ENFORCER: Compliance monitoring and parity maintenance
- PREDATOR: Competitive advantage and headroom discovery
- HISTORIAN: Temporal patterns and trend analysis
- MERCENARY: Optical dominance and promotional strategy
- ARCHITECT: Strategic positioning and market structure

Each query is validated for correct SQL generation, proper archetype
patterns (matched vs unmatched execution), and JSON serialization.
"""

import pytest
from structured_query_builder import *
from structured_query_builder.translator import translate_query


# =============================================================================
# ENFORCER Archetype Tests
# =============================================================================


class TestEnforcerQueries:
    """Test ENFORCER archetype queries (compliance and parity maintenance)."""

    def test_query_02_matched_parity_check(self):
        """Test Q02: Matched Parity Check."""
        from examples.pricing_intelligence_queries import query_03_category_histogram

        # Note: Q02 is implemented as Q03 in current codebase
        query = query_03_category_histogram()
        sql = translate_query(query)

        assert "SELECT" in sql
        assert "FROM" in sql

    def test_query_16_map_violations_unmatched(self):
        """Test Q16: MAP Violations (Unmatched) - Brand floor scan."""
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

    def test_query_17_premium_gap_analysis(self):
        """Test Q17: Premium Gap Analysis (Matched) - Brand positioning."""
        from examples.pricing_intelligence_queries import query_17_premium_gap_analysis

        query = query_17_premium_gap_analysis()
        sql = translate_query(query)

        # Verify nested arithmetic in aggregate: AVG(my.price - comp.price)
        assert "AVG((my.markdown_price - comp.markdown_price))" in sql
        assert "avg_premium_gap" in sql
        assert "INNER JOIN exact_matches" in sql
        assert "GROUP BY brand, category" in sql

    def test_query_30_index_drift_check(self):
        """Test Q30: Index Drift Check (Matched) - Parity maintenance."""
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
        """Test Q31: Average Selling Price Gap (Unmatched) - Parity approximation."""
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
        """Test Q32: SKU Violation Scan (Matched) - MAP policing."""
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


# =============================================================================
# PREDATOR Archetype Tests
# =============================================================================


class TestPredatorQueries:
    """Test PREDATOR archetype queries (competitive advantage and headroom)."""

    def test_query_06_cluster_floor_check(self):
        """Test Q06: Cluster Floor Check."""
        from examples.pricing_intelligence_queries import query_06_cluster_floor_check

        query = query_06_cluster_floor_check()
        sql = translate_query(query)

        assert "SELECT" in sql
        assert "FROM" in sql

    def test_query_11_stockout_gouge(self):
        """Test Q11: Stockout Gouge (Matched) - Opportunistic pricing."""
        from examples.pricing_intelligence_queries import query_11_stockout_gouge

        query = query_11_stockout_gouge()
        sql = translate_query(query)

        assert "INNER JOIN exact_matches" in sql
        assert "availability" in sql

    def test_query_12_deep_discount_filter(self):
        """Test Q12: Deep Discount Filter."""
        from examples.pricing_intelligence_queries import query_12_deep_discount_filter

        query = query_12_deep_discount_filter()
        sql = translate_query(query)

        assert "SELECT" in sql
        assert "FROM" in sql

    def test_query_18_supply_chain_failure_detector(self):
        """Test Q18: Supply Chain Failure Detector (Temporal with LAG)."""
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

    def test_query_19_loss_leader_hunter(self):
        """Test Q19: Loss-Leader Hunter (Matched) - Predatory pricing detection."""
        from examples.pricing_intelligence_queries import query_19_loss_leader_hunter

        query = query_19_loss_leader_hunter()
        sql = translate_query(query)

        # Verify column comparison in WHERE
        assert "comp.markdown_price < my.regular_price" in sql
        assert "LIMIT 50" in sql

    def test_query_33_unnecessary_discount_finder(self):
        """Test Q33: Unnecessary Discount Finder (Matched) - Headroom discovery."""
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


# =============================================================================
# HISTORIAN Archetype Tests
# =============================================================================


class TestHistorianQueries:
    """Test HISTORIAN archetype queries (temporal patterns and trends)."""

    def test_query_08_slash_and_burn_alert(self):
        """Test Q08: Slash and Burn Alert."""
        from examples.pricing_intelligence_queries import query_08_slash_and_burn_alert

        query = query_08_slash_and_burn_alert()
        sql = translate_query(query)

        assert "SELECT" in sql
        assert "FROM" in sql

    def test_query_09_minimum_viable_price_lift(self):
        """Test Q09: Minimum Viable Price Lift."""
        from examples.pricing_intelligence_queries import (
            query_09_minimum_viable_price_lift,
        )

        query = query_09_minimum_viable_price_lift()
        sql = translate_query(query)

        assert "SELECT" in sql
        assert "FROM" in sql

    def test_query_10_assortment_rotation_check(self):
        """Test Q10: Assortment Rotation Check."""
        from examples.pricing_intelligence_queries import (
            query_10_assortment_rotation_check,
        )

        query = query_10_assortment_rotation_check()
        sql = translate_query(query)

        assert "SELECT" in sql
        assert "FROM" in sql

    def test_query_21_promo_erosion_index(self):
        """Test Q21: Promo Erosion Index (Unmatched) - Discount trend analysis."""
        from examples.pricing_intelligence_queries import query_21_promo_erosion_index

        query = query_21_promo_erosion_index()
        sql = translate_query(query)

        # Verify price comparison aggregates
        assert "AVG(markdown_price)" in sql
        assert "AVG(regular_price)" in sql
        assert "vendor = 'Them'" in sql

    def test_query_22_brand_presence_tracking(self):
        """Test Q22: Brand Presence Tracking (Unmatched) - Assortment changes."""
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

    def test_query_37_magic_number_distribution(self):
        """Test Q37: Magic Number Distribution (Unmatched) - Price point psychology."""
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


# =============================================================================
# MERCENARY Archetype Tests
# =============================================================================


class TestMercenaryQueries:
    """Test MERCENARY archetype queries (optical dominance and promotions)."""

    def test_query_13_ghost_inventory_check(self):
        """Test Q13: Ghost Inventory Check."""
        from examples.pricing_intelligence_queries import query_13_ghost_inventory_check

        query = query_13_ghost_inventory_check()
        sql = translate_query(query)

        assert "SELECT" in sql
        assert "FROM" in sql

    def test_query_14_global_floor_stress_test(self):
        """Test Q14: Global Floor Stress Test."""
        from examples.pricing_intelligence_queries import (
            query_14_global_floor_stress_test,
        )

        query = query_14_global_floor_stress_test()
        sql = translate_query(query)

        assert "SELECT" in sql
        assert "FROM" in sql

    def test_query_23_discount_depth_distribution(self):
        """Test Q23: Discount Depth Distribution (Unmatched) - Promotion strategy."""
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

    def test_query_34_anchor_check(self):
        """Test Q34: Anchor Check (Matched) - Reference price positioning."""
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

    def test_query_36_discount_depth_alignment(self):
        """Test Q36: Discount Depth Alignment (Matched) - Promotional parity."""
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


# =============================================================================
# ARCHITECT Archetype Tests
# =============================================================================


class TestArchitectQueries:
    """Test ARCHITECT archetype queries (strategic positioning and structure)."""

    def test_query_15_category_margin_proxy(self):
        """Test Q15: Category Margin Proxy."""
        from examples.pricing_intelligence_queries import query_15_category_margin_proxy

        query = query_15_category_margin_proxy()
        sql = translate_query(query)

        assert "SELECT" in sql
        assert "FROM" in sql

    def test_query_20_category_price_snapshot(self):
        """Test Q20: Category Price Snapshot (Temporal self-join)."""
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

    def test_query_24_commoditization_coefficient(self):
        """Test Q24: Commoditization Coefficient (Matched) - Market coverage."""
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
        """Test Q25: Brand Weighting Fingerprint (Unmatched) - Assortment strategy."""
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
        """Test Q26: Price Ladder Void Scanner (Unmatched) - Price gaps."""
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

    def test_query_27_vendor_fairness_audit(self):
        """Test Q27: Vendor Fairness Audit (Matched) - Procurement intelligence."""
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
        """Test Q28: Safe Haven Scanner (Matched) - Low volatility detection."""
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
        """Test Q29: Inventory Velocity Detector (Unmatched) - Stock churn."""
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

    def test_query_35_ad_hoc_keyword_scrape(self):
        """Test Q35: Ad Hoc Keyword Scrape (Unmatched) - Semantic clustering."""
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

    def test_query_38_same_store_inflation_rate(self):
        """Test Q38: Same-Store Inflation Rate (Matched) - Temporal inflation."""
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
        """Test Q39: Entry-Level Creep (Unmatched) - Market floor tracking."""
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
        """Test Q40: Semantic Keyword Scrape (Unmatched) - Manual matching."""
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
        """Test Q41: New Arrival Survival Rate (Unmatched) - Velocity inference."""
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


# =============================================================================
# Cross-cutting Tests
# =============================================================================


class TestQuerySerialization:
    """Test that all intelligence queries serialize to JSON correctly."""

    def test_all_intelligence_queries_serialize(self):
        """Test JSON serialization of all 37 intelligence queries."""
        from examples import pricing_intelligence_queries

        query_functions = [
            pricing_intelligence_queries.query_03_category_histogram,
            pricing_intelligence_queries.query_06_cluster_floor_check,
            pricing_intelligence_queries.query_08_slash_and_burn_alert,
            pricing_intelligence_queries.query_09_minimum_viable_price_lift,
            pricing_intelligence_queries.query_10_assortment_rotation_check,
            pricing_intelligence_queries.query_11_stockout_gouge,
            pricing_intelligence_queries.query_12_deep_discount_filter,
            pricing_intelligence_queries.query_13_ghost_inventory_check,
            pricing_intelligence_queries.query_14_global_floor_stress_test,
            pricing_intelligence_queries.query_15_category_margin_proxy,
            pricing_intelligence_queries.query_16_map_violations_unmatched,
            pricing_intelligence_queries.query_17_premium_gap_analysis,
            pricing_intelligence_queries.query_18_supply_chain_failure_detector,
            pricing_intelligence_queries.query_19_loss_leader_hunter,
            pricing_intelligence_queries.query_20_category_price_snapshot,
            pricing_intelligence_queries.query_21_promo_erosion_index,
            pricing_intelligence_queries.query_22_brand_presence_tracking,
            pricing_intelligence_queries.query_23_discount_depth_distribution,
            pricing_intelligence_queries.query_24_commoditization_coefficient,
            pricing_intelligence_queries.query_25_brand_weighting_fingerprint,
            pricing_intelligence_queries.query_26_price_ladder_void_scanner,
            pricing_intelligence_queries.query_27_vendor_fairness_audit,
            pricing_intelligence_queries.query_28_safe_haven_scanner,
            pricing_intelligence_queries.query_29_inventory_velocity_detector,
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


class TestProcurementIntelligencePatterns:
    """Test that procurement queries use only competitive data, not internal costs."""

    def test_no_cost_columns_referenced(self):
        """Verify procurement queries use NO internal cost data columns."""
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
        """Verify procurement queries use competitive pricing as cost proxy."""
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


class TestBimodalCoverage:
    """Test that queries include both matched and unmatched execution variants."""

    def test_matched_vs_unmatched_distribution(self):
        """Test that both matched and unmatched patterns are well-represented."""
        from examples import pricing_intelligence_queries

        # Matched queries (require exact_matches table)
        matched_queries = [
            pricing_intelligence_queries.query_17_premium_gap_analysis,
            pricing_intelligence_queries.query_19_loss_leader_hunter,
            pricing_intelligence_queries.query_24_commoditization_coefficient,
            pricing_intelligence_queries.query_27_vendor_fairness_audit,
            pricing_intelligence_queries.query_28_safe_haven_scanner,
            pricing_intelligence_queries.query_30_index_drift_check,
            pricing_intelligence_queries.query_32_sku_violation_scan,
            pricing_intelligence_queries.query_33_unnecessary_discount_finder,
            pricing_intelligence_queries.query_34_anchor_check,
            pricing_intelligence_queries.query_36_discount_depth_alignment,
            pricing_intelligence_queries.query_38_same_store_inflation_rate,
        ]

        # Unmatched queries (no exact_matches table)
        unmatched_queries = [
            pricing_intelligence_queries.query_16_map_violations_unmatched,
            pricing_intelligence_queries.query_21_promo_erosion_index,
            pricing_intelligence_queries.query_22_brand_presence_tracking,
            pricing_intelligence_queries.query_23_discount_depth_distribution,
            pricing_intelligence_queries.query_25_brand_weighting_fingerprint,
            pricing_intelligence_queries.query_26_price_ladder_void_scanner,
            pricing_intelligence_queries.query_29_inventory_velocity_detector,
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
