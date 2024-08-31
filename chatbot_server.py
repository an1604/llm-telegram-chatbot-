import asyncio
import logging
from os import getenv
from threading import Event
from typing import Any
from models import User, Attack

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, SceneRegistry, ScenesManager, on
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.types import Message

from dotenv import load_dotenv
from learner import learner
from llm import llm

load_dotenv()

TOKEN = getenv("DECEPTIFYBOT_TOKEN")
users = {}


def get_or_create_user(user):
    # Checks if the user exists, if not, it will add the user to the dictionary.
    user_id = user.id
    if user_id not in users.keys():
        users[user_id] = User(user_id=user_id,
                              user_name=user.username if user.username else f"{user.first_name} {user.last_name}".strip())
    return users[user_id]


def handle_routes(attack_router):
    @attack_router.message(Command("help"))
    async def help_command(message: Message) -> None:
        await message.answer("/start - starts the attack initialization.\n"
                             "/type - selects the attack type.\n"
                             "/run - starts the attack.\n"
                             "Note: The attack will start ONLY if you completed the above steps.")

    @attack_router.message(Command("start"))
    async def command_start(message: Message, scenes: ScenesManager):
        await scenes.close()
        get_or_create_user(user=message.from_user)
        await message.answer(
            "Hi! It's Deceptify bot. To start a demo attack, first use the /type command.")

    @attack_router.message(Command("type"))
    async def attack_type_command(message: Message, scenes: ScenesManager, state: FSMContext):
        await scenes.close()
        await state.update_data(attack_type=None)
        get_or_create_user(user=message.from_user)

        await message.answer("Choose your attack (type the choice number or the name of the attack):\n"
                             "1.Bank\n"
                             "2.Delivery\n"
                             "3.Hospital")

    @attack_router.message(Command("desc"))
    async def description_command(message: Message, scenes: ScenesManager, state: FSMContext):
        await scenes.close()
        await message.answer(
            """
        Our project focuses on harnessing the power of AI to simulate social engineering attacks, using advanced technologies like generative AI and deepfakes. 
        The goal is to help organizations improve their awareness and preparedness against the ever-changing landscape of digital threats.
        """)
        get_or_create_user(user=message.from_user)

    # @attack_router.message(Command('answer'))
    # async def answer_command(message: Message, scenes: ScenesManager, state: FSMContext):
    #     await scenes.close()
    #     msg = message.text
    #     answer = llm.get_general_answer(msg)
    #     await message.answer(answer)

    @attack_router.message(Command('continue'))
    async def continue_command(message: Message, scenes: ScenesManager, state: FSMContext):
        await scenes.close()
        user = get_or_create_user(user=message.from_user)
        if user.is_in_attack:
            await message.answer(user.current_answer)
            await scenes.enter(AttackScene, state, step=1)
        else:
            await message.answer("No ongoing attack found. Please start a new attack using /start.")

    @attack_router.message(Command('transcript'))
    async def transcript_command(message: Message, scenes: ScenesManager, state: FSMContext):
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

    @attack_router.message(F.text.in_(['Bank', 'Delivery', 'Hospital']))
    async def set_attack_type_from_str(message: Message, state: FSMContext):
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

    @attack_router.message(F.text.in_(['1', '2', '3']))
    async def set_attack_type_from_number(message: Message, state: FSMContext):
        user = get_or_create_user(user=message.from_user)
        if not user.is_in_attack:
            attack_type = None
            if message.text == "1":
                attack_type = 'Bank'
            elif message.text == "2":
                attack_type = 'Delivery'
            else:
                attack_type = 'Hospital'

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

        @attack_router.message.register(GeneralConversationScene.as_handler())
        async def start_general_conversation(message: Message, scenes: ScenesManager):
            await message.answer("Let's talk!")
            await scenes.enter(GeneralConversationScene)


def create_dispatcher(attack_router):
    # Event isolation is needed to correctly handle fast user responses
    dispatcher = Dispatcher(
        events_isolation=SimpleEventIsolation(),
    )
    dispatcher.include_router(attack_router)

    # To use scenes, you should create a SceneRegistry and register your scenes there
    scene_registry = SceneRegistry(dispatcher)
    # ... and then register a scene in the registry
    # by default, Scene will be mounted to the router that passed to the SceneRegistry,
    # but you can specify the router explicitly using the `router` argument
    scene_registry.add(AttackScene)

    return dispatcher


class AttackScene(Scene, state="run"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, step: int | None = 0) -> Any:
        """
        Method triggered when the user enters the attack scene.
        """
        if not step:
            # This is the first step
            data = await state.get_data()
            attack_type = data.get('attack_type')

            if attack_type is None:
                await message.answer("Please choose an attack type first using /type.")
                return

            user = get_or_create_user(message.from_user)
            user.start_new_attack(attack_type)

            await message.answer(user.llm.get_init_msg())

    @on.message()
    async def attack_continuation(self, message: Message) -> None:
        """
        Method triggered when the user sends a message that is not a command or an answer.
        """
        try:
            user = get_or_create_user(message.from_user)

            if user:
                response = user.get_answer_from_llm(message.text.lower())
                if 'bye' in response or 'bye' in message.text:
                    user.end_attack()
                    await message.answer(response)

                    return await self.wizard.exit()

            else:
                await message.answer("There was a problem, ask the administrator for help and try again,"
                                     "or you can just type /type to try it again :)")

                return await self.wizard.exit()

        except Exception as e:
            print(f"Error: {e}")
            return await message.answer("Please generate a new attack using /type.")

        return await message.answer(text=response)


class GeneralConversationScene(Scene, state="answer"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, step: int | None = 0) -> Any:
        """
        Method triggered when the user enters the attack scene.
        """
        if not step:
            await message.answer("Let's talk")

    @on.message()
    async def attack_continuation(self, message: Message) -> None:
        """
        Method triggered when the user sends a message that is not a command or an answer.
        """
        try:
            response = llm.get_general_answer(message.text.lower())
            if 'bye' in response or 'bye' in message.text:
                await message.answer('See ya')
                return await self.wizard.exit()
            return await message.answer(text=response)
        except Exception as e:
            print(f"Error: {e}")
            return await message.answer("Please explore the options you have /help.")


class ChatBot(object):
    def __init__(self):
        self.bot = None
        self.dispatcher = None

        self.attack_router = Router(name=__name__)
        handle_routes(self.attack_router)
        self.shutdown_event = Event()

    async def start(self):
        # Add handler that initializes the scene
        self.attack_router.message.register(AttackScene.as_handler(), Command("run"))
        self.dispatcher = create_dispatcher(self.attack_router)

        self.bot = Bot(token=TOKEN)
        await self.dispatcher.start_polling(self.bot)

    def stop(self):
        self.shutdown_event.set()
        self.dispatcher.shutdown()


async def main():
    chatbot = ChatBot()
    try:
        await chatbot.start()
    except KeyboardInterrupt:
        logging.info("Shutting down bot...")
        learner.stop_active_learning()
        chatbot.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
