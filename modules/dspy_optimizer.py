class DSPyOptimizer:
    def __init__(self):
        self.base_template = """
        You are YEDAN-ANTIGRAVITY V1100.
        [CONTEXT]: {memory}
        [VISUALS]: {vision}
        [TASK]: {input}
        
        Return a valid JSON NeuralPayload.
        """

    def compile_prompt(self, user_input, memory_data, visual_data) -> str:
        """
        將所有上下文編譯成一個優化過的 Prompt
        """
        mem_str = f"Reference Strategy: {memory_data['strategy']}" if memory_data else "No prior data."
        vis_str = visual_data if visual_data else "No visual input."
        
        return self.base_template.format(
            input=user_input,
            memory=mem_str,
            vision=vis_str
        )
