#!/usr/bin/env python3
"""Quick smoke test to verify all 36 queries work."""

from structured_query_builder.translator import translate_query

# Import all query modules
from examples import phase1_queries, phase2_queries, phase3_queries

def test_all_queries():
    """Test that all 36 queries can be instantiated and translated."""

    # Phase 1 queries (23 queries)
    phase1_functions = [
        phase1_queries.query_03_category_histogram,
        phase1_queries.query_06_cluster_floor_check,
        phase1_queries.query_08_slash_and_burn_alert,
        phase1_queries.query_09_minimum_viable_price_lift,
        phase1_queries.query_10_assortment_rotation_check,
        phase1_queries.query_11_stockout_gouge,
        phase1_queries.query_12_deep_discount_filter,
        phase1_queries.query_13_ghost_inventory_check,
        phase1_queries.query_14_global_floor_stress_test,
        phase1_queries.query_16_map_violations_unmatched,
        phase1_queries.query_17_premium_gap_analysis,
        phase1_queries.query_18_supply_chain_failure_detector,
        phase1_queries.query_19_loss_leader_hunter,
        phase1_queries.query_20_category_price_snapshot,
        phase1_queries.query_21_promo_erosion_index,
        phase1_queries.query_22_brand_presence_tracking,
        phase1_queries.query_23_discount_depth_distribution,
        phase1_queries.query_30_index_drift_check,
        phase1_queries.query_31_average_selling_price_gap,
        phase1_queries.query_32_sku_violation_scan,
        phase1_queries.query_33_unnecessary_discount_finder,
        phase1_queries.query_34_anchor_check,
        phase1_queries.query_35_ad_hoc_keyword_scrape,
    ]

    # Phase 2 queries (6 queries)
    phase2_functions = [
        phase2_queries.query_15_category_margin_proxy,
        phase2_queries.query_24_commoditization_coefficient,
        phase2_queries.query_25_brand_weighting_fingerprint,
        phase2_queries.query_26_price_ladder_void_scanner,
        phase2_queries.query_36_discount_depth_alignment,
        phase2_queries.query_37_magic_number_distribution,
    ]

    # Phase 3 queries (8 queries)
    phase3_functions = [
        phase3_queries.query_27_vendor_fairness_audit,
        phase3_queries.query_28_safe_haven_scanner,
        phase3_queries.query_29_inventory_velocity_detector,
        phase3_queries.query_38_same_store_inflation_rate,
        phase3_queries.query_39_entry_level_creep,
        phase3_queries.query_40_semantic_keyword_scrape,
        phase3_queries.query_41_new_arrival_survival_rate,
    ]

    all_queries = phase1_functions + phase2_functions + phase3_functions

    print(f"Testing {len(all_queries)} queries...")

    failed = []
    for i, query_func in enumerate(all_queries, 1):
        try:
            query = query_func()
            sql = translate_query(query)
            assert "SELECT" in sql
            assert "FROM" in sql
            print(f"✓ {i:2d}. {query_func.__name__}")
        except Exception as e:
            print(f"✗ {i:2d}. {query_func.__name__}: {e}")
            failed.append((query_func.__name__, e))

    print(f"\n{'='*80}")
    if failed:
        print(f"FAILED: {len(failed)}/{len(all_queries)} queries failed")
        for name, error in failed:
            print(f"  - {name}: {error}")
        return False
    else:
        print(f"SUCCESS: All {len(all_queries)} queries passed!")
        return True

if __name__ == "__main__":
    success = test_all_queries()
    exit(0 if success else 1)
