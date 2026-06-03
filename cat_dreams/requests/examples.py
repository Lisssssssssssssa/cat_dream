from .requests import Request

REQUESTS = [
    Request(
        name="Боюсь пылесоса",
        problem="Мне снится пылесос. Помоги победить страх.",
        required=["enemy", "weapon"],
        forbidden=["замкнутые пространства"]
    ),
    Request(
        name="Где моя игрушка?",
        problem="Я забыл, где спрятал свою любимую мышку. Найди её во сне.",
        required=["объект", "финиш"],
        forbidden=[]
    ),
    Request(
        name="Первая любовь",
        problem="Хочу снова увидеть Мурку из двора — мою первую любовь.",
        required=["персонаж", "место", "эмоция"],
        forbidden=["агрессия"]
    ),
    Request(
        name="Летаю!",
        problem="Мне снилось, что я лечу. Хочу повторить это во сне.",
        required=["платформа", "эффект полёта", "финиш"],
        forbidden=["падение без защиты"]
    )
]
