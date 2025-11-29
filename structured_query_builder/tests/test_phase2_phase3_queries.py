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
        from examples.phase2_queries import query_24_commoditization_coefficient

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
        from examples.phase2_queries import query_25_brand_weighting_fingerprint

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
        from examples.phase2_queries import query_26_price_ladder_void_scanner

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
        from examples.phase3_queries import query_27_vendor_fairness_audit

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
        """Test Q28: Safe Haven Scanner (Matched)."""
        from examples.phase3_queries import query_28_safe_haven_scanner

        query = query_28_safe_haven_scanner()
        sql = translate_query(query)

        # Verify matched execution
        assert "INNER JOIN exact_matches" in sql

        # Verify multi-table aggregates for gap analysis
        assert "AVG(my.markdown_price)" in sql
        assert "AVG(comp.markdown_price)" in sql

        # Verify volatility metric (price stability)
        assert "STDDEV(comp.markdown_price)" in sql

        # Verify product counting
        assert "COUNT(*)" in sql

        # Verify grouping by category and brand
        assert "GROUP BY category, brand" in sql

    def test_query_29_inventory_velocity_detector(self):
        """Test Q29: Inventory Velocity Detector (Matched)."""
        from examples.phase3_queries import query_29_inventory_velocity_detector

        query = query_29_inventory_velocity_detector()
        sql = translate_query(query)

        # Verify matched execution
        assert "INNER JOIN exact_matches" in sql
        assert "INNER JOIN product_offers AS comp" in sql

        # Verify availability tracking columns
        assert "my.availability" in sql
        assert "comp.availability" in sql

        # Verify competitive pricing context
        assert "comp.markdown_price" in sql

        # Verify vendor filter
        assert "vendor = 'Us'" in sql

        # Verify ordering by category and brand
        assert "ORDER BY category ASC, brand ASC" in sql

        # Verify limit for top velocity products
        assert "LIMIT 200" in sql


class TestPhase2Phase3Serialization:
    """Test that all Phase 2 and Phase 3 queries serialize correctly."""

    def test_all_phase2_queries_serialize(self):
        """Test JSON serialization of all Phase 2 queries."""
        from examples import phase2_queries

        query_functions = [
            phase2_queries.query_24_commoditization_coefficient,
            phase2_queries.query_25_brand_weighting_fingerprint,
            phase2_queries.query_26_price_ladder_void_scanner,
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
        from examples import phase3_queries

        query_functions = [
            phase3_queries.query_27_vendor_fairness_audit,
            phase3_queries.query_28_safe_haven_scanner,
            phase3_queries.query_29_inventory_velocity_detector,
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
        from examples import phase2_queries, phase3_queries

        architect_queries = [
            # Phase 2: Range Architecture (3 queries)
            phase2_queries.query_24_commoditization_coefficient,
            phase2_queries.query_25_brand_weighting_fingerprint,
            phase2_queries.query_26_price_ladder_void_scanner,
            # Phase 3: Procurement Intelligence (3 queries)
            phase3_queries.query_27_vendor_fairness_audit,
            phase3_queries.query_28_safe_haven_scanner,
            phase3_queries.query_29_inventory_velocity_detector,
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
        from examples import phase2_queries, phase3_queries

        # Matched queries (require exact_matches table)
        matched_queries = [
            phase2_queries.query_24_commoditization_coefficient,  # LEFT JOIN for coefficient
            phase3_queries.query_27_vendor_fairness_audit,
            phase3_queries.query_28_safe_haven_scanner,
            phase3_queries.query_29_inventory_velocity_detector,
        ]

        # Unmatched queries (no exact_matches table)
        unmatched_queries = [
            phase2_queries.query_25_brand_weighting_fingerprint,
            phase2_queries.query_26_price_ladder_void_scanner,
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
        from examples import phase3_queries

        procurement_queries = [
            phase3_queries.query_27_vendor_fairness_audit,
            phase3_queries.query_28_safe_haven_scanner,
            phase3_queries.query_29_inventory_velocity_detector,
        ]

        # These column names should NEVER appear (system is air-gapped from cost data)
        forbidden_columns = ["cost", "wholesale", "cogs", "margin"]

        for query_func in procurement_queries:
            query = query_func()
            sql = translate_query(query).lower()

            for forbidden in forbidden_columns:
                assert forbidden not in sql, \
                    f"Query {query_func.__name__} uses forbidden column '{forbidden}'"

    def test_competitive_pricing_proxies_used(self):
        """Verify Phase 3 uses competitive pricing as cost proxy."""
        from examples import phase3_queries

        # Q27: Uses regular_price as cost proxy
        query = phase3_queries.query_27_vendor_fairness_audit()
        sql = translate_query(query)
        assert "regular_price" in sql
        assert "comp.regular_price < my.regular_price" in sql

        # Q28: Uses markdown_price for gap analysis
        query = phase3_queries.query_28_safe_haven_scanner()
        sql = translate_query(query)
        assert "AVG(my.markdown_price)" in sql
        assert "AVG(comp.markdown_price)" in sql

        # Q29: Uses availability as velocity proxy
        query = phase3_queries.query_29_inventory_velocity_detector()
        sql = translate_query(query)
        assert "availability" in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
