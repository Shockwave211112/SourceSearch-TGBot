from environs import Env
from dataclasses import dataclass

@dataclass
class Tokens:
    bot_token: str
    sauce_token: str
    
@dataclass
class Settings:
    tokens: Tokens
    
def get_settings(path: str):
    env = Env()
    env.read_env(path)
    
    return Settings(
        tokens=Tokens(
            bot_token=env.str("TG_TOKEN"),
            sauce_token=env.str("SAUCE_TOKEN")
        )
    )

settings = get_settings('creds')