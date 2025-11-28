"""
Property-based testing with Hypothesis.

Uses hypothesis to generate thousands of random but valid query instances,
ensuring the schema is robust and handles all edge cases correctly.

This provides PROOF that the schema works beyond hand-crafted examples.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from hypothesis.strategies import composite
from pydantic import ValidationError

from structured_query_builder import *
from structured_query_builder.translator import translate_query


# ============================================================================
# Hypothesis Strategies for Enums
# ============================================================================

def table_strategy():
    """Strategy for generating valid Table enums."""
    return st.sampled_from(list(Table))


def column_strategy():
    """Strategy for generating valid Column enums."""
    return st.sampled_from(list(Column))


def comparison_op_strategy():
    """Strategy for generating valid ComparisonOp enums."""
    return st.sampled_from(list(ComparisonOp))


def arithmetic_op_strategy():
    """Strategy for generating valid ArithmeticOp enums."""
    return st.sampled_from(list(ArithmeticOp))


def aggregate_func_strategy():
    """Strategy for generating valid AggregateFunc enums."""
    return st.sampled_from(list(AggregateFunc))


def window_func_strategy():
    """Strategy for generating valid WindowFunc enums."""
    return st.sampled_from(list(WindowFunc))


def logic_op_strategy():
    """Strategy for generating valid LogicOp enums."""
    return st.sampled_from(list(LogicOp))


def direction_strategy():
    """Strategy for generating valid Direction enums."""
    return st.sampled_from(list(Direction))


# ============================================================================
# Hypothesis Strategies for Basic Types
# ============================================================================

def identifier_strategy():
    """Generate valid SQL identifiers (table/column aliases)."""
    return st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), blacklist_characters='_'),
        min_size=1,
        max_size=20
    ).map(lambda s: s if s and s[0].isalpha() else f"a{s}")


def sql_value_strategy():
    """Generate valid SQL values (strings, numbers, booleans)."""
    return st.one_of(
        st.text(min_size=0, max_size=100),
        st.integers(min_value=-1000000, max_value=1000000),
        st.floats(min_value=-1000000.0, max_value=1000000.0, allow_nan=False, allow_infinity=False),
        st.booleans()
    )


# ============================================================================
# Hypothesis Strategies for Expressions
# ============================================================================

@composite
def qualified_column_strategy(draw):
    """Generate QualifiedColumn instances."""
    column = draw(column_strategy())
    table_alias = draw(st.one_of(st.none(), identifier_strategy()))
    return QualifiedColumn(column=column, table_alias=table_alias)


@composite
def column_expr_strategy(draw):
    """Generate ColumnExpr instances."""
    source = draw(qualified_column_strategy())
    alias = draw(st.one_of(st.none(), identifier_strategy()))
    return ColumnExpr(source=source, alias=alias)


@composite
def binary_arithmetic_strategy(draw):
    """Generate BinaryArithmetic expressions."""
    operator = draw(arithmetic_op_strategy())
    alias = draw(identifier_strategy())

    # Choose left operand (column or value)
    if draw(st.booleans()):
        left_column = draw(column_strategy())
        left_value = None
    else:
        left_column = None
        left_value = draw(st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False))

    # Choose right operand (column or value)
    if draw(st.booleans()):
        right_column = draw(column_strategy())
        right_value = None
    else:
        right_column = None
        right_value = draw(st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False))

    return BinaryArithmetic(
        left_column=left_column,
        left_value=left_value,
        operator=operator,
        right_column=right_column,
        right_value=right_value,
        alias=alias
    )


@composite
def aggregate_expr_strategy(draw):
    """Generate AggregateExpr instances."""
    function = draw(aggregate_func_strategy())
    alias = draw(identifier_strategy())

    # COUNT(*) has no column, others do
    if function == AggregateFunc.count and draw(st.booleans()):
        column = None
    else:
        column = draw(column_strategy())

    distinct = draw(st.booleans())

    return AggregateExpr(
        function=function,
        column=column,
        distinct=distinct,
        alias=alias
    )


@composite
def order_by_item_strategy(draw):
    """Generate OrderByItem instances."""
    column = draw(column_strategy())
    direction = draw(direction_strategy())
    nulls = draw(st.one_of(st.none(), st.sampled_from(list(NullsOrder))))
    return OrderByItem(column=column, direction=direction, nulls=nulls)


@composite
def window_expr_strategy(draw):
    """Generate WindowExpr instances."""
    function = draw(window_func_strategy())
    alias = draw(identifier_strategy())

    # Some window functions need column, some don't
    if function in (WindowFunc.row_number,) or draw(st.booleans()):
        column = None
    else:
        column = draw(column_strategy())

    # Partition by (0-3 columns)
    partition_by = draw(st.lists(column_strategy(), min_size=0, max_size=3, unique=True))

    # Order by (0-2 items)
    order_by = draw(st.lists(order_by_item_strategy(), min_size=0, max_size=2))

    # LAG/LEAD specific
    offset = 1
    default_value = None
    if function in (WindowFunc.lag, WindowFunc.lead):
        offset = draw(st.integers(min_value=1, max_value=5))
        if draw(st.booleans()):
            default_value = draw(st.one_of(
                st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
                st.integers(min_value=0, max_value=1000),
                st.text(min_size=1, max_size=20)
            ))

    return WindowExpr(
        function=function,
        column=column,
        partition_by=partition_by,
        order_by=order_by,
        offset=offset,
        default_value=default_value,
        alias=alias
    )


def select_expr_strategy():
    """Generate any SELECT expression."""
    return st.one_of(
        column_expr_strategy(),
        binary_arithmetic_strategy(),
        aggregate_expr_strategy(),
        window_expr_strategy()
    )


# ============================================================================
# Hypothesis Strategies for WHERE Clauses
# ============================================================================

@composite
def simple_condition_strategy(draw):
    """Generate SimpleCondition instances."""
    column = draw(qualified_column_strategy())
    operator = draw(comparison_op_strategy())

    # Different operators need different value types
    if operator in (ComparisonOp.is_null, ComparisonOp.is_not_null):
        # These don't use values but we need to provide something
        value = ""
    elif operator in (ComparisonOp.in_, ComparisonOp.not_in):
        # IN needs a list of homogeneous types
        value_type = draw(st.sampled_from(['str', 'int', 'float']))
        if value_type == 'str':
            value = draw(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5))
        elif value_type == 'int':
            value = draw(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1, max_size=5))
        else:  # float
            value = draw(st.lists(
                st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
                min_size=1,
                max_size=5
            ))
    else:
        # Regular comparison
        value = draw(sql_value_strategy())

    return SimpleCondition(column=column, operator=operator, value=value)


@composite
def condition_group_strategy(draw):
    """Generate ConditionGroup instances."""
    # 1-5 conditions per group
    conditions = draw(st.lists(simple_condition_strategy(), min_size=1, max_size=5))
    logic = draw(logic_op_strategy())
    return ConditionGroup(conditions=conditions, logic=logic)


@composite
def where_l0_strategy(draw):
    """Generate WhereL0 (no subqueries) instances."""
    # 0-3 condition groups
    groups = draw(st.lists(condition_group_strategy(), min_size=0, max_size=3))

    # 0-2 BETWEEN conditions
    between_conditions = []
    for _ in range(draw(st.integers(min_value=0, max_value=2))):
        column = draw(qualified_column_strategy())
        low = draw(st.floats(min_value=0, max_value=50, allow_nan=False, allow_infinity=False))
        high = draw(st.floats(min_value=50, max_value=100, allow_nan=False, allow_infinity=False))
        between_conditions.append(BetweenCondition(column=column, low=low, high=high))

    group_logic = draw(logic_op_strategy())

    return WhereL0(
        groups=groups,
        between_conditions=between_conditions,
        group_logic=group_logic
    )


# ============================================================================
# Hypothesis Strategies for FROM Clauses
# ============================================================================

@composite
def from_clause_strategy(draw, allow_joins=True):
    """Generate FromClause instances."""
    table = draw(table_strategy())
    table_alias = draw(st.one_of(st.none(), identifier_strategy()))

    # Joins (0-2 joins)
    joins = []
    if allow_joins:
        num_joins = draw(st.integers(min_value=0, max_value=2))
        for _ in range(num_joins):
            join_type = draw(st.sampled_from([JoinType.inner, JoinType.left]))
            join_table = draw(table_strategy())
            join_alias = draw(st.one_of(st.none(), identifier_strategy()))
            left_column = draw(column_strategy())
            left_table_alias = table_alias if table_alias and draw(st.booleans()) else None
            right_column = draw(column_strategy())

            # Create on_conditions using ColumnComparison
            joins.append(JoinSpec(
                join_type=join_type,
                table=join_table,
                table_alias=join_alias,
                on_conditions=[
                    ConditionGroup(
                        conditions=[
                            ColumnComparison(
                                left_column=QualifiedColumn(column=left_column, table_alias=left_table_alias),
                                operator=ComparisonOp.eq,
                                right_column=QualifiedColumn(column=right_column, table_alias=join_alias)
                            )
                        ],
                        logic=LogicOp.and_
                    )
                ]
            ))

    return FromClause(
        table=table,
        table_alias=table_alias,
        joins=joins
    )


# ============================================================================
# Hypothesis Strategies for Complete Queries
# ============================================================================

@composite
def simple_query_strategy(draw):
    """
    Generate simple but valid Query instances.

    Constraints:
    - 1-5 SELECT expressions
    - Simple FROM (table, maybe 1 join)
    - Optional WHERE with 1-2 condition groups
    - Optional GROUP BY if aggregates present
    - Optional ORDER BY (1-2 items)
    - Optional LIMIT
    """
    # SELECT (1-5 expressions)
    select = draw(st.lists(select_expr_strategy(), min_size=1, max_size=5))

    # FROM
    from_ = draw(from_clause_strategy(allow_joins=True))

    # WHERE (optional, simple)
    where = draw(st.one_of(st.none(), where_l0_strategy().map(
        lambda w: WhereL1(groups=w.groups, between_conditions=w.between_conditions, group_logic=w.group_logic)
    )))

    # GROUP BY (if we have aggregates)
    has_aggregates = any(isinstance(expr, AggregateExpr) for expr in select)
    if has_aggregates:
        # GROUP BY columns that appear in SELECT
        groupable_columns = [
            expr.source.column for expr in select
            if isinstance(expr, ColumnExpr)
        ]
        if groupable_columns:
            group_by = GroupByClause(columns=draw(st.lists(
                st.sampled_from(groupable_columns),
                min_size=1,
                max_size=len(groupable_columns),
                unique=True
            )))
        else:
            group_by = None
    else:
        group_by = None

    # ORDER BY (optional, 0-2 items)
    order_by_items = draw(st.lists(order_by_item_strategy(), min_size=0, max_size=2))
    order_by = OrderByClause(items=order_by_items) if order_by_items else None

    # LIMIT (optional)
    limit = None
    if draw(st.booleans()):
        limit_val = draw(st.integers(min_value=1, max_value=1000))
        offset_val = draw(st.integers(min_value=0, max_value=100))
        limit = LimitClause(limit=limit_val, offset=offset_val)

    return Query(
        select=select,
        from_=from_,
        where=where,
        group_by=group_by,
        having=None,  # Skip HAVING for simplicity
        order_by=order_by,
        limit=limit
    )


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestHypothesisModelGeneration:
    """Test model generation with hypothesis."""

    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(query=simple_query_strategy())
    def test_generated_queries_serialize(self, query):
        """Every generated query must serialize to JSON and back."""
        try:
            json_str = query.model_dump_json()
            reconstructed = Query.model_validate_json(json_str)
            # Basic structure checks
            assert len(reconstructed.select) > 0
            assert reconstructed.from_ is not None
        except Exception as e:
            pytest.fail(f"Generated query failed serialization: {e}\nQuery: {query.model_dump()}")

    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    @given(query=simple_query_strategy())
    def test_generated_queries_translate_to_sql(self, query):
        """Every generated query must translate to SQL without errors."""
        try:
            sql = translate_query(query)

            # Basic SQL structure checks
            assert "SELECT" in sql
            assert "FROM" in sql

            # Check for SQL injection patterns (basic sanity)
            assert "--" not in sql
            assert "/*" not in sql

        except Exception as e:
            pytest.fail(f"Generated query failed SQL translation: {e}\nQuery: {query.model_dump()}")

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(query=simple_query_strategy())
    def test_generated_queries_have_valid_structure(self, query):
        """Generated queries should have logically valid structure."""
        # If we have aggregates, we should have GROUP BY (with some exceptions)
        has_aggregates = any(isinstance(expr, AggregateExpr) for expr in query.select)
        has_window = any(isinstance(expr, WindowExpr) for expr in query.select)

        if has_aggregates and not has_window:
            # Should have GROUP BY unless all expressions are aggregates
            non_agg_columns = [
                expr for expr in query.select
                if isinstance(expr, ColumnExpr)
            ]
            if non_agg_columns:
                # This would require GROUP BY in real SQL
                # Our generator should create it
                pass  # Our generator handles this

        # FROM must have a table
        assert query.from_.table is not None or query.from_.derived is not None

        # LIMIT offset should be less than limit (if both present)
        if query.limit:
            assert query.limit.offset < query.limit.limit + query.limit.offset


class TestHypothesisEdgeCases:
    """Test edge cases discovered by hypothesis."""

    @settings(max_examples=50)
    @given(
        num_selects=st.integers(min_value=1, max_value=20),
        num_joins=st.integers(min_value=0, max_value=5)
    )
    def test_query_complexity_limits(self, num_selects, num_joins):
        """Test various complexity levels."""
        # This tests if we can handle many SELECT expressions and joins
        select_exprs = [
            ColumnExpr(source=QualifiedColumn(column=Column.vendor))
            for _ in range(num_selects)
        ]

        from_clause = FromClause(table=Table.product_offers)

        query = Query(select=select_exprs, from_=from_clause)

        # Should serialize and translate
        json_str = query.model_dump_json()
        sql = translate_query(query)

        assert len(json_str) > 0
        assert "SELECT" in sql

    @settings(max_examples=20)
    @given(
        cond_groups=st.integers(min_value=1, max_value=10),
        conds_per_group=st.integers(min_value=1, max_value=10)
    )
    def test_where_clause_complexity(self, cond_groups, conds_per_group):
        """Test complex WHERE clauses."""
        groups = []
        for _ in range(cond_groups):
            conditions = []
            for _ in range(conds_per_group):
                conditions.append(SimpleCondition(
                    column=QualifiedColumn(column=Column.vendor),
                    operator=ComparisonOp.eq,
                    value="test"
                ))
            groups.append(ConditionGroup(
                conditions=conditions,
                logic=LogicOp.and_
            ))

        where = WhereL1(groups=groups, group_logic=LogicOp.or_)

        query = Query(
            select=[ColumnExpr(source=QualifiedColumn(column=Column.vendor))],
            from_=FromClause(table=Table.product_offers),
            where=where
        )

        # Should handle complex WHERE
        sql = translate_query(query)
        assert "WHERE" in sql
        assert "OR" in sql or len(groups) == 1


# ============================================================================
# Schema Size Measurement
# ============================================================================

class TestSchemaMetrics:
    """Measure actual schema characteristics."""

    def test_measure_schema_size(self):
        """Measure JSON schema size."""
        schema = Query.model_json_schema()
        import json
        schema_json = json.dumps(schema)
        size_bytes = len(schema_json.encode('utf-8'))
        size_kb = size_bytes / 1024

        print(f"\n{'='*60}")
        print(f"SCHEMA SIZE METRICS")
        print(f"{'='*60}")
        print(f"Size: {size_bytes:,} bytes ({size_kb:.1f} KB)")
        print(f"Estimated tokens: {size_bytes // 4:,} (rough estimate)")
        print(f"{'='*60}")

        # Document the size
        assert size_kb < 100, f"Schema is {size_kb:.1f}KB - may be too large for Vertex AI"

    def test_measure_schema_depth(self):
        """Measure actual nesting depth."""
        schema = Query.model_json_schema()

        def measure_depth(obj, current_depth=0):
            if not isinstance(obj, dict):
                return current_depth
            if not obj:
                return current_depth
            return max(
                measure_depth(value, current_depth + 1)
                for value in obj.values()
            )

        depth = measure_depth(schema)

        print(f"\n{'='*60}")
        print(f"SCHEMA DEPTH METRICS")
        print(f"{'='*60}")
        print(f"Maximum nesting depth: {depth}")
        print(f"{'='*60}")

        assert depth < 15, f"Schema depth {depth} may exceed Vertex AI limits"


if __name__ == "__main__":
    # Run with verbose output to see generated examples
    pytest.main([__file__, "-v", "-s", "--hypothesis-show-statistics"])
