from fixmymods.analyzer import find_errors

errors = find_errors(path="examples/missing.txt")
print(errors)