from brain import SentimentFlowEngine
engine = SentimentFlowEngine()
res = engine.process("What is your return policy?")
print(res)
