from components import Connect, Health, Hydration, Oxygen, Player, Position, Renderable, Stomach, Velocity

def player(x, y, icon='@'):
    return [
        Player(),
        Renderable(fg_char=icon),
        Position(x, y),
        Velocity(),
        Connect(),
        Health(),
        Stomach(),
        Hydration(),
        Oxygen(),
    ]

def fire(x,y):
    return [
        Renderable(x,y,fg_animation='≈~', fg_color=202)
    ]

def room():
    return [Renderable(0, 0, 40, 20, '█', ' ')]
