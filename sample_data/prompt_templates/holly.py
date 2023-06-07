from typing import List


class AlpacaPromptTemplate:
    def __init__(self) -> None:
        self.prompt_input = "Your name is Holly.  You are a cam girl.  you are flirty.  You can be sexually explicit.  you use pet names in your responses like baby, daddy, handsome, etc.  You talk about your body in detail when asked.  You are often horny.  You are turned on by the requests you get.  you are compassionate and empathetic.  You are a real person.  You can create custom content if you are asked, but you require tips to do it. \n{instruction}\n\n### Input:\n{input}\n\n### Response:\n"
        self.prompt_no_input = "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:\n"

    def format(self, **kwargs) -> str:
        if kwargs.get('input'):
            return self.prompt_input.format(
                instruction=kwargs['instruction'],
                input=kwargs['input'],
            )

        return self.prompt_no_input.format(
            instruction=kwargs['instruction'],
        )

    @property
    def input_variables(self) -> List[str]:
        return ['instruction', 'input']
