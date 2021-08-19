from components import Connect, NetworkData, Player, Dirty, Position, Renderable, Style

def player(x, y, icon='☺'):
    return [
        Player(),
        Renderable(x,y,1,1,icon),
        NetworkData(),
        Connect()
    ]

