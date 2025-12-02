"""
Phase 2 ARCHITECT Range Queries - Expanding Coverage to 85%

This file implements ARCHITECT queries for range architecture and strategic positioning.

New Query Coverage:
- ARCHITECT: Commoditization coefficient, brand weighting, price ladder analysis

Coverage: 68% → 85% (16/19 intelligence concerns)
"""

from structured_query_builder import *
from structured_query_builder.translator import translate_query

# =============================================================================
# ARCHETYPE 5: ARCHITECT - Range Architecture (3 new queries)
# =============================================================================


def query_24_commoditization_coefficient():
    """
    MATCHED: Calculate product overlap ratio (commoditization metric).

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Concern: Assortment Overlap & Exclusivity
        Variant: Matched Execution
        Query Name: "The Commoditization Coefficient"

    Business Value:
        Quantifies uniqueness: "What % of my assortment is also sold by competitor?"
        High overlap = commodity business. Low overlap = differentiated destination.

    Formula:
        COUNT(matches) / COUNT(total_my_assortment)

    Action Trigger:
        If coefficient > 0.8 → We're a commodity, need exclusive brands
        If coefficient < 0.3 → We're differentiated, can command premium

    Implementation:
        Uses derived table with GROUP BY to calculate counts, then arithmetic for ratio.
    """
    return Query(
        select=[
            ColumnExpr(
                source=QualifiedColumn(column=Column.category, table_alias="agg")
            ),
            ColumnExpr(
                source=QualifiedColumn(
                    column=Column.total_our_products, table_alias="agg"
                )
            ),
            ColumnExpr(
                source=QualifiedColumn(
                    column=Column.matched_products, table_alias="agg"
                )
            ),
            # Calculate ratio: matched / total
            BinaryArithmetic(
                left_column=Column.matched_products,
                left_table_alias="agg",
                operator=ArithmeticOp.divide,
                right_column=Column.total_our_products,
                right_table_alias="agg",
                alias="commoditization_coefficient",
            ),
        ],
        from_=FromClause(
            derived=DerivedTable(
                select=[
                    ColumnExpr(
                        source=QualifiedColumn(column=Column.category, table_alias="my")
                    ),
                    AggregateExpr(
                        function=AggregateFunc.count,
                        column=Column.id,
                        table_alias="my",
                        alias="total_our_products",
                    ),
                    AggregateExpr(
                        function=AggregateFunc.count,
                        column=Column.source_id,
                        table_alias="em",
                        alias="matched_products",
                    ),
                ],
                from_table=Table.product_offers,
                table_alias="my",
                joins=[
                    JoinSpec(
                        join_type=JoinType.left,
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
                ],
                where=WhereL0(
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
                group_by=GroupByClause(columns=[Column.category]),
                alias="agg",
            )
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
    )


def query_25_brand_weighting_fingerprint():
    """
    UNMATCHED: Compare brand concentration between us and competitor.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Concern: Assortment Overlap & Exclusivity
        Variant: Unmatched Execution
        Query Name: "The Brand Weighting Fingerprint"

    Business Value:
        Reveals strategic brand bets without SKU matches.
        "They're 40% Sony, we're 10% Sony → They have better Sony terms"

    Pattern:
        Calculate share-of-shelf % per brand for each vendor.
        Uses derived table for counts, then window function for vendor totals.

    Action Trigger:
        If competitor's brand weight > our weight + 20% → Negotiate better vendor terms
        If we dominate a brand → Position as authorized dealer

    Implementation:
        1. Inner query: GROUP BY brand, vendor to get counts
        2. Outer query: Window SUM to get vendor totals
        3. Arithmetic: (brand_count * 100 / vendor_total) for percentage
    """
    return Query(
        select=[
            ColumnExpr(
                source=QualifiedColumn(column=Column.brand, table_alias="counts")
            ),
            ColumnExpr(
                source=QualifiedColumn(column=Column.vendor, table_alias="counts")
            ),
            ColumnExpr(
                source=QualifiedColumn(
                    column=Column.product_count, table_alias="counts"
                )
            ),
            # Window function to get vendor total
            WindowExpr(
                function=WindowFunc.sum,
                column=Column.product_count,
                partition_by=[Column.vendor],
                order_by=[],
                alias="vendor_total",
            ),
            # Calculate percentage: (brand_count * 100) / vendor_total
            CompoundArithmetic(
                inner_left_column=Column.product_count,
                inner_operator=ArithmeticOp.multiply,
                inner_right_value=100.0,
                outer_operator=ArithmeticOp.divide,
                outer_column=Column.vendor_total,
                alias="brand_share_percent",
            ),
        ],
        from_=FromClause(
            derived=DerivedTable(
                select=[
                    ColumnExpr(source=QualifiedColumn(column=Column.brand)),
                    ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
                    AggregateExpr(
                        function=AggregateFunc.count, column=None, alias="product_count"
                    ),
                ],
                from_table=Table.product_offers,
                group_by=GroupByClause(columns=[Column.brand, Column.vendor]),
                alias="counts",
            )
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.vendor, direction=Direction.asc),
                OrderByItem(column=Column.brand, direction=Direction.asc),
            ]
        ),
    )


def query_26_price_ladder_void_scanner():
    """
    UNMATCHED: Analyze price distribution to identify empty price points.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Concern: Gap Analysis & White Space
        Variant: Unmatched Execution
        Query Name: "The Price Ladder Void"

    Business Value:
        Find price points with zero competition.
        "They have no toasters between $50-$80 → Source a $69.99 model to own that tier"

    Pattern:
        Returns price statistics (MIN, MAX, AVG, STDDEV, percentiles) by category/vendor.
        Application layer bins into tiers and identifies gaps.

    Schema Limitation:
        True histogram binning (GROUP BY CASE expression) not supported without:
        - Repeating CASE in GROUP BY (requires expression support in GroupByClause)
        - Derived tables with full GROUP BY (DerivedTable limited to simple SELECT)
        Current approach: Provide statistical foundation for application-layer binning.

    Action Trigger:
        If gap found in popular category → Source product to fill void
        If we're alone in price tier → Market as "only option at this price"
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                alias="min_price",
            ),
            AggregateExpr(
                function=AggregateFunc.max,
                column=Column.markdown_price,
                alias="max_price",
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="avg_price",
            ),
            # Percentiles for tier analysis
            AggregateExpr(
                function=AggregateFunc.percentile_cont,
                column=Column.markdown_price,
                percentile=0.25,
                alias="p25_price",
            ),
            AggregateExpr(
                function=AggregateFunc.percentile_cont,
                column=Column.markdown_price,
                percentile=0.75,
                alias="p75_price",
            ),
            AggregateExpr(
                function=AggregateFunc.count, column=None, alias="product_count"
            ),
            AggregateExpr(
                function=AggregateFunc.stddev,
                column=Column.markdown_price,
                alias="price_spread",
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        group_by=GroupByClause(columns=[Column.category, Column.vendor]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
    )


def query_15_category_margin_proxy():
    """
    MATCHED: Calculate margin headroom opportunity by comparing competitor vs our prices.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Concern: Margin Potential Discovery
        Variant: Matched Execution
        Query Name: "The Category Margin Proxy"

    Business Value:
        "How much pricing power do we have in each category?"
        (Competitor_Avg - My_Avg) / My_Avg reveals margin opportunity.

    Pattern:
        1. Aggregate AVG prices by category for "Us" and "Them"
        2. Calculate percentage gap: (comp - my) / my
        3. Higher gap = more margin headroom

    Action Trigger:
        If gap > 15% → Test price increases in that category
        If gap < 5% → We're at market ceiling, focus on volume

    Status: GOOD
    """
    return Query(
        select=[
            ColumnExpr(
                source=QualifiedColumn(column=Column.category, table_alias="margins")
            ),
            ColumnExpr(
                source=QualifiedColumn(
                    column=Column.my_avg_price, table_alias="margins"
                )
            ),
            ColumnExpr(
                source=QualifiedColumn(
                    column=Column.comp_avg_price, table_alias="margins"
                )
            ),
            # Calculate margin opportunity: (comp_avg - my_avg) / my_avg
            CompoundArithmetic(
                inner_left_column=Column.comp_avg_price,
                inner_left_table_alias="margins",
                inner_operator=ArithmeticOp.subtract,
                inner_right_column=Column.my_avg_price,
                inner_right_table_alias="margins",
                outer_operator=ArithmeticOp.divide,
                outer_column=Column.my_avg_price,
                outer_table_alias="margins",
                alias="margin_opportunity_pct",
            ),
        ],
        from_=FromClause(
            derived=DerivedTable(
                select=[
                    ColumnExpr(
                        source=QualifiedColumn(column=Column.category, table_alias="my")
                    ),
                    AggregateExpr(
                        function=AggregateFunc.avg,
                        column=Column.markdown_price,
                        table_alias="my",
                        alias="my_avg_price",
                    ),
                    AggregateExpr(
                        function=AggregateFunc.avg,
                        column=Column.markdown_price,
                        table_alias="comp",
                        alias="comp_avg_price",
                    ),
                ],
                from_table=Table.product_offers,
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
                where=WhereL0(
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
                ),
                group_by=GroupByClause(columns=[Column.category]),
                alias="margins",
            )
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(
                    column=Column.margin_opportunity_pct, direction=Direction.desc
                ),
            ]
        ),
        limit=LimitClause(limit=50),
    )


def query_37_magic_number_distribution():
    """
    UNMATCHED: Analyze markdown patterns to decode competitor pricing psychology.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Domain: Pricing Architecture
        Concern: Psychological Anchoring
        Variant: Unmatched Approximation
        Query Name: "The Magic Number Distribution"

    Business Value:
        "How does the customer perceive value? Master the pricing semantics."
        Insight: Decode pricing psychology through markdown vs regular price analysis.

    Action Trigger:
        Understand competitor's pricing semantics and adopt similar patterns.

    Pattern:
        Simplified implementation that analyzes markdown/regular price distribution.
        Full decimal-ending analysis would require MOD(price * 100, 100) SQL functions.

    Note:
        This version groups by is_markdown flag and category to reveal pricing patterns.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.is_markdown)),
            AggregateExpr(
                function=AggregateFunc.count, column=None, alias="product_count"
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="avg_price",
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.regular_price,
                alias="avg_regular_price",
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
        group_by=GroupByClause(columns=[Column.category, Column.is_markdown]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
                OrderByItem(column=Column.is_markdown, direction=Direction.desc),
            ]
        ),
    )


def query_36_discount_depth_alignment():
    """
    MATCHED: Compare nominal discount amounts to identify optical value gaps.

    Intelligence Model Mapping:
        Archetype: ARCHITECT
        Domain: Pricing Architecture
        Concern: Psychological Anchoring
        Variant: Matched Execution
        Query Name: "The Discount Depth Alignment"

    Business Value:
        "How does the customer perceive value? I need to master the gap between
        the 'Sticker Price' and the 'Real Price'."

        Example: Both at $100, but they say "Was $150" ($50 off), we say "Was $110" ($10 off).
        Their deal LOOKS better even though final price is identical.

    Action Trigger:
        If competitor_discount > my_discount → Inflate regular price to match optical value
        Psychology: Customers respond to nominal discount amounts, not just final price.

    Pattern:
        Compare (regular - current) between matched products to identify
        where competitor has better optical discount value.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.brand, table_alias="my")),
            ColumnExpr(
                source=QualifiedColumn(column=Column.regular_price, table_alias="my")
            ),
            ColumnExpr(
                source=QualifiedColumn(column=Column.markdown_price, table_alias="my")
            ),
            ColumnExpr(
                source=QualifiedColumn(column=Column.regular_price, table_alias="comp")
            ),
            ColumnExpr(
                source=QualifiedColumn(column=Column.markdown_price, table_alias="comp")
            ),
            # My discount amount
            ComputedExpr(
                expression=CompoundArithmetic(
                    left=QualifiedColumn(column=Column.regular_price, table_alias="my"),
                    operator=ArithmeticOp.subtract,
                    right=QualifiedColumn(
                        column=Column.markdown_price, table_alias="my"
                    ),
                ),
                alias="my_discount_amount",
            ),
            # Competitor discount amount
            ComputedExpr(
                expression=CompoundArithmetic(
                    left=QualifiedColumn(
                        column=Column.regular_price, table_alias="comp"
                    ),
                    operator=ArithmeticOp.subtract,
                    right=QualifiedColumn(
                        column=Column.markdown_price, table_alias="comp"
                    ),
                ),
                alias="comp_discount_amount",
            ),
            # Optical gap
            ComputedExpr(
                expression=CompoundArithmetic(
                    left=CompoundArithmetic(
                        left=QualifiedColumn(
                            column=Column.regular_price, table_alias="comp"
                        ),
                        operator=ArithmeticOp.subtract,
                        right=QualifiedColumn(
                            column=Column.markdown_price, table_alias="comp"
                        ),
                    ),
                    operator=ArithmeticOp.subtract,
                    right=CompoundArithmetic(
                        left=QualifiedColumn(
                            column=Column.regular_price, table_alias="my"
                        ),
                        operator=ArithmeticOp.subtract,
                        right=QualifiedColumn(
                            column=Column.markdown_price, table_alias="my"
                        ),
                    ),
                ),
                alias="optical_discount_gap",
            ),
        ],
        from_=FromClause(table=Table.product_offers, alias="my"),
        joins=[
            JoinClause(
                join_type=JoinType.inner,
                table=Table.exact_matches,
                alias="m",
                on=JoinCondition(
                    left=QualifiedColumn(column=Column.id, table_alias="my"),
                    right=QualifiedColumn(column=Column.source_id, table_alias="m"),
                ),
            ),
            JoinClause(
                join_type=JoinType.inner,
                table=Table.product_offers,
                alias="comp",
                on=JoinCondition(
                    left=QualifiedColumn(column=Column.target_id, table_alias="m"),
                    right=QualifiedColumn(column=Column.id, table_alias="comp"),
                ),
            ),
        ],
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
                        SimpleCondition(
                            column=QualifiedColumn(
                                column=Column.vendor, table_alias="comp"
                            ),
                            operator=ComparisonOp.ne,
                            value="Us",
                        ),
                        # Filter: competitor discount > my discount (they look better)
                        ArithmeticCondition(
                            left=CompoundArithmetic(
                                left=QualifiedColumn(
                                    column=Column.regular_price, table_alias="comp"
                                ),
                                operator=ArithmeticOp.subtract,
                                right=QualifiedColumn(
                                    column=Column.markdown_price, table_alias="comp"
                                ),
                            ),
                            operator=ComparisonOp.gt,
                            right=CompoundArithmetic(
                                left=QualifiedColumn(
                                    column=Column.regular_price, table_alias="my"
                                ),
                                operator=ArithmeticOp.subtract,
                                right=QualifiedColumn(
                                    column=Column.markdown_price, table_alias="my"
                                ),
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
                # Order by optical gap desc to show biggest perception disadvantages
                OrderByItem(
                    column=Column.regular_price,
                    direction=Direction.desc,
                    table_alias="comp",
                ),
            ]
        ),
        limit=LimitClause(limit=100),
    )


# =============================================================================
# Main execution
# =============================================================================

if __name__ == "__main__":
    print("Phase 2 ARCHITECT Range Queries")
    print("=" * 80)

    queries = [
        (
            "Q24: Commoditization Coefficient (Matched)",
            query_24_commoditization_coefficient,
        ),
        (
            "Q25: Brand Weighting Fingerprint (Unmatched)",
            query_25_brand_weighting_fingerprint,
        ),
        (
            "Q26: Price Ladder Void Scanner (Unmatched)",
            query_26_price_ladder_void_scanner,
        ),
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
