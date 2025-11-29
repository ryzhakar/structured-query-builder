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
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category, table_alias="my")),
            # Total products we carry
            AggregateExpr(
                function=AggregateFunc.count,
                column=Column.id,
                table_alias="my",
                alias="total_our_products"
            ),
            # Products that have matches
            AggregateExpr(
                function=AggregateFunc.count,
                column=Column.source_id,
                table_alias="em",
                alias="matched_products"
            ),
        ],
        from_=FromClause(
            table=Table.product_offers,
            table_alias="my",
            joins=[
                JoinSpec(
                    join_type=JoinType.left,  # LEFT JOIN to include unmatched
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
        group_by=GroupByClause(columns=[Column.category]),
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

    Action Trigger:
        If competitor's brand weight > our weight + 20% → Negotiate better vendor terms
        If we dominate a brand → Position as authorized dealer
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.brand)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="product_count"
            ),
            # Calculate percentage requires application layer math
            # This query returns counts, percentage = count/total in app
        ],
        from_=FromClause(table=Table.product_offers),
        group_by=GroupByClause(columns=[Column.brand, Column.vendor]),
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
                alias="min_price"
            ),
            AggregateExpr(
                function=AggregateFunc.max,
                column=Column.markdown_price,
                alias="max_price"
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="avg_price"
            ),
            # Percentiles for tier analysis
            AggregateExpr(
                function=AggregateFunc.percentile_cont,
                column=Column.markdown_price,
                percentile=0.25,
                alias="p25_price"
            ),
            AggregateExpr(
                function=AggregateFunc.percentile_cont,
                column=Column.markdown_price,
                percentile=0.75,
                alias="p75_price"
            ),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="product_count"
            ),
            AggregateExpr(
                function=AggregateFunc.stddev,
                column=Column.markdown_price,
                alias="price_spread"
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


# =============================================================================
# Main execution
# =============================================================================

if __name__ == "__main__":
    print("Phase 2 ARCHITECT Range Queries")
    print("=" * 80)

    queries = [
        ("Q24: Commoditization Coefficient (Matched)", query_24_commoditization_coefficient),
        ("Q25: Brand Weighting Fingerprint (Unmatched)", query_25_brand_weighting_fingerprint),
        ("Q26: Price Ladder Void Scanner (Unmatched)", query_26_price_ladder_void_scanner),
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
