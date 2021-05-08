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
            self.throw_row_direction = 1  # for throwing the nth token, domain of available row is r0<=n<r0+n
        else:
            self.r0 = 4
            self.throw_row_direction = -1  # for throwing the nth token, domain of available row is r0<=n<r0-n

        self.state = {}
        # set board range, make the board circled by "Block" tokens to avoid overstepping the boundary
        # range_limit = board_range()
        # for item in range_limit:
        #    loc = {tuple(item[1:3]): item[0]}
        #    self.state.update(loc)
        self.player_action = ()
        self.board = [(4, -4), (4, -3), (4, -2), (4, -1), (4, 0),
                      (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1),
                      (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2),
                      (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3),
                      (0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
                      (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4),
                      (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4),
                      (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4),
                      (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4)]
        # format of state e.g., {(-5,0):"Block"}
        # 之后也可以通过 len(self.state[position]) 是否大于1来判断是否超出了boundary

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
        # 在state里找出所有player token； 所有opponent token
        current_state = self.state
        board = self.board
        r0 = self.r0
        player_list = token_list(current_state, "player")
        opponent_list = token_list(current_state, "opponent")

        # [[[[1,2],[2,3]],[[2,3],[1,3]]],[[[1,2],[2,3]],[[2,3],[1,3]]]]
        character = ["s", "p", "r"]
        # 考虑throw

        no_rows = len(player_list)
        throw_range = r0 + no_rows * self.throw_row_direction

        # store all possible throw actions for player and opponent
        # def possible_throw 写在最下面了
        possible_throw_player = possible_throw(current_state, board, r0, throw_range, player_list)
        possible_throw_opponent = possible_throw(current_state, board, r0, throw_range, opponent_list)

        # store all possible actions for player and opponent: slide, swing, throw
        # for player
        player_total = []
        for item in player_list:
            ol = possible_move(current_state, item, player_list, opponent_list)
            player_total.append(ol)
        player_total.append(possible_throw_player)

        # for opponent
        opp_total = []
        for opp in opponent_list:
            opp_ol = possible_move(current_state, opp, opponent_list, player_list)
            opp_total.append(opp_ol)
        opp_total.append(possible_throw_opponent)

        # build min_max tree
        max_layer = []
        min_max = 0

        for action in player_total:
            min_layer = []
            for opp_action in opp_total:
                update(self, action, opp_action)  # 可以这样用吗？ （如果再来一轮 ，应该从这里加入, 感觉可以再加一层）
                eval = evaluate(self.state)
                if eval > min_max:
                    min_layer.append(eval)
                    self.state = current_state
                    if opp_action == opp_total[-1]:  # 说明这个predecessor下面的node都大于之前的max_min => max_min更改
                        min_max = min(min_layer)  # update min_max
                        self.player_action = action  # update player_action leads to the state with min_max
                else:
                    self.state = current_state
                    break
            max_layer.append(min_layer)

        # [[1,2],[2,3]]

        # 加入pruning
        # 加入后续判断
        # def evaluation function没写
        # def 方位辨别找min dist没写
        # 换了board limit 方便找能thorw的位置， 记得把possible move里面加上if在board的条件

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
            
            self.win = 0 # no.tokens defeat compare to previous state
            self.loss = 0 #no.tokens loss compare to previous state
        
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

                    elif opponent_symbol == self.state[opponent_destination][0][1]:
                        # opponent and another remain in that hex
                        if if_defeat(opponent_symbol, player_symbol) == "WIN":
                            
                            self.loss += 1  
                            self.state[opponent_destination].append(
                                ["opponent", opponent_symbol])
                        # player remain in that hex
                        else:
                            self.win += 1
                            for item in self.state[opponent_destination]:
                                if item[0] == "opponent":
                                    self.win += 1  # player token eat opponent token
                                else:
                                    self.loss += 1
                            self.state[player_destination] = [
                                ["player", player_symbol]]
                    elif player_symbol == self.state[opponent_destination][0][1]:
                        # opponent and another remain in that hex
                        if if_defeat(player_symbol, opponent_symbol) == "WIN":
                            self.win += 1
                            self.state[player_destination].append(
                                ["player", player_symbol])
                        # player remain in that hex
                        else:
                            self.loss += 1
                            for item in self.state[opponent_destination]:
                                if item[0] == "player":
                                    self.loss += 1  # player token eat opponent token
                               
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
                if player_action[1] in prev_state_record:
                    prev_state_record[player_action[1]].append(["player", player_symbol]) 
                else:
                    prev_state_record.update(loc)
                if len(self.state[player_action[1]]) == 1:
                    del self.state[player_action[1]]
                else:
                    self.state[player_action[1]].remove(["player", player_symbol])

            # opponent_action is ("SLIDE or SWING", (x1, y1), (x2, y2))
            if opponent_action[0] != "THROW":
                loc = {opponent_action[1]: self.state[opponent_action[1]]}
                if opponent_action[1] in prev_state_record:
                    prev_state_record[opponent_action[1]].append(["opponent", opponent_symbol]) 
                else:
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

def possible_move(state, current_pos, player_or_opponent_list, the_other_list):
    # if player_or_opponent_list is player_list, then the_other_list is opponent_List, vice versa
    ol = []
    # six hex connected to the upper_current_pos
    layer1 = six_hex_surrond(current_pos)
    # player_current_pos的format是state的key ==> (x,y) ?
    # slide for all possible surrounding hexes
    for surround_item in layer1:
        # surround_item is [1,2]   upper_current_pos is [x, y]
        ol = if_ol_append(state, surround_item, current_pos, ol, "SLIDE", the_other_list)

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
                            state, layer2[0], current_pos, ol, "SWING", the_other_list)
                    else:
                        ol = if_ol_append(
                            state, layer2[j], current_pos, ol, "SWING", the_other_list)
    return ol  # 每一个action和update中action格式一样


# check if the action should be added to possible move

def if_ol_append(state, item, token, ol, method, the_other_list):
    ol_pos = [i[2] for i in ol]
    t1 = state[tuple(token)][1]  # whether s/p/r
    item_format = (method, tuple(token), item)
    if item not in ol_pos:  # to avoid double record
        if tuple(item) in state:
            if tuple(item) in the_other_list:
                t2 = state[tuple(item)][1]  # whether s/p/r
                if not (if_defeat(t1, t2) == "LOSE"):
                    ol.append(item_format)
        else:
            ol.append(item_format)
    else:
        return ol
    return ol


# return list of locations [[1,2], [2,5], [-1,]), [0,6], [9,3], [3,4]]
def six_hex_surrond(token):  # find the six surronding hex for a given hex
    if len(token) == 3:
        token = token[1:3]
    action = [[-1, 0], [0, -1], [1, -1], [1, 0], [0, 1],
              [-1, 1]]  # six direction list in clockwise order
    six_hex = []
    for item in action:
        x = item[0] + token[0]
        y = item[1] + token[1]
        loc = [x, y]  # coordinate of the hex
        six_hex.append(loc)
    return six_hex


def evaluation(state, which_side):
    eval_score = 0.0
    for coor in state.keys():
        # 1.same coordinate player defeat opponent 2.same coordinate opponent defeat player
        num_coor_tokens = len(state[coor])
        num_differ_symbols = func_symbolsInOneHex(state[coor])
        if num_coor_tokens > 1 and num_differ_symbols == 2:
            for i in range(num_coor_tokens):
                if state[coor][i][0] == 'player':
                    for j in range(num_coor_tokens):
                        if state[coor][j][0] == 'opponent':
                            if if_defeat(state[coor][i][1], state[coor][j][1]) == "WIN":
                                eval_score += 100
                            elif if_defeat(state[coor][i][1], state[coor][j][1]) == "LOSE":
                                eval_score -= 100
        # 3.how close together is player's tokens
        # loop through all tokens in that hex and check if it's player
        for token_i in range(len(state[coor])):
            if state[coor][token_i][0] == 'player':
                # loop through all tokens in the state
                for coor_i in state.keys():
                    if coor_i != coor:
                        for other_token in state[coor_i]:
                            # found token that is also player and has differnent symbol
                            if other_token[0] == 'player' and if_defeat(other_token[1], state[coor][token_i][1]) != "DRAW":
                                distance = func_hex_dist(coor, coor_i)
                                if distance == 1:
                                    eval_score += 3
                                elif distance == 2:
                                    eval_score += 2
                                elif distance == 3:
                                    eval_score += 1
                                elif distance == 6:
                                    eval_score += -1
                                elif distance == 7:
                                    eval_score += -2
                                elif distance == 8:
                                    eval_score += -3
                            # 4.how close are defeatable opponent tokens
                            if other_token[0] == 'opponent' and if_defeat(state[coor][token_i][1], other_token[1]) == "WIN":
                                distance = func_hex_dist(coor, coor_i)
                                if distance == 1:
                                    eval_score += 30
                                elif distance == 2:
                                    eval_score += 20
                                elif distance == 3:
                                    eval_score += 10
                            # 5.how close are undefeatable opponent tokens
                            if other_token[0] == 'opponent' and if_defeat(state[coor][token_i][1], other_token[1]) == "LOSE":
                                distance = func_hex_dist(coor, coor_i)
                                if distance == 1:
                                    eval_score += -30
                                elif distance == 2:
                                    eval_score += -20
                                elif distance == 3:
                                    eval_score += -10
                # 6.how close are player's token towards our side
                if which_side == 'lower':
                    if coor[0] == 4:
                        eval_score += 2
                    if coor[0] == 3:
                        eval_score += 1.5
                    if coor[0] == 2:
                        eval_score += 1
                    if coor[0] == 1:
                        eval_score += 0.5
                if which_side == 'upper':
                    if coor[0] == -4:
                        eval_score += 2
                    if coor[0] == -3:
                        eval_score += 1.5
                    if coor[0] == -2:
                        eval_score += 1
                    if coor[0] == -1:
                        eval_score += 0.5
    return eval_score


def token_list(state, side):  # side "player"/"opponent"
    token_dict = {}
    for key in state:
        for item in state[key]:
            if len(item) > 1:
                for i in item:
                    if state[key][0] == side:
                        j = {key: state[key][1]}
                        token_dict.update(j)

            elif len(item) == 1:
                if state[key][0] == side:
                    j = {key: state[key][1]}
                    token_dict.update(j)
    return token_dict


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


def possible_throw(state, board, r0, throw_range, player_or_opponent_list):
    character = ["r", "s", "p"]
    possible_throw_list = []
    for row in range(r0, throw_range):
        for item in board:
            if item[0] == row:
                if item not in state:
                    for char in character:
                        item_format = ["THROW", char, item]
                        possible_throw_list.append(item_format)
                else:
                    if item in player_or_opponent_list:
                        for char in character:
                            t = state[item][1]
                            if if_defeat(char, t) != "LOSE":
                                item_format = ["THROW", char, item]
                                possible_throw_list.append(item_format)
    return possible_throw_list


# least_distance with only consider slide
# go from token1 towards token2
# divide the board into 6 directions, and each 2 have the same properties => 3 kinds of direction properties
def least_slide_distance(p0, p1):  # format of token1 and token2 is the postion (-1,2)
    x0 = p0[0]
    y0 = p0[1]
    x1 = p1[0]
    y1 = p1[1]
    dx = x1 - x0
    dy = y1 - y0

    if dx * dy > 0:  # find what direction is token2 corresponding to token1
        dist = abs(dx + dy)  # calculate the min_dist based on the direction property
    else:
        dist = max(abs(dx), abs(dy))
    return dist


# least_distance with consider both slide and swing
# token_list is whether player_list or opponent_list depends on whether token1 is player token or opp token
def least_distance(state, token1, token2, player_or_opponent_list):  # consider both slide and swing 看token1 去到token2 的距离

    # six tokens surrounding token1
    layer1 = six_hex_surrond(token1)  # format is [[1,2],[-1,2],...]
    min_dist = least_slide_distance(token1, token2)

    # find swing , if can swing, count the distance as min(slide, dist after swing + 1)
    for i in range(6):
        surround_item = layer1[i]
        if tuple(surround_item) in state:
            # have neighbor with same team --> can swing
            if tuple(surround_item) in player_or_opponent_list:
                # find 6 hex connect to the previous neighbor
                layer2 = six_hex_surrond(surround_item)
                for j in range(i - 1, i + 2, 1):  # three hex opposite side
                    if j == 6:  # the hex next to no.5 in the clockwise list is no.0 and no.4
                        dist = least_slide_distance(tuple(layer2[0]),
                                                    token2) + 1  # count in swing movement to that position
                        if dist < min_dist:
                            min_dist = dist
                    else:
                        dist = least_slide_distance(tuple(layer2[j]), token2) + 1
                        if dist < min_dist:
                            min_dist = dist
    return min_dist
