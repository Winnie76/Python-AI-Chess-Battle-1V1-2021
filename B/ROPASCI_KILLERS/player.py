import copy
import time

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
        self.opponent = ""
        self.time = 0.0
        if self.player == "lower":
            self.opponent == "upper"
            self.r0 = -4
            # for throwing the nth token, domain of available row is r0<=n<r0+n
            self.throw_row_direction = 1
        else:
            self.opponent == "lower"
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
                      (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3),
                      (0, -4), (0, -3), (0, -2), (0, -1), (0,0), (0, 1), (0, 2), (0, 3), (0, 4),
                      (-1, -3), (-1, -2), (-1, -1), (-1,0), (-1, 1), (-1, 2), (-1, 3), (-1, 4),
                      (-2, -2), (-2, -1), (-2, 0), (-2,1), (-2, 2), (-2, 3), (-2, 4),
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
        start_time = time.time()
        current_state = copy.deepcopy(self.state)
        no_throw = copy.deepcopy(self.throw)
        no_oppo_throw = copy.deepcopy(self.oppo_throw)
        print("current_state initial",current_state)
#        current_state = {}
#        for key in self.state:
#            for element in self.state[key]:
#                if key not in current_state:
#                    current_state[key] = [element]
#                else:
#                    current_state[key].append(element)

        board = self.board
        r0 = self.r0
        r0_opp = -r0

        # existing player and oppo in the state
        # player_list = {(coor):['r', 's'], (coor):['p']}
        player_list = token_list(current_state, "player")
        opponent_list = token_list(current_state, "opponent")

#         print("player_list", player_list)

        character = ["s", "p", "r"]
    
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


        # store all possible throw actions for player and opponent -- cut out undefeatble possible throw already
        # possible_throw_player = [["THROW", 's', (coor)]]
        possible_throw_player = possible_throw(
            current_state, board, r0, throw_range, "player", self.throw)
        possible_throw_opponent = possible_throw(
            current_state, board, r0_opp, throw_range_opp, "opponent", self.oppo_throw)
        
        # player_total = [[...],[...]]     stores all possible actions for player and opponent: slide, swing, throw
        # for player
        player_total = []
        
        if self.throw < 7: #threw 3 tokens already
            for item in player_list:
                ol = possible_move(current_state, item,
                                   player_list, opponent_list, board)
                for each in ol:
                    player_total.append(each)
            player_total += possible_throw_player
                    
        else:
            player_total += possible_throw_player
#        print("player_total", player_total)
        # for opponent
        opp_total = []
        

        if self.oppo_throw < 7: #threw 3 tokens already
            for opp in opponent_list:
                opp_ol = possible_move(
                    current_state, opp, opponent_list, player_list, board)
                for each in opp_ol:
                    opp_total.append(each)
            opp_total += possible_throw_opponent
                    
        else:
            opp_total += possible_throw_opponent
        
        #opp_total += possible_throw_opponent
        
        #record the number of token throw in the current state
        player_no_throw = copy.deepcopy(self.throw)
        opponent_no_throw = copy.deepcopy(self.oppo_throw)
        
        # reorder the move of player for improving pruning
#        print("bfore reorder",current_state)
        copy_current_state = copy.deepcopy(current_state)
        player_total = reorder_move(player_total, copy_current_state, 
                                    self.player, player_list, opponent_list, board, "player")
#        print("player_total2", player_total)
        
        opp_total = reorder_move(opp_total, copy_current_state, 
                                    self.opponent, opponent_list, player_list, board, "opponent")
        if len(player_total) > 6:
            player_total = player_total[0:6]
        
        if len(opp_total) > 6:
            opp_total = opp_total[0:6]
            
        if self.time > 55.0:
            return tuple(player_total[0])
        
        # build min_max tree
        max_layer1 = []
        min_max1 = -10000
#         print("bf minmax current state", current_state)
        self.player_action = player_total[0]
#         print("player_total[0]", player_total[0])
#        print(no_throw)
        final_player_action = player_total[0]
        for action in player_total:
            min_layer1 = []
#             print("action in player_total", action)
            for opp_action in opp_total:
#                print("here self.state",self.state)
#                print("here current state", current_state)
                # max_layer2 = []
                #                 print("action in oppo_total", opp_action)
                #                 print("current state before Player_update", current_state)
                self.update(opp_action, action)  # 如果再来一轮 ，应该从这里加入, 感觉可以再加一层）
#                 print("after  Player.update(self, action, opp_action) current state is", current_state)
#                 print("after  Player.update(self, action, opp_action) self state is", self.state)
                # record the current state
                current_new_state = copy.deepcopy(self.state)
                # record the current number of token throw
                player_new_no_throw = copy.deepcopy(self.throw)
                opponent_new_no_throw = copy.deepcopy(self.oppo_throw)
                
 #               print("current_new_state initial", current_new_state)
                # existing player and oppo in the state
                player_new_list = token_list(current_new_state, "player")
                opponent_new_list = token_list(current_new_state, "opponent")
                
                
                new_throw_range = r0 + (9 - player_new_no_throw + 1) * self.throw_row_direction
                new_throw_range_opp = r0_opp + \
                    (9 - opponent_new_no_throw + 1) * (- self.throw_row_direction)
                
                # store all possible throw actions for player and opponent -- cut out undefeatble possible throw already
                new_possible_throw_player = possible_throw(
                current_new_state, board, r0, new_throw_range, "player", self.throw)
                new_possible_throw_opponent = possible_throw(
                current_new_state, board, r0_opp, new_throw_range_opp, "opponent", self.oppo_throw)
                
                # stores all possible actions for player and opponent: slide, swing, throw
                # for player
                player_new_total = []
        
                if player_new_no_throw < 7:
                    for item in player_new_list:
                        ol = possible_move(current_new_state, item,
                                   player_new_list, opponent_new_list, board)
                        for each in ol:
                            player_new_total.append(each)
                    
                player_new_total += new_possible_throw_player
#               print("player_new_total", player_new_total)
                # for opponent

                opp_new_total = []
        
                if opponent_new_no_throw < 7:
                    for opp in opponent_new_list:
                        opp_ol = possible_move(
                                        current_new_state, opp, opponent_new_list, player_new_list, board)
                        for each in opp_ol:
                            opp_new_total.append(each)
                    
                opp_new_total += new_possible_throw_opponent
                
                 # reorder the move of player for improving pruning
                copy_current_new_state = copy.deepcopy(current_new_state)
                player_new_total = reorder_move(player_new_total, copy_current_new_state, 
                                    self.player, player_new_list, opponent_new_list, board, "player")

#                print("player_new_total", player_new_total)

                opp_new_total = reorder_move(opp_new_total, copy_current_new_state, 
                                    self.opponent, opponent_new_list, player_new_list, board, "opponent")
                
                # limit the branch expand
                if len(player_new_total) > 6:
                    player_new_total = player_new_total[0:6]
                if len(opp_new_total) > 6:
                    opp_new_total = opp_new_total[0:6]
                
                min_max = -10000
                for new_action in player_new_total:
                    min_layer2 = []
#                   print("action in player_new_total", new_action)
                    for opp_new_action in opp_new_total:
                        #print("current_self.state",self.state)
                        self.update(opp_new_action, new_action)
                        eval_score = evaluation(self.state, self.player, self.win, self.loss, player_new_list, 
                                            opponent_new_list, board)
#                       print("after eval_score = evaluation(self.sta...) current state is", current_state)
#                        print("eval score", eval_score)
                        self.state = copy.deepcopy(current_new_state)
                        self.throw = copy.deepcopy(player_new_no_throw)
                        self.oppo_throw = copy.deepcopy(opponent_new_no_throw)
                        #print("after update_self.state",self.state)
#                 print("\nafter self.state = current_state, self state is", self.state)
#                 print("\nnafter self.state = current_state, current_state is", current_state)
#                 print("\n")
                        if eval_score > min_max:
                            min_layer2.append(eval_score)
#                       self.state = current_state
#                       print("eval score > min_mac then self state = current state", current_state)
                        # 说明这个predecessor下面的node都大于之前的max_min => max_min更改
                            if opp_new_action == opp_new_total[-1]:
                                min_max = min(min_layer2)  # update min_max
                                #max_layer2_action = action  # update player_action leads to the state with min_max
#                       print("self.player_action = action", eval_score)
                        else:
#                           print("eval score < min_mac then self state = current state", current_state)
                            break
                # min_max is the max of the mins for each second minimax round
#                min_layer1.append(min_max)
                self.state = copy.deepcopy(current_state)
                self.throw = copy.deepcopy(player_no_throw)
                self.oppo_throw = copy.deepcopy(opponent_no_throw)
                if min_max > min_max1:
                    min_layer1.append(min_max)
                    if opp_action == opp_total[-1]:  # loop 到了opp_total最后一个-->对于一个player action loop完了所有的opp action
                        min_max1 = min(min_layer1)
                        final_player_action = action
                else:
                    #min_layer1.append(min_max)
                    break

            max_layer1.append(min_layer1)
#        print(max_layer1)
        # decide action of first round minimax
#        length = len(max_layer1)
#        for i in range(length):
#            if max_layer1[i] == max(max_layer1):
#                final_player_action = player_total[i]         
#        print(player_total)
#        print("min_max",min_max1)
#        print(current_state)
        end_time = time.time()
        self.time += end_time - start_time
        return tuple(final_player_action)


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
            if self.throw > 0:
                self.throw -= 1
            player_symbol = player_action[1]
        else:
            # if more than one token in a hex , they must have the same symbol
            player_symbol = self.state[player_action[1]][0][1]
        if opponent_action[0] == "THROW":
            if self.oppo_throw > 0:
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
                        elif player_destination in self.state and if_defeat(player_symbol, self.state[player_destination][0][1]) != "WIN":
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


def possible_throw(state, board, r0, throw_range, who, no_throw):
    #print("no_throw",no_throw)
    character = ["r", "s", "p"]

    possible_throw_list = []

    if r0 == 4:
        reverse = -1
    else:
        reverse = 1

    # !!!!!!!!!!!!!等一下我写一下判断和对方symbols差距，然后有针对性的throw！！！！！！
    if no_throw == 9:  # no_throw is the number of throws remain
        only_action = ["THROW", character[0], (r0, 1 * reverse)]
        possible_throw_list.append(only_action)
        return possible_throw_list

    if no_throw == 8:
        only_action = ["THROW", character[1], (r0 + 1 * reverse, 1 * reverse)]
        possible_throw_list.append(only_action)
        return possible_throw_list

    if no_throw == 7:
        only_action = ["THROW", character[2], (r0 + 2 * reverse, 1 * reverse)]
        possible_throw_list.append(only_action)
        return possible_throw_list

    if no_throw == 0:
        return possible_throw_list

        # if no opponent in throw range + 1, then no throw
    has_oppo = 0
    player_s = 0
    player_r = 0
    player_p = 0

    opponent_s = 0
    opponent_r = 0
    opponent_p = 0
    for coor in state:
        # count symbols for player and oppo in the state
        for token in state[coor]:
            if token[0] == who:
                if token[1] == "s":
                    player_s += 1
                elif token[1] == "r":
                    player_r += 1
                else:
                    player_p += 1
            else:
                if token[1] == "s":
                    opponent_s += 1
                elif token[1] == "r":
                    opponent_r += 1
                else:
                    opponent_p += 1
        # throw on opponent tokens
        if r0 == 4 and coor[0] > throw_range:
            for token in state[coor]:  # all token in throw range
                if token[0] != who:  # if token in throw range is opponent
                    has_oppo = 1  # hasoppo = 1
                    for char in character:  # find the win symbol of that token
                        if if_defeat(char, token[1]) == "WIN":
                            symbol_win = char
                    six_hex = six_hex_surrond(coor)
                    has_other_oppo = 0
                    # check 6 hex has undefeatable token or not
                    for one_hex in six_hex:  # [x, y]
                        if tuple(one_hex) in state:
                            for one_token in state[tuple(one_hex)]:
                                if one_token[0] != who and if_defeat(symbol_win, one_token[1]) == "LOSE":
                                    has_other_oppo = 1
                    # no undefeatable oppo in 6 hex surrounds then append throw
                    if has_other_oppo == 0:
                        possible_throw_list.append(["THROW", symbol_win, coor])
                    # else not consider that coordinate to throw
                    else:
                        break
        elif r0 == -4 and coor[0] < throw_range:
            for token in state[coor]:  # all token in throw range
                if token[0] != who:  # if token in throw range is opponent
                    has_oppo = 1  # hasoppo = 1
                    for char in character:  # find the win symbol of that token
                        if if_defeat(char, token[1]) == "WIN":
                            symbol_win = char
                    six_hex = six_hex_surrond(coor)
                    has_other_oppo = 0
                    # check 6 hex has undefeatable token or not
                    for one_hex in six_hex:  # [x, y]
                        if tuple(one_hex) in state:
                            for one_token in state[tuple(one_hex)]:
                                if one_token[0] != who and if_defeat(symbol_win, one_token[1]) == "LOSE":
                                    has_other_oppo = 1
                    # no undefeatable oppo in 6 hex surrounds then append throw
                    if has_other_oppo == 0:
                        possible_throw_list.append(["THROW", symbol_win, coor])
                    # else not consider that coordinate to throw
                    else:
                        break

    # balance symbol in state
    throw_list_upp = [(1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, -4), (1, -3)]
    throw_list_low = [(-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, -3), (-1, -2)]
    if r0 == 4:
        throw_where = throw_list_upp
    else:
        throw_where = throw_list_low
    # throw more paper
    if (player_p == 0 and opponent_r > 0) or (opponent_r - player_p > 2 and player_p != 0):
        for coor in throw_where:
            if coor not in state:
                six_hex = six_hex_surrond(coor)
                has_other_oppo = 0
                # check 6 hex has undefeatable token or not
                for one_hex in six_hex:  # [x, y]
                    if tuple(one_hex) in state:
                        for one_token in state[tuple(one_hex)]:
                            if one_token[0] != who and if_defeat('p', one_token[1]) == "LOSE":
                                has_other_oppo = 1
                # no undefeatable oppo in 6 hex surrounds then append throw
                if has_other_oppo == 0:
                    possible_throw_list.append(["THROW", 'p', coor])
                    break
    if (player_s == 0 and opponent_p > 0) or (opponent_p - player_s > 2 and player_s != 0):
        for coor in throw_where:
            if coor not in state:
                six_hex = six_hex_surrond(coor)
                has_other_oppo = 0
                # check 6 hex has undefeatable token or not
                for one_hex in six_hex:  # [x, y]
                    if tuple(one_hex) in state:
                        for one_token in state[tuple(one_hex)]:
                            if one_token[0] != who and if_defeat('s', one_token[1]) == "LOSE":
                                has_other_oppo = 1
                # no undefeatable oppo in 6 hex surrounds then append throw
                if has_other_oppo == 0:
                    possible_throw_list.append(["THROW", 's', coor])
                    break
    if (player_r == 0 and opponent_s > 0) or (opponent_s - player_r > 2 and player_r != 0):
        for coor in throw_where:
            if coor not in state:
                six_hex = six_hex_surrond(coor)
                has_other_oppo = 0
                # check 6 hex has undefeatable token or not
                for one_hex in six_hex:  # [x, y]
                    if tuple(one_hex) in state:
                        for one_token in state[tuple(one_hex)]:
                            if one_token[0] != who and if_defeat('r', one_token[1]) == "LOSE":
                                has_other_oppo = 1
                # no undefeatable oppo in 6 hex surrounds then append throw
                if has_other_oppo == 0:
                    possible_throw_list.append(["THROW", 'r', coor])
                    break

    #     for row in range(r0, throw_range, reverse):  # -4, -3, -2, -1 or 4, 3, 2, 1(reverse)

    #         for item in board:
    #             if item[0] == row:
    #                 #                 print("yes if item[0] == row:")
    #                 if item not in state:
    #                     #                     print("yes if item not in state:")
    #                     for char in character:
    #                         item_format = ["THROW", char, item]
    #                         possible_throw_list.append(item_format)
    # #                         print("yes appended")
    #                 # 当（coor）在state里，说明有其他token，那就要看 我方 还是 敌方。如果是我方：不throw了，因为无论输赢平局都没给棋盘增加 eval_score
    #                 # 如果是敌方：只有赢的情况下 throw
    #                 # 这样做是为了减少 time complexity， 因为dime fox很容易超时
    #                 else:
    #                     has_who = 0
    #                     # check if token existed in the state is from our side or not
    #                     for token in state[item]:
    #                         if token[0] == who:
    #                             has_who = 1
    #                         else:
    #                             oppo_symb = token[1]
    #                     # if token at that hex is not from our side, put symbol that can defeat oppo into possible throw
    #                     if has_who == 0:
    #                         for char in character:
    #                             if if_defeat(char, oppo_symb) == "WIN":
    #                                 item_format = ["THROW", char, item]
    #                                 possible_throw_list.append(item_format)

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
                # ???????这里要加吗self.oppo_throw != 9 时限制在player side？？？？？
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
    # 2 > differnece >=0 (differnece within 0 or 1 is encouraged)
    if (player_s - opponent_p) >= 0 and (opponent_p > 0) and (player_s - opponent_p) < 2:
        eval_score +=  1000
    if (player_r - opponent_s) >= 0 and (opponent_s > 0) and (player_r - opponent_s) < 2:
        eval_score +=  1000
    if (player_p - opponent_r)  >= 0 and (opponent_r > 0) and (player_p - opponent_r) < 2:
        eval_score +=  1000
    return eval_score

def update_player_action(player_action, current_state, who): #前面记得把no_defeat和loss归0
    prev_state_record = {}
    no_defeat = 0
    no_loss = 0
#    print("带进去的current——state",current_state)
    copy_current_state = copy.deepcopy(current_state)
    # opponent_or_player带入“opponent” or “player”
    if player_action[0] != "THROW":
        # for multiple tokens in one state, all symbols should be the same
        # player_action[1] => previous position
#        print("---------------------------=================")
#        print(current_state)
#        print(player_action)
#        print("---------------------------=================")
        symbol = current_state[player_action[1]][0][1]
        loc = {player_action[1]: [who, symbol]}
        prev_state_record.update(loc)
        # if the position in the previous state only has one token, then delete it from the state
        # if there are multiple tokens, then delete the corresponding one
        if len(current_state[player_action[1]]) == 1:
            del current_state[player_action[1]]
        else:
 #           print("here notice", current_state)
 #           print("\n")
 #           print(player_action)
#            print(symbol)
            current_state[player_action[1]].remove([who, symbol])
    
    if player_action[0] == "THROW":
        if player_action[2] not in current_state:
            loc = {player_action[2]: [[who, player_action[1]]]}
            current_state.update(loc)
        else:
            # if another token occupy the same place, need to check which token wins
            # rps means rock paper or scissors
            rps = player_action[1]
            old_rps = (current_state[player_action[2]])[0][1]
            if if_defeat(rps, old_rps) == "WIN":
                for item in current_state[player_action[2]]:
                    if item[0] != who:
                        no_defeat += 1  # player token eat opponent token
                    else:
                        no_loss += 1  # player token eat player token
                current_state[player_action[2]] = [[who, rps]]
            elif if_defeat(rps, old_rps) == "DRAW":
                current_state[player_action[2]].append([who, rps])
            else:
                # if this token lose, then take this token away from the state
                pass
    else:
        # if the action is not throw, the rps has been recorded before
        previous_loc = player_action[1]
        rps = (prev_state_record[previous_loc])[1]
        if player_action[2] not in current_state:
            loc = {player_action[2]: [[who, rps]]}
            current_state.update(loc)
        else:
            # if another token occupy the same place, need to check which token wins
            old_rps = (current_state[player_action[2]])[0][1]
            if if_defeat(rps, old_rps) == "WIN":
                for item in current_state[player_action[2]]:
                    if item[0] != who:
                        no_defeat += 1  # player token eat opponent token
                    else:
                        no_loss += 1  # player token eat player token
                current_state[player_action[2]] = [[who, rps]]
            elif if_defeat(rps, old_rps) == "DRAW":
                current_state[player_action[2]].append([who, rps])
            else:
                # if this token lose, then take this token away from the state
                pass
    list_to_return = [current_state, no_defeat, no_loss]
    current_state = copy.deepcopy(copy_current_state)
    return list_to_return

def reorder_move(player_total, current_state, upper_or_lower, player_list, opponent_list, board, who):
    move_eval_list = []
    copy_current_state = copy.deepcopy(current_state)
    for move in player_total:
        list_of_return = update_player_action(move, current_state, who)
        move_state = list_of_return[0]
        move_no_defeat = list_of_return[1]
        move_no_loss = list_of_return[2]
        move_eval = evaluation(move_state, upper_or_lower, move_no_defeat, move_no_loss, player_list, 
                            opponent_list, board)
        move_eval_list.append(move_eval)
        current_state = copy.deepcopy(copy_current_state)

    #insertion sort
    for i in range(1, len(player_total)):
        val = move_eval_list[i]
        move = player_total[i]
        j = i
        while (move_eval_list[j-1] < val) & (j > 0):
            move_eval_list[j] = move_eval_list[j-1]
            player_total[j] = player_total[j-1]
            j-=1
        move_eval_list[j] = val
        player_total[j] = move
    current_state = copy.deepcopy(copy_current_state)
    return player_total