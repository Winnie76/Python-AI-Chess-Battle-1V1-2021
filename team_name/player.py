
class Player:
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        # put your code here
        self.player=player
        if self.player == "lower":
            self.r0=-4
            self.throw_row_direction = 1 #for throwing the nth token, domain of available row is r0<=n<r0+n
        else:
            self.r0=4
            self.throw_row_direction = 1 #for throwing the nth token, domain of available row is r0<=n<r0-n

        self.state = {}
        # set board range
        v1 = [0, -5]
        v2 = [5, -5]
        v3 = [5, 0]
        v4 = [0, 5]
        v5 = [-5, 5]
        v6 = [-5, 0]
        range_limit = []
        r = v1[0]
        q = v1[1]
        for i in range(6):
            r_q = ['Block', r + i, q]
            range_limit.append(r_q)
        r = v2[0]
        q = v2[1]
        for i in range(1, 6, 1):
            r_q = ['Block', r, q + i]
            range_limit.append(r_q)
        r = v3[0]
        q = v3[1]
        for i in range(1, 6, 1):
            r_q = ['Block', r - i, q + i]
            range_limit.append(r_q)
        r = v4[0]
        q = v4[1]
        for i in range(1, 6, 1):
            r_q = ['Block', r - i, q]
            range_limit.append(r_q)
        r = v5[0]
        q = v5[1]
        for i in range(1, 6, 1):
            r_q = ['Block', r, q - i]
            range_limit.append(r_q)
        r = v6[0]
        q = v6[1]
        for i in range(1, 6, 1):
            r_q = ['Block', r + i, q - i]
            range_limit.append(r_q)

        for item in range_limit:
            loc = {tuple(item[1:3]): item[0]}
            self.state.update(loc)



    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # put your code here

