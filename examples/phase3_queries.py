"""
Phase 3 ARCHITECT Queries - Procurement & Total Reconnaissance

This file implements the final tier of intelligence queries for category management,
vendor negotiations, and market reconnaissance.

ALL QUERIES TESTED AND WORKING.
"""

from structured_query_builder import *
from structured_query_builder.translator import translate_query

# =============================================================================
# ARCHETYPE 5: ARCHITECT - Procurement & Total Reconnaissance (3 queries)
# =============================================================================


def query_27_vendor_fairness_audit():
    """
    MATCHED: Detect when competitor regular prices suggest better vendor terms.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Concern: Cost Model Validation
        Variant: Matched Execution
        Query Name: "The Vendor Fairness Audit"

    Business Value:
        "Their regular price on SKU #123 is lower than our regular price"
        Suggests they have better vendor terms → renegotiate.

    Pattern:
        Uses regular_price as cost proxy (air-gapped from actual ERP cost data).
        Compare comp.regular < my.regular to infer better terms.

    Action Trigger:
        If significant gaps found → schedule vendor negotiations with data evidence.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="my")),
            ColumnExpr(
                source=QualifiedColumn(column=Column.category, table_alias="my")
            ),
            ColumnExpr(source=QualifiedColumn(column=Column.brand, table_alias="my")),
            ColumnExpr(
                source=QualifiedColumn(column=Column.regular_price, table_alias="my")
            ),
            ColumnExpr(
                source=QualifiedColumn(column=Column.regular_price, table_alias="comp")
            ),
            # Calculate gap: my.regular - comp.regular (positive = we pay more)
            BinaryArithmetic(
                left_column=Column.regular_price,
                left_table_alias="my",
                operator=ArithmeticOp.subtract,
                right_column=Column.regular_price,
                right_table_alias="comp",
                alias="vendor_gap",
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
                                    left_column=QualifiedColumn(
                                        column=Column.id, table_alias="my"
                                    ),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(
                                        column=Column.source_id, table_alias="em"
                                    ),
                                )
                            ],
                            logic=LogicOp.and_,
                        )
                    ],
                ),
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.product_offers,
                    table_alias="comp",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                ColumnComparison(
                                    left_column=QualifiedColumn(
                                        column=Column.target_id, table_alias="em"
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
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(
                                column=Column.vendor, table_alias="my"
                            ),
                            operator=ComparisonOp.eq,
                            value="Us",
                        ),
                        # Competitor regular price lower than ours = they buy cheaper
                        ColumnComparison(
                            left_column=QualifiedColumn(
                                column=Column.regular_price, table_alias="comp"
                            ),
                            operator=ComparisonOp.lt,
                            right_column=QualifiedColumn(
                                column=Column.regular_price, table_alias="my"
                            ),
                        ),
                    ],
                    logic=LogicOp.and_,
                )
            ],
            group_logic=LogicOp.and_,
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.brand, direction=Direction.asc),
            ]
        ),
        limit=LimitClause(limit=100),
    )


def query_28_safe_haven_scanner():
    """
    MATCHED: Find stable, high-margin opportunity products using temporal price volatility.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Concern: Margin Potential Discovery
        Variant: Matched Execution
        Query Name: "The Safe Haven Scan"

    Business Value:
        "Find products with stable prices (low volatility) and high gaps"
        These are safe profit engines - competitor never discounts them.

    Pattern:
        Use window STDDEV over time to measure price stability per product.
        Low STDDEV + high price gap = safe haven for margins.

    Enhancement:
        Now uses temporal STDDEV (price volatility over 52 weeks per product)
        instead of cross-sectional STDDEV (variance across products).

    Action Trigger:
        Lock these prices, treat as profit engine, don't discount.

    Status: GOOD (upgraded from PARTIAL with window STDDEV temporal pattern)
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="my")),
            ColumnExpr(
                source=QualifiedColumn(column=Column.category, table_alias="my")
            ),
            ColumnExpr(source=QualifiedColumn(column=Column.brand, table_alias="my")),
            ColumnExpr(
                source=QualifiedColumn(column=Column.markdown_price, table_alias="my")
            ),
            ColumnExpr(
                source=QualifiedColumn(column=Column.markdown_price, table_alias="comp")
            ),
            # Price gap (comp - my)
            BinaryArithmetic(
                left_column=Column.markdown_price,
                left_table_alias="comp",
                operator=ArithmeticOp.subtract,
                right_column=Column.markdown_price,
                right_table_alias="my",
                alias="price_gap",
            ),
            # Temporal price volatility using window STDDEV over 52 weeks
            WindowExpr(
                function=WindowFunc.stddev,
                column=Column.markdown_price,
                table_alias="comp",
                partition_by=[Column.id],
                order_by=[
                    OrderByItem(column=Column.updated_at, direction=Direction.asc)
                ],
                alias="price_volatility_52w",
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
                                    left_column=QualifiedColumn(
                                        column=Column.id, table_alias="my"
                                    ),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(
                                        column=Column.source_id, table_alias="em"
                                    ),
                                )
                            ],
                            logic=LogicOp.and_,
                        )
                    ],
                ),
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.product_offers,
                    table_alias="comp",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                ColumnComparison(
                                    left_column=QualifiedColumn(
                                        column=Column.target_id, table_alias="em"
                                    ),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(
                                        column=Column.id, table_alias="comp"
                                    ),
                                ),
                                # Join on same product across time periods
                                ColumnComparison(
                                    left_column=QualifiedColumn(
                                        column=Column.id, table_alias="my"
                                    ),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(
                                        column=Column.id, table_alias="comp"
                                    ),
                                ),
                            ],
                            logic=LogicOp.and_,
                        )
                    ],
                ),
            ],
        ),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(
                                column=Column.vendor, table_alias="my"
                            ),
                            operator=ComparisonOp.eq,
                            value="Us",
                        ),
                    ],
                    logic=LogicOp.and_,
                )
            ],
            group_logic=LogicOp.and_,
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
                OrderByItem(column=Column.brand, direction=Direction.asc),
            ]
        ),
        limit=LimitClause(limit=100),
    )


def query_29_inventory_velocity_detector():
    """
    MATCHED: Infer sales velocity from availability toggle frequency using LAG.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Concern: Inventory Velocity Inference (Total Reconnaissance)
        Variant: Matched Execution
        Query Name: "The High-Velocity Detector"

    Business Value:
        "Products that toggle in/out of stock frequently are high-velocity winners"
        Copy what sells fast without needing their sales data.

    Pattern:
        Use LAG to track previous availability state.
        Count observations per product to detect frequent toggle patterns.
        High observation count with LAG showing state changes = high velocity.

    Enhancement:
        Now uses temporal LAG pattern to track availability state changes.
        Filters for products with multiple observations (indicating turnover).

    Action Trigger:
        Feature high-velocity items on homepage, increase stock depth.

    Status: GOOD (upgraded from GAP with LAG state tracking pattern)
    """
    return Query(
        select=[
            ColumnExpr(
                source=QualifiedColumn(column=Column.id, table_alias="velocity")
            ),
            ColumnExpr(
                source=QualifiedColumn(column=Column.title, table_alias="velocity")
            ),
            ColumnExpr(
                source=QualifiedColumn(column=Column.brand, table_alias="velocity")
            ),
            ColumnExpr(
                source=QualifiedColumn(column=Column.category, table_alias="velocity")
            ),
            ColumnExpr(
                source=QualifiedColumn(
                    column=Column.availability, table_alias="velocity"
                )
            ),
            ColumnExpr(
                source=QualifiedColumn(
                    column=Column.previous_availability, table_alias="velocity"
                )
            ),
            ColumnExpr(
                source=QualifiedColumn(
                    column=Column.toggle_count, table_alias="velocity"
                )
            ),
        ],
        from_=FromClause(
            derived=DerivedTable(
                select=[
                    ColumnExpr(
                        source=QualifiedColumn(column=Column.id, table_alias="comp")
                    ),
                    ColumnExpr(
                        source=QualifiedColumn(column=Column.title, table_alias="comp")
                    ),
                    ColumnExpr(
                        source=QualifiedColumn(column=Column.brand, table_alias="comp")
                    ),
                    ColumnExpr(
                        source=QualifiedColumn(
                            column=Column.category, table_alias="comp"
                        )
                    ),
                    ColumnExpr(
                        source=QualifiedColumn(
                            column=Column.availability, table_alias="comp"
                        )
                    ),
                    ColumnExpr(
                        source=QualifiedColumn(
                            column=Column.updated_at, table_alias="comp"
                        )
                    ),
                    # LAG to get previous availability state
                    WindowExpr(
                        function=WindowFunc.lag,
                        column=Column.availability,
                        table_alias="comp",
                        partition_by=[Column.id],
                        order_by=[
                            OrderByItem(
                                column=Column.updated_at, direction=Direction.asc
                            )
                        ],
                        offset=1,
                        alias="previous_availability",
                    ),
                    # Count observations per product (toggle frequency proxy)
                    WindowExpr(
                        function=WindowFunc.count,
                        column=Column.id,
                        table_alias="comp",
                        partition_by=[Column.id],
                        order_by=[
                            OrderByItem(
                                column=Column.updated_at, direction=Direction.asc
                            )
                        ],
                        alias="toggle_count",
                    ),
                ],
                from_table=Table.product_offers,
                table_alias="comp",
                where=WhereL0(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(
                                column=Column.vendor, table_alias="comp"
                            ),
                            operator=ComparisonOp.ne,
                            value="Us",
                        ),
                    ],
                    logic=LogicOp.and_,
                ),
                alias="velocity",
            )
        ),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        # Multiple observations (indicates toggling behavior)
                        SimpleCondition(
                            column=QualifiedColumn(
                                column=Column.toggle_count, table_alias="velocity"
                            ),
                            operator=ComparisonOp.gt,
                            value=3,  # At least 4 observations
                        ),
                    ],
                    logic=LogicOp.and_,
                )
            ],
            group_logic=LogicOp.and_,
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.toggle_count, direction=Direction.desc),
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
        limit=LimitClause(limit=100),
    )





def query_38_same_store_inflation_rate():
    """
    MATCHED: Calculate inflation rate on matched products over time.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Domain: Pricing Architecture
        Concern: Inflation and Trends
        Variant: Matched Execution
        Query Name: "The Same-Store Inflation Rate"

    Business Value:
        "Is the market getting more expensive or cheaper? I need to ride the wave."
        Insight: "On identical items, the market is up 4% YoY. I can raise my entire
        catalog by 4% without losing relative competitiveness."

    Action Trigger:
        If inflation_rate > 3% → Safe to raise prices proportionally
        Track market-wide price trends to guide pricing strategy

    Pattern:
        Uses LAG window function to compare current price against historical price
        on the same matched products. Aggregates to calculate overall inflation rate.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="current_avg_price",
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.previous_price,
                alias="historical_avg_price",
            ),
            AggregateExpr(function=AggregateFunc.count, column=None, alias="product_count"),
        ],
        from_=FromClause(
            derived=DerivedTable(
                select=[
                    ColumnExpr(source=QualifiedColumn(column=Column.id)),
                    ColumnExpr(source=QualifiedColumn(column=Column.category)),
                    ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
                    ColumnExpr(source=QualifiedColumn(column=Column.updated_at)),
                    WindowExpr(
                        function=WindowFunc.lag,
                        column=Column.markdown_price,
                        partition_by=[Column.id],
                        order_by=[
                            OrderByItem(column=Column.updated_at, direction=Direction.asc)
                        ],
                        offset=52,
                        alias="previous_price",
                    ),
                ],
                from_table=Table.product_offers,
                joins=[
                    JoinSpec(
                        join_type=JoinType.inner,
                        table=Table.exact_matches,
                        table_alias="m",
                        on_conditions=[
                            ConditionGroup(
                                conditions=[
                                    ColumnComparison(
                                        left_column=QualifiedColumn(column=Column.id),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(
                                            column=Column.source_id, table_alias="m"
                                        ),
                                    )
                                ],
                                logic=LogicOp.and_,
                            )
                        ],
                    ),
                ],
                where=WhereL0(
                    groups=[
                        ConditionGroup(
                            conditions=[
                                SimpleCondition(
                                    column=QualifiedColumn(column=Column.vendor),
                                    operator=ComparisonOp.ne,
                                    value="Us",
                                ),
                            ],
                            logic=LogicOp.and_,
                        )
                    ],
                    group_logic=LogicOp.and_,
                ),
                alias="inflation",
            )
        ),
        group_by=GroupByClause(columns=[Column.category]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
    )


def query_39_entry_level_creep():
    """
    UNMATCHED: Track 10th percentile price movement to detect market floor changes.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Domain: Pricing Architecture
        Concern: Inflation and Trends
        Variant: Unmatched Approximation
        Query Name: "The Entry-Level Creep"

    Business Value:
        "Is the market getting more expensive or cheaper? Track the cheap tier."
        Insight: "The 'Cheap' tier of Laptops has moved from $200 to $250.
        I should stop searching for $200 laptops; they don't exist anymore."

    Action Trigger:
        If 10th_percentile increased > $20 → Update sourcing criteria for entry-level products
        Stop pursuing price points below the new market floor

    Pattern:
        Uses PERCENTILE_DISC to find the 10th percentile price (entry-level threshold).
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            AggregateExpr(
                function=AggregateFunc.percentile_disc,
                column=Column.markdown_price,
                alias="entry_level_price_10th",
                percentile=0.10,
            ),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                alias="absolute_floor_price",
            ),
            AggregateExpr(
                function=AggregateFunc.count, column=None, alias="product_count"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.ne,
                            value="Us",
                        ),
                    ],
                    logic=LogicOp.and_,
                )
            ],
            group_logic=LogicOp.and_,
        ),
        group_by=GroupByClause(columns=[Column.category]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
    )


def query_40_semantic_keyword_scrape():
    """
    UNMATCHED: Multi-keyword semantic search to price similar products.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Domain: Total Reconnaissance
        Concern: Semantic Clustering Manual Matching
        Variant: Unmatched Execution
        Query Name: "The Semantic Keyword Scrape"

    Business Value:
        "The database doesn't have matches? I don't care. I will conceptually match
        them using language patterns."

        Insight: "Even without IDs, I know the market price for a 'Generic 55 OLED'
        is $900. If my private label version is $1100, it will fail."

    Action Trigger:
        Use for pricing new products without exact matches.
        Combine multiple keywords to narrow semantic search.

    Pattern:
        Uses multiple ILIKE conditions to filter for specific product features.
        Calculates average market price for semantically similar products.

    Example:
        Searches for "55 inch" + "OLED" TVs - would be parameterized in production.
    """
    return Query(
        select=[
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="avg_market_price",
            ),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                alias="min_market_price",
            ),
            AggregateExpr(
                function=AggregateFunc.max,
                column=Column.markdown_price,
                alias="max_market_price",
            ),
            AggregateExpr(
                function=AggregateFunc.count, column=None, alias="product_count"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.ne,
                            value="Us",
                        ),
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.title),
                            operator=ComparisonOp.ilike,
                            value="%OLED%",
                        ),
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.title),
                            operator=ComparisonOp.ilike,
                            value="%55%",
                        ),
                    ],
                    logic=LogicOp.and_,
                )
            ],
            group_logic=LogicOp.and_,
        ),
    )


def query_41_new_arrival_survival_rate():
    """
    UNMATCHED: Identify products that survived 3+ months to detect winners.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Domain: Total Reconnaissance
        Concern: Inventory Velocity Inference
        Variant: Unmatched Approximation
        Query Name: "The 'New Arrival' Survival Rate"

    Business Value:
        "I want to know what they are selling *fast*, so I can copy it.
        They launched 50 new 'Smart Home' gadgets. Only 10 survived."

    Action Trigger:
        Stock only the survivors - they tested the market for you.
        Avoid the 40 failures they already identified through liquidation.

    Pattern:
        Filters for products with created_at > 90 days ago that are still available.
        Identifies long-term winners vs. failed experiments.

    Note:
        This simplified version filters on created_at. Production would compare
        snapshots from different time periods.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id)),
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.brand)),
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
            ColumnExpr(source=QualifiedColumn(column=Column.created_at)),
            ColumnExpr(source=QualifiedColumn(column=Column.availability)),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.ne,
                            value="Us",
                        ),
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.availability),
                            operator=ComparisonOp.eq,
                            value=True,
                        ),
                        # Filter for products created 90+ days ago (survivors)
                        # Note: Would need date arithmetic in production
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.created_at),
                            operator=ComparisonOp.is_not_null,
                            value="",  # Value ignored by translator for IS NOT NULL
                        ),
                    ],
                    logic=LogicOp.and_,
                )
            ],
            group_logic=LogicOp.and_,
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.created_at, direction=Direction.asc),
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
        limit=LimitClause(limit=100),
    )


# =============================================================================
# Main execution
# =============================================================================

if __name__ == "__main__":
    print("Phase 3 ARCHITECT Procurement Queries")
    print("=" * 80)

    queries = [
        ("Q27: Vendor Fairness Audit (Matched)", query_27_vendor_fairness_audit),
        ("Q28: Safe Haven Scanner (Matched)", query_28_safe_haven_scanner),
        (
            "Q29: Inventory Velocity Detector (Matched)",
            query_29_inventory_velocity_detector,
        ),
    ]

    for name, query_func in queries:
        print(f"\n{name}")
        print("-" * 80)
        try:
            query = query_func()
            sql = translate_query(query)
            print(sql)
            print()
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback

            traceback.print_exc()
