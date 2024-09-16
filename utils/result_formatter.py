def format_results(all_solutions, final_solution):
    formatted_text = ""
    formatted_text += "=== Agent Solutions ===\n\n"
    for agent_name, solution_text in all_solutions:
        formatted_text += f"--- {agent_name} ---\n{solution_text}\n\n"
    formatted_text += "=== Final Synthesized Solution ===\n\n"
    formatted_text += final_solution + "\n\n"
    return formatted_text
