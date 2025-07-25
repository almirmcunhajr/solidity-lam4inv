from enum import Enum
from typing import Optional

from openai import NotGiven, OpenAI as OpenAIClient, NOT_GIVEN

from llm.llm import LLM, ChatOptions, Chat

class OpenAIModel(Enum):
    pass

class ChatGPTModel(OpenAIModel):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    O1_MINI = "o1-mini"
    O3_MINI = "o3-mini"

class DeepseekModel(OpenAIModel):
    DEEPSEEK_R1 = "deepseek-reasoner"

class OpenAI(LLM):
    def __init__(self, model: OpenAIModel, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model
        self.client = OpenAIClient(api_key=api_key, base_url=base_url)
        self._unsupported_params : dict[OpenAIModel, list[str]] = {
            ChatGPTModel.O1_MINI: ["presence_penalty"],
            ChatGPTModel.O3_MINI: ["presence_penalty"],
        }

    def _get_messages(self, chat: Chat) -> list:
        return [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in chat.messages
        ]
    
    def _get_presence_penalty(self, options: Optional[ChatOptions]) -> float|NotGiven:
        if not options or options.presence_penalty is None:
            return NOT_GIVEN
        if self.model in self._unsupported_params and 'presence_penalty' in self._unsupported_params[self.model]:
            return NOT_GIVEN
        return 2*options.presence_penalty
    
    def _get_temperature(self, options: Optional[ChatOptions]) -> float|NotGiven:
        if not options or options.temperature is None:
            return NOT_GIVEN
        if self.model in self._unsupported_params and 'temperature' in self._unsupported_params[self.model]:
            return NOT_GIVEN
        return 2*options.temperature

    def chat(self, chat: Chat, options: Optional[ChatOptions] = None) -> Optional[str]:
        completions = self.client.chat.completions.create(
            model=self.model.value,
            messages=self._get_messages(chat),
            presence_penalty=self._get_presence_penalty(options),
            temperature=self._get_temperature(options),
        )
        response = completions.choices[0].message.content
        return response
