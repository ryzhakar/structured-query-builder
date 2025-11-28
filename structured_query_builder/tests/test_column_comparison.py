"""
Tests for ColumnComparison functionality.

Tests column-to-column comparisons for JOIN ON clauses and cross-table conditions.
"""

import pytest
from structured_query_builder import *
from structured_query_builder.translator import translate_query


class TestColumnComparison:
    """Test ColumnComparison model and translation."""

    def test_column_comparison_creation(self):
        """Test creating a ColumnComparison instance."""
        comp = ColumnComparison(
            left_column=QualifiedColumn(column=Column.id, table_alias="a"),
            operator=ComparisonOp.eq,
            right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
        )

        assert comp.cond_type == "column_comparison"
        assert comp.left_column.column == Column.id
        assert comp.right_column.column == Column.source_id
        assert comp.operator == ComparisonOp.eq

    def test_column_comparison_in_condition_group(self):
        """Test ColumnComparison works in ConditionGroup."""
        group = ConditionGroup(
            conditions=[
                ColumnComparison(
                    left_column=QualifiedColumn(column=Column.id, table_alias="a"),
                    operator=ComparisonOp.eq,
                    right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
                )
            ],
            logic=LogicOp.and_
        )

        assert len(group.conditions) == 1
        assert group.conditions[0].cond_type == "column_comparison"

    def test_mixed_conditions_in_group(self):
        """Test mixing SimpleCondition and ColumnComparison in same group."""
        group = ConditionGroup(
            conditions=[
                ColumnComparison(
                    left_column=QualifiedColumn(column=Column.id, table_alias="a"),
                    operator=ComparisonOp.eq,
                    right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
                ),
                SimpleCondition(
                    column=QualifiedColumn(column=Column.vendor, table_alias="a"),
                    operator=ComparisonOp.eq,
                    value="Us"
                )
            ],
            logic=LogicOp.and_
        )

        assert len(group.conditions) == 2
        assert group.conditions[0].cond_type == "column_comparison"
        assert group.conditions[1].cond_type == "simple"


class TestColumnComparisonTranslation:
    """Test SQL translation of ColumnComparison."""

    def test_simple_column_comparison_translation(self):
        """Test translating a simple column comparison."""
        from structured_query_builder.translator import SQLTranslator

        translator = SQLTranslator()
        comp = ColumnComparison(
            left_column=QualifiedColumn(column=Column.id, table_alias="a"),
            operator=ComparisonOp.eq,
            right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
        )

        sql = translator._translate_column_comparison(comp)
        assert sql == "a.id = em.source_id"

    def test_column_comparison_in_join(self):
        """Test column comparison in JOIN ON clause."""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="a")),
                ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="a")),
            ],
            from_=FromClause(
                table=Table.product_offers,
                table_alias="a",
                joins=[
                    JoinSpec(
                        join_type=JoinType.inner,
                        table=Table.exact_matches,
                        table_alias="em",
                        on_conditions=[
                            ConditionGroup(
                                conditions=[
                                    ColumnComparison(
                                        left_column=QualifiedColumn(column=Column.id, table_alias="a"),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
                                    )
                                ],
                                logic=LogicOp.and_
                            )
                        ]
                    )
                ]
            )
        )

        sql = translate_query(query)
        assert "INNER JOIN exact_matches AS em ON a.id = em.source_id" in sql
        # Check SELECT clause (allowing for whitespace variations)
        assert "a.id" in sql and "a.title" in sql
        assert "FROM product_offers AS a" in sql

    def test_multi_table_join_with_column_comparisons(self):
        """Test query with multiple JOINs using ColumnComparison."""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="my")),
                ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="comp")),
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
                                        left_column=QualifiedColumn(column=Column.id, table_alias="my"),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
                                    )
                                ],
                                logic=LogicOp.and_
                            )
                        ]
                    ),
                    JoinSpec(
                        join_type=JoinType.inner,
                        table=Table.product_offers,
                        table_alias="comp",
                        on_conditions=[
                            ConditionGroup(
                                conditions=[
                                    ColumnComparison(
                                        left_column=QualifiedColumn(column=Column.target_id, table_alias="em"),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(column=Column.id, table_alias="comp")
                                    )
                                ],
                                logic=LogicOp.and_
                            )
                        ]
                    ),
                ]
            )
        )

        sql = translate_query(query)
        assert "FROM product_offers AS my" in sql
        assert "INNER JOIN exact_matches AS em ON my.id = em.source_id" in sql
        assert "INNER JOIN product_offers AS comp ON em.target_id = comp.id" in sql

    def test_join_with_multiple_conditions(self):
        """Test JOIN with both ColumnComparison and SimpleCondition."""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="a")),
            ],
            from_=FromClause(
                table=Table.product_offers,
                table_alias="a",
                joins=[
                    JoinSpec(
                        join_type=JoinType.inner,
                        table=Table.product_offers,
                        table_alias="b",
                        on_conditions=[
                            ConditionGroup(
                                conditions=[
                                    ColumnComparison(
                                        left_column=QualifiedColumn(column=Column.category, table_alias="a"),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(column=Column.category, table_alias="b")
                                    ),
                                    SimpleCondition(
                                        column=QualifiedColumn(column=Column.vendor, table_alias="b"),
                                        operator=ComparisonOp.eq,
                                        value="Them"
                                    )
                                ],
                                logic=LogicOp.and_
                            )
                        ]
                    )
                ]
            )
        )

        sql = translate_query(query)
        assert "INNER JOIN product_offers AS b ON (a.category = b.category AND b.vendor = 'Them')" in sql

    def test_column_comparison_gt_operator(self):
        """Test column comparison with greater-than operator."""
        from structured_query_builder.translator import SQLTranslator

        translator = SQLTranslator()
        comp = ColumnComparison(
            left_column=QualifiedColumn(column=Column.markdown_price, table_alias="a"),
            operator=ComparisonOp.gt,
            right_column=QualifiedColumn(column=Column.markdown_price, table_alias="b")
        )

        sql = translator._translate_column_comparison(comp)
        assert sql == "a.markdown_price > b.markdown_price"

    def test_column_comparison_serialization(self):
        """Test ColumnComparison serializes to JSON correctly."""
        comp = ColumnComparison(
            left_column=QualifiedColumn(column=Column.id, table_alias="a"),
            operator=ComparisonOp.eq,
            right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
        )

        json_str = comp.model_dump_json()
        assert '"cond_type":"column_comparison"' in json_str
        assert "left_column" in json_str
        assert "right_column" in json_str

        # Test round-trip
        deserialized = ColumnComparison.model_validate_json(json_str)
        assert deserialized.cond_type == "column_comparison"
        assert deserialized.left_column.column == Column.id
        assert deserialized.right_column.column == Column.source_id


class TestBimodalQueryPatterns:
    """Test realistic bimodal query patterns using ColumnComparison."""

    def test_matched_price_comparison_query(self):
        """Test matched execution pattern: side-by-side price comparison."""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="my")),
                ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="my")),
                ColumnExpr(source=QualifiedColumn(column=Column.markdown_price, table_alias="my")),
                ColumnExpr(source=QualifiedColumn(column=Column.markdown_price, table_alias="comp")),
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
                                        left_column=QualifiedColumn(column=Column.id, table_alias="my"),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
                                    )
                                ],
                                logic=LogicOp.and_
                            )
                        ]
                    ),
                    JoinSpec(
                        join_type=JoinType.inner,
                        table=Table.product_offers,
                        table_alias="comp",
                        on_conditions=[
                            ConditionGroup(
                                conditions=[
                                    ColumnComparison(
                                        left_column=QualifiedColumn(column=Column.target_id, table_alias="em"),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(column=Column.id, table_alias="comp")
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
                            SimpleCondition(
                                column=QualifiedColumn(column=Column.vendor, table_alias="comp"),
                                operator=ComparisonOp.eq,
                                value="Them"
                            ),
                        ],
                        logic=LogicOp.and_
                    )
                ]
            ),
            limit=LimitClause(limit=100)
        )

        sql = translate_query(query)

        # Verify structure (allowing for whitespace variations)
        assert "my.id" in sql and "my.title" in sql and "my.markdown_price" in sql and "comp.markdown_price" in sql
        assert "FROM product_offers AS my" in sql
        assert "INNER JOIN exact_matches AS em ON my.id = em.source_id" in sql
        assert "INNER JOIN product_offers AS comp ON em.target_id = comp.id" in sql
        assert "WHERE (my.vendor = 'Us' AND comp.vendor = 'Them')" in sql
        assert "LIMIT 100" in sql

    def test_stockout_advantage_query(self):
        """Test stockout exploitation pattern with availability check."""
        query = Query(
            select=[
                ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="my")),
                ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="my")),
                ColumnExpr(source=QualifiedColumn(column=Column.markdown_price, table_alias="my")),
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
                                        left_column=QualifiedColumn(column=Column.id, table_alias="my"),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
                                    )
                                ],
                                logic=LogicOp.and_
                            )
                        ]
                    ),
                    JoinSpec(
                        join_type=JoinType.inner,
                        table=Table.product_offers,
                        table_alias="comp",
                        on_conditions=[
                            ConditionGroup(
                                conditions=[
                                    ColumnComparison(
                                        left_column=QualifiedColumn(column=Column.target_id, table_alias="em"),
                                        operator=ComparisonOp.eq,
                                        right_column=QualifiedColumn(column=Column.id, table_alias="comp")
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
                                column=QualifiedColumn(column=Column.availability, table_alias="my"),
                                operator=ComparisonOp.eq,
                                value=True
                            ),
                            SimpleCondition(
                                column=QualifiedColumn(column=Column.availability, table_alias="comp"),
                                operator=ComparisonOp.eq,
                                value=False
                            ),
                        ],
                        logic=LogicOp.and_
                    )
                ]
            ),
            limit=LimitClause(limit=50)
        )

        sql = translate_query(query)

        # Verify stockout filter
        assert "my.availability = TRUE" in sql or "my.availability = true" in sql
        assert "comp.availability = FALSE" in sql or "comp.availability = false" in sql
        assert "LIMIT 50" in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
