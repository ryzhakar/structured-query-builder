"""
Pricing analyst query examples - Real business use cases with technical patterns.

This module demonstrates real-world pricing analysis patterns used by e-commerce
pricing analysts, complete with business context and technical implementation details.

Each query shows:
1. Business Context - When/why/who uses this query
2. Natural Language - The analyst's original request
3. Pydantic Model - The structured query implementation
4. Generated SQL - The resulting query
5. Technical Patterns - Window functions, JOINs, subqueries, CASE expressions

Query Categories:
- Discount calculations and markdown analysis
- Competitor price comparisons (self-join patterns)
- Price rankings and competitive positioning (window functions)
- Trend analysis and price change detection (LAG/RANK)
- Price segmentation and tier classification (CASE expressions)

These are REAL queries that pricing analysts run daily, not toy examples.
"""

from structured_query_builder import *
from structured_query_builder.translator import translate_query


def example_1_discount_percentage():
    """
    Calculate discount percentage for markdown products.

    Business Context:
    Post-promotional period analysis - measure which markdowns are deepest.
    Used by Pricing Analysts in weekly/monthly post-promotion reports.

    Natural Language:
    "Show me all products on markdown with discount percentage. I want to see
    which ones have the deepest discounts to evaluate promotion effectiveness."

    SQL Equivalent:
    SELECT title, regular_price, markdown_price,
           ((regular_price - markdown_price) / regular_price) AS discount_pct
    FROM product_offers
    WHERE is_markdown = TRUE
    ORDER BY discount_pct DESC
    LIMIT 20

    Technical Pattern: CompoundArithmetic for nested calculations
    """
    print("\n" + "="*80)
    print("Pricing Example 1: Discount Percentage Analysis")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
            ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
            CompoundArithmetic(
                inner_left_column=Column.regular_price,
                inner_operator=ArithmeticOp.subtract,
                inner_right_column=Column.markdown_price,
                outer_operator=ArithmeticOp.divide,
                outer_column=Column.regular_price,
                alias="discount_pct"
            )
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
                        )
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.regular_price, direction=Direction.desc)
            ]
        ),
        limit=LimitClause(limit=20)
    )

    sql = translate_query(query)
    print(sql)
    print("\nUse Case: Identify products with highest discount percentages")
    return query


def example_2_price_ranking():
    """
    Rank products by price within each category.

    Business Context:
    Monthly strategy sessions - understand market position in each category.
    Used by Director of Pricing presenting to executives.

    Natural Language:
    "For each category, rank all products by price from lowest to highest.
    Where do we stand - cheapest, most expensive, or middle of the pack?"

    SQL Equivalent:
    SELECT vendor, category, title, regular_price,
           RANK() OVER (PARTITION BY category
                        ORDER BY regular_price ASC) AS price_rank
    FROM product_offers

    Technical Pattern: RANK() window function with PARTITION BY
    """
    print("\n" + "="*80)
    print("Pricing Example 2: Price Ranking by Category")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
            WindowExpr(
                function=WindowFunc.rank,
                column=Column.regular_price,
                partition_by=[Column.category],
                order_by=[
                    OrderByItem(column=Column.regular_price, direction=Direction.asc)
                ],
                alias="price_rank"
            )
        ],
        from_=FromClause(table=Table.product_offers)
    )

    sql = translate_query(query)
    print(sql)
    print("\nUse Case: See how products rank by price within their categories")
    return query


def example_3_competitor_comparison():
    """
    Compare our prices to Amazon's for the same products.

    Business Context:
    Daily competitive intelligence - direct price comparison on matched products.
    Used by Competitive Intelligence Analysts for rapid response pricing.

    Natural Language:
    "Show me side-by-side price comparison for products we both carry.
    Calculate the price difference so I can see where we're over/underpriced."

    SQL Equivalent:
    SELECT ours.title,
           ours.regular_price AS our_price,
           theirs.regular_price AS amazon_price,
           (ours.regular_price - theirs.regular_price) AS price_diff
    FROM product_offers ours
    INNER JOIN product_offers theirs
        ON ours.product_match_id = theirs.product_match_id
    WHERE ours.vendor = 'our_company' AND theirs.vendor = 'amazon'

    Technical Pattern: Self-join with table aliases for comparison
    """
    print("\n" + "="*80)
    print("Pricing Example 3: Competitor Price Comparison (Self-Join)")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(
                source=QualifiedColumn(table_alias="ours", column=Column.title)
            ),
            ColumnExpr(
                source=QualifiedColumn(table_alias="ours", column=Column.regular_price),
                alias="our_price"
            ),
            ColumnExpr(
                source=QualifiedColumn(table_alias="theirs", column=Column.regular_price),
                alias="amazon_price"
            ),
            BinaryArithmetic(
                left_column=Column.regular_price,
                operator=ArithmeticOp.subtract,
                right_column=Column.regular_price,
                alias="price_diff"
            )
        ],
        from_=FromClause(
            table=Table.product_offers,
            table_alias="ours",
            joins=[
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.product_offers,
                    table_alias="theirs",
                    left_column=Column.product_match_id,
                    left_table_alias="ours",
                    right_column=Column.product_match_id
                )
            ]
        )
    )

    sql = translate_query(query)
    print(sql)
    print("\nUse Case: Direct price comparison with specific competitor")
    return query


def example_4_above_category_average():
    """
    Find products priced above their category average.

    Business Context:
    Premium product identification - find items positioned above category norm.
    Used by Category Managers for assortment and merchandising decisions.

    Natural Language:
    "Show me products priced above the average for their category.
    These are our premium-positioned items that deserve special attention."

    SQL Equivalent:
    SELECT title, category, regular_price
    FROM product_offers
    WHERE regular_price > (
        SELECT AVG(regular_price)
        FROM product_offers sub
        WHERE sub.category = product_offers.category
    )

    Technical Pattern: Correlated subquery for category-level comparison
    """
    print("\n" + "="*80)
    print("Pricing Example 4: Products Above Category Average")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            subquery_conditions=[
                SubqueryCondition(
                    column=QualifiedColumn(column=Column.regular_price),
                    operator=ComparisonOp.gt,
                    subquery=ScalarSubquery(
                        table=Table.product_offers,
                        aggregate=AggregateExpr(
                            function=AggregateFunc.avg,
                            column=Column.regular_price,
                            alias="avg_price"
                        ),
                        group_by=[Column.category]
                    )
                )
            ],
            group_logic=LogicOp.and_
        )
    )

    sql = translate_query(query)
    print(sql)
    print("\nUse Case: Identify premium-priced products in each category")
    return query


def example_5_price_tier_classification():
    """
    Classify products into price tiers.

    Business Context:
    Product categorization for merchandising - segment by price point.
    Used by Merchandising team for promotions, messaging, and assortment planning.

    Natural Language:
    "Classify products into tiers: budget (<$20), value ($20-$50),
    standard ($50-$100), premium (>$100). This helps us target promotions
    and understand our price point distribution."

    SQL Equivalent:
    SELECT title, regular_price,
           CASE
               WHEN regular_price < 20 THEN 'budget'
               WHEN regular_price < 50 THEN 'value'
               WHEN regular_price < 100 THEN 'standard'
               ELSE 'premium'
           END AS price_tier
    FROM product_offers

    Technical Pattern: CASE expression for conditional bucketing
    """
    print("\n" + "="*80)
    print("Pricing Example 5: Price Tier Classification")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
            CaseExpr(
                whens=[
                    CaseWhen(
                        condition_column=Column.regular_price,
                        condition_operator=ComparisonOp.lt,
                        condition_value=20,
                        then_value="budget"
                    ),
                    CaseWhen(
                        condition_column=Column.regular_price,
                        condition_operator=ComparisonOp.lt,
                        condition_value=50,
                        then_value="value"
                    ),
                    CaseWhen(
                        condition_column=Column.regular_price,
                        condition_operator=ComparisonOp.lt,
                        condition_value=100,
                        then_value="standard"
                    ),
                ],
                else_value="premium",
                alias="price_tier"
            )
        ],
        from_=FromClause(table=Table.product_offers)
    )

    sql = translate_query(query)
    print(sql)
    print("\nUse Case: Segment products by price tier for reporting")
    return query


def example_6_vendor_price_stats():
    """
    Aggregate pricing statistics by vendor.

    Business Context:
    Quarterly vendor performance reviews - understand pricing strategies.
    Used by Category Buyers in vendor negotiations and assortment decisions.

    Natural Language:
    "For each vendor, show me min, max, and average price along with product count.
    This tells me if they're a discount vendor (low avg) or varied-assortment
    vendor (high range). Filter to vendors with significant volume."

    SQL Equivalent:
    SELECT vendor,
           COUNT(*) AS product_count,
           AVG(regular_price) AS avg_price,
           MIN(regular_price) AS min_price,
           MAX(regular_price) AS max_price
    FROM product_offers
    GROUP BY vendor
    HAVING COUNT(*) > 100
    ORDER BY avg_price DESC

    Technical Pattern: Multiple aggregates with GROUP BY and HAVING
    """
    print("\n" + "="*80)
    print("Pricing Example 6: Vendor Price Statistics")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="product_count"
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.regular_price,
                alias="avg_price"
            ),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.regular_price,
                alias="min_price"
            ),
            AggregateExpr(
                function=AggregateFunc.max,
                column=Column.regular_price,
                alias="max_price"
            )
        ],
        from_=FromClause(table=Table.product_offers),
        group_by=GroupByClause(columns=[Column.vendor]),
        having=HavingClause(
            conditions=[
                HavingCondition(
                    function=AggregateFunc.count,
                    column=None,
                    operator=ComparisonOp.gt,
                    value=100
                )
            ],
            logic=LogicOp.and_
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.regular_price, direction=Direction.desc)
            ]
        )
    )

    sql = translate_query(query)
    print(sql)
    print("\nUse Case: Overview of vendor pricing strategies")
    return query


def example_7_week_over_week_changes():
    """
    Track week-over-week price changes.

    Business Context:
    Monday mornings - detect competitor price movements to respond quickly.
    Used by Competitive Intelligence Analysts for rapid reaction pricing.

    Natural Language:
    "Show me products where price changed from last week to this week.
    I need current price and previous price side-by-side so I can calculate
    the change and decide if we need to respond."

    SQL Equivalent:
    SELECT vendor, title, regular_price, created_at,
           LAG(regular_price, 1, 0) OVER (
               PARTITION BY vendor, title
               ORDER BY created_at ASC
           ) AS prev_price
    FROM product_offers

    Technical Pattern: LAG() window function for temporal comparison
    Note: Application layer computes (current_price - prev_price) for change amount
    """
    print("\n" + "="*80)
    print("Pricing Example 7: Week-over-Week Price Changes")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
            ColumnExpr(source=QualifiedColumn(column=Column.created_at)),
            WindowExpr(
                function=WindowFunc.lag,
                column=Column.regular_price,
                partition_by=[Column.vendor, Column.title],
                order_by=[
                    OrderByItem(column=Column.created_at, direction=Direction.asc)
                ],
                offset=1,
                default_value=0,
                alias="prev_price"
            )
        ],
        from_=FromClause(table=Table.product_offers)
    )

    sql = translate_query(query)
    print(sql)
    print("\nUse Case: Detect price trends and changes over time")
    return query


def main():
    """Run all pricing analyst examples."""
    print("\n" + "="*80)
    print(" PRICING ANALYST QUERY EXAMPLES")
    print("="*80)
    print("\nThese queries demonstrate real-world pricing analysis patterns")
    print("used by e-commerce pricing analysts.")

    examples = [
        example_1_discount_percentage,
        example_2_price_ranking,
        example_3_competitor_comparison,
        example_4_above_category_average,
        example_5_price_tier_classification,
        example_6_vendor_price_stats,
        example_7_week_over_week_changes,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print(" All pricing analyst examples completed!")
    print("="*80)


if __name__ == "__main__":
    main()
