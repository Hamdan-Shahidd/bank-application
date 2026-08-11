from ai.agent import interpret

kind, payload = interpret("send 500 to 9943019054")
print(kind)
print(payload)