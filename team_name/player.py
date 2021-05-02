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
        self.player = player
        if self.player == "lower":
            self.r0 = -4
            # for throwing the nth token, domain of available row is r0 <= n < r0+n
            self.throw_row_direction = 1
        else:
            self.r0 = 4
            # for throwing the nth token, domain of available row is r0 <= n < r0-n
            self.throw_row_direction = -1

        # set board range, make the board circled by "Block" tokens to avoid overstepping the boundary
         # 之后也可以通过 len(self.state[position]) 是否大于1来判断是否超出了boundary
        self.state = {(0, -5): 'Block', (1, -5): 'Block', (2, -5): 'Block', (3, -5): 'Block', (4, -5): 'Block', (5, -5): 'Block', (5, -4): 'Block',
                      (5, -3): 'Block', (5, -2): 'Block', (5, -1): 'Block', (5, 0): 'Block', (4, 1): 'Block', (3, 2): 'Block', (2, 3): 'Block', (1, 4): 'Block', (0, 5): 'Block',
                      (-1, 5): 'Block', (-2, 5): 'Block', (-3, 5): 'Block', (-4, 5): 'Block', (-5, 5): 'Block', (-5, 4): 'Block', (-5, 3): 'Block', (-5, 2): 'Block', (-5, 1): 'Block',
                      (-5, 0): 'Block', (-4, -1): 'Block', (-3, -2): 'Block', (-2, -3): 'Block', (-1, -4): 'Block'}

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
        # format of state & prev_state_record      e.g., {(-5,0):"Block", (-3,2):["player","s"], (-2,3):["opponent","p"]}
        # record the 2 moving tokens' positions in previous state, and delete from the current state

        # get the destination(x, y) opponent and player are going
        opponent_destination = opponent_action[2]
        player_destination = player_action[2]

        # get symbols for opponent and player
        if player_action[0] == "THROW":
            player_symbol = player_action[1]
        else:
            # if more than one token in a hex , they must have the same symbol
            player_symbol = self.state[player_action[1]][0][1]
        if opponent_action[0] == "THROW":
            opponent_symbol = opponent_action[1]
        else:
            opponent_symbol = self.state[opponent_action[1]][0][1]

        ####################################################################################################
        # player and opponent go to same destination
        if opponent_destination == player_destination:
            # check how many symbols
            symbols = set()
            symbols.add(player_symbol)
            symbols.add(opponent_symbol)
            if opponent_destination in self.state:
                symbols.add(self.state[opponent_destination][0][1])

            # 3 different symbols occupying 1 hex
            if len(symbols) == 3:
                del self.state[opponent_destination]

            # 2 different symbols occupying 1 hex
            elif len(symbols) == 2:
                if opponent_symbol == player_symbol:
                    # opponent and player remain in that hex
                    if if_defeat(opponent_symbol, self.state[opponent_destination][0][1]) == "WIN":
                        self.state[opponent_destination] = [
                            ["player", player_symbol], ["opponent", opponent_symbol]]
                    # opponent and player both been defeated
                    else:
                        pass

                elif opponent_symbol == self.state[opponent_destination][0][1]:
                    # opponent and another remain in that hex
                    if if_defeat(opponent_symbol, player_symbol) == "WIN":
                        self.state[opponent_destination].append(
                            ["opponent", opponent_symbol])
                    # player remain in that hex
                    else:
                        self.state[player_destination] = [
                            ["player", player_symbol]]
                elif player_symbol == self.state[opponent_destination][0][1]:
                    # opponent and another remain in that hex
                    if if_defeat(player_symbol, opponent_symbol) == "WIN":
                        self.state[player_destination].append(
                            ["player", player_symbol])
                    # player remain in that hex
                    else:
                        self.state[opponent_destination] = [
                            ["opponent", opponent_symbol]]

            # opponent, player and destination token all have same symbol
            else:
                self.state[player_destination].append(
                    ["player", player_symbol])
                self.state[opponent_destination].append(
                    ["opponent", opponent_symbol])

        # player and opponent actions are not "THROW" then update prev state and delete from current state
        prev_state_record = {}  # ?????????????????????????????只记录上一轮的位置吗？？？？？？？？每次update（）都变成空？
        # player_action is ("SLIDE or SWING", (x1, y1), (x2, y2))
        if player_action[0] != "THROW":
            loc = {player_action[1]: self.state[player_action[1]]}
            prev_state_record.update(loc)
            if len(self.state[player_action[1]]) == 1:
                del self.state[player_action[1]]
            else:
                self.state[player_action[1]].remove(["player", player_symbol])

        # opponent_action is ("SLIDE or SWING", (x1, y1), (x2, y2))
        if opponent_action[0] != "THROW":
            loc = {opponent_action[1]: self.state[opponent_action[1]]}
            prev_state_record.update(loc)
            if len(self.state[opponent_action[1]]) == 1:
                del self.state[opponent_action[1]]
            else:
                self.state[opponent_action[1]].remove(
                    ["opponent", opponent_symbol])

        ####################################################################################################
        # player and opponent go to different destinations

        # consider the movement in this turn
        # idea: 若是throw说明之前没在state里出现过 只要考虑它要放的位置需不需要和别的token battle，
        # 赢了则在state里把这个位置改为这个token的信息，输了则不在state记入这个token, 相同则加进去value里
        # 若不是throw，则可以通过原位置在prev_state_record里找到相应的信息，在判断要放的位置是否需要和别的token battle
        # battle -> 赢了则在state里把这个位置改为这个token的信息，输了则不在state记入这个token
        # (因为最开始都把本轮要move的token的原位置在state里删掉了，只是在prev_state_record里有
        if opponent_destination != player_destination:
            if player_action[0] == "THROW":
                # key not in state then add key value pair
                if player_destination not in self.state:
                    loc = {player_destination: [["player", player_symbol]]}
                    self.state.update(loc)
                # key in state then 1.defeat 2.couldn't defeat 3.draw
                else:
                    # if another token occupy the same place, need to check which token wins or draw
                    # 's' or 'r' or 'p' in the state including both players
                    occypiedHex_symbol = (self.state[player_destination])[0][1]
                    if if_defeat(player_symbol, occypiedHex_symbol) == "WIN":
                        self.state[player_destination] = [
                            ["player", player_symbol]]
                    elif if_defeat(player_symbol, occypiedHex_symbol) == "DRAW":
                        self.state[player_destination].append(
                            ["player", player_symbol])
                    else:
                        # if this token lose, then take this token away from the state
                        pass

            # player action is not "THROW"
            else:
                # if the action is not throw, the rps has been recorded before  #player_action is ("SLIDE or SWING", (x1, y1), (x2, y2))
                previous_loc = player_action[1]  # (x1, y1)
                # rps is 's' or 'p' or 'r'  #要移动过去的棋子的标志 rps
                rps = (prev_state_record[previous_loc])[0][1]

                if player_destination not in self.state:
                    loc = {player_action[2]: [["player", rps]]}
                    self.state.update(loc)
                else:
                    # if >=1 tokens occupy the same place, need to check which token wins or draw
                    if if_defeat(rps, self.state[player_action[2]][0][1]) == "DRAW":
                        self.state[player_action[2]].append(["player", rps])
                    elif if_defeat(rps, self.state[player_action[2]][0][1]) == "WIN":
                        self.state[player_action[2]] = [["player", rps]]
                    else:
                        pass
    #                 old_rps = (self.state[player_action[2]])[1] #现在占着的棋子 我方或敌方 的标志
    #                 if if_defeat(rps, old_rps):
    #                     self.state[player_action[2]] = ["player", rps]
    #                 else:
    #                     # if this token lose, then take this token away from the state
    #                     pass

            # update opponent action
            if opponent_action[0] == "THROW":
                if opponent_destination not in self.state:
                    loc = {opponent_destination: [
                        ["opponent", opponent_symbol]]}
                    self.state.update(loc)
                else:
                    # if another token occupy the same place, need to check which token wins
                    occypiedHex_symbol = (
                        self.state[opponent_destination])[0][1]
                    if if_defeat(opponent_symbol, occypiedHex_symbol) == "WIN":
                        self.state[opponent_destination] = [
                            ["opponent", opponent_symbol]]
                    elif if_defeat(opponent_symbol, occypiedHex_symbol) == "DRAW":
                        self.state[opponent_destination].append(
                            ["opponent", opponent_symbol])
                    else:
                        # if this token lose, then take this token away from the state
                        pass

            # opponent not "THROW"
            else:
                # rps means whether the token is rock/paper/scissors
                # if the action is not throw, the rps has been recorded before
                previous_loc = opponent_action[1]
                if opponent_destination not in self.state:
                    loc = {opponent_destination: [
                        ["opponent", opponent_symbol]]}
                    self.state.update(loc)
                else:
                    # if another token occupy the same place, need to check which token wins
                    occypiedHex_symbol = (
                        self.state[opponent_destination])[0][1]
                    if if_defeat(opponent_symbol, occypiedHex_symbol) == "WIN":
                        self.state[opponent_destination] = [
                            ["opponent", opponent_symbol]]
                    if if_defeat(opponent_symbol, occypiedHex_symbol) == "DRAW":
                        self.state[opponent_destination].append(
                            ["opponent", opponent_symbol])
                    else:
                        # if this token lose, then take this token away from the state
                        pass


def if_defeat(new, old):
    if (new == old):
        return "DRAW"
    elif (new == 'r') & (old == 's'):
        return "WIN"
    elif (new == 'p') & (old == 'r'):
        return "WIN"
    elif (new == 's') & (old == 'p'):
        return "WIN"
    else:
        return "LOSE"
