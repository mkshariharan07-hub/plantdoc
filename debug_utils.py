import utils
print(dir(utils))
if hasattr(utils, 'build_quantum_circuit'):
    print("Found build_quantum_circuit")
else:
    print("build_quantum_circuit NOT found")
