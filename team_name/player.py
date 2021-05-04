
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
            self.throw_row_direction = -1 # for throwing the nth token, domain of available row is r0<=n<r0-n

        self.state = {}
        # set board range, make the board circled by "Block" tokens to avoid overstepping the boundary
        #range_limit = board_range()
        #for item in range_limit:
        #    loc = {tuple(item[1:3]): item[0]}
        #    self.state.update(loc)

        self.board = [(4,-4),(4,-3),(4,-2),(4,-1),(4,0),
                      (3,-4),(3,-3),(3,-2),(3,-1),(3,0),(3,1),
                      (2,-4),(2,-3),(2,-2),(2,-1),(2,0),(2,1),(2,2),
                      (1,-4),(1,-3),(1,-2),(1,-1),(1,0),(1,1),(1,2),(1,3),
                      (0,-4),(0,-3),(0,-2),(0,-1),(0,0),(0,1),(0,2),(0,3),(0,4),
                      (-1,-3),(-1,-2),(-1,-1),(-1,0),(-1,1),(-1,2),(-1,3),(-1,4),
                      (-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-2,3),(-2,4),
                      (-3,-1),(-3,0),(-3,1),(-3,2),(-3,3),(-3,4),
                      (-4,0),(-4,1),(-4,2),(-4,3),(-4,4)]
        # format of state e.g., {(-5,0):"Block"}
        # 之后也可以通过 len(self.state[position]) 是否大于1来判断是否超出了boundary

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
        # 在state里找出所有player token； 所有opponent token
        current_state=self.state
        board = self.board
        r0 = self.r0
        player_list=token_list(current_state, "player")
        opponent_list=token_list(current_state, "opponent")

        #[[[[1,2],[2,3]],[[2,3],[1,3]]],[[[1,2],[2,3]],[[2,3],[1,3]]]]
        character = ["s", "p", "r"]
        # 考虑throw

        no_rows = len(player_list)
        throw_range = r0 + no_rows * self.throw_row_direction

        # store all possible throw actions for player and opponent
        # def possible_throw 写在最下面了
        possible_throw_player = possible_throw(current_state, board, r0, throw_range, "player")
        possible_throw_opponent = possible_throw(current_state, board, r0, throw_range, "opponent")

        # store all possible actions for player and opponent: slide, swing, throw
        # for player
        player_total = []
        for item in player_list:
            ol = possible_move(current_state, item, "player")
            player_total.append(ol)
        player_total.append(possible_throw_player)

        # for opponent
        opp_total = []
        for opp in opponent_list:
            opp_ol = possible_move(current_state, opp, "opponent")
            opp_total.append(opp_ol)
        opp_total.append(possible_throw_opponent)

        # build min_max tree
        max_layer=[]
        for action in player_total:
            min_layer=[]
            for opp_action in opp_total:
                update(self, action, opp_action)  # 可以这样用吗？ （如果再来一轮 ，应该从这里加入, 感觉可以再加一层）
                eval = evaluate(self.state)
                min_layer.append(eval)
                self.state = current_state
            max_layer.append(min_layer)

        #[[1,2],[2,3]]

        # 加入pruning
        # 加入后续判断
        # def evaluation function没写
        # def 方位辨别找min dist没写
        # 换了board limit 方便找能thorw的位置， 记得把possible move里面加上if在board的条件


    
    def update(self, opponent_action, player_action): # 这里没考虑draw
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

def possible_move(state, current_pos, player_or_opponent):
    ol = []
    # six hex connected to the upper_current_pos
    layer1 = six_hex_surrond(current_pos)
    # player_current_pos的format是state的key ==> (x,y) ?
    # slide for all possible surrounding hexes
    for surround_item in layer1:
        # surround_item is [1,2]   upper_current_pos is [x, y]
        ol = if_ol_append(state, surround_item, current_pos, ol, "SLIDE")

    # swing
    for i in range(6):
        surround_item = layer1[i]
        if (tuple(surround_item) in state):
            # have upper upper_current_pos --> can swing
            if (state[tuple(surround_item)][0] == player_or_opponent):
                # six hex connected to the upper upper_current_pos for swing
                layer2 = six_hex_surrond(surround_item)
                for j in range(i - 1, i + 2, 1):  # three hex opposite side
                    if (j == 6):  # the hex next to no.5 in the clockwise list is no.0 and no.4
                        ol = if_ol_append(
                            state, layer2[0], current_pos, ol, "SWING")
                    else:
                        ol = if_ol_append(
                            state, layer2[j], current_pos, ol, "SWING")
    return ol #每一个action和update中action格式一样

def if_ol_append(state, item, token, ol, method):  # check if the item should be added to open list

    ol_pos = [i[2] for i in ol]
    t1 = state[tuple(token)][1] # whether s/p/r
    item_format = (method, t1, item)
    if item not in ol_pos:  # to avoid double record
        if tuple(item) in state:
            if state[tuple(item)][0]=="opponent":
                t2 = state[tuple(item)][1] # whether s/p/r
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
        x = item[0]+token[0]
        y = item[1]+token[1]
        loc = [x, y]  # coordinate of the hex
        six_hex.append(loc)
    return six_hex

#def evaluate(state):

#def least_distance(t1, t2):


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

def possible_throw(state, board, r0, throw_range, player_or_opponent):
    character = ["r", "s", "p"]
    for row in range(r0, throw_range):
        for item in board:
            if (item[0] == row):
                if (item not in state):
                    for char in character:
                        item_format = ["THROW", char, item]
                        possible_throw.append(item_format)
                else:
                    if (state[item][0] != player_or_opponent):
                        for char in character:
                            t = state[item][1]
                            if (if_defeat(char, t) != "LOSE"):
                                item_format = ["THROW", char, item]
                                possible_throw.append(item_format)
    return (possible_throw)

# least_distance with only consider slide
# go from token1 towards token2
# divide the board into 6 directions, and each 2 have the same properties => 3 kinds of direction properties
def least_slide_distance(token1, token2): # format of token1 and token2 is the postion (-1,2)
    x1 = token1[0]
    y1 = token1[1]
    x2 = token2[0]
    y2 = token2[1]
    if ((x1-x2)*(y1-y2) >= 0): # find what direction is token2 corresponding to token1
        dist = abs(x1-x2) + abs(y1-y2) # calculate the min_dist based on the direction property
    else:
        if (abs(x2-x1) >= abs(y2-y1)):
            dist = abs(x1-x2)
        else:
            dist = abs(y1-y2)
    return dist

# least_distance with consider both slide and swing
# token_list is whether player_list or opponent_list depends on whether token1 is player token or opp token
def least_distance(state, token1, token2, player_or_opponent): #consider both slide and swing 看token1 去到token2 的距离

    # six tokens surrounding token1
    layer1 = six_hex_surrond(token1) # format is [[1,2],[-1,2],...]
    min_dist = least_slide_distance(token1, token2)

    # find swing , if can swing, count the distance as min(slide, dist after swing + 1)
    for i in range(6):
        surround_item = layer1[i]
        if (tuple(surround_item) in state):
            # have neighbor with same team --> can swing
            if (state[tuple(surround_item)][0] == player_or_opponent):
                # find 6 hex connect to the previous neighbor
                layer2 = six_hex_surrond(surround_item)
                for j in range(i - 1, i + 2, 1):  # three hex opposite side
                    if (j == 6):  # the hex next to no.5 in the clockwise list is no.0 and no.4
                        dist = least_slide_distance(tuple(layer2[0]), token2) + 1 # count in swing movement to that position
                        if (dist < min_dist):
                            min_dist = dist
                    else:
                        dist = least_slide_distance(tuple(layer2[j]), token2) + 1
                        if (dist < min_dist):
                            min_dist = dist
    return min_dist
