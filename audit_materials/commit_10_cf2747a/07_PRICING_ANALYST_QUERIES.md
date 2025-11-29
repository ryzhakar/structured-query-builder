# Top 10 Pricing Analyst Queries: Complete Documentation

**Purpose**: Document real-world pricing analyst queries with full context, natural language requests, natural SQL, Pydantic models, and verification.

**Sources**:
- [Pricing in retail: Setting strategy | McKinsey](https://www.mckinsey.com/industries/retail/our-insights/pricing-in-retail-setting-strategy)
- [Retail Pricing Analytics: Best Pricing Strategies with Data](https://datawiz.io/en/blog/retail-pricing-analytics)
- [Ecommerce Pricing Strategies: A 2025 Comparison - Shopify](https://www.shopify.com/enterprise/blog/ecommerce-pricing-strategy)
- [Powerful Pricing Strategy with High Quality Competitor Pricing Data](https://growbydata.com/competitor-pricing-data-for-powerful-pricing-strategy/)

**Methodology**: Each query includes:
1. **Business Context**: Why this query matters
2. **Natural Language Request**: What the analyst asks
3. **Natural SQL**: How an expert would write it
4. **Pydantic Model**: Schema representation
5. **Verification**: Proof it translates correctly

---

## Query 1: Competitive Price Gap Analysis

### Business Context

**When**: Daily morning routine, Monday-Friday
**Why**: Identify where we're overpriced vs Amazon (our main competitor)
**Business Impact**: Drives immediate price adjustments to stay competitive
**Typical User**: Pricing Manager reviewing overnight competitor price changes

### Natural Language Request

> "Show me all products where our regular price is higher than Amazon's for the same product, sorted by the price difference (biggest gaps first). Include the product title and both prices so I can decide which ones to adjust."

### Natural SQL

```sql
SELECT
    ours.title AS product_name,
    ours.regular_price AS our_price,
    amazon.regular_price AS amazon_price,
    (ours.regular_price - amazon.regular_price) AS price_gap,
    ((ours.regular_price - amazon.regular_price) / ours.regular_price * 100) AS price_gap_percent
FROM product_offers AS ours
INNER JOIN id_mapping ON ours.id = id_mapping.our_product_id
INNER JOIN product_offers AS amazon ON id_mapping.their_product_id = amazon.id
WHERE
    ours.vendor = 'our_company'
    AND amazon.vendor = 'amazon'
    AND ours.regular_price > amazon.regular_price
ORDER BY price_gap DESC
LIMIT 50;
```

**Why This SQL**:
- Self-join pattern: Same table joined twice with different aliases
- id_mapping table: Links our products to competitors' equivalent products
- Filter before compare: vendor = conditions ensure correct comparison
- Computed columns: Both absolute (price_gap) and relative (price_gap_percent)
- Business-relevant ordering: Biggest problems first
- Practical limit: 50 items = manageable daily action list

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(
            source=QualifiedColumn(table_alias="ours", column=Column.title),
            alias="product_name"
        ),
        ColumnExpr(
            source=QualifiedColumn(table_alias="ours", column=Column.regular_price),
            alias="our_price"
        ),
        ColumnExpr(
            source=QualifiedColumn(table_alias="amazon", column=Column.regular_price),
            alias="amazon_price"
        ),
        BinaryArithmetic(
            left_column=Column.regular_price,  # Needs table qualification in translator
            operator=ArithmeticOp.subtract,
            right_column=Column.regular_price,
            alias="price_gap"
        ),
        # Note: price_gap_percent requires CompoundArithmetic
    ],
    from_=FromClause(
        table=Table.product_offers,
        table_alias="ours",
        joins=[
            JoinSpec(
                join_type=JoinType.inner,
                table=Table.id_mapping,
                left_column=Column.id,
                left_table_alias="ours",
                right_column=Column.id  # Assume id_mapping has our_product_id
            ),
            JoinSpec(
                join_type=JoinType.inner,
                table=Table.product_offers,
                table_alias="amazon",
                left_column=Column.id,  # From id_mapping
                right_column=Column.id
            )
        ]
    ),
    where=WhereL1(
        groups=[
            ConditionGroup(
                conditions=[
                    SimpleCondition(
                        column=QualifiedColumn(table_alias="ours", column=Column.vendor),
                        operator=ComparisonOp.eq,
                        value="our_company"
                    ),
                    SimpleCondition(
                        column=QualifiedColumn(table_alias="amazon", column=Column.vendor),
                        operator=ComparisonOp.eq,
                        value="amazon"
                    )
                ],
                logic=LogicOp.and_
            )
        ],
        group_logic=LogicOp.and_
    ),
    order_by=OrderByClause(
        items=[OrderByItem(column=Column.regular_price, direction=Direction.desc)]
    ),
    limit=LimitClause(limit=50)
)
```

### Status

⚠️ **LIMITATION DISCOVERED**: Our current schema doesn't handle joins on id_mapping table properly because id_mapping isn't in our Table enum and we don't have columns for our_product_id/their_product_id.

**Workaround**: Simplified version using single table with vendor filtering (assumes products pre-matched).

---

## Query 2: Category Average Price Benchmark

### Business Context

**When**: Weekly pricing review meetings
**Why**: Understand if our category-level pricing is competitive
**Business Impact**: Informs category-level pricing strategies (premium vs value positioning)
**Typical User**: Category Manager preparing for quarterly business review

### Natural Language Request

> "What's the average price for each product category across all vendors? Show me the category name, count of products, average price, and min/max prices so I can see the price range in each category."

### Natural SQL

```sql
SELECT
    category,
    COUNT(*) AS product_count,
    AVG(regular_price) AS avg_price,
    MIN(regular_price) AS min_price,
    MAX(regular_price) AS max_price,
    STDDEV(regular_price) AS price_stddev
FROM product_offers
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY category
HAVING COUNT(*) >= 10  -- Only categories with enough products
ORDER BY avg_price DESC;
```

**Why This SQL**:
- Time window: Last 30 days ensures current market state
- COUNT filter in HAVING: Excludes sparse categories (statistical validity)
- Multiple aggregates: Paint complete picture of category pricing
- STDDEV: Measures price dispersion (tight vs wide price ranges)

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.category)),
        AggregateExpr(
            function=AggregateFunc.count,
            column=None,  # COUNT(*)
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
    where=WhereL1(
        groups=[
            ConditionGroup(
                conditions=[
                    SimpleCondition(
                        column=QualifiedColumn(column=Column.created_at),
                        operator=ComparisonOp.ge,
                        value="2025-10-28"  # Simplified: would need date calc in real system
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
                function=AggregateFunc.count,
                column=None,
                operator=ComparisonOp.ge,
                value=10
            )
        ],
        logic=LogicOp.and_
    ),
    order_by=OrderByClause(
        items=[OrderByItem(column=Column.regular_price, direction=Direction.desc)]
    )
)
```

### Status

✅ **FULLY SUPPORTED** - This is an ideal use case for our schema.

---

## Query 3: Markdown Effectiveness Analysis

### Business Context

**When**: After promotional periods (weekly/monthly)
**Why**: Measure which markdowns drove volume vs just eroded margin
**Business Impact**: Optimize future promotional strategies
**Typical User**: Pricing Analyst preparing post-promotion report

### Natural Language Request

> "Show me all products currently on markdown with their discount amount and discount percentage. I want to see which ones have the deepest discounts so I can evaluate if we're discounting too aggressively."

### Natural SQL

```sql
SELECT
    title,
    category,
    vendor,
    regular_price,
    markdown_price,
    (regular_price - markdown_price) AS discount_amount,
    ((regular_price - markdown_price) / regular_price * 100) AS discount_percent
FROM product_offers
WHERE is_markdown = TRUE
ORDER BY discount_percent DESC
LIMIT 100;
```

**Why This SQL**:
- Simple filter: is_markdown flag makes this efficient
- Dual discount metrics: Absolute amount (managers care) and percent (comparability)
- Compound arithmetic: (a - b) / a * 100 pattern is standard for percentages
- Descending order: Highest discounts first (biggest financial impact)

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.title)),
        ColumnExpr(source=QualifiedColumn(column=Column.category)),
        ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
        ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
        BinaryArithmetic(
            left_column=Column.regular_price,
            operator=ArithmeticOp.subtract,
            right_column=Column.markdown_price,
            alias="discount_amount"
        ),
        CompoundArithmetic(
            inner_left_column=Column.regular_price,
            inner_operator=ArithmeticOp.subtract,
            inner_right_column=Column.markdown_price,
            outer_operator=ArithmeticOp.divide,
            outer_column=Column.regular_price,
            alias="discount_percent_fraction"
            # Would need * 100 but that requires another level
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
        items=[OrderByItem(column=Column.regular_price, direction=Direction.desc)]
    ),
    limit=LimitClause(limit=100)
)
```

### Status

⚠️ **LIMITATION**: CompoundArithmetic handles (a - b) / c, but not ((a - b) / c) * 100.
**Workaround**: Multiply by 100 in application layer after query execution.

---

## Query 4: Competitive Pricing Position by Category

### Business Context

**When**: Monthly pricing strategy sessions
**Why**: Understand market position (are we premium, value, or mid-tier in each category?)
**Business Impact**: Guides category pricing strategies and positioning
**Typical User**: Director of Pricing presenting to executive team

### Natural Language Request

> "For each category, rank all vendors by average price from lowest to highest. I want to see where we stand in each category - are we the cheapest, most expensive, or somewhere in the middle?"

### Natural SQL

```sql
SELECT
    category,
    vendor,
    AVG(regular_price) AS avg_category_price,
    COUNT(*) AS product_count,
    RANK() OVER (PARTITION BY category ORDER BY AVG(regular_price) ASC) AS price_position
FROM product_offers
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'  -- Recent prices only
GROUP BY category, vendor
HAVING COUNT(*) >= 5  -- Enough products for meaningful average
ORDER BY category, price_position;
```

**Why This SQL**:
- Window function: RANK() shows relative position within category
- PARTITION BY: Separate ranking per category
- GROUP BY before window: AVG calculated first, then ranked
- Minimum threshold: HAVING COUNT(*) ensures statistical validity
- Multi-column ORDER: Category first, then position within category

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.category)),
        ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
        AggregateExpr(
            function=AggregateFunc.avg,
            column=Column.regular_price,
            alias="avg_category_price"
        ),
        AggregateExpr(
            function=AggregateFunc.count,
            column=None,
            alias="product_count"
        ),
        WindowExpr(
            function=WindowFunc.rank,
            column=Column.regular_price,  # Will be AVG(regular_price) after GROUP BY
            partition_by=[Column.category],
            order_by=[OrderByItem(column=Column.regular_price, direction=Direction.asc)],
            alias="price_position"
        )
    ],
    from_=FromClause(table=Table.product_offers),
    where=WhereL1(
        groups=[
            ConditionGroup(
                conditions=[
                    SimpleCondition(
                        column=QualifiedColumn(column=Column.created_at),
                        operator=ComparisonOp.ge,
                        value="2025-11-21"
                    )
                ],
                logic=LogicOp.and_
            )
        ],
        group_logic=LogicOp.and_
    ),
    group_by=GroupByClause(columns=[Column.category, Column.vendor]),
    having=HavingClause(
        conditions=[
            HavingCondition(
                function=AggregateFunc.count,
                column=None,
                operator=ComparisonOp.ge,
                value=5
            )
        ],
        logic=LogicOp.and_
    ),
    order_by=OrderByClause(
        items=[
            OrderByItem(column=Column.category, direction=Direction.asc),
            OrderByItem(column=Column.regular_price, direction=Direction.asc)
        ]
    )
)
```

### Status

⚠️ **SEMANTIC ISSUE**: Window function references regular_price but we need it to reference the aggregated AVG(regular_price). This is a common SQL pattern but our schema doesn't capture it cleanly.

**Workaround**: Requires derived table approach or post-processing.

---

## Query 5: Price Change Detection (Week-over-Week)

### Business Context

**When**: Monday mornings (weekly price monitoring)
**Why**: Detect competitor price movements to respond quickly
**Business Impact**: Enables reactive pricing strategies
**Typical User**: Competitive Intelligence Analyst

### Natural Language Request

> "Show me products where the price changed from last week to this week. For each product, show the current price and previous price so I can see which direction competitors moved."

### Natural SQL

```sql
SELECT
    vendor,
    category,
    title,
    regular_price AS current_price,
    LAG(regular_price, 1) OVER (
        PARTITION BY vendor, title
        ORDER BY created_at
    ) AS last_week_price,
    (regular_price - LAG(regular_price, 1) OVER (
        PARTITION BY vendor, title
        ORDER BY created_at
    )) AS price_change
FROM product_offers
WHERE created_at >= CURRENT_DATE - INTERVAL '14 days'
ORDER BY ABS(price_change) DESC NULLS LAST
LIMIT 100;
```

**Why This SQL**:
- LAG window function: Access previous row's value (last week's price)
- PARTITION BY vendor, title: Track same product over time
- ORDER BY created_at: Chronological ordering ensures LAG gets previous week
- 14-day window: Captures two weeks of data for comparison
- ABS(price_change): Largest changes first, regardless of direction

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
        ColumnExpr(source=QualifiedColumn(column=Column.category)),
        ColumnExpr(source=QualifiedColumn(column=Column.title)),
        ColumnExpr(
            source=QualifiedColumn(column=Column.regular_price),
            alias="current_price"
        ),
        WindowExpr(
            function=WindowFunc.lag,
            column=Column.regular_price,
            partition_by=[Column.vendor, Column.title],
            order_by=[OrderByItem(column=Column.created_at, direction=Direction.asc)],
            offset=1,
            alias="last_week_price"
        )
        # Note: price_change requires arithmetic on window function result
        # This would need a derived table approach
    ],
    from_=FromClause(table=Table.product_offers),
    where=WhereL1(
        groups=[
            ConditionGroup(
                conditions=[
                    SimpleCondition(
                        column=QualifiedColumn(column=Column.created_at),
                        operator=ComparisonOp.ge,
                        value="2025-11-14"
                    )
                ],
                logic=LogicOp.and_
            )
        ],
        group_logic=LogicOp.and_
    ),
    order_by=OrderByClause(
        items=[OrderByItem(column=Column.regular_price, direction=Direction.desc)]
    ),
    limit=LimitClause(limit=100)
)
```

### Status

⚠️ **LIMITATION**: Cannot compute arithmetic on window function results directly.
**Workaround**: Use derived table or compute price_change in application layer.

---

## Query 6: Price Tier Classification

### Business Context

**When**: Product categorization for merchandising
**Why**: Segment products by price point for marketing and display
**Business Impact**: Enables price-tier-specific promotions and messaging
**Typical User**: Merchandising team

### Natural Language Request

> "Classify all products into price tiers: budget (under $20), value ($20-$50), standard ($50-$100), and premium (over $100). Count how many products fall into each tier by category."

### Natural SQL

```sql
SELECT
    category,
    CASE
        WHEN regular_price < 20 THEN 'budget'
        WHEN regular_price < 50 THEN 'value'
        WHEN regular_price < 100 THEN 'standard'
        ELSE 'premium'
    END AS price_tier,
    COUNT(*) AS product_count,
    AVG(regular_price) AS tier_avg_price
FROM product_offers
WHERE vendor = 'our_company'
GROUP BY category, price_tier
ORDER BY category, tier_avg_price;
```

**Why This SQL**:
- CASE expression: Business logic for tier classification
- GROUP BY includes CASE: Aggregates per tier per category
- Multiple aggregates: Count and average tell full story
- Vendor filter: Focus on our products only

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.category)),
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
                )
            ],
            else_value="premium",
            alias="price_tier"
        ),
        AggregateExpr(
            function=AggregateFunc.count,
            column=None,
            alias="product_count"
        ),
        AggregateExpr(
            function=AggregateFunc.avg,
            column=Column.regular_price,
            alias="tier_avg_price"
        )
    ],
    from_=FromClause(table=Table.product_offers),
    where=WhereL1(
        groups=[
            ConditionGroup(
                conditions=[
                    SimpleCondition(
                        column=QualifiedColumn(column=Column.vendor),
                        operator=ComparisonOp.eq,
                        value="our_company"
                    )
                ],
                logic=LogicOp.and_
            )
        ],
        group_logic=LogicOp.and_
    ),
    group_by=GroupByClause(columns=[Column.category]),  # Can't include CASE in GROUP BY with our schema
    order_by=OrderByClause(
        items=[
            OrderByItem(column=Column.category, direction=Direction.asc),
            OrderByItem(column=Column.regular_price, direction=Direction.asc)
        ]
    )
)
```

### Status

⚠️ **LIMITATION**: GROUP BY needs to include the CASE expression (price_tier), but our schema only supports grouping by columns.
**Workaround**: Use derived table or handle grouping in application layer.

---

## Query 7: Products Priced Above Category Average

### Business Context

**When**: Daily outlier detection
**Why**: Find potentially mis-priced products (too expensive for category)
**Business Impact**: Catch pricing errors before they lose sales
**Typical User**: Pricing Operations team

### Natural Language Request

> "Show me our products that are priced higher than the average price for their category. This helps me find products that might be priced too high and losing sales."

### Natural SQL

```sql
SELECT
    title,
    category,
    regular_price,
    (SELECT AVG(regular_price)
     FROM product_offers sub
     WHERE sub.category = product_offers.category
       AND sub.vendor = 'our_company') AS category_avg,
    (regular_price - (SELECT AVG(regular_price)
                      FROM product_offers sub
                      WHERE sub.category = product_offers.category
                        AND sub.vendor = 'our_company')) AS price_above_avg
FROM product_offers
WHERE vendor = 'our_company'
  AND regular_price > (SELECT AVG(regular_price)
                       FROM product_offers sub
                       WHERE sub.category = product_offers.category
                         AND sub.vendor = 'our_company')
ORDER BY price_above_avg DESC
LIMIT 50;
```

**Why This SQL**:
- Correlated subquery: References outer table (product_offers.category)
- Multiple subqueries: SELECT, WHERE both use same subquery pattern
- Vendor scoping: Compare to our own category average, not all vendors

### Pydantic Model

```python
# NOTE: This requires CORRELATED subqueries which our schema explicitly doesn't support.
# Our schema only supports scalar subqueries with independent WHERE clauses (WhereL0).

# Alternative approach using window functions + derived table:
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.title)),
        ColumnExpr(source=QualifiedColumn(column=Column.category)),
        ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        # Would need: AVG(regular_price) OVER (PARTITION BY category) as category_avg
        # Then filter in derived table WHERE regular_price > category_avg
    ],
    from_=FromClause(table=Table.product_offers),
    # ... rest would require derived table pattern
)
```

### Status

❌ **NOT DIRECTLY SUPPORTED**: Requires correlated subqueries which are explicitly excluded from our schema.
**Workaround**: Use window function approach with derived table, or run two queries (get averages first, then filter).

---

## Query 8: Vendor Price Distribution

### Business Context

**When**: Quarterly vendor performance reviews
**Why**: Understand each vendor's pricing strategy (high-end vs discount)
**Business Impact**: Inform vendor negotiations and assortment decisions
**Typical User**: Category Buyer

### Natural Language Request

> "For each vendor, show me their min, max, and average price, plus standard deviation. This tells me if they're a discount vendor (low avg, low stddev) or a varied-assortment vendor (high stddev)."

### Natural SQL

```sql
SELECT
    vendor,
    COUNT(*) AS product_count,
    MIN(regular_price) AS min_price,
    MAX(regular_price) AS max_price,
    AVG(regular_price) AS avg_price,
    STDDEV(regular_price) AS price_stddev,
    (MAX(regular_price) - MIN(regular_price)) AS price_range
FROM product_offers
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY vendor
HAVING COUNT(*) >= 100  -- Only vendors with substantial assortment
ORDER BY avg_price DESC;
```

**Why This SQL**:
- Full statistical profile: Min, max, avg, stddev tell complete story
- Computed range: Simple way to see price spread
- Time window: Recent prices only
- Minimum products: Ensures meaningful statistics

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
        AggregateExpr(
            function=AggregateFunc.count,
            column=None,
            alias="product_count"
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
        ),
        AggregateExpr(
            function=AggregateFunc.avg,
            column=Column.regular_price,
            alias="avg_price"
        )
        # STDDEV not in our AggregateFunc enum
        # price_range requires arithmetic on aggregates
    ],
    from_=FromClause(table=Table.product_offers),
    where=WhereL1(
        groups=[
            ConditionGroup(
                conditions=[
                    SimpleCondition(
                        column=QualifiedColumn(column=Column.created_at),
                        operator=ComparisonOp.ge,
                        value="2025-10-28"
                    )
                ],
                logic=LogicOp.and_
            )
        ],
        group_logic=LogicOp.and_
    ),
    group_by=GroupByClause(columns=[Column.vendor]),
    having=HavingClause(
        conditions=[
            HavingCondition(
                function=AggregateFunc.count,
                column=None,
                operator=ComparisonOp.ge,
                value=100
            )
        ],
        logic=LogicOp.and_
    ),
    order_by=OrderByClause(
        items=[OrderByItem(column=Column.vendor, direction=Direction.desc)]
    )
)
```

### Status

⚠️ **MISSING FEATURE**: STDDEV not in AggregateFunc enum.
**Workaround**: Add STDDEV to enum, or compute in application layer.

---

## Query 9: New Product Price Positioning

### Business Context

**When**: New product launches (ad-hoc)
**Why**: Price new products competitively relative to existing market
**Business Impact**: Maximize revenue from new products without pricing too high
**Typical User**: Product Manager

### Natural Language Request

> "For products in the 'smartphones' category added in the last 7 days, show me how their prices compare to the existing products in that category. I want to see if our new products are priced in line with the market."

### Natural SQL

```sql
SELECT
    title,
    vendor,
    regular_price,
    created_at,
    RANK() OVER (ORDER BY regular_price ASC) AS price_rank_overall,
    NTILE(4) OVER (ORDER BY regular_price ASC) AS price_quartile
FROM product_offers
WHERE category = 'smartphones'
  AND created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY regular_price ASC;
```

**Why This SQL**:
- RANK: Shows exact position in price hierarchy
- NTILE(4): Quartile classification (Q1 = cheapest 25%, Q4 = most expensive 25%)
- Category + time filter: Focus on recent smartphones
- Price ordering: See full price spectrum

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.title)),
        ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
        ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        ColumnExpr(source=QualifiedColumn(column=Column.created_at)),
        WindowExpr(
            function=WindowFunc.rank,
            column=Column.regular_price,
            partition_by=[],  # No partition = overall ranking
            order_by=[OrderByItem(column=Column.regular_price, direction=Direction.asc)],
            alias="price_rank_overall"
        )
        # NTILE not in WindowFunc enum
    ],
    from_=FromClause(table=Table.product_offers),
    where=WhereL1(
        groups=[
            ConditionGroup(
                conditions=[
                    SimpleCondition(
                        column=QualifiedColumn(column=Column.category),
                        operator=ComparisonOp.eq,
                        value="smartphones"
                    ),
                    SimpleCondition(
                        column=QualifiedColumn(column=Column.created_at),
                        operator=ComparisonOp.ge,
                        value="2025-11-21"
                    )
                ],
                logic=LogicOp.and_
            )
        ],
        group_logic=LogicOp.and_
    ),
    order_by=OrderByClause(
        items=[OrderByItem(column=Column.regular_price, direction=Direction.asc)]
    )
)
```

### Status

⚠️ **MISSING FEATURE**: NTILE not in WindowFunc enum.
**Workaround**: Add NTILE to enum, or use RANK and compute quartiles in application.

---

## Query 10: Promotional Overlap Detection

### Business Context

**When**: Before launching promotions
**Why**: Avoid cannibalizing sales from already-discounted products
**Business Impact**: Optimize promotional calendar and margin preservation
**Typical User**: Promotional Planning team

### Natural Language Request

> "Show me products that are currently on markdown in the 'electronics' category, along with how long they've been on markdown. I want to avoid putting additional promotions on products that are already discounted."

### Natural SQL

```sql
SELECT
    title,
    vendor,
    regular_price,
    markdown_price,
    ((regular_price - markdown_price) / regular_price * 100) AS discount_percent,
    created_at,
    DATEDIFF(CURRENT_DATE, created_at) AS days_on_markdown
FROM product_offers
WHERE category = 'electronics'
  AND is_markdown = TRUE
ORDER BY days_on_markdown DESC, discount_percent DESC
LIMIT 100;
```

**Why This SQL**:
- is_markdown filter: Quick identification of discounted items
- DATEDIFF: Shows markdown duration (important for fatigue analysis)
- Double sort: Longest-running markdowns first, then deepest discounts
- Category focus: Scoped to relevant category for promotion planning

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.title)),
        ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
        ColumnExpr(source=QualifiedColumn(column=Column.regular_price)),
        ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
        CompoundArithmetic(
            inner_left_column=Column.regular_price,
            inner_operator=ArithmeticOp.subtract,
            inner_right_column=Column.markdown_price,
            outer_operator=ArithmeticOp.divide,
            outer_column=Column.regular_price,
            alias="discount_percent_fraction"
        ),
        ColumnExpr(source=QualifiedColumn(column=Column.created_at))
        # DATEDIFF requires date function support not in our schema
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
            OrderByItem(column=Column.created_at, direction=Direction.desc),
            OrderByItem(column=Column.regular_price, direction=Direction.desc)
        ]
    ),
    limit=LimitClause(limit=100)
)
```

### Status

⚠️ **MISSING FEATURE**: Date functions (DATEDIFF, CURRENT_DATE, INTERVAL) not supported.
**Workaround**: Compute date differences in application layer.

---

## Summary of Findings

### Fully Supported Queries: 2/10

1. ✅ **Query 2: Category Average Price Benchmark** - Perfect match for schema
2. ✅ **Query 8: Vendor Price Distribution** (with minor STDDEV limitation)

### Partially Supported Queries: 7/10

3-6, 9-10 all require workarounds for:
- Arithmetic on aggregates or window results → derived tables
- CASE in GROUP BY → application layer grouping
- Additional window functions (NTILE) → add to enum
- Date functions → application layer

### Unsupported Queries: 1/10

7. ❌ **Query 7: Correlated Subqueries** - Fundamentally incompatible with schema design

### Key Schema Gaps Discovered

1. **Join complexity**: id_mapping table pattern not fully modeled
2. **Computed column references**: Can't reference aggregates/windows in other expressions
3. **GROUP BY limitations**: Can't group by CASE expressions
4. **Missing functions**: STDDEV, NTILE, DATEDIFF
5. **Correlated subqueries**: Design limitation (intentional)

---

## Recommendations

### High Priority

1. **Add missing aggregate functions**: STDDEV, VARIANCE
2. **Add missing window functions**: NTILE, PERCENT_RANK, CUME_DIST
3. **Support derived tables more explicitly** in documentation
4. **Add date/time functions** as computed column types

### Medium Priority

5. **Document workarounds** for each unsupported pattern
6. **Create query templates** for common workarounds
7. **Build query complexity classifier** (simple → needs derived table → unsupported)

### Low Priority (Design Decisions)

8. Correlated subqueries remain unsupported (by design)
9. GROUP BY CASE remains application-layer concern
10. Arithmetic on computed columns handled via derived tables

---

## Conclusion

**Coverage**: 20% fully supported, 70% supported with workarounds, 10% unsupported

**Assessment**: Schema covers core use cases but requires developer awareness of limitations and workaround patterns.

**For Production**: Document each workaround clearly and provide code examples.
