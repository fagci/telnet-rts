from components import Connect, NetworkData, Player, Dirty, Position, Style

def player(x, y, icon='☺'):
    return [
        Player(),
        Style(icon),
        Position(x, y),
        NetworkData(),
        Connect()
    ]

