# random action

import random
import copy


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
            # for throwing the nth token, domain of available row is r0<=n<r0+n
            self.throw_row_direction = 1
        else:
            self.r0 = 4
            # for throwing the nth token, domain of available row is r0<=n<r0-n
            self.throw_row_direction = -1

        self.throw = 9
        self.oppo_throw = 9
        self.state = {}
        self.player_action = ()
        self.player_total = []
        self.board = [(4, -4), (4, -3), (4, -2), (4, -1), (4, 0),
                      (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1),
                      (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),
                      (1, -4), (1, -3), (1, -2), (1, -
                                                  1), (1, 0), (1, 1), (1, 2), (1, 3),
                      (0, -4), (0, -3), (0, -2), (0, -1), (0,
                                                           0), (0, 1), (0, 2), (0, 3), (0, 4),
                      (-1, -3), (-1, -2), (-1, -1), (-1,
                                                     0), (-1, 1), (-1, 2), (-1, 3), (-1, 4),
                      (-2, -2), (-2, -1), (-2, 0), (-2,
                                                    1), (-2, 2), (-2, 3), (-2, 4),
                      (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4),
                      (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4)]

        self.win = 0  # no.tokens defeat compare to previous state
        self.loss = 0  # no.tokens loss compare to previous state

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
        current_state = copy.deepcopy(self.state)

        board = self.board
        r0 = self.r0

        # existing player and oppo in the state
        # player_list = {(coor):['r', 's'], (coor):['p']}
        player_list = token_list(current_state, "player")


#        character = ["s", "p", "r"]
        if self.throw <= 0:
            throw_range = r0
        else:
            # if player could throw 2 lines --> line 4 and line 3, then throw range is 2 !
            throw_range = r0 + (9 - self.throw + 1) * self.throw_row_direction
#         if self.oppo_throw <= 0:
#             throw_range_opp = r0_opp
#         else:
#             throw_range_opp = r0_opp + \
#             (9 - self.oppo_throw + 1) * (- self.throw_row_direction)
#         print("throw_range", throw_range)
#         print("throw_range_opp", throw_range_opp)

        # store all possible throw actions for player and opponent -- cut out undefeatble possible throw already
        # possible_throw_player = [["THROW", 's', (coor)]]
        possible_throw_player = possible_throw(
            current_state, board, r0, throw_range, "player")

        player_total = []

        for item in player_list:
            ol = possible_move(current_state, item,
                               player_list, board)
#             print("/n/n/n",ol,"/n/n/n")
            for each in ol:
                player_total.append(each)
        player_total += possible_throw_player

        no_action = len(player_total)  # length of all possible moves
#         print(player_total)
        i = random.randrange(0, no_action, 1)
        self.player_action = tuple(player_total[i])
        
        return self.player_action

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

        self.win = 0  # no.tokens defeat compare to previous state
        self.loss = 0  # no.tokens loss compare to previous state

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
            if self.oppo_throw >= 0:
                self.oppo_throw -= 1
            opponent_symbol = opponent_action[1]
        else:
            opponent_symbol = self.state[opponent_action[1]][0][1]

        ####################################################################################################
        # player and opponent actions are not "THROW" then update prev state and delete from current state
        prev_state_record = {}  # ?????????????????????????????只记录上一轮的位置吗？？？？？？？？每次update（）都变成空？
        # player_action is ("SLIDE or SWING", (x1, y1), (x2, y2))
        if player_action[0] != "THROW":
            loc = {player_action[1]: [["player", player_symbol]]}
            if player_action[1] in prev_state_record:
                prev_state_record[player_action[1]].append(
                    ["player", player_symbol])
            else:
                prev_state_record.update(loc)
            if len(self.state[player_action[1]]) == 1:
                #                     print("yes deleted player and hence whole state")
                del self.state[player_action[1]]
            else:
                #                     print("yes removed player")
                self.state[player_action[1]].remove(["player", player_symbol])

        # opponent_action is ("SLIDE or SWING", (x1, y1), (x2, y2))
        if opponent_action[0] != "THROW":
            loc = {opponent_action[1]: [["opponent", opponent_symbol]]}
            if opponent_action[1] in prev_state_record:
                prev_state_record[opponent_action[1]].append(
                    ["opponent", opponent_symbol])
            else:
                prev_state_record.update(loc)
            if len(self.state[opponent_action[1]]) == 1:
                #                     print("yes deleted oppo and hence whole state")
                del self.state[opponent_action[1]]
            else:
                #                 print("yes removed oppo")
                self.state[opponent_action[1]].remove(
                    ["opponent", opponent_symbol])
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
            # !!!!有问题， Jupyter有报错！！！！！！！！！！！！！！！！！！！暂时不知道哪里错了
            # 2 different symbols occupying 1 hex
            elif len(symbols) == 2:
                if opponent_symbol == player_symbol:
                    # opponent and player remain in that hex
                    if if_defeat(player_symbol, self.state[player_destination][0][1]) == "WIN":
                        self.win += 1
                        for item in self.state[opponent_destination]:
                            if item[0] == "opponent":
                                self.win += 1  # player token eat opponent token
                            else:
                                self.loss += 1  # player token eat player token
                        self.state[opponent_destination] = [
                            ["player", player_symbol], ["opponent", opponent_symbol]]
                    # opponent and player both been defeated
                    else:
                        pass
                elif opponent_symbol != player_symbol:
                    if if_defeat(opponent_symbol, player_symbol) == "WIN":
                        self.loss += 1
                        if opponent_destination in self.state and if_defeat(opponent_symbol, self.state[opponent_destination][0][1]) == "WIN":
                            for item in self.state[opponent_destination]:
                                if item[0] == "player":
                                    self.loss += 1
                                else:
                                    self.win += 1
                            self.state[opponent_destination] = [
                                ["opponent", opponent_symbol]]
                        elif opponent_destination in self.state and if_defeat(opponent_symbol, self.state[opponent_destination][0][1]) != "WIN":
                            self.state[opponent_destination].append(
                                ["opponent", opponent_symbol])
                        elif opponent_destination not in self.state:
                            self.state[opponent_destination] = [
                                ["opponent", opponent_symbol]]

                    if if_defeat(opponent_symbol, player_symbol) == "LOSE":
                        self.win += 1
                        if player_destination in self.state and if_defeat(player_symbol, self.state[player_destination][0][1]) == "WIN":
                            for item in self.state[player_destination]:
                                if item[0] == "opponent":
                                    self.win += 1  # player token eat opponent token
                                else:
                                    self.loss += 1  # player token eat player token
                            self.state[player_destination] = [
                                ["player", player_symbol]]
                        elif player_destination in self.state and if_defeat(player_symbol, self.state[playre_destination][0][1]) != "WIN":
                            self.state[player_destination].append(
                                ["player", player_symbol])
                        elif player_destination not in self.state:
                            self.state[player_destination] = [
                                ["player", player_symbol]]

            # opponent, player and destination token all have same symbol
            else:
                if player_destination in self.state:

                    self.state[player_destination].append(
                        ["player", player_symbol])
                    self.state[opponent_destination].append(
                        ["opponent", opponent_symbol])
                else:
                    self.state[player_destination] = [
                        ["player", player_symbol], ["opponent", opponent_symbol]]

#             # player and opponent actions are not "THROW" then update prev state and delete from current state
#             prev_state_record = {}  # ?????????????????????????????只记录上一轮的位置吗？？？？？？？？每次update（）都变成空？
#             # player_action is ("SLIDE or SWING", (x1, y1), (x2, y2))
#             if player_action[0] != "THROW":
#                 loc = {player_action[1]: self.state[player_action[1]]}
#                 if player_action[1] in prev_state_record:
#                     prev_state_record[player_action[1]].append(["player", player_symbol])
#                 else:
#                     prev_state_record.update(loc)
#                 if len(self.state[player_action[1]]) == 1:
#                     del self.state[player_action[1]]
#                 else:
#                     self.state[player_action[1]].remove(["player", player_symbol])

#             # opponent_action is ("SLIDE or SWING", (x1, y1), (x2, y2))
#             if opponent_action[0] != "THROW":
#                 loc = {opponent_action[1]: self.state[opponent_action[1]]}
#                 if opponent_action[1] in prev_state_record:
#                     prev_state_record[opponent_action[1]].append(["opponent", opponent_symbol])
#                 else:
#                     prev_state_record.update(loc)
#                 if len(self.state[opponent_action[1]]) == 1:
#                     del self.state[opponent_action[1]]
#                 else:
#                     self.state[opponent_action[1]].remove(["opponent", opponent_symbol])

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
                        for item in self.state[player_destination]:
                            if item[0] == "opponent":
                                self.win += 1  # player token eat opponent token
                            else:
                                self.loss += 1  # player token eat player token
                        self.state[player_destination] = [
                            ["player", player_symbol]]
                    elif if_defeat(player_symbol, occypiedHex_symbol) == "DRAW":
                        self.state[player_destination].append(
                            ["player", player_symbol])
                    else:
                        self.loss += 1  # player token eat player token
                        # if this token lose, then take this token away from the state

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
                        for item in self.state[player_destination]:
                            if item[0] == "opponent":
                                self.win += 1  # player token eat opponent token
                            else:
                                self.loss += 1
                        self.state[player_action[2]] = [["player", rps]]
                    else:
                        self.loss += 1  # player token eat player token
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
                        for item in self.state[opponent_destination]:
                            if item[0] == "player":
                                self.loss += 1  # player token eat opponent token
                            else:
                                self.win += 1  # player token eat player token
                        self.state[opponent_destination] = [
                            ["opponent", opponent_symbol]]
                    elif if_defeat(opponent_symbol, occypiedHex_symbol) == "DRAW":
                        self.state[opponent_destination].append(
                            ["opponent", opponent_symbol])
                    else:
                        self.win += 1
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
                        for item in self.state[opponent_destination]:
                            if item[0] == "player":
                                self.loss += 1  # player token eat opponent token
                            else:
                                self.win += 1
                        self.state[opponent_destination] = [
                            ["opponent", opponent_symbol]]
                    elif if_defeat(opponent_symbol, occypiedHex_symbol) == "DRAW":

                        self.state[opponent_destination].append(
                            ["opponent", opponent_symbol])
                    else:
                        # if this token lose, then take this token away from the state
                        self.win += 1


def possible_move(state, current_pos, player_or_opponent_list, board):
    # list of action
    ol = []

    # six hex connected to the upper_current_pos
    layer1 = six_hex_surrond(current_pos)

    # slide for all possible surrounding hexes
    for surround_item in layer1:
        # surround_item is [1,2]   upper_current_pos is [x, y]
        ol = if_ol_append(state, surround_item, current_pos,
                          ol, "SLIDE", board)

    # swing
    for i in range(6):
        surround_item = layer1[i]
        if tuple(surround_item) in state:
            # have upper upper_current_pos --> can swing
            if tuple(surround_item) in player_or_opponent_list:
                # six hex connected to the upper upper_current_pos for swing
                layer2 = six_hex_surrond(surround_item)
                for j in range(i - 1, i + 2, 1):  # three hex opposite side
                    # the hex next to no.5 in the clockwise list is no.0 and no.4
                    if j == 6:
                        ol = if_ol_append(
                            state, layer2[0], current_pos, ol, "SWING", board)
                    else:
                        ol = if_ol_append(
                            state, layer2[j], current_pos, ol, "SWING", board)
    return ol  # 每一个action和update中action格式一样


# check if the action should be added to possible move
def if_ol_append(state, item, token, ol, method, board):
    #ol_pos = [i[2] for i in ol]
    # whether s/p/r, as only two token with the same symbol can stay in the same position
    t1 = state[tuple(token)][0][1]
    item_format = (method, tuple(token), tuple(item))
    if item_format in ol:  # avoid double recording
        return ol
    if tuple(item) not in board:
        return ol
    ol.append(item_format)
    return ol


def if_defeat(new, old):
    if new == old:
        return "DRAW"
    elif (new == 'r') & (old == 's'):
        return "WIN"
    elif (new == 'p') & (old == 'r'):
        return "WIN"
    elif (new == 's') & (old == 'p'):
        return "WIN"
    else:
        return "LOSE"

# possible_throw_list = [["THROW", char, item]]


def possible_throw(state, board, r0, throw_range, who):
    character = ["r", "s", "p"]
    possible_throw_list = []
    if r0 == 4:
        reverse = -1
    else:
        reverse = 1
    for row in range(r0, throw_range, reverse):  # -4, -3, -2, -1 or 4, 3, 2, 1(reverse)
        #         print("r0, throw_range", r0, throw_range)
        for item in board:
            if item[0] == row and item not in state:
                for char in character:
                    item_format = ["THROW", char, item]
                    possible_throw_list.append(item_format)

    return possible_throw_list

# return list of locations [[1,2], [2,5], [-1,]), [0,6], [9,3], [3,4]]


def six_hex_surrond(token):  # find the six surronding hex for a given hex
    action = [[-1, 0], [0, -1], [1, -1], [1, 0], [0, 1],
              [-1, 1]]  # six direction list in clockwise order
    six_hex = []
    for item in action:
        x = item[0] + token[0]
        y = item[1] + token[1]
        loc = [x, y]  # coordinate of the hex
        six_hex.append(loc)
    return six_hex


def token_list(state, side):  # side "player"/"opponent"
    token_dict = {}
    for key in state:
        for item in state[key]:
            if item[0] == side:
                if key in token_dict:
                    token_dict[key].append(item[1])
                else:
                    token_dict[key] = [item[1]]
    # {(coor):['r', 's'], (coor):['p']}
    return token_dict
