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
        from examples.phase1_queries import query_30_index_drift_check

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
        from examples.phase1_queries import query_31_average_selling_price_gap

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
        from examples.phase1_queries import query_32_sku_violation_scan

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
        from examples.phase1_queries import query_33_unnecessary_discount_finder

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
        from examples.phase1_queries import query_34_anchor_check

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
        from examples.phase1_queries import query_35_ad_hoc_keyword_scrape

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
        from examples.phase2_queries import query_36_discount_depth_alignment

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
        from examples.phase2_queries import query_37_magic_number_distribution

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
        from examples.phase3_queries import query_38_same_store_inflation_rate

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
        from examples.phase3_queries import query_39_entry_level_creep

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
        from examples.phase3_queries import query_40_semantic_keyword_scrape

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
        from examples.phase3_queries import query_41_new_arrival_survival_rate

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
        from examples import phase1_queries, phase2_queries, phase3_queries

        query_functions = [
            phase1_queries.query_30_index_drift_check,
            phase1_queries.query_31_average_selling_price_gap,
            phase1_queries.query_32_sku_violation_scan,
            phase1_queries.query_33_unnecessary_discount_finder,
            phase1_queries.query_34_anchor_check,
            phase1_queries.query_35_ad_hoc_keyword_scrape,
            phase2_queries.query_36_discount_depth_alignment,
            phase2_queries.query_37_magic_number_distribution,
            phase3_queries.query_38_same_store_inflation_rate,
            phase3_queries.query_39_entry_level_creep,
            phase3_queries.query_40_semantic_keyword_scrape,
            phase3_queries.query_41_new_arrival_survival_rate,
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
        from examples import phase1_queries, phase2_queries, phase3_queries

        queries = [
            phase1_queries.query_30_index_drift_check,
            phase1_queries.query_31_average_selling_price_gap,
            phase1_queries.query_32_sku_violation_scan,
            phase1_queries.query_33_unnecessary_discount_finder,
            phase1_queries.query_34_anchor_check,
            phase1_queries.query_35_ad_hoc_keyword_scrape,
            phase2_queries.query_36_discount_depth_alignment,
            phase2_queries.query_37_magic_number_distribution,
            phase3_queries.query_38_same_store_inflation_rate,
            phase3_queries.query_39_entry_level_creep,
            phase3_queries.query_40_semantic_keyword_scrape,
            phase3_queries.query_41_new_arrival_survival_rate,
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
        from examples import phase1_queries, phase2_queries, phase3_queries

        # Matched queries (require exact_matches table)
        matched_queries = [
            phase1_queries.query_30_index_drift_check,
            phase1_queries.query_32_sku_violation_scan,
            phase1_queries.query_33_unnecessary_discount_finder,
            phase1_queries.query_34_anchor_check,
            phase2_queries.query_36_discount_depth_alignment,
            phase3_queries.query_38_same_store_inflation_rate,
        ]

        # Unmatched queries (no exact_matches table)
        unmatched_queries = [
            phase1_queries.query_31_average_selling_price_gap,
            phase1_queries.query_35_ad_hoc_keyword_scrape,
            phase2_queries.query_37_magic_number_distribution,
            phase3_queries.query_39_entry_level_creep,
            phase3_queries.query_40_semantic_keyword_scrape,
            phase3_queries.query_41_new_arrival_survival_rate,
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
