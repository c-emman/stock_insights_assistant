# Data Engineer - Take-Home Assignment

## Overview

You are applying for a Data Engineer role at a Balderton. We are building internal tools that allow our team to query and analyze in-house data using natural language.

This take-home task is a miniature version of that problem: build a small web application that lets users ask natural language questions about financial/stock data, and get AI-powered answers.

**Time expectation:** ~5 hours
**Submission:** GitHub repository with CI/CD + Docker setup

---

## The Task

Build a **Stock Insights Assistant**—a simple web application where users can:

1. **Ask natural language questions** about stocks/companies (e.g., "How is Apple doing today?", "Compare Tesla and Ford's recent performance", "What are the top gainers in tech?")
2. **Get intelligent, summarized responses** powered by AI that fetches relevant data and presents it clearly

### Example Interactions

```
User: "How is AAPL doing today?"
Assistant: "Apple (AAPL) is currently trading at $182.52, up 1.3% today.
The stock opened at $180.10 with a day range of $179.80 - $183.20.
Trading volume is 45M shares, slightly below the average of 52M."

User: "Compare TSLA and F"
Assistant: "Tesla (TSLA) vs Ford (F) comparison:
- TSLA: $248.50 (+2.1%), P/E: 62.3, Market Cap: $789B
- F: $12.30 (-0.5%), P/E: 11.2, Market Cap: $49B
Tesla shows stronger momentum today but trades at a significant premium..."
```

---

## Technical Requirements

### Must Have

| Requirement | Details |
|-------------|---------|
| **Language** | Python 3.10+ |
| **Web Framework** | Your choice (FastAPI, Flask, Streamlit, etc.) |
| **Data Source** | [Finnhub.io](https://finnhub.io/) recommended (generous free tier), but alternatives acceptable (Alpha Vantage, yfinance, etc.) |
| **AI Integration** | OpenAI API for query interpretation and response generation |
| **UI** | Simple web interface (can be minimal—functionality over aesthetics) |
| **Containerization** | Must run via `docker compose up` with no additional setup |
| **CI/CD** | GitHub Actions workflow that runs linting (e.g., `ruff`, `flake8`) and tests |
| **Tests** | Unit tests for core business logic |
| **Documentation** | README with setup instructions and brief architecture overview |

### Architecture Expectations

- **Well-partitioned code**: Separate concerns (API layer, business logic, data fetching, AI integration)
- **DRY & KISS**: No unnecessary abstractions, but don't repeat yourself
- **Testable**: Core logic should be testable without hitting external APIs
- **Error handling**: Graceful handling of API failures, invalid queries, rate limits

---

## What We Provide

- **OpenAI API Key**: We will provide you with an OpenAI API key. Use it for:
  - **Building**: You may use it with AI coding assistants (e.g., Cursor, Aider, Claude Code) during development
  - **Runtime**: Your application must use OpenAI for its AI features

Note: You're welcome to use other AI tools you already have access to (GitHub Copilot, Claude, etc.) for development assistance, but the OpenAI key we provide is the only one you should need.

---

## Deliverables

1. **GitHub Repository** (public or private with access granted to us)
   - Clean commit history showing your development process
   - Working CI/CD pipeline (GitHub Actions)
   - All code and configuration files

2. **Working Application**
   - Must start with `docker compose up`
   - Include `.env.example` showing required environment variables

3. **README.md** containing:
   - How to run the application
   - Brief architecture overview (1-2 paragraphs or a simple diagram)
   - Any trade-offs or decisions you made
   - What you would improve with more time
   - Which AI tools you used and how they helped

---

## Evaluation Criteria

| Criteria | Weight | What We Look For |
|----------|--------|------------------|
| **Functionality** | 25% | Does it work? Can users ask questions and get useful responses? |
| **Code Quality** | 25% | Clean, readable, well-organized. Follows Python best practices. |
| **Architecture** | 20% | Sensible separation of concerns. Easy to extend and test. |
| **AI Integration** | 15% | Smart use of LLM—good prompts, appropriate use of context, handles edge cases. |
| **DevOps** | 10% | Docker works, CI/CD runs, environment properly configured. |
| **Documentation** | 5% | Clear README, code comments where needed (not excessive). |

### What Impresses Us
- Elegant solutions to tricky problems
- Good error handling and edge case coverage
- Evidence of thoughtful prompt engineering
- Clean abstractions that aren't over-engineered

### What Concerns Us
- Over-engineering (unnecessary patterns, excessive abstraction)
- Copy-paste code without understanding
- No tests or broken tests
- Ignoring error cases
- Poor commit hygiene (single giant commit, meaningless messages)

---

## AI Usage Policy

**You must use AI tools** (Claude, ChatGPT, Copilot, Cursor, etc.) to help build this solution. This is intentional—we want to see:
- How effectively you leverage AI as a productivity multiplier
- Your ability to guide AI toward good solutions
- Your judgment in accepting, modifying, or rejecting AI suggestions
- The final code quality regardless of how it was produced

---

## Time Expectation

This should take approximately **5 hours**. If you find yourself spending significantly more time, step back and simplify. We value pragmatic solutions over perfect ones.

---


## Questions?

If anything is unclear, email us. We'd rather answer questions than have you make incorrect assumptions.

Good luck! We're excited to see what you build.
