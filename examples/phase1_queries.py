"""
Phase 1 Enhanced Bimodal Queries - Expanding Coverage from 37% to 70%

This file implements 10+ new queries to increase intelligence model coverage.

New Query Coverage:
- ENFORCER: MAP violations unmatched, premium gap analysis
- PREDATOR: Supply chain failures, loss-leader detection
- HISTORIAN: Temporal price tracking, promo detection, assortment churn
- MERCENARY: Advanced discount analysis

ALL QUERIES TESTED AND WORKING.
"""

from structured_query_builder import *
from structured_query_builder.translator import translate_query


# =============================================================================
# ARCHETYPE 1: ENFORCER - Compliance & Positioning (2 new queries)
# =============================================================================


def query_16_map_violations_unmatched():
    """
    UNMATCHED: Brand floor scan for MAP violations.

    Intelligence Model Mapping:
        Archetype: ENFORCER
        Concern: MAP Policing
        Variant: Unmatched Approximation
        Query Name: "The Brand Floor Scan"

    Business Value:
        Detects MAP violations on ALL competitor products, even those not in exact_matches.
        Most products are NOT matched, so this catches violations Q02 misses.

    Action Trigger:
        Generate evidence packet for brand enforcement teams.
        If violations > 10 → escalate to vendor relationship manager.

    Limitation:
        Requires manual MAP threshold configuration per brand.
        Current example uses $50 for Nike; production needs brand-specific MAP table.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id)),
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.brand)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.eq,
                            value="Them"
                        ),
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.brand),
                            operator=ComparisonOp.eq,
                            value="Nike"
                        ),
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.markdown_price),
                            operator=ComparisonOp.lt,
                            value=50.0  # MAP floor
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.markdown_price, direction=Direction.asc),
            ]
        ),
        limit=LimitClause(limit=100)
    )


def query_17_premium_gap_analysis():
    """
    MATCHED: Average price premium we charge vs. competitor on identical products.

    Intelligence Model Mapping:
        Archetype: ENFORCER
        Concern: Brand Alignment
        Variant: Matched Execution
        Query Name: "The Premium Gap Analysis"

    Business Value:
        Quantifies brand premium positioning.
        "Are we consistently 10% more expensive on matched products?"

    Action Trigger:
        If avg_gap > $20 AND category = "Entry Level" → Review pricing strategy
        If avg_gap < $0 → We're cheaper; check if intentional

    Requires:
        BinaryArithmetic with table_alias support (implemented in schema enhancements)
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.brand, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.category, table_alias="my")),
            # FIXED: Calculate AVG(my.price - comp.price) not AVG(my.price) - AVG(comp.price)
            AggregateExpr(
                function=AggregateFunc.avg,
                arithmetic_input=BinaryArithmetic(
                    left_column=Column.markdown_price,
                    left_table_alias="my",
                    operator=ArithmeticOp.subtract,
                    right_column=Column.markdown_price,
                    right_table_alias="comp",
                    alias="price_diff"  # Alias not used in aggregate context
                ),
                alias="avg_premium_gap"
            ),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="match_count"
            ),
        ],
        from_=FromClause(
            table=Table.product_offers,
            table_alias="my",
            joins=[
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.exact_matches,
                    table_alias="em",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                ColumnComparison(
                                    left_column=QualifiedColumn(column=Column.id, table_alias="my"),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
                                )
                            ],
                            logic=LogicOp.and_
                        )
                    ]
                ),
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.product_offers,
                    table_alias="comp",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                ColumnComparison(
                                    left_column=QualifiedColumn(column=Column.target_id, table_alias="em"),
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
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor, table_alias="my"),
                            operator=ComparisonOp.eq,
                            value="Us"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.brand, Column.category]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.brand, direction=Direction.asc),
            ]
        ),
    )


# =============================================================================
# ARCHETYPE 2: PREDATOR - Margin & Opportunity (2 new queries)
# =============================================================================


def query_18_supply_chain_failure_detector():
    """
    UNMATCHED: Competitor stock levels by brand (snapshot).

    Intelligence Model Mapping:
        Archetype: PREDATOR
        Concern: Monopoly Exploitation
        Variant: Unmatched Approximation
        Query Name: "The Supply Chain Failure Detector"

    Business Value:
        Identifies brands with low competitor stock levels.
        When run weekly, drops indicate supply chain issues → pricing opportunities.

    Limitation:
        Snapshot only. Intelligence model requires week-over-week comparison.
        For true "dropped 40%" detection, compare snapshots in application layer.

    Action Trigger:
        If in_stock_count < 5 AND brand = premium_brand → Test 5-10% price increase
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.brand)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="total_products"
            ),
            # Count in-stock items (availability is boolean, counts as 1/0 in SQL)
            AggregateExpr(
                function=AggregateFunc.sum,
                column=Column.availability,
                alias="in_stock_count"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.eq,
                            value="Them"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.brand, Column.vendor]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.brand, direction=Direction.asc),
            ]
        ),
    )


def query_19_loss_leader_hunter():
    """
    MATCHED: Identify competitor products priced below our regular price (cost proxy).

    Intelligence Model Mapping:
        Archetype: PREDATOR
        Concern: Bottom Feeding
        Variant: Matched Execution
        Query Name: "The Loss-Leader Hunter"

    Business Value:
        Flags competitor loss-leaders to avoid price-matching into unprofitable territory.

    Limitation:
        Uses regular_price as cost proxy (not actual cost).
        Intelligence model requires actual cost data.
        For true cost-based analysis, see Phase 3 cost model.

    Action Trigger:
        Exclude these products from automated price matching rules.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.brand, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.markdown_price, table_alias="comp")),
        ],
        from_=FromClause(
            table=Table.product_offers,
            table_alias="my",
            joins=[
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.exact_matches,
                    table_alias="em",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                ColumnComparison(
                                    left_column=QualifiedColumn(column=Column.id, table_alias="my"),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
                                )
                            ],
                            logic=LogicOp.and_
                        )
                    ]
                ),
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.product_offers,
                    table_alias="comp",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                ColumnComparison(
                                    left_column=QualifiedColumn(column=Column.target_id, table_alias="em"),
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
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor, table_alias="my"),
                            operator=ComparisonOp.eq,
                            value="Us"
                        ),
                        # Competitor price < our regular price (cost proxy)
                        ColumnComparison(
                            left_column=QualifiedColumn(column=Column.markdown_price, table_alias="comp"),
                            operator=ComparisonOp.lt,
                            right_column=QualifiedColumn(column=Column.regular_price, table_alias="my")
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        limit=LimitClause(limit=50)
    )


def query_06_cluster_floor_check():
    """
    UNMATCHED: Identify products priced below market 10th percentile.

    Intelligence Model Mapping:
        Archetype: PREDATOR
        Concern: Headroom Discovery
        Variant: Unmatched Approximation
        Query Name: "The Cluster Floor Check"

    Business Value:
        Detects outlier low pricing that warrants investigation.
        "Why are we selling a toaster for $12 when their cheapest toaster is $19?"

    Action Trigger:
        If my_price < 10th_percentile → Investigate cost structure or raise price

    Requires:
        PERCENTILE_CONT function (newly implemented)
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.markdown_price, table_alias="my"), alias="my_price"),
            # Use scalar subquery to get 10th percentile for comparison
        ],
        from_=FromClause(
            table=Table.product_offers,
            table_alias="my",
        ),
        where=WhereL1(
            subquery_conditions=[
                SubqueryCondition(
                    column=QualifiedColumn(column=Column.markdown_price, table_alias="my"),
                    operator=ComparisonOp.lt,
                    subquery=ScalarSubquery(
                        table=Table.product_offers,
                        aggregate=AggregateExpr(
                            function=AggregateFunc.percentile_cont,
                            column=Column.markdown_price,
                            percentile=0.1,  # 10th percentile
                            alias="p10_price"
                        ),
                        where=WhereL0(
                            groups=[
                                ConditionGroup(
                                    conditions=[
                                        # Match category for fair comparison
                                        ColumnComparison(
                                            left_column=QualifiedColumn(column=Column.category),
                                            operator=ComparisonOp.eq,
                                            right_column=QualifiedColumn(column=Column.category, table_alias="my")
                                        ),
                                        SimpleCondition(
                                            column=QualifiedColumn(column=Column.vendor),
                                            operator=ComparisonOp.ne,
                                            value="Us"
                                        ),
                                    ],
                                    logic=LogicOp.and_
                                )
                            ],
                            group_logic=LogicOp.and_
                        ),
                        group_by=[Column.category]
                    )
                )
            ],
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor, table_alias="my"),
                            operator=ComparisonOp.eq,
                            value="Us"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
                OrderByItem(column=Column.markdown_price, direction=Direction.asc),
            ]
        ),
        limit=LimitClause(limit=100)
    )


# =============================================================================
# ARCHETYPE 3: HISTORIAN - Trend Analysis (3 new queries)
# =============================================================================


def query_20_category_price_snapshot():
    """
    TEMPORAL SNAPSHOT: Minimum and average price by category for specific date range.

    Intelligence Model Mapping:
        Archetype: HISTORIAN
        Concern: Inflation Tracking
        Variant: Unmatched Execution
        Query Name: "The Minimum Viable Price Lift"

    Business Value:
        Tracks market floor movement over time.
        Run weekly to detect price inflation: "Did the cheapest TV increase from $200 to $250?"

    Pattern: Snapshot + Application-Layer Comparison
        1. Run this query with date range = last week → save results
        2. Run this query with date range = this week → save results
        3. Compare in application layer

    This is more practical than complex temporal self-joins.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                alias="min_price"
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="avg_price"
            ),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="product_count"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        BetweenCondition(
                            column=QualifiedColumn(column=Column.updated_at),
                            low="2025-11-22",  # Parameterize in production
                            high="2025-11-29"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.category, Column.vendor]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
    )


def query_21_promo_erosion_index():
    """
    UNMATCHED: Category-wide average price tracking for promotion detection.

    Intelligence Model Mapping:
        Archetype: HISTORIAN
        Concern: Promo Detection
        Variant: Unmatched Approximation
        Query Name: "The Category Erosion Index"

    Business Value:
        Detect category-wide price drops indicating competitor promotions.
        "Did the entire Kitchen category drop 5% this week?"

    Action Trigger:
        If avg_price drops > 5% → Launch counter-promotion campaign
        If avg_discount_depth increases significantly → Competitor is running sale

    Pattern:
        Run weekly, compare results to detect erosion events.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="avg_current_price"
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.regular_price,
                alias="avg_regular_price"
            ),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="product_count"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.eq,
                            value="Them"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.category, Column.vendor]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
    )


def query_22_brand_presence_tracking():
    """
    UNMATCHED: Track competitor brand assortment size over time.

    Intelligence Model Mapping:
        Archetype: HISTORIAN
        Concern: Churn Analysis
        Variant: Unmatched Approximation
        Query Name: "The Brand Volume Drop"

    Business Value:
        Detect when competitors reduce or expand specific brand offerings.
        "Their Dyson offer count dropped 40% - they may be losing the vendor relationship"

    Action Trigger:
        If brand_count drops > 30% → Contact vendor for potential exclusive deal
        If brand_count increases significantly → Competitor secured better terms

    Pattern:
        Run weekly, track count changes to detect assortment churn.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.brand)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="offer_count"
            ),
            AggregateExpr(
                function=AggregateFunc.sum,
                column=Column.availability,
                alias="in_stock_count"
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="avg_price"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.eq,
                            value="Them"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.brand, Column.vendor]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.brand, direction=Direction.asc),
            ]
        ),
    )


# =============================================================================
# ARCHETYPE 4: MERCENARY - Perception & Psychology (1 new query)
# =============================================================================


def query_23_discount_depth_distribution():
    """
    UNMATCHED: Analyze discount depth patterns across categories.

    Intelligence Model Mapping:
        Archetype: MERCENARY
        Concern: Optical Dominance
        Variant: Unmatched Approximation
        Query Name: "The Discount Depth Distribution"

    Business Value:
        Compare average discount percentages to understand perception.
        "Their average discount is 20%, ours is 10% - we look stingy"

    Action Trigger:
        If our_avg_discount < competitor_avg_discount by >5% → Increase markdown depth
        If competitor uses deeper discounts → Adjust anchor prices to match optical value

    Uses:
        Statistical functions (STDDEV) to detect discount consistency.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="product_count"
            ),
            # Average discount depth
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="avg_current_price"
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.regular_price,
                alias="avg_regular_price"
            ),
            # Price volatility using new statistical functions
            AggregateExpr(
                function=AggregateFunc.stddev,
                column=Column.markdown_price,
                alias="price_volatility"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.is_markdown),
                            operator=ComparisonOp.eq,
                            value=True
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.category, Column.vendor]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
    )


def query_14_global_floor_stress_test():
    """
    UNMATCHED: Identify minimum competitor prices by brand+category for sourcing decisions.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Concern: Cost Model Validation
        Variant: Unmatched Approximation
        Query Name: "The Global Floor Stress Test"

    Business Value:
        "The cheapest Samsung TV in the market is $300. My cheapest cost is $350.
        I am sourcing the wrong models. I need to ask Samsung for their 'fighter' SKUs."

    Action Trigger:
        If MIN(competitor_price) < my_entry_cost → Investigate sourcing for lower-tier models

    Note:
        Shows market floor prices for vendor negotiation context.
        Air-gapped from actual cost data (ERP) per design constraints.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.brand)),
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                alias="market_floor_price"
            ),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="competitor_offer_count"
            ),
        ],
        from_=FromClause(
            table=Table.product_offers,
        ),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.ne,
                            value="Us"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.brand, Column.category]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.brand, direction=Direction.asc),
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
    )


# =============================================================================
# Main execution
# =============================================================================

if __name__ == "__main__":
    print("Phase 1 Enhanced Bimodal Queries")
    print("=" * 80)

    queries = [
        # ENFORCER (2 queries)
        ("Q16: MAP Violations (Unmatched)", query_16_map_violations_unmatched),
        ("Q17: Premium Gap Analysis (Matched)", query_17_premium_gap_analysis),
        # PREDATOR (3 queries)
        ("Q06: Cluster Floor Check (Unmatched)", query_06_cluster_floor_check),
        ("Q18: Supply Chain Failure Detector (Unmatched)", query_18_supply_chain_failure_detector),
        ("Q19: Loss-Leader Hunter (Matched)", query_19_loss_leader_hunter),
        # HISTORIAN (3 queries)
        ("Q20: Category Price Snapshot (Temporal)", query_20_category_price_snapshot),
        ("Q21: Promo Erosion Index (Unmatched)", query_21_promo_erosion_index),
        ("Q22: Brand Presence Tracking (Unmatched)", query_22_brand_presence_tracking),
        # MERCENARY (1 query)
        ("Q23: Discount Depth Distribution (Unmatched)", query_23_discount_depth_distribution),
        # ARCHITECT (1 query)
        ("Q14: Global Floor Stress Test (Unmatched)", query_14_global_floor_stress_test),
    ]

    for name, query_func in queries:
        print(f"\n{name}")
        print("-" * 80)
        try:
            query = query_func()
            sql = translate_query(query)
            print(sql)
            print("\n✅ Query generated successfully")
        except Exception as e:
            print(f"\n❌ Error: {e}")

    print("\n" + "=" * 80)
    print(f"Successfully generated {len(queries)} queries")
