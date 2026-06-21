from rag_system import TraumaKnotRAG

rag = TraumaKnotRAG()

print('Running clinical assessment test...')
user_input = "I was in a car accident and now I panic when driving; I avoid roads and sometimes have flashbacks at night."
res = rag.clinical_assess_and_plan(user_input, followup_questions=3)
print('\n--- CLINICIAN ANALYSIS ---\n')
print(res['analysis'][:1000])

q = rag.generate_followup_question()
print('\n--- NEXT FOLLOW-UP QUESTION ---\n')
print(q)

