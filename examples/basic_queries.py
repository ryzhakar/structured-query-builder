"""
Basic query examples demonstrating core functionality.

These examples show simple queries that cover the most common use cases.
"""

from structured_query_builder import *
from structured_query_builder.translator import translate_query


def example_1_simple_select():
    """
    SELECT vendor, category, regular_price
    FROM product_offers
    """
    print("\n" + "="*80)
    print("Example 1: Simple SELECT")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        ],
        from_=FromClause(table=Table.product_offers)
    )

    sql = translate_query(query)
    print(sql)
    return query


def example_2_with_filter():
    """
    SELECT vendor, category, regular_price
    FROM product_offers
    WHERE category = 'electronics' AND vendor = 'amazon'
    """
    print("\n" + "="*80)
    print("Example 2: SELECT with WHERE")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.category),
                            operator=ComparisonOp.eq,
                            value="electronics"
                        ),
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.eq,
                            value="amazon"
                        )
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        )
    )

    sql = translate_query(query)
    print(sql)
    return query


def example_3_in_operator():
    """
    SELECT vendor, category, regular_price
    FROM product_offers
    WHERE vendor IN ('amazon', 'walmart', 'target')
    """
    print("\n" + "="*80)
    print("Example 3: Using IN operator")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.in_,
                            value=["amazon", "walmart", "target"]
                        )
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        )
    )

    sql = translate_query(query)
    print(sql)
    return query


def example_4_aggregate():
    """
    SELECT category, AVG(regular_price) AS avg_price
    FROM product_offers
    GROUP BY category
    """
    print("\n" + "="*80)
    print("Example 4: Aggregate with GROUP BY")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.regular_price,
                alias="avg_price"
            )
        ],
        from_=FromClause(table=Table.product_offers),
        group_by=GroupByClause(columns=[Column.category])
    )

    sql = translate_query(query)
    print(sql)
    return query


def example_5_order_limit():
    """
    SELECT vendor, regular_price
    FROM product_offers
    ORDER BY regular_price DESC
    LIMIT 10
    """
    print("\n" + "="*80)
    print("Example 5: ORDER BY with LIMIT")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        ],
        from_=FromClause(table=Table.product_offers),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.regular_price, direction=Direction.desc)
            ]
        ),
        limit=LimitClause(limit=10)
    )

    sql = translate_query(query)
    print(sql)
    return query


def example_6_count_by_category():
    """
    SELECT category, COUNT(*) AS product_count
    FROM product_offers
    GROUP BY category
    ORDER BY product_count DESC
    """
    print("\n" + "="*80)
    print("Example 6: COUNT by category")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,  # COUNT(*)
                alias="product_count"
            )
        ],
        from_=FromClause(table=Table.product_offers),
        group_by=GroupByClause(columns=[Column.category]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.desc)
            ]
        )
    )

    sql = translate_query(query)
    print(sql)
    return query


def example_7_between():
    """
    SELECT title, regular_price
    FROM product_offers
    WHERE regular_price BETWEEN 50 AND 100
    """
    print("\n" + "="*80)
    print("Example 7: BETWEEN condition")
    print("="*80)

    query = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            between_conditions=[
                BetweenCondition(
                    column=QualifiedColumn(column=Column.regular_price),
                    low=50,
                    high=100
                )
            ],
            group_logic=LogicOp.and_
        )
    )

    sql = translate_query(query)
    print(sql)
    return query


def main():
    """Run all basic examples."""
    print("\n" + "="*80)
    print(" BASIC QUERY EXAMPLES")
    print("="*80)

    examples = [
        example_1_simple_select,
        example_2_with_filter,
        example_3_in_operator,
        example_4_aggregate,
        example_5_order_limit,
        example_6_count_by_category,
        example_7_between,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print(" All examples completed!")
    print("="*80)


if __name__ == "__main__":
    main()
