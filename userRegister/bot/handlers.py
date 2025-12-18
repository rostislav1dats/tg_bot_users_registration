from aiogram import Router, types

router = Router()

@router.message()
async def echo(message: types.Message):
    await message.answer(f'Your wrote: {message.text}')
