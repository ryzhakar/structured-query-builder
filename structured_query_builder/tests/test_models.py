"""
Unit tests for Pydantic models.

Tests model construction, validation, and serialization to ensure
compatibility with LLM structured outputs.
"""

import pytest
from pydantic import ValidationError
from structured_query_builder import *


class TestEnums:
    """Test enum definitions."""

    def test_table_enum(self):
        assert Table.product_offers.value == "product_offers"
        assert len(Table) >= 4

    def test_column_enum(self):
        assert Column.regular_price.value == "regular_price"
        assert Column.vendor.value == "vendor"

    def test_operators(self):
        assert ComparisonOp.eq.value == "="
        assert ComparisonOp.in_.value == "IN"
        assert ArithmeticOp.divide.value == "/"


class TestExpressions:
    """Test SELECT expression models."""

    def test_column_expr(self):
        expr = ColumnExpr(
            source=QualifiedColumn(column=Column.vendor),
            alias="vendor_name"
        )
        assert expr.expr_type == "column"
        assert expr.source.column == Column.vendor
        assert expr.alias == "vendor_name"

    def test_qualified_column_with_alias(self):
        col = QualifiedColumn(
            table_alias="ours",
            column=Column.regular_price
        )
        assert col.table_alias == "ours"
        assert col.column == Column.regular_price

    def test_binary_arithmetic(self):
        expr = BinaryArithmetic(
            left_column=Column.regular_price,
            operator=ArithmeticOp.subtract,
            right_column=Column.markdown_price,
            alias="discount_amount"
        )
        assert expr.expr_type == "binary_arithmetic"
        assert expr.left_column == Column.regular_price
        assert expr.alias == "discount_amount"

    def test_compound_arithmetic(self):
        # (regular_price - markdown_price) / regular_price * 100
        expr = CompoundArithmetic(
            inner_left_column=Column.regular_price,
            inner_operator=ArithmeticOp.subtract,
            inner_right_column=Column.markdown_price,
            outer_operator=ArithmeticOp.divide,
            outer_column=Column.regular_price,
            alias="discount_percent"
        )
        assert expr.expr_type == "compound_arithmetic"
        assert expr.inner_operator == ArithmeticOp.subtract
        assert expr.outer_operator == ArithmeticOp.divide

    def test_aggregate_expr(self):
        expr = AggregateExpr(
            function=AggregateFunc.avg,
            column=Column.regular_price,
            alias="avg_price"
        )
        assert expr.expr_type == "aggregate"
        assert expr.function == AggregateFunc.avg
        assert not expr.distinct

    def test_aggregate_count_star(self):
        expr = AggregateExpr(
            function=AggregateFunc.count,
            column=None,
            alias="total_count"
        )
        assert expr.column is None

    def test_window_expr_rank(self):
        expr = WindowExpr(
            function=WindowFunc.rank,
            column=Column.regular_price,
            partition_by=[Column.category],
            order_by=[
                OrderByItem(column=Column.regular_price, direction=Direction.asc)
            ],
            alias="price_rank"
        )
        assert expr.expr_type == "window"
        assert expr.function == WindowFunc.rank
        assert len(expr.partition_by) == 1

    def test_window_expr_lag(self):
        expr = WindowExpr(
            function=WindowFunc.lag,
            column=Column.regular_price,
            partition_by=[Column.vendor],
            order_by=[
                OrderByItem(column=Column.created_at, direction=Direction.asc)
            ],
            offset=1,
            default_value=0.0,
            alias="prev_price"
        )
        assert expr.function == WindowFunc.lag
        assert expr.offset == 1
        assert expr.default_value == 0.0

    def test_case_expr(self):
        expr = CaseExpr(
            whens=[
                CaseWhen(
                    condition_column=Column.regular_price,
                    condition_operator=ComparisonOp.lt,
                    condition_value=50,
                    then_value="cheap"
                ),
                CaseWhen(
                    condition_column=Column.regular_price,
                    condition_operator=ComparisonOp.lt,
                    condition_value=100,
                    then_value="medium"
                )
            ],
            else_value="expensive",
            alias="price_tier"
        )
        assert expr.expr_type == "case"
        assert len(expr.whens) == 2
        assert expr.else_value == "expensive"


class TestConditions:
    """Test WHERE clause condition models."""

    def test_simple_condition(self):
        cond = SimpleCondition(
            column=QualifiedColumn(column=Column.vendor),
            operator=ComparisonOp.eq,
            value="amazon"
        )
        assert cond.operator == ComparisonOp.eq
        assert cond.value == "amazon"

    def test_in_condition(self):
        cond = SimpleCondition(
            column=QualifiedColumn(column=Column.category),
            operator=ComparisonOp.in_,
            value=["electronics", "books", "toys"]
        )
        assert cond.operator == ComparisonOp.in_
        assert isinstance(cond.value, list)
        assert len(cond.value) == 3

    def test_between_condition(self):
        cond = BetweenCondition(
            column=QualifiedColumn(column=Column.regular_price),
            low=10.0,
            high=100.0
        )
        assert cond.low == 10.0
        assert cond.high == 100.0

    def test_condition_group(self):
        group = ConditionGroup(
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
        )
        assert len(group.conditions) == 2
        assert group.logic == LogicOp.and_

    def test_where_l0(self):
        where = WhereL0(
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
        assert len(where.groups) == 1
        assert where.group_logic == LogicOp.and_

    def test_scalar_subquery(self):
        subq = ScalarSubquery(
            table=Table.product_offers,
            aggregate=AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.regular_price,
                alias="avg_price"
            ),
            where=WhereL0(
                groups=[
                    ConditionGroup(
                        conditions=[
                            SimpleCondition(
                                column=QualifiedColumn(column=Column.category),
                                operator=ComparisonOp.eq,
                                value="electronics"
                            )
                        ],
                        logic=LogicOp.and_
                    )
                ],
                group_logic=LogicOp.and_
            )
        )
        assert subq.table == Table.product_offers
        assert subq.aggregate.function == AggregateFunc.avg

    def test_where_l1_with_subquery(self):
        where = WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.category),
                            operator=ComparisonOp.eq,
                            value="electronics"
                        )
                    ],
                    logic=LogicOp.and_
                )
            ],
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
        assert len(where.subquery_conditions) == 1


class TestFromJoin:
    """Test FROM and JOIN models."""

    def test_simple_from(self):
        from_clause = FromClause(
            table=Table.product_offers
        )
        assert from_clause.table == Table.product_offers
        assert from_clause.table_alias is None

    def test_from_with_alias(self):
        from_clause = FromClause(
            table=Table.product_offers,
            table_alias="po"
        )
        assert from_clause.table_alias == "po"

    def test_join_spec(self):
        join = JoinSpec(
            join_type=JoinType.inner,
            table=Table.id_mapping,
            table_alias="im",
            left_column=Column.id,
            left_table_alias="po",
            right_column=Column.product_match_id
        )
        assert join.join_type == JoinType.inner
        assert join.table == Table.id_mapping
        assert join.table_alias == "im"

    def test_self_join(self):
        # Self-join for competitor comparison
        from_clause = FromClause(
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
        assert from_clause.table_alias == "ours"
        assert len(from_clause.joins) == 1
        assert from_clause.joins[0].table_alias == "theirs"

    def test_derived_table(self):
        derived = DerivedTable(
            select=[
                ColumnExpr(
                    source=QualifiedColumn(column=Column.vendor)
                ),
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
            from_table=Table.product_offers,
            alias="ranked"
        )
        assert len(derived.select) == 2
        assert derived.alias == "ranked"


class TestAggregation:
    """Test GROUP BY and HAVING models."""

    def test_group_by(self):
        group_by = GroupByClause(
            columns=[Column.vendor, Column.category]
        )
        assert len(group_by.columns) == 2

    def test_having(self):
        having = HavingClause(
            conditions=[
                HavingCondition(
                    function=AggregateFunc.avg,
                    column=Column.regular_price,
                    operator=ComparisonOp.gt,
                    value=50
                )
            ],
            logic=LogicOp.and_
        )
        assert len(having.conditions) == 1
        assert having.conditions[0].value == 50


class TestOrdering:
    """Test ORDER BY and LIMIT models."""

    def test_order_by(self):
        order_by = OrderByClause(
            items=[
                OrderByItem(column=Column.regular_price, direction=Direction.desc),
                OrderByItem(column=Column.vendor, direction=Direction.asc)
            ]
        )
        assert len(order_by.items) == 2
        assert order_by.items[0].direction == Direction.desc

    def test_limit(self):
        limit = LimitClause(limit=100, offset=50)
        assert limit.limit == 100
        assert limit.offset == 50


class TestCompleteQuery:
    """Test complete Query model construction."""

    def test_simple_query(self):
        """SELECT vendor, category, AVG(regular_price) FROM product_offers GROUP BY vendor, category"""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
                ColumnExpr(source=QualifiedColumn(column=Column.category)),
                AggregateExpr(
                    function=AggregateFunc.avg,
                    column=Column.regular_price,
                    alias="avg_price"
                )
            ],
            from_=FromClause(table=Table.product_offers),
            group_by=GroupByClause(columns=[Column.vendor, Column.category])
        )
        assert len(query.select) == 3
        assert query.group_by is not None

    def test_query_with_where(self):
        """SELECT * FROM product_offers WHERE category = 'electronics' AND vendor IN ('amazon', 'walmart')"""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.id)),
                ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
                ColumnExpr(source=QualifiedColumn(column=Column.category))
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
                                operator=ComparisonOp.in_,
                                value=["amazon", "walmart"]
                            )
                        ],
                        logic=LogicOp.and_
                    )
                ],
                group_logic=LogicOp.and_
            )
        )
        assert query.where is not None
        assert len(query.where.groups) == 1

    def test_query_json_serialization(self):
        """Test that queries can be serialized to JSON (important for LLM structured outputs)."""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.vendor))
            ],
            from_=FromClause(table=Table.product_offers)
        )

        # Should serialize without error
        json_str = query.model_dump_json()
        assert "vendor" in json_str
        assert "product_offers" in json_str

        # Should deserialize back
        reconstructed = Query.model_validate_json(json_str)
        assert reconstructed.select[0].source.column == Column.vendor
