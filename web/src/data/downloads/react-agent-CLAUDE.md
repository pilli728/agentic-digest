# CLAUDE.md — React + AI Agent Project

## what this project is
[Your app description — e.g. "SaaS dashboard that uses AI agents to automate customer support workflows"]

## tech stack
- Language: TypeScript (strict mode)
- Framework: Next.js 15 (App Router)
- UI: Tailwind CSS + shadcn/ui v2
- Database: PostgreSQL via Prisma
- Auth: Auth.js v5 (formerly NextAuth)
- AI: Anthropic Claude API via @anthropic-ai/sdk
- Agent Framework: Claude Agent SDK / Vercel AI SDK / custom
- Testing: Vitest + Playwright
- Package manager: pnpm

## essential commands
```bash
pnpm install          # install deps
pnpm dev              # dev server on :3000
CI=true pnpm test     # run tests
pnpm lint             # eslint + prettier
pnpm typecheck        # tsc --noEmit
pnpm build            # production build
pnpm db:push          # push schema to DB
pnpm db:generate      # generate Prisma client
```

## architecture
```
src/
├── app/              # Next.js pages and API routes
│   ├── (marketing)/  # Public pages (server components)
│   ├── (dashboard)/  # Protected pages (server components)
│   └── api/          # Route handlers
├── components/
│   ├── ui/           # shadcn/ui v2 components (DO NOT EDIT — managed by CLI)
│   └── custom/       # Project-specific components
├── lib/
│   ├── agents/       # AI agent definitions and tools
│   ├── db/           # Prisma client and repository functions
│   ├── auth/         # Auth configuration and session helpers
│   └── utils/        # Pure utility functions
├── types/            # Shared TypeScript types
└── __tests__/        # Integration tests
```

API routes in `app/api/`. Server components by default. Client components
only when interactivity is needed (forms, modals). Agent logic isolated
in `lib/agents/` — never in components or API routes directly.

## React Server Components + AI patterns
- **Data fetching in RSC:** Fetch agent results in server components using async/await. No useEffect for initial data.
- **Streaming with Suspense:** Wrap slow AI calls in `<Suspense>` with a fallback. Use React's streaming to show partial UI.
- **Server Actions for mutations:** Use `"use server"` actions to trigger agent calls from forms — no API route needed.
- **Client boundary:** Only add `"use client"` for interactive elements (chat input, real-time status). Keep AI orchestration on the server.
- **Caching:** Use `unstable_cache` or `next/cache` for expensive agent results that don't change per-request.
```tsx
// Server component — fetches agent result at request time
export default async function AnalysisPage({ params }: Props) {
  const result = await runAnalysisAgent(params.id) // runs on server
  return <AnalysisView data={result} />
}

// Server Action — triggers agent from client interaction
"use server"
export async function submitQuery(formData: FormData) {
  const query = formData.get("query") as string
  const result = await runAgent(query)
  revalidatePath("/dashboard")
  return result
}
```

## streaming response patterns
For real-time AI responses, use streaming from server to client:
```tsx
// app/api/chat/route.ts — streaming route handler
import Anthropic from "@anthropic-ai/sdk"

const client = new Anthropic()

export async function POST(req: Request) {
  const { messages } = await req.json()

  const stream = await client.messages.stream({
    model: process.env.CLAUDE_MODEL ?? "claude-sonnet-4-20250514",
    max_tokens: 4096,
    messages,
  })

  // Return as a ReadableStream
  return new Response(
    new ReadableStream({
      async start(controller) {
        for await (const event of stream) {
          if (event.type === "content_block_delta" &&
              event.delta.type === "text_delta") {
            controller.enqueue(
              new TextEncoder().encode(event.delta.text)
            )
          }
        }
        controller.close()
      },
    }),
    { headers: { "Content-Type": "text/plain; charset=utf-8" } }
  )
}
```
```tsx
// Client component — consuming the stream
"use client"
import { useState, useCallback } from "react"

export function ChatUI() {
  const [response, setResponse] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)

  const sendMessage = useCallback(async (message: string) => {
    setIsStreaming(true)
    setResponse("")
    const res = await fetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({ messages: [{ role: "user", content: message }] }),
    })
    const reader = res.body?.getReader()
    const decoder = new TextDecoder()
    while (reader) {
      const { done, value } = await reader.read()
      if (done) break
      setResponse((prev) => prev + decoder.decode(value))
    }
    setIsStreaming(false)
  }, [])

  return (/* render response with streaming indicator */)
}
```

## Anthropic SDK patterns
```ts
// lib/agents/client.ts — singleton Anthropic client
import Anthropic from "@anthropic-ai/sdk"

export const anthropic = new Anthropic() // reads ANTHROPIC_API_KEY from env

// Tool use pattern
const response = await anthropic.messages.create({
  model: process.env.CLAUDE_MODEL ?? "claude-sonnet-4-20250514",
  max_tokens: 4096,
  tools: [
    {
      name: "lookup_customer",
      description: "Look up customer by email address",
      input_schema: {
        type: "object" as const,
        properties: {
          email: { type: "string", description: "Customer email" },
        },
        required: ["email"],
      },
    },
  ],
  messages,
})

// Handle tool use in an agentic loop
for (const block of response.content) {
  if (block.type === "tool_use") {
    const toolResult = await executeTool(block.name, block.input)
    // Continue conversation with tool result...
  }
}
```

## agent-specific rules
- Agent prompts live in `lib/agents/prompts/` as template literals
- Tool definitions in `lib/agents/tools/` — one file per tool
- Never hardcode model names — use `CLAUDE_MODEL` env var
- Always set `max_tokens` explicitly — never rely on defaults
- Log every agent invocation with: model, tokens used, latency, success/fail
- Agent errors must be caught and returned as structured responses, never thrown to the client
- Rate limit agent calls per user: check `lib/agents/rate-limiter.ts`
- Use `AbortController` with timeouts for all agent calls — never let them hang indefinitely

## shadcn/ui v2 notes
- Install components via `pnpm dlx shadcn@latest add <component>`
- Do NOT manually edit files in `components/ui/` — they are managed by the CLI
- Customize theming in `tailwind.config.ts` and `globals.css`, not in component files
- Use the `cn()` utility from `lib/utils` for conditional class merging
- shadcn/ui v2 components use Radix UI primitives — check Radix docs for advanced usage

## what NOT to do
- Do not use `any` — ever
- Do not call Claude API directly from components — go through `lib/agents/`
- Do not store API keys in code — use .env
- Do not skip error handling on agent calls — they fail often
- Do not make assumptions about Claude's output format — always validate/parse
- Do not use `dangerouslySetInnerHTML` with agent output
- Do not mix server and client concerns — keep `"use client"` boundaries tight
- Do not call `fetch()` inside server components when you can call the function directly
- Do not put agent logic in middleware — it runs on every request

## before finishing a task
1. `CI=true pnpm test` — all pass
2. `pnpm lint && pnpm typecheck` — zero errors
3. If you touched agents: test with a real Claude call (not just mocked)
4. If you touched auth: test login/logout/protected routes
5. If you touched DB: verify migration runs on empty database
6. Check git diff — nothing unintended

## lessons learned
<!-- Claude appends here when mistakes are corrected -->
