from typing import List, Dict
from app import webapp
import os
import json
import yaml
import openai


class Conversation:
    PROMPT = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly."
    BOT_START = "Hello. I am an AI agent designed to help you manage your mood and mental health. How can I help you?"
    USER = "Human"
    CHATBOT = "AI"
    WARNING = "Warning"
    END = "End"
    NOTI = "Notification"

    def __init__(self, user: str, chatbot: str, chat_log: str=None) -> None:
        self.user_name = user
        self.chatbot_name = chatbot
        self.chat_log = chat_log if chat_log is not None and chat_log != "" else self.PROMPT

        self.start_sequence = f"\n{self.CHATBOT}:"
        self.restart_sequence = f"\n\n{self.USER}: "

    def get_user(self) -> str:
        return self.user_name

    def get_chatbot(self) -> str:
        return self.chatbot_name
    
    def sync_chatlog(self, chatlog: str) -> None:
        self.chat_log = chatlog
    
    def append_user_message_to_chatlog(self, user_message: str) -> str:
        self.chat_log = f"{self.chat_log}{self.restart_sequence}{user_message}{self.start_sequence} "

        return self.chat_log

    def append_dummy_bot_message_to_chatlog(self) -> str:
        self.chat_log = f"{self.chat_log}{self.start_sequence} THIS IS A DUMMY BOT MESSAGE."

        return self.chat_log

    def append_bot_message_to_chatlog(self, bot_message) -> str:
        self.chat_log = f"{self.chat_log}{bot_message}"

        return self.chat_log

    def get_conversation(self, end: bool=False, test: bool=False) -> List[Dict]:
        chat_log_clean = self.chat_log.split(self.PROMPT)[1]
        dialogs = chat_log_clean.split(self.restart_sequence)

        converation = []

        if test:
            converation.append({
                "from": self.chatbot_name,
                "to": self.WARNING,
                "message": self.PROMPT,
                "send_time": None
            })
        
        converation.append({
            "from": self.chatbot_name,
            "to": self.user_name,
            "message": self.BOT_START,
            "send_time": None
        })

        for i in range(1, len(dialogs)):
            messages = dialogs[i].split(self.start_sequence)

            for msg_idx, msg in enumerate(messages):
                if msg_idx == 0:
                    from_idt = self.user_name
                    to_idt = self.chatbot_name
                else:
                    to_idt = self.user_name
                    from_idt = self.chatbot_name

                convo = []
                for text in msg.split("\n"):
                    if len(text) != 0:
                        convo.append({
                            "from": from_idt,
                            "to": to_idt,
                            "message": text.strip(),
                            "send_time": None
                        })
                converation.extend(convo)
        
        if end:
            converation.append({
                "from": self.chatbot_name,
                "to": self.END,
                "message": "This conversation is ended. You can close this window and restart another conversation.",
                "send_time": None
            })
        
        return converation


class GPTConversation(Conversation):
    CONFIGS = {
        "engine": "text-davinci-002",
        "temperature": 0.9,
        "max_tokens": 300,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0.6,
    }

    def __init__(self, user: str, chatbot: str, chat_log: str = None) -> None:
        super().__init__(user, chatbot, chat_log)
        with open(os.path.join(webapp.config['CONFIG_FOLDER'], 'openai_config.yaml'), 'r') as f:
            openai_config_str = json.dumps(yaml.safe_load(f))
        openai_config = json.loads(openai_config_str)
        openai.api_key = openai_config['openai_api_key']

    def get_answer(self) -> str:
        response = openai.Completion.create(
            prompt=self.chat_log,
            stop=[" {}:".format(self.USER), " {}:".format(self.CHATBOT)],
            **self.CONFIGS
        )

        story = response['choices'][0]['text']
        answer = str(story).strip().split(self.restart_sequence.rstrip())[0]

        return answer

