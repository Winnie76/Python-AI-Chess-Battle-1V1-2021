
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
            self.throw_row_direction = 1 # for throwing the nth token, domain of available row is r0<=n<r0+n
        else:
            self.r0=4
            self.throw_row_direction = 1 # for throwing the nth token, domain of available row is r0<=n<r0-n

        self.state = {}
        # set board range, make the board circled by "Block" tokens to avoid overstepping the boundary
        range_limit = board_range()
        for item in range_limit:
            loc = {tuple(item[1:3]): item[0]}
            self.state.update(loc)

        # format of state e.g., {(-5,0):"Block"}
        # 之后也可以通过 len(self.state[position]) 是否大于1来判断是否超出了boundary

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
        # update player action
        # format of state e.g., {(-5,0):"Block", (-3,2):["player","s"], (-2,3):["opponent","p"]}
        # format of prev_state_record same as state e.g., {(-3,2):["player","s"], (-2,3):["opponent","p"]}
        # record the 6 moving tokens' positions in previous turn, and delete from the previous state
        prev_state_record = {}
        for item in player_action:
            if item[0] != "THROW":
                loc = {item[1]: self.state[item[1]]}
                prev_state_record.update(loc)
                del self.state[item[1]]
        for item in opponent_action:
            if item[0] != "THROW":
                loc = {item[1]: self.state[item[1]]}
                prev_state_record.update(loc)
                del self.state[item[1]]

        # consider the movement in this turn
        for item in player_action:
            if item[0] == "THROW":
                if item[2] not in self.state:
                    loc = {item[2]: ["player", item[1]]}
                    self.state.update(loc)
                else:
                    # if another token occupy the same place, need to check which token wins
                    rps = item[1]
                    old_rps = (self.state[item[2]])[1]
                    if if_defeat(rps, old_rps):
                        self.state[item[2]] = ["player",rps]
                    else:
                        # if this token lose, then take this token away from the state
                        pass
            else:
                # rps means whether the token is rock/paper/scissors
                # if the action is not throw, the rps has been recorded before
                previous_loc = item[1]
                rps = (prev_state_record[previous_loc])[1]
                if item[2] not in self.state:
                    loc = {item[2]: ["player", rps]}
                    self.state.update(loc)
                else:
                    # if another token occupy the same place, need to check which token wins
                    old_rps = (self.state[item[2]])[1]
                    if if_defeat(rps, old_rps):
                        self.state[item[2]] = ["player",rps]
                    else:
                        # if this token lose, then take this token away from the state
                        pass

        # update opponent action
        for item in opponent_action:
            if item[0] == "THROW":
                if item[2] not in self.state:
                    loc = {item[2]: ["opponent", item[1]]}
                    self.state.update(loc)
                else:
                    # if another token occupy the same place, need to check which token wins
                    rps = item[1]
                    old_rps = (self.state[item[2]])[1]
                    if if_defeat(rps, old_rps):
                        self.state[item[2]] = ["opponent", rps]
                    else:
                        # if this token lose, then take this token away from the state
                        pass
            else:
                # rps means whether the token is rock/paper/scissors
                # if the action is not throw, the rps has been recorded before
                previous_loc = item[1]
                rps = (prev_state_record[previous_loc])[1]
                if item[2] not in self.state:
                    loc = {item[2]: ["opponent", rps]}
                    self.state.update(loc)
                else:
                    # if another token occupy the same place, need to check which token wins
                    old_rps = (self.state[item[2]])[1]
                    if if_defeat(rps, old_rps):
                        self.state[item[2]] = ["opponent", rps]
                    else:
                        # if this token lose, then take this token away from the state
                        pass

def if_defeat(new,old):
    if (new == 's') & (old == 'p'):
        return 1
    elif (new == 'r') & (old == 's'):
        return 1
    elif (new == 'p') & (old == 'r'):
        return 1
    else:
        return 0

def board_range():
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
    return (range_limit)