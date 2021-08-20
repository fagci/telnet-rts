from components import Connect, NetworkData, Player, Renderable

def player(x, y, icon='☺'):
    return [
        Player(),
        Renderable(x,y,fg_char=icon),
        NetworkData(),
        Connect()
    ]

def fire(x,y):
    return [
        Renderable(x,y,fg_animation='≈~')
    ]

def room():
    return [Renderable(0, 0, 40, 20, '█', ' ')]
