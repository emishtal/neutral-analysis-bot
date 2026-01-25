from enum import Enum, auto

class ConversationState(Enum):
    """Состояния разговора с ботом"""
    
    # Начальное состояние
    START = auto()
    
    # 8 основных вопросов
    ASKING_Q1_SITUATION = auto()        # Краткое описание ситуации
    ASKING_Q2_PARTICIPANTS = auto()     # Участники
    ASKING_Q3_AGREEMENT = auto()        # Была ли договорённость
    ASKING_Q4_AGREEMENT_DETAILS = auto() # Что было оговорено
    ASKING_Q5_COMPLETION = auto()       # Что считается выполнением (КЛЮЧЕВОЙ!)
    ASKING_Q6_WHAT_HAPPENED = auto()    # Что произошло фактически
    ASKING_Q7_EVIDENCE = auto()         # Доказательства
    ASKING_Q8_CONCERN = auto()          # Что беспокоит
    
    # Подтверждение данных
    CONFIRMING_DATA = auto()
    
    # Выбор тарифа (первичный)
    CHOOSING_BASIC_TARIFF = auto()      # 49₽
    
    # Уточнение фактов
    OFFERING_REFINEMENT = auto()        # Предложение уточнить
    ASKING_REFINEMENT = auto()          # Ввод уточнений
    
    # Апгрейд до расширенного
    OFFERING_UPGRADE = auto()           # Предложение 99₽
    
    # Персонализация (опционально)
    OFFERING_PERSONALIZATION = auto()   # Предложить указать имя
    ASKING_NAME = auto()                # Ввод имени
    ASKING_AGE = auto()                 # Ввод возраста
    ASKING_GENDER = auto()              # Выбор пола
    
    # Завершение
    COMPLETED = auto()


# Словарь для хранения данных пользователя в процессе диалога
# Структура: {user_id: {'state': ConversationState, 'data': {...}}}
USER_DATA = {}


def get_user_state(user_id: int) -> ConversationState:
    """Получить текущее состояние пользователя"""
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            'state': ConversationState.START,
            'data': {}
        }
    return USER_DATA[user_id]['state']


def set_user_state(user_id: int, state: ConversationState):
    """Установить состояние пользователя"""
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            'state': state,
            'data': {}
        }
    else:
        USER_DATA[user_id]['state'] = state


def get_user_data(user_id: int, key: str = None):
    """Получить данные пользователя"""
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            'state': ConversationState.START,
            'data': {}
        }
    
    if key:
        return USER_DATA[user_id]['data'].get(key)
    return USER_DATA[user_id]['data']


def set_user_data(user_id: int, key: str, value):
    """Сохранить данные пользователя"""
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            'state': ConversationState.START,
            'data': {}
        }
    USER_DATA[user_id]['data'][key] = value


def clear_user_data(user_id: int):
    """Очистить данные пользователя"""
    if user_id in USER_DATA:
        del USER_DATA[user_id]


def reset_user_session(user_id: int):
    """Сбросить сессию пользователя (начать заново)"""
    USER_DATA[user_id] = {
        'state': ConversationState.START,
        'data': {}
    }
