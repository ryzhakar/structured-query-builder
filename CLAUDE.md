# Working with This Repository - User Preferences

## Core Philosophy
- **Ship working code, not excuses**
- **Fix problems, don't document limitations**
- **"Addressing" = bullshit. Need exemplar implementations.**
- **No application layer handwaving** - queries must be self-contained for LLM structured outputs

## Data Model Reality
- Data IS historical (has `updated_at` timestamps)
- Can do temporal comparisons within queries
- Stop claiming "single snapshot limitation" - that's wrong

## Commit Standards
- **Short, granular, conventional commits**
- Make implementation trackable through commit history
- Each commit should be atomic and clear

## Quality Standards
- **Proof-of-work required**: Code + tests + committed
- **Never mark complete without**: All acceptance criteria met, code works, tests pass
- **Working and exemplar**: Not "foundation queries" that need app layer - full intelligence delivery

## When Blocked
- **Add missing schema features** instead of documenting gaps
- **Implement the pattern** instead of saying "requires application layer"
- **Use available SQL features** (window functions, subqueries, temporal filtering)

## Documentation
- Be honest about what works/doesn't
- But don't use honesty as excuse to ship incomplete work
- If spec says X, implement X - don't implement X-lite and call it "partial"

## Communication
- No cheerleading, no superlatives
- Professional objectivity
- When wrong, acknowledge and fix
- Action over explanation
