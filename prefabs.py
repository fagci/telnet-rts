from components import Connect, Player, Renderable

def player(x, y, icon='@'):
    return [
        Player(cam_x=x, cam_y=y),
        Renderable(x,y,fg_char=icon),
        Connect()
    ]

def fire(x,y):
    return [
        Renderable(x,y,fg_animation='≈~', fg_color=202)
    ]

def room():
    return [Renderable(0, 0, 40, 20, '█', ' ')]
