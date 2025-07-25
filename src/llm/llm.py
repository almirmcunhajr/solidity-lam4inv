from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel
from enum import Enum

class ChatOptions(BaseModel):
    presence_penalty: Optional[float] = None
    temperature: Optional[float] = None

class ChatMessageRole(Enum):
    user = "user"
    assistant = "assistant"

class ChatMessage(BaseModel):
    role: ChatMessageRole
    content: str

class Chat(BaseModel):
    messages: list[ChatMessage] = []

    def add_user_message(self, message: str):
        self.messages.append(ChatMessage(role=ChatMessageRole.user, content=message))

    def add_assistant_response(self, message: str):
        self.messages.append(ChatMessage(role=ChatMessageRole.assistant, content=message))

    def reset(self):
        self.messages = []

class LLM(ABC):
    @abstractmethod
    def chat(self, chat: Chat, options: Optional[ChatOptions] = None) -> str:
        pass

    def __str__(self) -> str:
        return self.model.value
