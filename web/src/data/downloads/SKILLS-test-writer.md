# .claude/skills/test-writer/SKILL.md

## what this skill does
Write tests for new or existing code. Focus on edge cases and failure modes.

## approach
1. Read the function/module being tested — understand all code paths
2. Identify edge cases: empty inputs, null, undefined, boundary values
3. Identify failure modes: network errors, timeouts, invalid data
4. Write tests using AAA pattern: Arrange, Act, Assert
5. Each test should test ONE thing — if it fails, you know exactly what broke

## test structure
```
describe('functionName', () => {
  it('should handle the happy path', () => {})
  it('should handle empty input', () => {})
  it('should handle null/undefined', () => {})
  it('should throw on invalid input', () => {})
  it('should handle concurrent calls', () => {})
})
```

## rules
- Mock external services (APIs, databases) — never hit real services in unit tests
- Don't test implementation details — test behavior
- Don't write tests that always pass (assert something meaningful)
- One assertion per test when possible
- Use descriptive test names: "should return 404 when user not found"
- Co-locate tests with source: `auth.ts` -> `auth.test.ts`

## what NOT to mock
- Your own utility functions (test them for real)
- Simple data transformations
- Pure functions with no side effects

## property-based testing
Use property-based testing for functions with wide input ranges:
```ts
// Using fast-check (JS/TS)
import fc from "fast-check"

test("encode then decode is identity", () => {
  fc.assert(
    fc.property(fc.string(), (input) => {
      expect(decode(encode(input))).toBe(input)
    })
  )
})

test("sort output is always sorted", () => {
  fc.assert(
    fc.property(fc.array(fc.integer()), (arr) => {
      const sorted = mySort(arr)
      for (let i = 1; i < sorted.length; i++) {
        expect(sorted[i]).toBeGreaterThanOrEqual(sorted[i - 1])
      }
    })
  )
})
```
```python
# Using hypothesis (Python)
from hypothesis import given, strategies as st

@given(st.text())
def test_encode_decode_roundtrip(s):
    assert decode(encode(s)) == s
```
Good candidates for property-based testing: serialization/deserialization, sorting, parsers, validators, math operations, data transformations.

## snapshot testing guidance
Use snapshots for complex output that is tedious to assert manually:
```ts
// Good use: rendered component output, large structured responses
it("renders the dashboard correctly", () => {
  const { container } = render(<Dashboard data={mockData} />)
  expect(container).toMatchSnapshot()
})
```
Rules for snapshots:
- Review snapshot diffs carefully — do not blindly update with `--update`
- Avoid snapshots for frequently changing output (dates, IDs, random values)
- Keep snapshot scope small — snapshot one component, not a whole page
- Use inline snapshots for small, stable values: `expect(result).toMatchInlineSnapshot()`
- If a snapshot changes with every PR, it is not a useful test — rewrite as explicit assertions

## integration test patterns
For testing real interactions between components:
```ts
// API integration test with real database
describe("POST /api/users", () => {
  beforeEach(async () => {
    await db.execute(sql`DELETE FROM users`) // clean state
  })

  it("creates user and returns 201", async () => {
    const res = await app.inject({
      method: "POST",
      url: "/api/users",
      payload: { email: "test@example.com", name: "Test" },
    })
    expect(res.statusCode).toBe(201)

    // Verify side effects
    const user = await db.query.users.findFirst({
      where: eq(users.email, "test@example.com"),
    })
    expect(user).not.toBeNull()
  })
})
```
Integration test rules:
- Use a real test database, not mocks
- Each test gets a clean state (transactions or truncation)
- Test the full request/response cycle including middleware
- Verify side effects (database writes, queue messages, emails sent)
- Slower is OK — correctness matters more than speed for integration tests

## testing AI agent outputs
AI responses are non-deterministic. Test structure, not exact content:
```ts
describe("summarization agent", () => {
  it("returns a summary within length limits", async () => {
    const result = await summarize(longArticle)
    expect(result.summary.length).toBeLessThan(500)
    expect(result.summary.length).toBeGreaterThan(10)
  })

  it("returns valid structured output", async () => {
    const result = await analyzeArticle(article)
    expect(result).toHaveProperty("sentiment")
    expect(result.sentiment).toBeGreaterThanOrEqual(-1)
    expect(result.sentiment).toBeLessThanOrEqual(1)
    expect(result.topics).toBeInstanceOf(Array)
  })

  it("handles malformed input gracefully", async () => {
    const result = await summarize("")
    expect(result.error).toBeDefined()
  })

  // Use deterministic mocks for unit tests
  it("formats agent response correctly (mocked)", async () => {
    vi.mocked(anthropic.messages.create).mockResolvedValue(mockResponse)
    const result = await formatAgentOutput(query)
    expect(result.formatted).toContain("<h2>")
  })
})
```
Guidelines:
- Unit tests: mock the AI API and test your code around it (parsing, formatting, error handling)
- Integration tests: use real API calls, but test structure/schema, not exact wording
- Set temperature to 0 in tests for more deterministic output
- Use snapshot tests sparingly — AI output changes too often
- Test timeout handling and rate limit behavior, not just happy paths

## mutation testing
Mutation testing verifies your tests actually catch bugs. A mutation testing tool modifies your source code (e.g., flipping `>` to `<`, removing lines) and checks if tests fail.
- Tools: Stryker (JS/TS), mutmut (Python), pitest (Java)
- Target: >80% mutation score on critical business logic
- Run on CI weekly (too slow for every commit)
- Focus on: services, validators, and calculation logic — skip UI components
