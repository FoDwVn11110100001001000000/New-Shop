from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class StateList(StatesGroup):
    LOT_MENU = State()
    TOPUP_BALANCE = State()


class StateManager:
    def __init__(self, fsm_context: FSMContext):
        self.fsm = fsm_context

    async def set_state(self, state: State) -> None:
        await self.fsm.set_state(state.state)

    async def get_state(self) -> str | None:
        return await self.fsm.get_state()

    async def set_data(self, key: str, value) -> None:
        await self.fsm.update_data(**{key: value})

    async def get_data(self, key: str):
        data = await self.fsm.get_data()
        return data.get(key)

    async def get_all_data(self) -> dict:
        return await self.fsm.get_data()
