from enum import Enum
from typing import Optional

from openai import  Omit, OpenAI as OpenAIClient, omit
from llm.llm import LLM, ChatOptions, Chat

class OpenAIModel(Enum):
    pass

class ChatGPTModel(OpenAIModel):
    GPT_5="gpt-5"
    GPT_5_MINI="gpt-5-mini"
    GPT_5_NANO="gpt-5-nano"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O3 = "o3"
    O4_MINI = "o4-mini"

class DeepseekModel(OpenAIModel):
    DEEPSEEK_R1 = "deepseek-reasoner"

class OpenAI(LLM):
    def __init__(self, model: OpenAIModel, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model
        self.client = OpenAIClient(api_key=api_key, base_url=base_url)
        self._unsupported_params : dict[OpenAIModel, list[str]] = {
            ChatGPTModel.O3: ["presence_penalty"],
            ChatGPTModel.O4_MINI: ["presence_penalty"],
            ChatGPTModel.GPT_5_NANO: ["presence_penalty"],
            ChatGPTModel.GPT_5_MINI: ["presence_penalty"],
            ChatGPTModel.GPT_5: ["presence_penalty"],
        }

    def _get_messages(self, chat: Chat) -> list:
        return [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in chat.messages
        ]
    
    def _get_presence_penalty(self, options: Optional[ChatOptions]) -> float|Omit:
        if not options or options.presence_penalty is None:
            return omit
        if self.model in self._unsupported_params and 'presence_penalty' in self._unsupported_params[self.model]:
            return omit
        return 2*options.presence_penalty
    
    def _get_temperature(self, options: Optional[ChatOptions]) -> float|Omit:
        if not options or options.temperature is None:
            return omit
        if self.model in self._unsupported_params and 'temperature' in self._unsupported_params[self.model]:
            return omit
        return 2*options.temperature

    def chat(self, chat: Chat, options: Optional[ChatOptions] = None) -> str:
        completions = self.client.chat.completions.create(
            model=self.model.value,
            messages=self._get_messages(chat),
            presence_penalty=self._get_presence_penalty(options),
            temperature=self._get_temperature(options),
        )
        response = completions.choices[0].message.content
        if response is None:
            raise ValueError("No response from OpenAI API")
        return response

    def __str__(self) -> str:
        return self.model.value
