"""
Unit tests for SQL translator.

Tests translation from Pydantic models to SQL strings.
"""

import pytest
from structured_query_builder import *
from structured_query_builder.translator import translate_query, SQLTranslator


class TestBasicTranslation:
    """Test basic translation cases."""

    def test_simple_select(self):
        """SELECT vendor, category FROM product_offers"""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
                ColumnExpr(source=QualifiedColumn(column=Column.category))
            ],
            from_=FromClause(table=Table.product_offers)
        )
        sql = translate_query(query)
        assert "SELECT vendor" in sql
        assert "category" in sql
        assert "FROM product_offers" in sql

    def test_select_with_alias(self):
        """SELECT vendor AS vendor_name FROM product_offers"""
        query = Query(
            select=[
                ColumnExpr(
                    source=QualifiedColumn(column=Column.vendor),
                    alias="vendor_name"
                )
            ],
            from_=FromClause(table=Table.product_offers)
        )
        sql = translate_query(query)
        assert "AS vendor_name" in sql


class TestArithmeticTranslation:
    """Test arithmetic expression translation."""

    def test_binary_arithmetic(self):
        """SELECT regular_price - markdown_price AS discount"""
        query = Query(
            select=[
                BinaryArithmetic(
                    left_column=Column.regular_price,
                    operator=ArithmeticOp.subtract,
                    right_column=Column.markdown_price,
                    alias="discount"
                )
            ],
            from_=FromClause(table=Table.product_offers)
        )
        sql = translate_query(query)
        assert "regular_price - markdown_price" in sql
        assert "AS discount" in sql

    def test_compound_arithmetic(self):
        """SELECT (regular_price - markdown_price) / regular_price AS discount_pct"""
        query = Query(
            select=[
                CompoundArithmetic(
                    inner_left_column=Column.regular_price,
                    inner_operator=ArithmeticOp.subtract,
                    inner_right_column=Column.markdown_price,
                    outer_operator=ArithmeticOp.divide,
                    outer_column=Column.regular_price,
                    alias="discount_pct"
                )
            ],
            from_=FromClause(table=Table.product_offers)
        )
        sql = translate_query(query)
        assert "regular_price - markdown_price" in sql
        assert "/ regular_price" in sql


class TestAggregateTranslation:
    """Test aggregate function translation."""

    def test_simple_aggregate(self):
        """SELECT AVG(regular_price) AS avg_price FROM product_offers"""
        query = Query(
            select=[
                AggregateExpr(
                    function=AggregateFunc.avg,
                    column=Column.regular_price,
                    alias="avg_price"
                )
            ],
            from_=FromClause(table=Table.product_offers)
        )
        sql = translate_query(query)
        assert "AVG(regular_price)" in sql
        assert "AS avg_price" in sql

    def test_count_star(self):
        """SELECT COUNT(*) AS total FROM product_offers"""
        query = Query(
            select=[
                AggregateExpr(
                    function=AggregateFunc.count,
                    column=None,
                    alias="total"
                )
            ],
            from_=FromClause(table=Table.product_offers)
        )
        sql = translate_query(query)
        assert "COUNT(*)" in sql

    def test_group_by(self):
        """SELECT vendor, AVG(regular_price) FROM product_offers GROUP BY vendor"""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
                AggregateExpr(
                    function=AggregateFunc.avg,
                    column=Column.regular_price,
                    alias="avg_price"
                )
            ],
            from_=FromClause(table=Table.product_offers),
            group_by=GroupByClause(columns=[Column.vendor])
        )
        sql = translate_query(query)
        assert "GROUP BY vendor" in sql


class TestWindowTranslation:
    """Test window function translation."""

    def test_rank_window(self):
        """SELECT RANK() OVER (PARTITION BY category ORDER BY regular_price ASC) AS rank"""
        query = Query(
            select=[
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
        assert "RANK(" in sql
        assert "PARTITION BY category" in sql
        assert "ORDER BY regular_price ASC" in sql

    def test_lag_window(self):
        """SELECT LAG(regular_price, 1, 0) OVER (PARTITION BY vendor ORDER BY created_at)"""
        query = Query(
            select=[
                WindowExpr(
                    function=WindowFunc.lag,
                    column=Column.regular_price,
                    partition_by=[Column.vendor],
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
        assert "LAG(regular_price" in sql
        assert "PARTITION BY vendor" in sql


class TestCaseTranslation:
    """Test CASE expression translation."""

    def test_case_expression(self):
        """SELECT CASE WHEN price < 50 THEN 'cheap' ELSE 'expensive' END AS tier"""
        query = Query(
            select=[
                CaseExpr(
                    whens=[
                        CaseWhen(
                            condition_column=Column.regular_price,
                            condition_operator=ComparisonOp.lt,
                            condition_value=50,
                            then_value="cheap"
                        )
                    ],
                    else_value="expensive",
                    alias="price_tier"
                )
            ],
            from_=FromClause(table=Table.product_offers)
        )
        sql = translate_query(query)
        assert "CASE" in sql
        assert "WHEN regular_price < 50" in sql
        assert "THEN 'cheap'" in sql
        assert "ELSE 'expensive'" in sql
        assert "AS price_tier" in sql


class TestWhereTranslation:
    """Test WHERE clause translation."""

    def test_simple_where(self):
        """SELECT * FROM product_offers WHERE vendor = 'amazon'"""
        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.vendor))],
            from_=FromClause(table=Table.product_offers),
            where=WhereL1(
                groups=[
                    ConditionGroup(
                        conditions=[
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
        assert "WHERE vendor = 'amazon'" in sql

    def test_in_condition(self):
        """SELECT * FROM product_offers WHERE category IN ('electronics', 'books')"""
        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.category))],
            from_=FromClause(table=Table.product_offers),
            where=WhereL1(
                groups=[
                    ConditionGroup(
                        conditions=[
                            SimpleCondition(
                                column=QualifiedColumn(column=Column.category),
                                operator=ComparisonOp.in_,
                                value=["electronics", "books"]
                            )
                        ],
                        logic=LogicOp.and_
                    )
                ],
                group_logic=LogicOp.and_
            )
        )
        sql = translate_query(query)
        assert "IN ('electronics', 'books')" in sql

    def test_between_condition(self):
        """SELECT * FROM product_offers WHERE price BETWEEN 10 AND 100"""
        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.regular_price))],
            from_=FromClause(table=Table.product_offers),
            where=WhereL1(
                between_conditions=[
                    BetweenCondition(
                        column=QualifiedColumn(column=Column.regular_price),
                        low=10,
                        high=100
                    )
                ],
                group_logic=LogicOp.and_
            )
        )
        sql = translate_query(query)
        assert "BETWEEN 10 AND 100" in sql

    def test_complex_where(self):
        """Test (A AND B) OR (C AND D)"""
        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.vendor))],
            from_=FromClause(table=Table.product_offers),
            where=WhereL1(
                groups=[
                    ConditionGroup(
                        conditions=[
                            SimpleCondition(
                                column=QualifiedColumn(column=Column.vendor),
                                operator=ComparisonOp.eq,
                                value="amazon"
                            ),
                            SimpleCondition(
                                column=QualifiedColumn(column=Column.category),
                                operator=ComparisonOp.eq,
                                value="electronics"
                            )
                        ],
                        logic=LogicOp.and_
                    ),
                    ConditionGroup(
                        conditions=[
                            SimpleCondition(
                                column=QualifiedColumn(column=Column.vendor),
                                operator=ComparisonOp.eq,
                                value="walmart"
                            ),
                            SimpleCondition(
                                column=QualifiedColumn(column=Column.category),
                                operator=ComparisonOp.eq,
                                value="books"
                            )
                        ],
                        logic=LogicOp.and_
                    )
                ],
                group_logic=LogicOp.or_
            )
        )
        sql = translate_query(query)
        assert "vendor = 'amazon'" in sql
        assert "category = 'electronics'" in sql
        assert "OR" in sql


class TestJoinTranslation:
    """Test JOIN translation."""

    def test_simple_join(self):
        """SELECT * FROM product_offers po JOIN id_mapping im ON po.id = im.product_match_id"""
        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.id))],
            from_=FromClause(
                table=Table.product_offers,
                table_alias="po",
                joins=[
                    JoinSpec(
                        join_type=JoinType.inner,
                        table=Table.id_mapping,
                        table_alias="im",
                        left_column=Column.id,
                        left_table_alias="po",
                        right_column=Column.product_match_id
                    )
                ]
            )
        )
        sql = translate_query(query)
        assert "FROM product_offers AS po" in sql
        assert "INNER JOIN id_mapping AS im" in sql
        assert "ON po.id = im.product_match_id" in sql

    def test_self_join(self):
        """Test self-join for competitor comparison."""
        query = Query(
            select=[
                ColumnExpr(
                    source=QualifiedColumn(
                        table_alias="ours",
                        column=Column.regular_price
                    ),
                    alias="our_price"
                ),
                ColumnExpr(
                    source=QualifiedColumn(
                        table_alias="theirs",
                        column=Column.regular_price
                    ),
                    alias="their_price"
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
        assert "ours.regular_price AS our_price" in sql
        assert "theirs.regular_price AS their_price" in sql


class TestSubqueryTranslation:
    """Test subquery translation."""

    def test_scalar_subquery_in_where(self):
        """SELECT * FROM product_offers WHERE price > (SELECT AVG(price) FROM product_offers)"""
        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.regular_price))],
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
                            )
                        )
                    )
                ],
                group_logic=LogicOp.and_
            )
        )
        sql = translate_query(query)
        assert "WHERE regular_price >" in sql
        assert "(SELECT AVG(regular_price)" in sql


class TestOrderByLimit:
    """Test ORDER BY and LIMIT translation."""

    def test_order_by(self):
        """SELECT * FROM product_offers ORDER BY regular_price DESC"""
        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.regular_price))],
            from_=FromClause(table=Table.product_offers),
            order_by=OrderByClause(
                items=[
                    OrderByItem(column=Column.regular_price, direction=Direction.desc)
                ]
            )
        )
        sql = translate_query(query)
        assert "ORDER BY regular_price DESC" in sql

    def test_limit(self):
        """SELECT * FROM product_offers LIMIT 10"""
        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.vendor))],
            from_=FromClause(table=Table.product_offers),
            limit=LimitClause(limit=10)
        )
        sql = translate_query(query)
        assert "LIMIT 10" in sql

    def test_limit_offset(self):
        """SELECT * FROM product_offers LIMIT 10 OFFSET 20"""
        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.vendor))],
            from_=FromClause(table=Table.product_offers),
            limit=LimitClause(limit=10, offset=20)
        )
        sql = translate_query(query)
        assert "LIMIT 10 OFFSET 20" in sql


class TestComplexQueries:
    """Test complex realistic queries."""

    def test_pricing_analyst_query_1(self):
        """
        Average price by category, filtered by vendor, sorted by average descending.
        SELECT category, AVG(regular_price) AS avg_price
        FROM product_offers
        WHERE vendor IN ('amazon', 'walmart')
        GROUP BY category
        HAVING AVG(regular_price) > 50
        ORDER BY avg_price DESC
        LIMIT 10
        """
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
            where=WhereL1(
                groups=[
                    ConditionGroup(
                        conditions=[
                            SimpleCondition(
                                column=QualifiedColumn(column=Column.vendor),
                                operator=ComparisonOp.in_,
                                value=["amazon", "walmart"]
                            )
                        ],
                        logic=LogicOp.and_
                    )
                ],
                group_logic=LogicOp.and_
            ),
            group_by=GroupByClause(columns=[Column.category]),
            having=HavingClause(
                conditions=[
                    HavingCondition(
                        function=AggregateFunc.avg,
                        column=Column.regular_price,
                        operator=ComparisonOp.gt,
                        value=50
                    )
                ],
                logic=LogicOp.and_
            ),
            order_by=OrderByClause(
                items=[OrderByItem(column=Column.regular_price, direction=Direction.desc)]
            ),
            limit=LimitClause(limit=10)
        )
        sql = translate_query(query)
        assert "SELECT category" in sql
        assert "AVG(regular_price)" in sql
        assert "WHERE vendor IN ('amazon', 'walmart')" in sql
        assert "GROUP BY category" in sql
        assert "HAVING AVG(regular_price) > 50" in sql
        assert "LIMIT 10" in sql

    def test_pricing_analyst_query_2(self):
        """
        Products with discount percentage.
        SELECT title, regular_price, markdown_price,
               (regular_price - markdown_price) / regular_price AS discount_pct
        FROM product_offers
        WHERE is_markdown = TRUE
        ORDER BY discount_pct DESC
        """
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
            )
        )
        sql = translate_query(query)
        assert "title" in sql
        assert "regular_price - markdown_price" in sql
        assert "is_markdown = TRUE" in sql
