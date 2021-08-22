from components import Connect, Health, Hydration, Player, Position, Renderable, Stomach

def player(x, y, icon='@'):
    return [
        Player(),
        Renderable(fg_char=icon),
        Position(x, y),
        Connect(),
        Health(),
        Stomach(),
        Hydration()
    ]

def fire(x,y):
    return [
        Renderable(x,y,fg_animation='≈~', fg_color=202)
    ]

def room():
    return [Renderable(0, 0, 40, 20, '█', ' ')]
