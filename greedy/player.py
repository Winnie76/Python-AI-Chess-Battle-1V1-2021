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
        print("no_throw", self.throw)
        board = self.board
        r0 = self.r0
        r0_opp = -r0
        best_move = ()
        current_state = copy.deepcopy(self.state)
        # existing player and oppo in the state
        # player_list = {(coor):['r', 's'], (coor):['p']}
        player_list = token_list(current_state, "player")
        opponent_list = token_list(current_state, "opponent")

#         print("player_list", player_list)

#        character = ["s", "p", "r"]

        if self.throw <= 0:
            throw_range = r0
        else:
            # if player could throw 2 lines --> line 4 and line 3, then throw range is 2 !
            throw_range = r0 + (9 - self.throw + 1) * self.throw_row_direction
        if self.oppo_throw <= 0:
            throw_range_opp = r0_opp
        else:
            throw_range_opp = r0_opp + \
            (9 - self.oppo_throw + 1) * (- self.throw_row_direction)

#         print("throw_range", throw_range)
#         print("throw_range_opp", throw_range_opp)

        # store all possible throw actions for player and opponent -- cut out undefeatble possible throw already
        # possible_throw_player = [["THROW", 's', (coor)]]
        if self.throw > 0:
            possible_throw_player = possible_throw(
                current_state, board, r0, throw_range, "player")
        else:
            possible_throw_player = []
        if self.oppo_throw > 0:
            possible_throw_opponent = possible_throw(
                current_state, board, r0_opp, throw_range_opp, "opponent")
        else:
            possible_throw_opponent = []
            
#         print("possible_throw_player", possible_throw_player)
#         print("possible_throw_opponent", possible_throw_opponent)
        # player_total = [[...],[...]]     stores all possible actions for player and opponent: slide, swing, throw
        # for player
        player_total = []
        for item in player_list:
            ol = possible_move(current_state, item,
                               player_list, opponent_list, board)
            for each in ol:
                player_total.append(each)
        player_total += possible_throw_player

        # for opponent
        opp_total = []
        for opp in opponent_list:
            opp_ol = possible_move(
                current_state, opp, opponent_list, player_list, board)
            for each in opp_ol:
                opp_total.append(each)
        opp_total += possible_throw_opponent

        max_eval = 0
        best_move = player_total[0]
        for item in player_total:
            current_state = copy.deepcopy(self.state)
            # print("current_state0000:",current_state)
            # print("self0000:",self.state)

            list_of_result = update_player_action(item, self.state)
            # print("current_state1111:",current_state)
            # print("self1111:",self.state)
            new_state = list_of_result[0]
            no_defeat = list_of_result[1]
            no_loss = list_of_result[2]
            eval_score = evaluation(
                new_state, self.player, no_defeat, no_loss, player_list, opponent_list, board)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = item
            # print("current_state2222:",current_state)
            # print("self2222:",self.state)
            self.state = copy.deepcopy(current_state)
        self.player_action = best_move
        if self.player_action[0] == "THROW":
            self.throw -= 1
        return tuple(self.player_action)

        # [[1,2],[2,3]]

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


def possible_move(state, current_pos, player_or_opponent_list, the_other_list, board):
    # list of action
    ol = []

    # six hex connected to the upper_current_pos
    layer1 = six_hex_surrond(current_pos)

    # slide for all possible surrounding hexes
    for surround_item in layer1:
        # surround_item is [1,2]   upper_current_pos is [x, y]
        ol = if_ol_append(state, surround_item, current_pos,
                          ol, "SLIDE", the_other_list, board)

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
                            state, layer2[0], current_pos, ol, "SWING", the_other_list, board)
                    else:
                        ol = if_ol_append(
                            state, layer2[j], current_pos, ol, "SWING", the_other_list, board)
    return ol  # 每一个action和update中action格式一样


# check if the action should be added to possible move
def if_ol_append(state, item, token, ol, method, the_other_list, board):
    #ol_pos = [i[2] for i in ol]
    # whether s/p/r, as only two token with the same symbol can stay in the same position
    t1 = state[tuple(token)][0][1]
    item_format = (method, tuple(token), tuple(item))

    if item_format in ol:  # avoid double recording
        return ol
    if tuple(item) not in board:
        return ol
    else:
        # if item not in ol_pos:  # to avoid double record
        # ??????????????? 我comment掉了上面条件， 因为这个判断的是（coordinate）在不在 ol 里，
        # ????????????????但如果一个slide一个throw分数eval_score可能不一样，而且想尽量保留着throw
        if tuple(item) in state:
            if tuple(item) in the_other_list:
                t2 = state[tuple(item)][0][1]  # whether s/p/r
                if not (if_defeat(t1, t2) == "LOSE"):
                    ol.append(item_format)
        else:
            ol.append(item_format)
#         else:
#             return ol
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
            if item[0] == row:
                #                 print("yes if item[0] == row:")
                if item not in state:
                    #                     print("yes if item not in state:")
                    for char in character:
                        item_format = ["THROW", char, item]
                        possible_throw_list.append(item_format)
#                         print("yes appended")
                # 当（coor）在state里，说明有其他token，那就要看 我方 还是 敌方。如果是我方：不throw了，因为无论输赢平局都没给棋盘增加 eval_score
                # 如果是敌方：只有赢的情况下 throw
                # 这样做是为了减少 time complexity， 因为dime fox很容易超时
                else:
                    has_who = 0
                    # check if token existed in the state is from our side or not
                    for token in state[item]:
                        if token[0] == who:
                            has_who = 1
                        else:
                            oppo_symb = token[1]
                    # if token at that hex is not from our side, put symbol that can defeat oppo into possible throw
                    if has_who == 0:
                        for char in character:
                            if if_defeat(char, oppo_symb) == "WIN":
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

#[('SLIDE', (-2, 2), (-3, 2)), ('SLIDE', (-2, 2), (-2, 1)), ('SLIDE', (-2, 2), (-1, 1)), ('SLIDE', (-2, 2), (-1, 2)), ('SLIDE', (-2, 2), (-3, 3))]


def least_slide_distance(p0, p1):  # format of token1 and token2 is the postion (-1,2)
    x0 = p0[0]
    y0 = p0[1]
    x1 = p1[0]
    y1 = p1[1]
    dx = x1 - x0
    dy = y1 - y0

    if dx * dy > 0:  # find what direction is token2 corresponding to token1
        # calculate the min_dist based on the direction property
        dist = abs(dx + dy)
    else:
        dist = max(abs(dx), abs(dy))
    return dist


# least_distance with consider both slide and swing
# token_list is whether player_list or opponent_list depends on whether token1 is player token or opp token
# consider both slide and swing 看token1 去到token2 的距离
def least_distance(state, token1, token2, player_or_opponent_list, the_other_list, board):

    # six tokens surrounding token1
    min_dist = least_slide_distance(token1, token2)

    # find swing , if can swing, count the distance as min(slide, dist after swing + 1)
    possible_pos = possible_move(
        state, token1, player_or_opponent_list, the_other_list, board)
    for action in possible_pos:
        dist = least_slide_distance(action[2], token2) + 1
        if dist < min_dist:
            min_dist = dist
    return min_dist


def evaluation(state, which_side, no_defeat, no_loss, player_or_opponent_list, the_other_list, board):
    eval_score = 10000 * (no_defeat - no_loss)

    for coor in state.keys():
        # 1.same coordinate player defeat opponent 2.same coordinate opponent defeat player
        num_coor_tokens = len(state[coor])
        # 这是已经变化过的静止的state，一个token上不能出现两个不同的symbol，不同的话在update的时候一个就把另一个吃掉了，
        # 在同一个position上的多个token只可能拥有同一种人symbol吧？
        # num_differ_symbols = func_symbolsInOneHex(state[coor])
        # if num_coor_tokens > 1 and num_differ_symbols == 2:
        #    for i in range(num_coor_tokens):
        #        if state[coor][i][0] == 'player':
        #            for j in range(num_coor_tokens):
        #                if state[coor][j][0] == 'opponent':
        #                    if if_defeat(state[coor][i][1], state[coor][j][1]) == "WIN":
        #                        eval_score += 100
        #                    elif if_defeat(state[coor][i][1], state[coor][j][1]) == "LOSE":
        #                        eval_score -= 100

        # 3.how close together is player's tokens
        # loop through all tokens in that hex and check if it's player
        for token_i in range(len(state[coor])):
            if state[coor][token_i][0] == 'player':
                # loop through all tokens in the state
                for coor_i in state.keys():
                    if coor_i != coor:
                        for other_token in state[coor_i]:
                            # found token that is also player and has differnent symbol --> player going to protect other token
                            #                             if other_token[0] == 'player' and if_defeat(other_token[1], state[coor][token_i][1]) == "LOSE":
                            #                                 distance = least_distance(
                            #                                     state, coor, coor_i, player_or_opponent_list, the_other_list, board)
                            #                                 if distance == 1:
                            #                                     eval_score += 3
                            #                                 elif distance == 2:
                            #                                     eval_score += 2
                            #                                 elif distance == 3:
                            #                                     eval_score += 1
                            #                                 elif distance == 6:
                            #                                     eval_score += -1
                            #                                 elif distance == 7:
                            #                                     eval_score += -2
                            #                                 elif distance == 8:
                            #                                     eval_score += -3
                            # 4.how close are defeatable opponent tokens
                            if other_token[0] == 'opponent' and if_defeat(state[coor][token_i][1],
                                                                          other_token[1]) == "WIN":
                                distance = least_distance(
                                    state, coor, coor_i, player_or_opponent_list, the_other_list, board)
                                if distance == 1:
                                    eval_score += 80
                                elif distance == 2:
                                    eval_score += 70
                                elif distance == 3:
                                    eval_score += 60
                                elif distance == 4:
                                    eval_score += 50
                                elif distance == 5:
                                    eval_score += 40
                                elif distance == 6:
                                    eval_score += 30
                                elif distance == 7:
                                    eval_score += 20
                                elif distance == 8:
                                    eval_score += 10
                            # 5.how close are undefeatable opponent tokens
                            if other_token[0] == 'opponent' and if_defeat(state[coor][token_i][1],
                                                                          other_token[1]) == "LOSE":
                                distance = least_distance(
                                    state, coor, coor_i, player_or_opponent_list, the_other_list, board)
                                if distance == 1:
                                    eval_score += -80
                                elif distance == 2:
                                    eval_score += -70
                                elif distance == 3:
                                    eval_score += -60
                                elif distance == 4:
                                    eval_score += -50
                                elif distance == 5:
                                    eval_score += -40
                                elif distance == 6:
                                    eval_score += -30
                                elif distance == 7:
                                    eval_score += -20
                                elif distance == 8:
                                    eval_score += -10
                # 6.how close are player's token towards our side
                if which_side == 'upper':
                    if coor[0] == 4:
                        eval_score += 2
                    if coor[0] == 3:
                        eval_score += 1.5
                    if coor[0] == 2:
                        eval_score += 1
                    if coor[0] == 1:
                        eval_score += 0.5
                if which_side == 'lower':
                    if coor[0] == -4:
                        eval_score += 2
                    if coor[0] == -3:
                        eval_score += 1.5
                    if coor[0] == -2:
                        eval_score += 1
                    if coor[0] == -1:
                        eval_score += 0.5

    # if there is defeatable token
    # accumulate no of symbols for each side
    # player
    player_s = 0
    player_r = 0
    player_p = 0
    for item in player_or_opponent_list:
        for symbol in player_or_opponent_list[item]:
            if symbol == "s":
                player_s += 1
            elif symbol == "r":
                player_r += 1
            else:
                player_p += 1
    # opponent
    opponent_s = 0
    opponent_r = 0
    opponent_p = 0
    for item in the_other_list:
        for symbol in the_other_list[item]:
            if symbol == "s":
                opponent_s += 1
            elif symbol == "r":
                opponent_r += 1
            else:
                opponent_p += 1
    #eval_score += (player_s - opponent_p + player_r - opponent_s + player_p - opponent_r) * 10000
    if (player_s - opponent_p) >= 2:
        eval_score -=  1000
    if (player_r - opponent_s) >= 2:
        eval_score -=  1000
    if (player_p - opponent_r) >= 2:
        eval_score -=  1000
    return eval_score


def update_player_action(player_action, current_state):  # 前面记得把no_defeat和loss归0
    prev_state_record = {}
    no_defeat = 0
    no_loss = 0

    # opponent_or_player带入“opponent” or “player”
    if player_action[0] != "THROW":
        # for multiple tokens in one state, all symbols should be the same
        # player_action[1] => previous position
        symbol = current_state[player_action[1]][0][1]
        loc = {player_action[1]: ["player", symbol]}
        prev_state_record.update(loc)
        # if the position in the previous state only has one token, then delete it from the state
        # if there are multiple tokens, then delete the corresponding one
        if len(current_state[player_action[1]]) == 1:
            del current_state[player_action[1]]
        else:
            current_state[player_action[1]].remove(["player", symbol])

    # consider the movement in this turn
    # idea: 若是throw说明之前没在state里出现过 只要考虑它要放的位置需不需要和别的token battle，
    # 赢了则在state里把这个位置改为这个token的信息，输了则不在state记入这个token
    # 若不是throw，则可以通过原位置在prev_state_record里找到相应的信息，在判断要放的位置是否需要和别的token battle
    # battle -> 赢了则在state里把这个位置改为这个token的信息，输了则不在state记入这个token
    # (因为最开始都把本轮要move的token的原位置在state里删掉了，只是在prev_state_record里有

    if player_action[0] == "THROW":
        if player_action[2] not in current_state:
            loc = {player_action[2]: [["player", player_action[1]]]}
            current_state.update(loc)
        else:
            # if another token occupy the same place, need to check which token wins
            # rps means rock paper or scissors
            rps = player_action[1]
            old_rps = (current_state[player_action[2]])[0][1]
            if if_defeat(rps, old_rps) == "WIN":
                for item in current_state[player_action[2]]:
                    if item[0] == "opponent":
                        no_defeat += 1  # player token eat opponent token
                    else:
                        no_loss += 1  # player token eat player token
                current_state[player_action[2]] = [["player", rps]]
            elif if_defeat(rps, old_rps) == "DRAW":
                current_state[player_action[2]].append(["player", rps])
            else:
                # if this token lose, then take this token away from the state
                pass
    else:
        # if the action is not throw, the rps has been recorded before
        previous_loc = player_action[1]
        rps = (prev_state_record[previous_loc])[1]
        if player_action[2] not in current_state:
            loc = {player_action[2]: [["player", rps]]}
            current_state.update(loc)
        else:
            # if another token occupy the same place, need to check which token wins
            old_rps = (current_state[player_action[2]])[0][1]
            if if_defeat(rps, old_rps) == "WIN":
                for item in current_state[player_action[2]]:
                    if item[0] == "opponent":
                        no_defeat += 1  # player token eat opponent token
                    else:
                        no_loss += 1  # player token eat player token
                current_state[player_action[2]] = [["player", rps]]
            elif if_defeat(rps, old_rps) == "DRAW":
                current_state[player_action[2]].append(["player", rps])
            else:
                # if this token lose, then take this token away from the state
                pass
    list_to_return = [current_state, no_defeat, no_loss]
    return list_to_return
