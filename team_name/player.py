
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
        //在state里找出所有player token； 所有opponent token
        state=self.state
        player_list=token_list(current_state, "player")
        opponent_list=token_list(current_state, "opponent")
        max1_layer=[]
        for item in player_list: #max level
            ol = possible_move(current_state, item)
            min1_layer=[]
            for opp in opponent_list; #min_level
                opp_ol = possible_move(current_state, opp)
                max2_layer=[]
                for action in ol: #max_level
                    min2_layer=[]
                    for opp_action in opp_ol: #min_level
                        current_state=update(self, action, opp_action) #如果再来一轮 ，应该从这里加入
                        eval=evaluate(current_state)
                        min2_layer.append(eval)
                        self.state = state
                    max2_layer.append(min_layer)
                min1_layer.append(max2_layer)
            max1_layer.append(min1_layer)

        #[[[[1,2],[2,3]],[[2,3],[1,3]]],[[[1,2],[2,3]],[[2,3],[1,3]]]]
        # 加入pruning
        # 加入后续判断





    
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
        # record the 2 moving tokens' positions in previous state, and delete from the previous state
        # idea:把这次移动的token位置记下来 然后把他们在state里面删掉 为了后面battle不和这次移动的token上一轮的位置发生冲突

        prev_state_record = {}
        if player_action[0] != "THROW":
            loc = {player_action[1]: self.state[player_action[1]]}
            prev_state_record.update(loc)
            del self.state[player_action[1]]

        if opponent_action[0] != "THROW":
            loc = {opponent_action[1]: self.state[opponent_action[1]]}
            prev_state_record.update(loc)
            del self.state[opponent_action[1]]

        # consider the movement in this turn
        # idea: 若是throw说明之前没在state里出现过 只要考虑它要放的位置需不需要和别的token battle，
        # 赢了则在state里把这个位置改为这个token的信息，输了则不在state记入这个token
        # 若不是throw，则可以通过原位置在prev_state_record里找到相应的信息，在判断要放的位置是否需要和别的token battle
        # battle -> 赢了则在state里把这个位置改为这个token的信息，输了则不在state记入这个token
        # (因为最开始都把本轮要move的token的原位置在state里删掉了，只是在prev_state_record里有

        if player_action[0] == "THROW":
            if player_action[2] not in self.state:
                loc = {player_action[2]: ["player", player_action[1]]}
                self.state.update(loc)
            else:
                # if another token occupy the same place, need to check which token wins
                rps = player_action[1]
                old_rps = (self.state[player_action[2]])[1]
                if if_defeat(rps, old_rps):
                    self.state[player_action[2]] = ["player", rps]
                else:
                    # if this token lose, then take this token away from the state
                    pass
        else:
            # rps means whether the token is rock/paper/scissors
            # if the action is not throw, the rps has been recorded before
            previous_loc = player_action[1]
            rps = (prev_state_record[previous_loc])[1]
            if player_action[2] not in self.state:
                loc = {player_action[2]: ["player", rps]}
                self.state.update(loc)
            else:
                # if another token occupy the same place, need to check which token wins
                old_rps = (self.state[player_action[2]])[1]
                if if_defeat(rps, old_rps):
                    self.state[player_action[2]] = ["player", rps]
                else:
                    # if this token lose, then take this token away from the state
                    pass

        # update opponent action
        if opponent_action[0] == "THROW":
            if opponent_action[2] not in self.state:
                loc = {opponent_action[2]: ["opponent", opponent_action[1]]}
                self.state.update(loc)
            else:
                # if another token occupy the same place, need to check which token wins
                rps = opponent_action[1]
                old_rps = (self.state[opponent_action[2]])[1]
                if if_defeat(rps, old_rps):
                    self.state[opponent_action[2]] = ["opponent", rps]
                else:
                    # if this token lose, then take this token away from the state
                    pass
        else:
            # rps means whether the token is rock/paper/scissors
            # if the action is not throw, the rps has been recorded before
            previous_loc = opponent_action[1]
            rps = (prev_state_record[previous_loc])[1]
            if opponent_action[2] not in self.state:
                loc = {opponent_action[2]: ["opponent", rps]}
                self.state.update(loc)
            else:
                # if another token occupy the same place, need to check which token wins
                old_rps = (self.state[opponent_action[2]])[1]
                if if_defeat(rps, old_rps):
                    self.state[opponent_action[2]] = ["opponent", rps]
                else:
                    # if this token lose, then take this token away from the state
                    pass

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

def possible_move(state, token):
    ol = []
    layer1 = six_hex_surrond(token)
    for surround_item in layer1:
        # surround_item is [1,2]   upper_current_pos is [x, y]
        ol = if_ol_append(state, surround_item, upper_current_pos, ol)
        #print("upper_current",upper_current_pos)
        #print("state",state)
        ...
    return ol #每一个action和update中action格式一样

def func_open_list(state, upper_current_pos, target, list_no_cost):
    # upper_current_pos means upper upper_current_pos
    #possible_random_move = func_open_list(
       # state, list(upper_tuple[1:3]), ['r', 1, 1], 1)
    ol = []
    ol_with_cost = []
    # six hex connected to the upper_current_pos
    layer1 = six_hex_surrond(upper_current_pos)
    #if upper_current_pos not in state:
    # slide for all possible surrounding hexes
    #print(state)
    #print(upper_current_pos)
    #print(layer1)
    for surround_item in layer1:
        # surround_item is [1,2]   upper_current_pos is [x, y]
        ol = if_ol_append(state, surround_item, upper_current_pos, ol)
        #print("upper_current",upper_current_pos)
        #print("state",state)
    print(ol)
    # swing
    for i in range(6):
        surround_item = layer1[i]
        if (tuple(surround_item) in state):
            # have upper upper_current_pos --> can swing
            if (state[tuple(surround_item)].isupper()):
                # six hex connected to the upper upper_current_pos for swing
                layer2 = six_hex_surrond(surround_item)
                for j in range(i-1, i+2, 1):  # three hex opposite side
                    if (j == 6):  # the hex next to no.5 in the clockwise list is no.0 and no.4
                        ol = if_ol_append(
                            state, layer2[0], upper_current_pos, ol)
                    else:
                        ol = if_ol_append(
                            state, layer2[j], upper_current_pos, ol)
    if list_no_cost == 1:
        return ol
    for movable_hex in ol:
        movable_hex = list(movable_hex)
        # print('movable_hex', movable_hex, 'target', target)
        cost = func_upper_lower_distance(movable_hex, target)
        movable_hex.append(cost)
        ol_with_cost.append(movable_hex)

    return ol_with_cost

def if_ol_append(state, item, token, ol):  # check if the item should be added to open list

    new_ol = [i[0:2] for i in ol]

    if item not in new_ol:  # to avoid double record
        if tuple(item) in state:
            t1 = [state[tuple(token)]]+[token]
            #print("ut",ut)
            t2 = [state[tuple(item)]]+[item]
            #print("lt",lt)
            # append if not block or undefeatable lower token (upper, lower) uppper couldn't defeat lower --> 0
            if not (if_defeat(t1, t2) == 0):
                ol.append(item)
        else:
            ol.append(item)
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
        x = item[0]+token[0]
        y = item[1]+token[1]
        loc = [x, y]  # coordinate of the hex
        six_hex.append(loc)
    return six_hex

def evaluate(state):


def least_distance(t1, t2):



def token_list(state, side): #side "player"/"opponent"
    token_list={}
    for key in state:
        if item in state[key]:
            if len(item) > 1:
                for i in item:
                    if state[key][0] == side:
                        j = {key: state[key][1]}
                        token_list.update(j)

            elif len(item) == 1:
                if item != 'Block':
                    if state[key][0] == side:
                        j = {key: state[key][1]}
                        token_list.update(j)
    return token_list

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