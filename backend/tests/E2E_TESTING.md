# End-to-End Testing with Real LLM Calls

This guide explains how to use the E2E tests that make **real API calls** to LLM providers.

## ⚠️ Important Notes

- **These tests are SLOW** - Each test can take 10-30 seconds
- **These tests cost money** - They use real API tokens
- **These tests require API keys** - Set them in your environment
- **These tests are skipped by default** - You must run them explicitly

## Setup

### 1. Set Your API Keys

Create or edit `backend/.env.development`:

```bash
# At least one of these is required:
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### 2. Verify Keys Are Loaded

```bash
cd backend
uv run python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
```

## Running E2E Tests

### Run All E2E Tests

```bash
# Using make
make test-e2e

# Or directly
cd backend
uv run pytest -m e2e -v -s
```

The `-s` flag shows print statements so you can see the LLM responses in real-time.

### Run Specific E2E Test

```bash
# Test only OpenAI direct call
cd backend
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_direct_agent_call -v -s

# Test complete session flow
cd backend
uv run pytest tests/test_e2e_real_llm.py::TestFullE2ESession::test_complete_session_openai_only -v -s

# Test specific provider
cd backend
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_anthropic_agent_call -v -s
```

### Run Regular Tests (Skip E2E)

```bash
# E2E tests are excluded by default
make test

# Or explicitly exclude them
make test-no-e2e

# Or with pytest
cd backend
uv run pytest -m "not e2e"
```

## Available E2E Tests

### 1. Individual Provider Tests

Test each LLM provider in isolation:

- `test_openai_direct_agent_call` - Basic OpenAI call
- `test_openai_communicator_role` - OpenAI as communicator with secret word
- `test_openai_receiver_role` - OpenAI as receiver analyzing messages
- `test_anthropic_agent_call` - Basic Anthropic/Claude call
- `test_google_agent_call` - Basic Google/Gemini call

**Use these to debug specific provider issues!**

### 2. Full Session Tests

Test complete game flows:

- `test_complete_session_openai_only` - Full game with all OpenAI agents
- `test_mixed_providers_session` - Cross-model communication

**Warning:** These are SLOW and EXPENSIVE!

### 3. Error Handling Tests

Test failure scenarios:

- `test_invalid_api_key_handling` - How system handles bad keys
- `test_no_api_key_behavior` - What happens when key is missing

## Debugging Your OpenAI Issue

Since you mentioned having trouble with OpenAI calls during `next-turn`, here's the recommended debugging approach:

### Step 1: Test Direct OpenAI Call

```bash
cd backend
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_direct_agent_call -v -s
```

This will:
- ✅ Make a direct call to OpenAI
- ✅ Show you the exact error if it fails
- ✅ Display the response if it succeeds

### Step 2: Test Each Role

```bash
# Test communicator role
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_communicator_role -v -s

# Test receiver role  
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_receiver_role -v -s
```

### Step 3: Test Full Session

```bash
uv run pytest tests/test_e2e_real_llm.py::TestFullE2ESession::test_complete_session_openai_only -v -s
```

This runs a complete game and shows you the conversation in real-time!

## Expected Output

### Success Example

```
🔄 Making real OpenAI API call...
✅ Success!
   Comms: I think we should explore the distant horizons of Mars...
   Thoughts: Attempting to naturally embed the word 'horizon' in the conversation...
```

### Error Example

```
🔄 Making real OpenAI API call...
❌ Error occurred: AuthenticationError: Incorrect API key provided
```

## Common Issues

### Issue: "No LLM API keys found in environment"

**Solution:** Set your API keys in `backend/.env.development`

```bash
cd backend
echo "OPENAI_API_KEY=sk-your-key-here" >> .env.development
```

### Issue: "pytest: command not found"

**Solution:** Use `uv run pytest` instead of `pytest` directly

### Issue: Tests are too slow

**Solution:** Run specific tests instead of the full suite:

```bash
# Just test OpenAI
uv run pytest -k "openai" -m e2e -v -s
```

### Issue: Rate limits / Too many requests

**Solution:** Run tests one at a time:

```bash
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_direct_agent_call -v -s
# Wait a moment...
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_communicator_role -v -s
```

## Cost Estimation

Approximate token costs per test:

- **Direct agent call**: ~500 tokens (~$0.001)
- **Single role test**: ~800 tokens (~$0.002)  
- **Full session test**: ~5000 tokens (~$0.01)

Running all E2E tests: **~$0.05 - $0.15**

## Tips

1. **Use `-s` flag** to see real-time output:
   ```bash
   pytest -m e2e -v -s
   ```

2. **Run specific providers** to save money:
   ```bash
   pytest -k "openai" -m e2e
   ```

3. **Capture output** to a file for analysis:
   ```bash
   pytest -m e2e -v -s > e2e_output.log 2>&1
   ```

4. **Debug a specific issue**:
   ```bash
   # Set environment variable and run test
   cd backend
   export OPENAI_API_KEY=sk-...
   uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_direct_agent_call -v -s
   ```

## Next Steps

After running these tests, you'll see exactly where your OpenAI integration is failing. Common issues:

1. **Authentication** - Wrong API key format
2. **Model name** - Invalid model specification  
3. **JSON parsing** - LLM not returning proper format
4. **Rate limits** - Too many requests
5. **Timeout** - Response taking too long

The test output will show you the exact error message, which you can use to fix the issue!
