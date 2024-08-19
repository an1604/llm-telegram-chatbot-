import asyncio
import logging
from dataclasses import dataclass
from os import getenv
from threading import Event
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, SceneRegistry, ScenesManager, on
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.types import Message

from llm import llm_factory
from dotenv import load_dotenv
from learner import learner

load_dotenv()

TOKEN = getenv("DECEPTIFYBOT_TOKEN")
user_attacks = {}


@dataclass
class Attack:
    def __init__(self, attack_type, profile_name):
        self.attack_type = attack_type
        self.profile_name = profile_name
        self.llm = llm_factory.generate_new_attack(attack_type, profile_name)


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
        await message.answer(
            "Hi! It's Deceptify bot. To start a demo, first use the /type command.")

    @attack_router.message(Command("type"))
    async def attack_type_command(message: Message, scenes: ScenesManager, state: FSMContext):
        await scenes.close()
        await state.update_data(attack_type=None)
        await message.answer("Choose an attack type:\n"
                             "1. Bank\n"
                             "2. Delivery\n"
                             "3. Hospital")

    @attack_router.message(Command("desc"))
    async def description_command(message: Message, scenes: ScenesManager, state: FSMContext):
        await scenes.close()
        await message.answer(
            """
        Our project focuses on harnessing the power of AI to simulate social engineering attacks, using advanced technologies like generative AI and deepfakes. 
        The goal is to help organizations improve their awareness and preparedness against the ever-changing landscape of digital threats.
        """)

    @attack_router.message(Command('transcript'))
    async def transcript_command(message: Message, scenes: ScenesManager, state: FSMContext):
        await scenes.close()
        user_id = message.from_user.id
        if user_id in user_attacks.keys() and 'transcript' in user_attacks[user_id]:
            await message.answer(user_attacks[user_id]['transcript'])
        else:
            await message.answer('No transcript is available for you.')

    @attack_router.message(F.text.in_(['Bank', 'Delivery', 'Hospital']))
    async def set_attack_type_from_str(message: Message, state: FSMContext):
        await state.update_data(attack_type=message.text)
        await message.answer(f"Attack type '{message.text}' chosen. You can now run the attack with /run.")

    @attack_router.message(F.text.in_(['1', '2', '3']))
    async def set_attack_type_from_number(message: Message, state: FSMContext):
        attack_type = None
        if message.text == "1":
            attack_type = 'Bank'
        elif message.text == "2":
            attack_type = 'Delivery'
        else:
            attack_type = 'Hospital'

        await state.update_data(attack_type=attack_type)
        await message.answer(f"Attack type '{attack_type}' chosen. You can now run the attack with /run.")


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

            user = message.from_user
            profile_name = user.username if user.username else f"{user.first_name} {user.last_name}".strip()

            attack = Attack(attack_type=attack_type, profile_name=profile_name)
            llm = llm_factory.generate_new_attack(attack_type, profile_name)

            user_attacks[user.id] = {'llm': (attack, llm),
                                     }
            await message.answer(llm.get_init_msg())

    @on.message()
    async def attack_continuation(self, message: Message) -> None:
        """
        Method triggered when the user sends a message that is not a command or an answer.
        """
        try:
            user = message.from_user
            llm = user_attacks[user.id]['llm'][1]
            response = llm.get_answer(message.text.lower())
            if 'bye' in response or 'bye' in message.text:
                user_attacks[user.id]['transcript'] = llm.get_transcript()
                user_attacks[user.user.id]['llm'] = None
                await message.answer("Goodbye")
                return await self.wizard.exit()

        except Exception as e:
            print(f"Error: {e}")
            return await message.answer("Please generate a new attack using /type.")

        return await message.answer(text=response)


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
        learner.stop_active_learning()


async def main():
    chatbot = ChatBot()
    try:
        await chatbot.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down bot...")
        chatbot.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
