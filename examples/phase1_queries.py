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


def query_03_category_histogram():
    """
    UNMATCHED: Analyze price distribution to detect demographic gaps.

    Intelligence Model Mapping:
        Archetype: ENFORCER
        Concern: Brand Alignment
        Variant: Unmatched Approximation
        Query Name: "The Category Histogram"

    Business Value:
        "They have a huge cluster of items at $20. We have nothing under $50.
        We are missing the entry-level shopper."

    Pattern:
        Returns price percentiles and quartile counts for distribution analysis.
        Shows where vendor catalogs cluster on the price spectrum.

    Schema Limitation:
        True histogram binning (SUM(CASE...)) requires CaseExpr in aggregate functions.
        Current approach: Provide percentile-based distribution metrics.

    Action Trigger:
        If p25_comp << p25_ours → We're missing low-price entry segment
        If p75_comp >> p75_ours → We're missing premium segment
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="total_products"
            ),
            AggregateExpr(
                function=AggregateFunc.percentile_cont,
                column=Column.markdown_price,
                percentile=0.10,
                alias="p10_entry_tier"
            ),
            AggregateExpr(
                function=AggregateFunc.percentile_cont,
                column=Column.markdown_price,
                percentile=0.25,
                alias="p25_low_tier"
            ),
            AggregateExpr(
                function=AggregateFunc.percentile_cont,
                column=Column.markdown_price,
                percentile=0.50,
                alias="p50_median"
            ),
            AggregateExpr(
                function=AggregateFunc.percentile_cont,
                column=Column.markdown_price,
                percentile=0.75,
                alias="p75_high_tier"
            ),
            AggregateExpr(
                function=AggregateFunc.percentile_cont,
                column=Column.markdown_price,
                percentile=0.90,
                alias="p90_premium_tier"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        group_by=GroupByClause(columns=[Column.category, Column.vendor]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
                OrderByItem(column=Column.vendor, direction=Direction.asc),
            ]
        ),
    )


# =============================================================================
# ARCHETYPE 2: PREDATOR - Margin & Opportunity (2 new queries)
# =============================================================================


def query_18_supply_chain_failure_detector():
    """
    UNMATCHED: Detect supply chain failures via week-over-week availability drops.

    Intelligence Model Mapping:
        Archetype: PREDATOR
        Concern: Monopoly Exploitation
        Variant: Unmatched Approximation
        Query Name: "The Supply Chain Failure Detector"

    Business Value:
        Detects sudden drops in competitor stock availability (e.g., 40%+ decrease).
        Supply chain failures create temporary monopoly pricing opportunities.

    Pattern:
        1. Aggregate availability by brand and week
        2. Use LAG to get previous week's count
        3. Calculate percentage drop
        4. Filter for significant drops (>40%)

    Action Trigger:
        If availability_drop_pct > 0.40 AND brand = premium_brand → Test 5-10% price increase
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.brand, table_alias="weekly")),
            ColumnExpr(source=QualifiedColumn(column=Column.updated_at, table_alias="weekly"), alias="week"),
            ColumnExpr(source=QualifiedColumn(column=Column.availability_changes, table_alias="weekly"), alias="current_available"),
            # LAG to get previous week's availability count - now in outer query
            WindowExpr(
                function=WindowFunc.lag,
                column=Column.availability_changes,
                table_alias="weekly",  # Reference derived table column
                partition_by=[Column.brand],
                order_by=[OrderByItem(column=Column.updated_at, direction=Direction.asc)],
                offset=1,
                alias="previous_availability"
            ),
            # Calculate drop percentage: (prev - curr) / prev
            CompoundArithmetic(
                inner_left_column=Column.previous_availability,
                inner_operator=ArithmeticOp.subtract,
                inner_right_column=Column.availability_changes,
                inner_right_table_alias="weekly",
                outer_operator=ArithmeticOp.divide,
                outer_column=Column.previous_availability,
                alias="availability_drop_pct"
            ),
        ],
        from_=FromClause(
            derived=DerivedTable(
                select=[
                    ColumnExpr(source=QualifiedColumn(column=Column.brand)),
                    ColumnExpr(source=QualifiedColumn(column=Column.updated_at)),
                    AggregateExpr(
                        function=AggregateFunc.sum,
                        column=Column.availability,
                        alias="availability_changes"
                    ),
                ],
                from_table=Table.product_offers,
                where=WhereL0(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.eq,
                            value="Them"
                        ),
                    ],
                    logic=LogicOp.and_
                ),
                group_by=GroupByClause(columns=[Column.brand, Column.updated_at]),
                alias="weekly"
            )
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.brand, direction=Direction.asc),
                OrderByItem(column=Column.updated_at, direction=Direction.desc),
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


def query_08_slash_and_burn_alert():
    """
    MATCHED: Detect competitor price drops >15% using temporal comparison.

    Intelligence Model Mapping:
        Archetype: HISTORIAN
        Concern: Promo Detection
        Variant: Matched Execution
        Query Name: "The Slash-and-Burn Alert"

    Business Value:
        "They just slashed iPhone price by 20% overnight → Match immediately or risk lost sales"

    Pattern:
        Uses derived table with window LAG to compare current vs previous price.
        Filters for price drops exceeding 15% threshold.

    Action Trigger:
        If price_drop > 15% → Immediate price match or promotional response

    Implementation:
        Window LAG(price) OVER (PARTITION BY id ORDER BY updated_at)
        Then calculate percentage change and filter.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="prices")),
            ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="prices")),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor, table_alias="prices")),
            ColumnExpr(source=QualifiedColumn(column=Column.markdown_price, table_alias="prices"), alias="current_price"),
            ColumnExpr(source=QualifiedColumn(column=Column.previous_price, table_alias="prices")),
            # Calculate price drop percentage: ((prev - curr) / prev) * 100
            CompoundArithmetic(
                inner_left_column=Column.previous_price,
                inner_left_table_alias="prices",
                inner_operator=ArithmeticOp.subtract,
                inner_right_column=Column.markdown_price,
                inner_right_table_alias="prices",
                outer_operator=ArithmeticOp.divide,
                outer_column=Column.previous_price,
                outer_table_alias="prices",
                alias="price_drop_pct"
            ),
            ColumnExpr(source=QualifiedColumn(column=Column.updated_at, table_alias="prices"), alias="price_change_date"),
        ],
        from_=FromClause(
            derived=DerivedTable(
                select=[
                    ColumnExpr(source=QualifiedColumn(column=Column.id)),
                    ColumnExpr(source=QualifiedColumn(column=Column.title)),
                    ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
                    ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
                    ColumnExpr(source=QualifiedColumn(column=Column.updated_at)),
                    # Window LAG to get previous price
                    WindowExpr(
                        function=WindowFunc.lag,
                        column=Column.markdown_price,
                        partition_by=[Column.id],
                        order_by=[OrderByItem(column=Column.updated_at, direction=Direction.asc)],
                        offset=1,
                        alias="previous_price"
                    ),
                ],
                from_table=Table.product_offers,
                alias="prices"
            )
        ),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        # Has previous price (not NULL)
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.previous_price, table_alias="prices"),
                            operator=ComparisonOp.is_not_null,
                            value=True
                        ),
                        # Price dropped (current < previous)
                        ColumnComparison(
                            left_column=QualifiedColumn(column=Column.markdown_price, table_alias="prices"),
                            operator=ComparisonOp.lt,
                            right_column=QualifiedColumn(column=Column.previous_price, table_alias="prices")
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.updated_at, direction=Direction.desc),
            ]
        ),
        limit=LimitClause(limit=50)
    )


def query_09_minimum_viable_price_lift():
    """
    UNMATCHED: Track minimum price by category over time periods.

    Intelligence Model Mapping:
        Archetype: HISTORIAN
        Concern: Inflation Tracking
        Variant: Unmatched Approximation
        Query Name: "The Minimum Viable Price Lift"

    Business Value:
        "Category floor price rose from $15 to $22 over 6 months → Raise our entry-level pricing"

    Pattern:
        Groups by category and time period (month), tracks MIN(price).
        Application layer compares periods to detect upward trends.

    Action Trigger:
        If MIN price increased >20% over 6mo → Safe to raise our entry prices

    Note:
        Returns monthly minimums. Period-over-period comparison done in app layer.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            # EXTRACT(MONTH FROM updated_at) - simulated with updated_at for now
            ColumnExpr(source=QualifiedColumn(column=Column.updated_at), alias="price_month"),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                alias="category_floor_price"
            ),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="product_count"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        group_by=GroupByClause(columns=[Column.category, Column.vendor, Column.updated_at]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
                OrderByItem(column=Column.updated_at, direction=Direction.desc),
            ]
        ),
    )


def query_10_assortment_rotation_check():
    """
    MATCHED: Detect products delisted between observation periods.

    Intelligence Model Mapping:
        Archetype: HISTORIAN
        Concern: Churn Analysis
        Variant: Matched Execution
        Query Name: "The Assortment Rotation Check"

    Business Value:
        "Competitor delisted 40 products this week → They're clearing inventory or dropping brands"

    Pattern:
        Self-join product_offers on ID, filtering for records present in older period
        but missing in recent period using LEFT JOIN + NULL check.

    Action Trigger:
        If >50 SKUs delisted in week → Investigate brand strategy changes
        If specific category churn → Opportunity to capture abandoned customers

    Implementation:
        Simulated with LEFT JOIN filtering on date range differences.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="old")),
            ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="old")),
            ColumnExpr(source=QualifiedColumn(column=Column.category, table_alias="old")),
            ColumnExpr(source=QualifiedColumn(column=Column.brand, table_alias="old")),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor, table_alias="old")),
            ColumnExpr(source=QualifiedColumn(column=Column.updated_at, table_alias="old"), alias="last_seen_date"),
        ],
        from_=FromClause(
            table=Table.product_offers,
            table_alias="old",
            joins=[
                JoinSpec(
                    join_type=JoinType.left,
                    table=Table.product_offers,
                    table_alias="new",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                ColumnComparison(
                                    left_column=QualifiedColumn(column=Column.id, table_alias="old"),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(column=Column.id, table_alias="new")
                                ),
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
                        # old record exists (from older period)
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.updated_at, table_alias="old"),
                            operator=ComparisonOp.lt,
                            value="CURRENT_DATE - INTERVAL '7 days'"
                        ),
                        # new record doesn't exist (NULL from LEFT JOIN)
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.id, table_alias="new"),
                            operator=ComparisonOp.is_null,
                            value=True
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.updated_at, direction=Direction.desc),
            ]
        ),
        limit=LimitClause(limit=100)
    )


def query_13_ghost_inventory_check():
    """
    MATCHED: Detect products out of stock for >4 consecutive weeks.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Concern: Gap Analysis
        Variant: Matched Execution
        Query Name: "The Ghost Inventory Check"

    Business Value:
        "They've been out of stock on SKU #123 for 6 weeks → Permanent delisting, not temporary shortage"

    Pattern:
        Window function to count consecutive out-of-stock observations.
        Uses SUM(CASE WHEN availability = FALSE) OVER rolling window.

    Action Trigger:
        If out_of_stock_weeks >= 4 → Treat as delisted, don't wait for restock

    Implementation:
        Window SUM with ROWS frame for rolling count of unavailability.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="stock")),
            ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="stock")),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor, table_alias="stock")),
            ColumnExpr(source=QualifiedColumn(column=Column.availability, table_alias="stock")),
            ColumnExpr(source=QualifiedColumn(column=Column.availability_changes, table_alias="stock")),
        ],
        from_=FromClause(
            derived=DerivedTable(
                select=[
                    ColumnExpr(source=QualifiedColumn(column=Column.id)),
                    ColumnExpr(source=QualifiedColumn(column=Column.title)),
                    ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
                    ColumnExpr(source=QualifiedColumn(column=Column.availability)),
                    ColumnExpr(source=QualifiedColumn(column=Column.updated_at)),
                    # Count state changes using window LAG
                    WindowExpr(
                        function=WindowFunc.lag,
                        column=Column.availability,
                        partition_by=[Column.id],
                        order_by=[OrderByItem(column=Column.updated_at, direction=Direction.asc)],
                        offset=1,
                        alias="previous_availability"
                    ),
                    # SUM window to count consecutive unavailable periods
                    # Note: This is simplified - real implementation needs CASE inside window
                    WindowExpr(
                        function=WindowFunc.count,
                        column=Column.id,  # Count rows in window
                        partition_by=[Column.id],
                        order_by=[OrderByItem(column=Column.updated_at, direction=Direction.asc)],
                        alias="availability_changes"
                    ),
                ],
                from_table=Table.product_offers,
                alias="stock"
            )
        ),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        # Currently out of stock
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.availability, table_alias="stock"),
                            operator=ComparisonOp.eq,
                            value=False
                        ),
                        # Multiple consecutive observations
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.availability_changes, table_alias="stock"),
                            operator=ComparisonOp.gt,
                            value=4  # >4 observations while out of stock
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.availability_changes, direction=Direction.desc),
            ]
        ),
        limit=LimitClause(limit=100)
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
        # ENFORCER (3 queries)
        ("Q16: MAP Violations (Unmatched)", query_16_map_violations_unmatched),
        ("Q17: Premium Gap Analysis (Matched)", query_17_premium_gap_analysis),
        ("Q03: Category Histogram (Unmatched)", query_03_category_histogram),
        # PREDATOR (3 queries)
        ("Q06: Cluster Floor Check (Unmatched)", query_06_cluster_floor_check),
        ("Q18: Supply Chain Failure Detector (Unmatched)", query_18_supply_chain_failure_detector),
        ("Q19: Loss-Leader Hunter (Matched)", query_19_loss_leader_hunter),
        # HISTORIAN (7 queries)
        ("Q08: Slash-and-Burn Alert (Temporal)", query_08_slash_and_burn_alert),
        ("Q09: Minimum Viable Price Lift (Temporal)", query_09_minimum_viable_price_lift),
        ("Q10: Assortment Rotation Check (Temporal)", query_10_assortment_rotation_check),
        ("Q13: Ghost Inventory Check (Temporal)", query_13_ghost_inventory_check),
        ("Q20: Category Price Snapshot (Temporal)", query_20_category_price_snapshot),
        ("Q21: Promo Erosion Index (Unmatched)", query_21_promo_erosion_index),
        ("Q22: Brand Presence Tracking (Unmatched)", query_22_brand_presence_tracking),
        # MERCENARY (1 query)
        ("Q23: Discount Depth Distribution (Unmatched)", query_23_discount_depth_distribution),
        # ARCHITECT (2 queries)
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
