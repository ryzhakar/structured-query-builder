"""
SQL translator for converting Pydantic query models to SQL strings.

Each model type has a deterministic translation to SQL.
Handles proper quoting, escaping, and formatting.
"""

from typing import Union
from .query import Query
from .expressions import (
    ColumnExpr,
    BinaryArithmetic,
    CompoundArithmetic,
    AggregateExpr,
    WindowExpr,
    CaseExpr,
    QualifiedColumn,
    SelectExpr,
)
from .clauses import (
    SimpleCondition,
    BetweenCondition,
    ConditionGroup,
    WhereL0,
    WhereL1,
    ScalarSubquery,
    SubqueryCondition,
    FromClause,
    JoinSpec,
    DerivedTable,
    GroupByClause,
    HavingCondition,
    HavingClause,
    OrderByClause,
    LimitClause,
)
from .enums import ComparisonOp, AggregateFunc


class SQLTranslator:
    """
    Translates Pydantic query models to SQL strings.

    Design principles:
    - Each model type has exactly one translation
    - Output is properly formatted and ready to execute
    - No additional validation (models are correct by construction)
    """

    def translate(self, query: Query) -> str:
        """
        Translate a complete Query to SQL.

        Returns a formatted, executable SQL string.
        """
        parts = []

        # SELECT clause
        parts.append(self._translate_select(query.select))

        # FROM clause
        parts.append(self._translate_from(query.from_))

        # WHERE clause
        if query.where:
            parts.append(self._translate_where(query.where))

        # GROUP BY clause
        if query.group_by:
            parts.append(self._translate_group_by(query.group_by))

        # HAVING clause
        if query.having:
            parts.append(self._translate_having(query.having))

        # ORDER BY clause
        if query.order_by:
            parts.append(self._translate_order_by(query.order_by))

        # LIMIT clause
        if query.limit:
            parts.append(self._translate_limit(query.limit))

        return "\n".join(parts)

    # ========================================================================
    # SELECT Expressions
    # ========================================================================

    def _translate_select(self, expressions: list[SelectExpr]) -> str:
        """Translate SELECT clause."""
        expr_strs = [self._translate_select_expr(expr) for expr in expressions]
        return "SELECT " + ",\n       ".join(expr_strs)

    def _translate_select_expr(self, expr: SelectExpr) -> str:
        """Translate a single SELECT expression."""
        if isinstance(expr, ColumnExpr):
            return self._translate_column_expr(expr)
        elif isinstance(expr, BinaryArithmetic):
            return self._translate_binary_arithmetic(expr)
        elif isinstance(expr, CompoundArithmetic):
            return self._translate_compound_arithmetic(expr)
        elif isinstance(expr, AggregateExpr):
            return self._translate_aggregate(expr)
        elif isinstance(expr, WindowExpr):
            return self._translate_window(expr)
        elif isinstance(expr, CaseExpr):
            return self._translate_case(expr)
        else:
            raise ValueError(f"Unknown expression type: {type(expr)}")

    def _translate_qualified_column(self, col: QualifiedColumn) -> str:
        """Translate a qualified column reference."""
        if col.table_alias:
            return f"{col.table_alias}.{col.column.value}"
        return col.column.value

    def _translate_column_expr(self, expr: ColumnExpr) -> str:
        """Translate simple column selection."""
        col_str = self._translate_qualified_column(expr.source)
        if expr.alias:
            return f"{col_str} AS {expr.alias}"
        return col_str

    def _translate_binary_arithmetic(self, expr: BinaryArithmetic) -> str:
        """Translate two-operand arithmetic."""
        # Left operand
        if expr.left_column:
            if expr.left_table_alias:
                left = f"{expr.left_table_alias}.{expr.left_column.value}"
            else:
                left = expr.left_column.value
        elif expr.left_value is not None:
            left = str(expr.left_value)
        else:
            raise ValueError("Binary arithmetic must have left operand")

        # Right operand
        if expr.right_column:
            if expr.right_table_alias:
                right = f"{expr.right_table_alias}.{expr.right_column.value}"
            else:
                right = expr.right_column.value
        elif expr.right_value is not None:
            right = str(expr.right_value)
        else:
            raise ValueError("Binary arithmetic must have right operand")

        return f"({left} {expr.operator.value} {right}) AS {expr.alias}"

    def _translate_compound_arithmetic(self, expr: CompoundArithmetic) -> str:
        """Translate three-operand nested arithmetic."""
        # Inner expression
        if expr.inner_left_column:
            inner_left = expr.inner_left_column.value
        elif expr.inner_left_value is not None:
            inner_left = str(expr.inner_left_value)
        else:
            raise ValueError("Compound arithmetic must have inner left operand")

        if expr.inner_right_column:
            inner_right = expr.inner_right_column.value
        elif expr.inner_right_value is not None:
            inner_right = str(expr.inner_right_value)
        else:
            raise ValueError("Compound arithmetic must have inner right operand")

        inner = f"({inner_left} {expr.inner_operator.value} {inner_right})"

        # Outer operand
        if expr.outer_column:
            outer = expr.outer_column.value
        elif expr.outer_value is not None:
            outer = str(expr.outer_value)
        else:
            raise ValueError("Compound arithmetic must have outer operand")

        return f"({inner} {expr.outer_operator.value} {outer}) AS {expr.alias}"

    def _translate_aggregate(self, expr: AggregateExpr) -> str:
        """Translate aggregate function."""
        func = expr.function.value

        # Handle COUNT(*)
        if expr.column is None:
            if expr.function == AggregateFunc.count:
                arg = "*"
            else:
                raise ValueError(f"{func} requires a column argument")
        else:
            arg = expr.column.value
            if expr.distinct:
                arg = f"DISTINCT {arg}"

        return f"{func}({arg}) AS {expr.alias}"

    def _translate_window(self, expr: WindowExpr) -> str:
        """Translate window function."""
        func = expr.function.value

        # Function argument
        if expr.column is None:
            if expr.function.value == "COUNT":
                arg = "*"
            else:
                arg = ""
        else:
            arg = expr.column.value

        # Handle LAG/LEAD with offset and default
        if expr.function.value in ("LAG", "LEAD"):
            parts = [arg] if arg else []
            if expr.offset != 1:
                parts.append(str(expr.offset))
            if expr.default_value is not None:
                if isinstance(expr.default_value, str):
                    parts.append(f"'{expr.default_value}'")
                else:
                    parts.append(str(expr.default_value))
            arg = ", ".join(parts)

        # OVER clause
        over_parts = []

        if expr.partition_by:
            partition_cols = ", ".join(col.value for col in expr.partition_by)
            over_parts.append(f"PARTITION BY {partition_cols}")

        if expr.order_by:
            order_items = ", ".join(
                f"{item.column.value} {item.direction.value}"
                for item in expr.order_by
            )
            over_parts.append(f"ORDER BY {order_items}")

        over_clause = " ".join(over_parts)

        return f"{func}({arg}) OVER ({over_clause}) AS {expr.alias}"

    def _translate_case(self, expr: CaseExpr) -> str:
        """Translate CASE expression."""
        parts = ["CASE"]

        for when in expr.whens:
            # Condition
            cond_col = when.condition_column.value
            cond_op = when.condition_operator.value
            cond_val = self._format_value(when.condition_value)
            parts.append(f"WHEN {cond_col} {cond_op} {cond_val}")

            # Result
            if when.then_column:
                result = when.then_column.value
            elif when.then_value is not None:
                result = self._format_value(when.then_value)
            else:
                raise ValueError("CASE WHEN must have THEN value")
            parts.append(f"THEN {result}")

        # ELSE clause
        if expr.else_column:
            else_val = expr.else_column.value
        elif expr.else_value is not None:
            else_val = self._format_value(expr.else_value)
        else:
            else_val = "NULL"
        parts.append(f"ELSE {else_val}")

        parts.append(f"END AS {expr.alias}")

        return " ".join(parts)

    # ========================================================================
    # WHERE Clause
    # ========================================================================

    def _translate_where(self, where: WhereL1) -> str:
        """Translate WHERE clause (level 1 with subqueries)."""
        conditions = []

        # Simple condition groups
        for group in where.groups:
            conditions.append(self._translate_condition_group(group))

        # BETWEEN conditions
        for between in where.between_conditions:
            col = self._translate_qualified_column(between.column)
            low = self._format_value(between.low)
            high = self._format_value(between.high)
            conditions.append(f"{col} BETWEEN {low} AND {high}")

        # Subquery conditions
        for subq_cond in where.subquery_conditions:
            conditions.append(self._translate_subquery_condition(subq_cond))

        if not conditions:
            return ""

        combined = f" {where.group_logic.value} ".join(conditions)
        return f"WHERE {combined}"

    def _translate_condition_group(self, group: ConditionGroup) -> str:
        """Translate a group of conditions."""
        cond_strs = [self._translate_condition(cond) for cond in group.conditions]
        combined = f" {group.logic.value} ".join(cond_strs)
        return f"({combined})" if len(cond_strs) > 1 else combined

    def _translate_condition(self, cond) -> str:
        """Translate a condition (dispatches to specific type handler based on cond_type)."""
        # Use discriminator field to determine type
        cond_type = getattr(cond, 'cond_type', None)

        if cond_type == 'simple':
            return self._translate_simple_condition(cond)
        elif cond_type == 'column_comparison':
            return self._translate_column_comparison(cond)
        elif cond_type == 'between':
            return self._translate_between_condition(cond)
        else:
            # Fallback for backward compatibility (old tests might not have cond_type)
            from .clauses import SimpleCondition, ColumnComparison, BetweenCondition
            if isinstance(cond, SimpleCondition):
                return self._translate_simple_condition(cond)
            elif isinstance(cond, ColumnComparison):
                return self._translate_column_comparison(cond)
            elif isinstance(cond, BetweenCondition):
                return self._translate_between_condition(cond)
            else:
                raise ValueError(f"Unknown condition type: {type(cond)}")

    def _translate_simple_condition(self, cond) -> str:
        """Translate a single condition (column OP value)."""
        col = self._translate_qualified_column(cond.column)
        op = cond.operator.value

        # Handle NULL checks
        if cond.operator in (ComparisonOp.is_null, ComparisonOp.is_not_null):
            return f"{col} {op}"

        # Handle IN/NOT IN
        if cond.operator in (ComparisonOp.in_, ComparisonOp.not_in):
            if isinstance(cond.value, list):
                values = ", ".join(self._format_value(v) for v in cond.value)
                return f"{col} {op} ({values})"
            else:
                return f"{col} {op} ({self._format_value(cond.value)})"

        # Regular comparison
        value = self._format_value(cond.value)
        return f"{col} {op} {value}"

    def _translate_column_comparison(self, cond) -> str:
        """Translate column-to-column comparison (left_column OP right_column)."""
        left_col = self._translate_qualified_column(cond.left_column)
        right_col = self._translate_qualified_column(cond.right_column)
        op = cond.operator.value
        return f"{left_col} {op} {right_col}"

    def _translate_between_condition(self, cond) -> str:
        """Translate BETWEEN condition (column BETWEEN low AND high)."""
        col = self._translate_qualified_column(cond.column)
        low = self._format_value(cond.low)
        high = self._format_value(cond.high)
        return f"{col} BETWEEN {low} AND {high}"

    def _translate_subquery_condition(self, subq_cond: SubqueryCondition) -> str:
        """Translate condition with scalar subquery."""
        col = self._translate_qualified_column(subq_cond.column)
        op = subq_cond.operator.value
        subq = self._translate_scalar_subquery(subq_cond.subquery)
        return f"{col} {op} ({subq})"

    def _translate_scalar_subquery(self, subq: ScalarSubquery) -> str:
        """Translate scalar subquery."""
        parts = []

        # SELECT aggregate
        agg_str = self._translate_aggregate(subq.aggregate)
        parts.append(f"SELECT {agg_str}")

        # FROM
        parts.append(f"FROM {subq.table.value}")

        # WHERE
        if subq.where:
            parts.append(self._translate_where_l0(subq.where))

        # GROUP BY
        if subq.group_by:
            group_cols = ", ".join(col.value for col in subq.group_by)
            parts.append(f"GROUP BY {group_cols}")

        return " ".join(parts)

    def _translate_where_l0(self, where: WhereL0) -> str:
        """Translate WHERE clause (level 0 without subqueries)."""
        conditions = []

        for group in where.groups:
            conditions.append(self._translate_condition_group(group))

        for between in where.between_conditions:
            col = self._translate_qualified_column(between.column)
            low = self._format_value(between.low)
            high = self._format_value(between.high)
            conditions.append(f"{col} BETWEEN {low} AND {high}")

        if not conditions:
            return ""

        combined = f" {where.group_logic.value} ".join(conditions)
        return f"WHERE {combined}"

    # ========================================================================
    # FROM and JOIN
    # ========================================================================

    def _translate_from(self, from_clause: FromClause) -> str:
        """Translate FROM clause with joins."""
        parts = []

        # Base table or derived table
        if from_clause.table:
            table_str = from_clause.table.value
            if from_clause.table_alias:
                table_str = f"{table_str} AS {from_clause.table_alias}"
            parts.append(f"FROM {table_str}")
        elif from_clause.derived:
            derived_str = self._translate_derived_table(from_clause.derived)
            parts.append(f"FROM ({derived_str}) AS {from_clause.derived.alias}")
        else:
            raise ValueError("FROM clause must have table or derived table")

        # Joins
        for join in from_clause.joins:
            parts.append(self._translate_join(join))

        return "\n".join(parts)

    def _translate_join(self, join: JoinSpec) -> str:
        """Translate JOIN specification with flexible ON conditions."""
        join_type = join.join_type.value
        table = join.table.value
        if join.table_alias:
            table = f"{table} AS {join.table_alias}"

        # Translate ON conditions using ConditionGroup
        on_parts = [self._translate_condition_group(cg) for cg in join.on_conditions]

        # If multiple condition groups, combine with AND
        if len(on_parts) == 1:
            on_clause = on_parts[0]
        else:
            on_clause = " AND ".join(f"({part})" for part in on_parts)

        return f"{join_type} JOIN {table} ON {on_clause}"

    def _translate_derived_table(self, derived: DerivedTable) -> str:
        """Translate derived table (subquery in FROM)."""
        parts = []

        # SELECT
        expr_strs = [self._translate_select_expr(expr) for expr in derived.select]
        parts.append("SELECT " + ", ".join(expr_strs))

        # FROM
        parts.append(f"FROM {derived.from_table.value}")

        # WHERE
        if derived.where:
            parts.append(self._translate_where_l0(derived.where))

        return " ".join(parts)

    # ========================================================================
    # GROUP BY, HAVING, ORDER BY, LIMIT
    # ========================================================================

    def _translate_group_by(self, group_by: GroupByClause) -> str:
        """Translate GROUP BY clause."""
        cols = ", ".join(col.value for col in group_by.columns)
        return f"GROUP BY {cols}"

    def _translate_having(self, having: HavingClause) -> str:
        """Translate HAVING clause."""
        cond_strs = []
        for cond in having.conditions:
            func = cond.function.value
            col = cond.column.value if cond.column else "*"
            op = cond.operator.value
            value = str(cond.value)
            cond_strs.append(f"{func}({col}) {op} {value}")

        combined = f" {having.logic.value} ".join(cond_strs)
        return f"HAVING {combined}"

    def _translate_order_by(self, order_by: OrderByClause) -> str:
        """Translate ORDER BY clause."""
        item_strs = []
        for item in order_by.items:
            item_str = f"{item.column.value} {item.direction.value}"
            if item.nulls:
                item_str += f" NULLS {item.nulls.value}"
            item_strs.append(item_str)

        return f"ORDER BY {', '.join(item_strs)}"

    def _translate_limit(self, limit: LimitClause) -> str:
        """Translate LIMIT clause."""
        if limit.offset > 0:
            return f"LIMIT {limit.limit} OFFSET {limit.offset}"
        return f"LIMIT {limit.limit}"

    # ========================================================================
    # Utility
    # ========================================================================

    def _format_value(self, value: Union[str, int, float, bool]) -> str:
        """Format a value for SQL."""
        if isinstance(value, str):
            # Escape single quotes
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        else:
            return str(value)


# Convenience function
def translate_query(query: Query) -> str:
    """
    Translate a Query model to SQL string.

    Args:
        query: Query model to translate

    Returns:
        Formatted SQL string ready for execution
    """
    translator = SQLTranslator()
    return translator.translate(query)
