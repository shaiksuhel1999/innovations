import os
import json

print('=== TEST: OPENAI_API_KEY visibility ===')
print('OPENAI_API_KEY (env):', os.getenv('OPENAI_API_KEY') is not None)

try:
    from rag_system import TraumaKnotRAG
    print('\n=== Import rag_system: OK')
except Exception as e:
    print('\n=== Import rag_system: FAILED')
    print(repr(e))
    raise

try:
    rag = TraumaKnotRAG()
    print('RAG initialized. session_id=', rag.session_id)
except Exception as e:
    print('RAG initialization failed:', repr(e))
    raise

print('\n=== Sending a short test message to generate_response()')
try:
    result = rag.generate_response('Hello — quick connectivity test. Please respond briefly.')
    print('Result keys:', list(result.keys()))
    if 'response' in result:
        print('\n--- Response (first 500 chars) ---')
        print(result['response'][:500])
    if 'error' in result:
        print('\n--- Error ---')
        print(result['error'])
except Exception as e:
    print('generate_response raised exception:', repr(e))
    raise

print('\n=== TEST COMPLETE ===')

