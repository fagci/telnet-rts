from components import Connect, NetworkData, Player, Renderable

def player(x, y, icon='☺'):
    return [
        Player(),
        Renderable(x,y,fg_char=icon),
        NetworkData(),
        Connect()
    ]

