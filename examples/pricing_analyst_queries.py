"""
Pricing analyst query examples.

Real-world queries for e-commerce pricing analysis, including:
- Discount calculations
- Competitor comparisons
- Price rankings
- Trend analysis
- Price segmentation
"""

from structured_query_builder import *
from structured_query_builder.translator import translate_query


def example_1_discount_percentage():
    """
    Calculate discount percentage for markdown products.

    SELECT title, regular_price, markdown_price,
           ((regular_price - markdown_price) / regular_price) AS discount_pct
    FROM product_offers
    WHERE is_markdown = TRUE
    ORDER BY discount_pct DESC
    LIMIT 20
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

    SELECT vendor, category, title, regular_price,
           RANK() OVER (PARTITION BY category
                        ORDER BY regular_price ASC) AS price_rank
    FROM product_offers
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

    SELECT ours.title,
           ours.regular_price AS our_price,
           theirs.regular_price AS amazon_price,
           (ours.regular_price - theirs.regular_price) AS price_diff
    FROM product_offers ours
    INNER JOIN product_offers theirs
        ON ours.product_match_id = theirs.product_match_id
    WHERE ours.vendor = 'our_company' AND theirs.vendor = 'amazon'
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

    SELECT title, category, regular_price
    FROM product_offers
    WHERE regular_price > (
        SELECT AVG(regular_price)
        FROM product_offers sub
        WHERE sub.category = product_offers.category
    )
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

    SELECT title, regular_price,
           CASE
               WHEN regular_price < 20 THEN 'budget'
               WHEN regular_price < 50 THEN 'value'
               WHEN regular_price < 100 THEN 'standard'
               ELSE 'premium'
           END AS price_tier
    FROM product_offers
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

    SELECT vendor,
           COUNT(*) AS product_count,
           AVG(regular_price) AS avg_price,
           MIN(regular_price) AS min_price,
           MAX(regular_price) AS max_price
    FROM product_offers
    GROUP BY vendor
    HAVING COUNT(*) > 100
    ORDER BY avg_price DESC
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

    SELECT vendor, title, regular_price, created_at,
           LAG(regular_price, 1, 0) OVER (
               PARTITION BY vendor, title
               ORDER BY created_at ASC
           ) AS prev_price
    FROM product_offers
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
