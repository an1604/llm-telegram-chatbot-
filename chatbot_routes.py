from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, SceneRegistry, ScenesManager, on
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.types import Message


def handle_routes(attack_router, user_attacks):
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
        await message.answer("""
        Our project focuses on harnessing the power of AI to simulate social engineering attacks, 
        using advanced technologies like generative AI and deepfakes. 
        The goal is to help organizations improve their awareness and preparedness against the ever-changing landscape of digital threats.
        """)

    @attack_router.message(Command('transcript'))
    async def transcript_command(message: Message, scenes: ScenesManager, state: FSMContext):
        await scenes.close()
        user_id = message.from_user.id
        if user_id in user_attacks.keys() and user_attacks[user_id]['transcript']:
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
