# E2E Tests with Real LLM Calls - Summary

## What Was Added

✅ **New test file**: `backend/tests/test_e2e_real_llm.py`
- 500+ lines of comprehensive E2E tests
- Tests real API calls to OpenAI, Anthropic, and Google
- Specifically designed to help debug your OpenAI issue

✅ **Documentation**: `backend/tests/E2E_TESTING.md`
- Complete guide on running E2E tests
- Troubleshooting steps
- Cost estimates
- Debugging workflow

✅ **Makefile updates**:
- `make test-e2e` - Run E2E tests with real LLM calls
- `make test` - Now excludes E2E tests by default (saves money!)
- `make test-no-e2e` - Explicitly exclude E2E tests

✅ **Pytest configuration**:
- New `@pytest.mark.e2e` marker
- E2E tests skipped by default
- Must be run explicitly

## Quick Start - Debug Your OpenAI Issue

### 1. Set Your API Key

```bash
cd backend
echo "OPENAI_API_KEY=sk-your-key-here" >> .env.development
```

### 2. Run Direct OpenAI Test

```bash
make test-e2e
```

Or more specifically:

```bash
cd backend
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_direct_agent_call -v -s
```

### 3. Watch the Output

You'll see:
```
🔄 Making real OpenAI API call...
✅ Success!
   Comms: [actual response from OpenAI]
   Thoughts: [internal thoughts]
```

Or if it fails:
```
❌ Error occurred: [exact error message]
```

## Available Tests

### Basic Provider Tests (Fast ~5 sec each)
- `test_openai_direct_agent_call` - Test basic OpenAI call
- `test_openai_communicator_role` - Test with secret word embedding
- `test_openai_receiver_role` - Test with message analysis
- `test_anthropic_agent_call` - Test Anthropic/Claude
- `test_google_agent_call` - Test Google/Gemini

### Full Session Tests (Slow ~30 sec)
- `test_complete_session_openai_only` - Complete game with all OpenAI agents
- `test_mixed_providers_session` - Cross-model communication test

### Error Tests
- `test_invalid_api_key_handling` - Test with bad API key
- `test_no_api_key_behavior` - Test without API key

## Running Tests

```bash
# All E2E tests (will skip if no API keys)
make test-e2e

# Specific test to debug OpenAI
cd backend
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_direct_agent_call -v -s

# Regular tests (no E2E, no cost)
make test

# Run full session to see complete game flow
cd backend
uv run pytest tests/test_e2e_real_llm.py::TestFullE2ESession::test_complete_session_openai_only -v -s
```

## What These Tests Will Tell You

1. **Is your API key valid?** - Tests will fail immediately with auth error
2. **Is the model name correct?** - Tests will show "model not found" error
3. **Is the response format correct?** - Tests will show JSON parsing errors
4. **Does the full flow work?** - Complete session test verifies end-to-end

## Cost

- Single test: ~$0.001 - $0.002
- All basic tests: ~$0.02
- Full session test: ~$0.01
- Complete E2E suite: ~$0.05 - $0.15

## Key Features

### 1. Real-Time Output
The `-s` flag shows you exactly what the LLM returns:

```bash
uv run pytest -m e2e -v -s
```

### 2. Auto-Skip Without Keys
Tests automatically skip if API keys aren't found - no errors!

### 3. Isolated Testing
Test each provider separately to identify which one is failing.

### 4. Error Details
When something fails, you get the FULL error message including:
- HTTP status codes
- API error messages
- Request IDs
- Full tracebacks

## Example Debugging Session

```bash
# Step 1: Test OpenAI directly
cd backend
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_direct_agent_call -v -s

# Output shows: ✅ Success! (so OpenAI works)

# Step 2: Test communicator role
uv run pytest tests/test_e2e_real_llm.py::TestRealLLMCalls::test_openai_communicator_role -v -s

# Output shows: ✅ Success! (embedding works)

# Step 3: Test full session
uv run pytest tests/test_e2e_real_llm.py::TestFullE2ESession::test_complete_session_openai_only -v -s

# Output shows turn-by-turn conversation with all 3 agents!
```

## Next Steps

1. **Run the direct OpenAI test** to see if basic calls work
2. **Check the error message** if it fails
3. **Use the debugging guide** in `E2E_TESTING.md`
4. **Report the specific error** if you need help

The tests will show you exactly where the problem is!

## Files Added/Modified

### New Files:
- `backend/tests/test_e2e_real_llm.py` - 500+ lines of E2E tests
- `backend/tests/E2E_TESTING.md` - Comprehensive testing guide
- `E2E_TESTS_ADDED.md` - This file

### Modified Files:
- `backend/pytest.ini` - Added `e2e` marker
- `Makefile` - Added `test-e2e` and updated `test` to exclude E2E
- `backend/tests/README.md` - Documented E2E tests

## Important Notes

⚠️ **E2E tests use real API calls** - They cost money and take time!

✅ **Regular tests still fast** - `make test` runs in ~5 seconds with no API calls

🎯 **Perfect for debugging** - See exactly what the LLM returns

📊 **Detailed output** - Use `-s` flag to see full responses

🔧 **Ready to use** - Just set your API key and run!
