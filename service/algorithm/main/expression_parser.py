def evaluate_criteria(expression, variables):
    """
    Evaluates the criteria expression given variables.

    Args:
    - expression (str): The expression to evaluate.
    - variables (dict): Dictionary containing variable names as keys and their corresponding values.

    Returns:
    - bool: True if the criteria expression is satisfied, False otherwise.
    """
    # Replace variable names with their values in the expression
    for var, val in variables.items():
        expression = expression.replace(var, str(val))
    print(expression)
    # Evaluate the expression
    try:
        result = eval(expression)
        return bool(result)
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression: {e}")

def calculate_score(expression, variables):
    """
    Calculates the score based on the expression and variable values.

    Args:
    - expression (str): The expression to evaluate.
    - variables (dict): Dictionary containing variable names as keys and their corresponding values.

    Returns:
    - float: The calculated score.
    """
    # Replace variable names with their values in the expression
    for var, val in variables.items():
        expression = expression.replace(var, str(val))

    # Evaluate the expression
    try:
        score = eval(expression)
        return score
    except Exception as e:
        raise ValueError(f"Failed to calculate score: {e}")
