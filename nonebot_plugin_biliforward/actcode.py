from enum import Enum

class ActCode(Enum):
    follow = 1
    unfollow = 2
    silence_follow = 3
    silence_unfollow = 4
    block = 5
    unblock = 6
    kick_from_fans = 7