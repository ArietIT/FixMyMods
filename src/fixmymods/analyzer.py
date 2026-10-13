def find_errors(path):
    try:
        with open(path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        return []

    errors = []

    for line in lines:
        if "error" in line.lower() or "exception" in line.lower():
            errors.append(line)

    return errors