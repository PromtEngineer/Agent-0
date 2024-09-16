# main.py

import logging
import os
import time

from agents.agent_factory import AgentFactory
from utils.user_input_handler import get_user_input
from utils.result_formatter import format_results

import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='logs/system.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure the Gemini API
genai.configure(api_key=os.environ.get("API_KEY"))

def main():
    # Step 1: User Input Handler
    user_problem = get_user_input()
    logger.info("User problem received: %s", user_problem)

    # Step 2: Sequential Processing through Agents
    agent_factory = AgentFactory()
    agents = agent_factory.create_agents()  # Returns the list of agents in sequence

    previous_solution = None
    all_solutions = []

    for agent in agents:
        solution = agent.get_solution(user_problem, previous_solution)
        all_solutions.append((agent.name, solution))
        previous_solution = solution  # Pass the current solution to the next agent

    # Step 3: Final Output
    final_solution = previous_solution

    # Step 4: Result Formatting and Output
    formatted_result = format_results(all_solutions, final_solution)
    print("Final Answer:")
    print(final_solution)
    print("\nDetailed Reasoning and Steps:")
    print(formatted_result)

if __name__ == "__main__":
    main()
