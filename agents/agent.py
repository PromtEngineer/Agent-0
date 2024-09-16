# agents/agent.py

import logging
import google.generativeai as genai
import re
import json

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, name, role_prompt):
        self.name = name
        self.role_prompt = role_prompt

    def get_solution(self, problem, previous_solution=None):
        messages = []

        # System prompt
        messages.append({"role": "system", "content": self.role_prompt})

        # User prompt
        if previous_solution:
            messages.append({"role": "user", "content": f"Problem:\n{problem}\n\nPrevious Solution:\n{previous_solution}\n\nPlease proceed with your analysis."})
        else:
            messages.append({"role": "user", "content": f"Problem:\n{problem}\n\nPlease provide your solution."})

        # Assistant initial acknowledgment
        messages.append({"role": "assistant", "content": "Understood. I will begin my reasoning steps now."})

        steps = []
        step_count = 1

        while True:
            # Build the prompt for the current reasoning step
            prompt = self.build_prompt(messages)

            response_text = self.make_api_call(prompt)

            if not response_text:
                logger.error(f"{self.name} did not return a valid response.")
                break  # Exit the loop if no response

            step_data = self.parse_response(response_text)

            if not step_data:
                logger.error(f"{self.name} failed to parse response: {response_text}")
                break  # Exit the loop on parsing failure

            # Log the response for debugging
            logger.info(f"{self.name} received response: {response_text}")
            logger.info(f"Parsed step data: {step_data}")

            # Store the step and content
            steps.append((f"Step {step_count}: {step_data['title']}", step_data['content']))

            messages.append({"role": "assistant", "content": response_text})

            if step_data['next_action'] == 'final_answer':
                break

            step_count += 1

        # Compile the agent's solution
        agent_solution = self.compile_solution(steps)
        logger.info(f"{self.name} completed their solution with steps: {steps}")
        return agent_solution

    def build_prompt(self, messages):
        # Combine messages into a single prompt
        prompt = ''
        for message in messages:
            role = message['role']
            content = message['content']
            if role == 'system':
                prompt += f"System: {content}\n\n"
            elif role == 'user':
                prompt += f"User: {content}\n\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n\n"
        return prompt

    def make_api_call(self, prompt):
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-exp-0827',
            tools='code_execution'
        )
        try:
            response = model.generate_content(prompt)
            return response.text if hasattr(response, 'text') else ""
        except Exception as e:
            logger.error(f"Error during API call for {self.name}: {str(e)}")
            return ""

    def parse_response(self, response_text):
        if not isinstance(response_text, str):
            logger.error(f"{self.name} received a non-string response: {response_text}")
            return None

        try:
            # Extract JSON from the response
            json_pattern = r"```json\s*(\{[\s\S]*?\})\s*```"
            match = re.search(json_pattern, response_text)
            if match:
                response_json = match.group(1)
                return json.loads(response_json)
            else:
                # Attempt to parse the entire response as JSON
                return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"{self.name} error parsing JSON response: {str(e)} - Response Text: {response_text}")
            return None

    def compile_solution(self, steps):
        solution_text = ""
        for title, content in steps:
            solution_text += f"### {title}\n{content}\n\n"
        return solution_text
