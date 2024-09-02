import asyncio
import logging
import random
from threading import Event
from typing import Any
from models import User

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, SceneRegistry, ScenesManager, on
from aiogram.types import Message

from dotenv import load_dotenv
from learner import learner

from aiogram.fsm.storage.memory import SimpleEventIsolation
from bot_utils import *

load_dotenv()

chatbot = None
TOKEN = os.getenv("DECEPTIFYBOT_TOKEN")
users = {}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_dispatcher(attack_router):
    try:
        dispatcher = Dispatcher(
            events_isolation=SimpleEventIsolation(),
        )
        dispatcher.include_router(attack_router)

        scene_registry = SceneRegistry(dispatcher)
        scene_registry.add(AttackScene)

        return dispatcher
    except Exception as e:
        logging.error(f"Error in create_dispatcher: {e}")


def get_or_create_user(user):
    try:
        user_id = user.id
        if user_id not in users.keys():
            users[user_id] = User(user_id=user_id,
                                  user_name=user.username if user.username else f"{user.first_name} {user.last_name}".strip())
        return users[user_id]
    except Exception as e:
        logging.error(f"Error in get_or_create_user: {e}")


def handle_routes(attack_router):
    @attack_router.message(Command("help"))
    async def help_command(message: Message) -> None:
        try:
            await message.answer("/start - starts the attack initialization.\n"
                                 "/type - selects the attack type.\n"
                                 "/run - starts the attack.\n"
                                 "Note: The attack will start ONLY if you completed the above steps.")
        except Exception as e:
            logging.error(f"Error in help_command: {e}")

    @attack_router.message(Command("start"))
    async def command_start(message: Message, scenes: ScenesManager):
        try:
            await scenes.close()
            get_or_create_user(user=message.from_user)
            await message.answer("Hi! It's Deceptify bot. To start a demo attack, first use the /type command.")
        except Exception as e:
            logging.error(f"Error in command_start: {e}")

    @attack_router.message(Command("type"))
    async def attack_type_command(message: Message, scenes: ScenesManager, state: FSMContext):
        try:
            await scenes.close()
            await state.update_data(attack_type=None)
            get_or_create_user(user=message.from_user)

            await message.answer("Choose your attack (type the choice number or the name of the attack):\n"
                                 "1.Bank\n\n"
                                 "2.Delivery\n\n"
                                 "3.Hospital\n\n"
                                 "4. Chat (for voice clone attack) - "
                                 "This attack is used to describes a general chat that the attacker can send messages to the victim "
                                 "through Deceptify app.\n\n"
                                 "You can type as the number or the name of the attack :)")
        except Exception as e:
            logging.error(f"Error in attack_type_command: {e}")

    @attack_router.message(Command("desc"))
    async def description_command(message: Message, scenes: ScenesManager, state: FSMContext):
        try:
            await scenes.close()
            await message.answer(random.choice(project_descriptions))
            get_or_create_user(user=message.from_user)
        except Exception as e:
            logging.error(f"Error in description_command: {e}")

    @attack_router.message(Command('continue'))
    async def continue_command(message: Message, scenes: ScenesManager, state: FSMContext):
        try:
            await scenes.close()
            user = get_or_create_user(user=message.from_user)
            if user.is_in_attack:
                await message.answer(user.current_answer)
                await scenes.enter(AttackScene, state, step=1)
            else:
                await message.answer("No ongoing attack found. Please start a new attack using /start.")
        except Exception as e:
            logging.error(f"Error in continue_command: {e}")

    @attack_router.message(Command('transcript'))
    async def transcript_command(message: Message, scenes: ScenesManager, state: FSMContext):
        try:
            await scenes.close()
            user = get_or_create_user(message.from_user)

            if user and not user.is_in_attack:
                transcript = user.transcript
                if transcript:
                    await message.answer(transcript)
                else:
                    await message.answer('No transcript is available for you.')
            else:
                if not user.is_restart_session():
                    await message.answer(
                        f"I am sorry but I can not provide you information during the attack itself.\n"
                        f"run /continue to come back to the attack, or /start to start a new attack.")
                else:
                    await message.answer(
                        f"Your message can not be processed on the last time, It seems to be a problem on the server.\n"
                        f"I am sorry but I restarted your session. run /start to start a new attack.")
        except Exception as e:
            logging.error(f"Error in transcript_command: {e}")

    @attack_router.message(F.text.in_(['Bank', 'Delivery', 'Hospital', 'Chat']))
    async def set_attack_type_from_str(message: Message, state: FSMContext):
        try:
            await state.update_data(attack_type=message.text)
            user = get_or_create_user(user=message.from_user)
            if not user.is_in_attack:
                await message.answer(f"Attack type '{message.text}' chosen. You can now run the attack with /run.")
            else:
                if not user.is_restart_session():
                    await message.answer(
                        f"Your message can not be processed, maybe the format or the type is not correct.\n"
                        f"run /continue to come back to the attack, or /start to start a new attack.")
                else:
                    await message.answer(
                        f"Your message can not be processed on the last time, It seems to be a problem on the server.\n"
                        f"I am sorry but I restarted your session. Run /start to start a new attack.")
        except Exception as e:
            logging.error(f"Error in set_attack_type_from_str: {e}")

    @attack_router.message(F.text.in_(['1', '2', '3', '4']))
    async def set_attack_type_from_number(message: Message, state: FSMContext):
        try:
            user = get_or_create_user(user=message.from_user)
            if not user.is_in_attack:
                attack_type = None
                if message.text == "1":
                    attack_type = 'Bank'
                elif message.text == "2":
                    attack_type = 'Delivery'
                elif message.text == '3':
                    attack_type = 'Hospital'
                else:
                    attack_type = 'chat'

                await state.update_data(attack_type=attack_type)
                await message.answer(f"Attack type '{attack_type}' chosen. You can now run the attack with /run.")

            else:
                if not user.is_restart_session():
                    await message.answer(
                        f"Your message can not be processed, maybe the format or the type is not correct.\n"
                        f"run /continue to come back to the attack, or /start to start a new attack.")
                else:
                    await message.answer(
                        f"Your message can not be processed on the last time, It seems to be a problem on the server.\n"
                        f"I am sorry but I restarted your session. Run /start to start a new attack.")
        except Exception as e:
            logging.error(f"Error in set_attack_type_from_number: {e}")


class AttackScene(Scene, state="run"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, step: int | None = 0) -> Any:
        try:
            if not step:
                data = await state.get_data()
                attack_type = data.get('attack_type')

                if attack_type is None:
                    await message.answer("Please choose an attack type first using /type.")
                    return

                user = get_or_create_user(message.from_user)
                user.start_new_attack(attack_type)
                if 'chat' not in attack_type.lower():
                    await message.answer(user.llm.get_init_msg())
        except Exception as e:
            logging.error(f"Error in AttackScene.on_enter: {e}")

    @on.message()
    async def attack_continuation(self, message: Message) -> None:
        global chatbot

        try:
            user = get_or_create_user(message.from_user)
            transcription = None
            if user:
                logging.info(f"From AttackScene.attack_continuation, Message type: {message.content_type}")
                if message.content_type in ['audio', 'document']:
                    transcription = await handle_audio_message(message, chatbot.bot)
                response = user.get_answer_from_llm(
                    message.text.lower()) if transcription is None \
                    else \
                    user.get_answer_from_llm(transcription.lower())

                if 'bye' in response or 'bye' in message.text:
                    user.end_attack()
                    await message.answer(response)
                    return await self.wizard.exit()

            else:
                await message.answer("There was a problem, ask the administrator for help and try again,"
                                     "or you can just type /type to try it again :)")
                return await self.wizard.exit()

        except Exception as e:
            logging.error(f"Error in AttackScene.attack_continuation: {e}")
            return await message.answer("Please generate a new attack using /type.")


class ChatBot(object):
    def __init__(self):
        try:
            self.bot = None
            self.dispatcher = None

            self.attack_router = Router(name=__name__)
            handle_routes(self.attack_router)
            self.shutdown_event = Event()
            logging.info("ChatBot initialized.")
        except Exception as e:
            logging.error(f"Error in ChatBot.__init__: {e}")

    async def start(self):
        try:
            self.attack_router.message.register(AttackScene.as_handler(), Command("run"))
            self.dispatcher = create_dispatcher(self.attack_router)

            self.bot = Bot(token=TOKEN)
            await self.dispatcher.start_polling(self.bot)
        except Exception as e:
            logging.error(f"Error in ChatBot.start: {e}")

    def stop(self):
        try:
            self.shutdown_event.set()
            self.dispatcher.shutdown()
        except Exception as e:
            logging.error(f"Error in ChatBot.stop: {e}")


async def main():
    global chatbot

    chatbot = ChatBot()
    try:
        await chatbot.start()
    except KeyboardInterrupt:
        logging.info("Shutting down bot...")
        learner.stop_active_learning()
        chatbot.stop()
    except Exception as e:
        logging.error(f"Error in main: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
