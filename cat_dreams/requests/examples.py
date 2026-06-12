from .requests import Request

REQUESTS = [
    Request(
        name="Где моя игрушка?",
        problem="Я забыл, где спрятал мышку. Помоги вспомнить.",
        required=["помочь вспомнить"],
        forbidden=[]
    ),
    Request(
        name="Мне грустно",
        problem="Мне снится, что я один. Помоги сделать сон менее грустным.",
        required=["грустный"],
        forbidden=[]
    ),
    Request(
        name="Хочу улыбнуться",
        problem="Мне нужен веселый сон!",
        required=["веселый"],
        forbidden=[]
    )
]
