#На самом деле нужно было бы вынести данные для
#конкретного бота в базу данных
#и тогда это была бы pydantic-схема
class PayBotConfig:
    token: str = "7757143982:AAETbv8WCulHRNx_Z1vSSeDVEHO75ZCTWJQ"

    name: str
    photo: str | None
