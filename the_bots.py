########
##
## The many bots with different strategies
##
########


import random
import sys

from bot_player import BotPlayer


class ALL_D(BotPlayer):
    def __init__(self):
        d = "ALL_D defects unconditionally."
        BotPlayer.__init__(self, "ALL_D", description=d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Always defect
        """
        return 'D'

class ALL_C(BotPlayer):
    def __init__(self):
        d = "ALL_C cooperates unconditionally."
        BotPlayer.__init__(self, "ALL_C", description=d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Always cooperate
        """
        return 'C'

class RANDOM(BotPlayer):
    def __init__(self, p_cooperate=0.5):
        d = "RANDOM chooses randomly between cooperation and defection with "+\
        "some specified probability for each, independent of its partner's "+\
        "moves."
        BotPlayer.__init__(self, "RANDOM_"+str(p_cooperate), description=d)
        self.p_cooperate = p_cooperate

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Randomly choose an action, independent of past history
        p_cooperate is the probability of cooperating
        """
        r = random.random()
        if r < self.p_cooperate:
            return 'C'
        else:
            return 'D'

class PAVLOV(BotPlayer):
    def __init__(self):
        d = "PAVLOV defaults to cooperation on the first turn, and "+\
        "thereafter cooperates if and only if both players made the same "+\
        "choice last turn. This is known as 'win-stay, lose-shift', because "+\
        "PAVLOV repeats its own last move after it receives T or R (the good "+\
        "scores) and changes its move after it receives P or S (the bad "+\
        "scores), like a reflex demonstrated in Pavlov's dog experiment."
        BotPlayer.__init__(self, "PAVLOV", d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Defect exactly after the players' moves last turn do not match, and
        cooperate after they do match.
        """
        if not pastMoves:
            # this is the first turn, default to cooperation
            return 'C'
        else:
            # otherwise, cooperate if last moves match
            if pastMoves[-1][0] == pastMoves[-1][1]:
                return 'C'
            # last moves do not match, so defect
            else:
                return 'D'

class TIT_FOR_TAT(BotPlayer):
    def __init__(self):
        d = "TIT_FOR_TAT defaults to cooperation on the first turn, and "+\
        "thereafter mirrors its partner's previous move."
        BotPlayer.__init__(self, "TIT_FOR_TAT", description=d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Do whatever the other player did last turn
        """
        if not pastMoves:
            # this is the first turn, default to cooperation
            return 'C'
        else:
            # otherwise, reciprocate the other player's last move
            their_last_move = pastMoves[-1][1]
            return their_last_move

class TIT_FOR_TWO_TATS(BotPlayer):
    def __init__(self):
        d = "TIT_FOR_TWO_TATS defects if and only if its partner has "+\
        "defected for the past two turns."
        BotPlayer.__init__(self, "TIT_FOR_TWO_TATS", description=d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Cooperate unless the other player defected the past two turns
        """
        if len(pastMoves)<2:
            # this is one of the first few turns, default to cooperation
            return 'C'
        else:
            # if partner defected past two turns, reciprocate
            if (pastMoves[-1][1], pastMoves[-2][1]) == ('D', 'D'):
                return 'D'
            # otherwise, cooperate
            else:
                return 'C'

class TWO_TITS_FOR_TAT(BotPlayer):
    def __init__(self):
        d = "TWO_TITS_FOR_TAT cooperates unless its partner defects in which "+\
        "case TWO_TITS_FOR_TAT retaliates with two defections."
        BotPlayer.__init__(self, "TWO_TITS_FOR_TAT", description=d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Defect twice after each defection of the partner
        """
        if not pastMoves:
            # this is the first turn, default to cooperation
            return 'C'
        else:
            # if the partner has defected in the last two turns, defect
            if len(pastMoves) == 1:
                their_last_move = pastMoves[-1][1]
                return their_last_move
            else:
                if 'D' in (pastMoves[-1][1], pastMoves[-2][1]):
                    return 'D'
                # otherwise, cooperate
                else:
                    return 'C'

class SUSPICIOUS_TIT_FOR_TAT(BotPlayer):
    def __init__(self):
        d = "SUSPICIOUS_TIT_FOR_TAT defaults to defection on the first turn, "+\
        "and thereafter mirrors its partner's previous move."
        BotPlayer.__init__(self, "SUSPICIOUS_TIT_FOR_TAT", description=d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Do whatever the other player did last turn
        """
        if not pastMoves:
            # this is the first turn, default to defection
            return 'D'
        else:
            # otherwise, reciprocate the other player's last move
            their_last_move = pastMoves[-1][1]
            return their_last_move

class GENEROUS_TIT_FOR_TAT(BotPlayer):
    def __init__(self, p_generous=0.1):
        d = "GENEROUS_TIT_FOR_TAT defaults to cooperation on the first turn, "+\
        "and thereafter mirrors its partner's previous move, except after "+\
        "its partner defects GENEROUS_TIT_FOR_TAT cooperates with some "+\
        "probability to forgive occasional mistakes and avoid unnecessary "+\
        "mutual punishment."
        BotPlayer.__init__(self, "GENEROUS_TIT_FOR_TAT_"+str(p_generous),\
                            description=d)
        self.p_generous = p_generous

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Do whatever the other player did last turn, except probabilistically
        cooperate even if the other player defected
        """
        if not pastMoves:
            # this is the first turn, default to cooperation
            return 'C'
        else:
            # otherwise, reciprocate the other player's last move
            their_last_move = pastMoves[-1][1]
            action = their_last_move
            if action == 'D':
                # with the specified probability, generously cooperate
                r = random.random()
                if r < self.p_generous:
                    action = 'C'
            return action

class JOSS(BotPlayer):
    def __init__(self, p_sneaky=0.1):
        d = "JOSS defaults to cooperation on the first turn, and "+\
        "thereafter mirrors its partner's previous move, except after its "+\
        "partner cooperates JOSS defects with some probability to see what "+\
        "it can get away with every once in a while."
        BotPlayer.__init__(self, "JOSS_"+str(p_sneaky), description=d)
        self.p_sneaky = p_sneaky

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Do whatever the other player did last turn, except probabilistically
        defect even if the other player cooperated
        """
        if not pastMoves:
            # this is the first turn, default to cooperation
            return 'C'
        else:
            # otherwise, reciprocate the other player's last move
            their_last_move = pastMoves[-1][1]
            action = their_last_move
            if action == 'C':
                # with the specified probability, sneakily defect
                r = random.random()
                if r < self.p_sneaky:
                    action = 'D'
            return action

class MAJORITY(BotPlayer):
    def __init__(self, soft=True):
        d = "MAJORITY cooperates as long as its partner has cooperated more "+\
        "than it has defected (if partner has cooperated and defected equal "+\
        "amounts, MAJORITY cooperates if it is soft and defects if it is "+\
        "hard)."
        if soft:
            name = "MAJORITY_SOFT"
        else:
            name = "MAJORITY_HARD"
        BotPlayer.__init__(self, name, description=d)
        self.soft = soft

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Cooperate if the partner has cooperated more than defected
        """
        if not pastMoves:
            # this is the first turn, default to cooperation
            return 'C'
        # calculate their defection rate and act accordingly
        else:
            total_moves = len(pastMoves)
            their_defections =\
             len([1 for turn in pastMoves if turn[1] == 'D'])
            defection_ratio = float(their_defections)/float(total_moves)
            if defection_ratio < 0.5:
                return 'C'
            elif defection_ratio > 0.5:
                return 'D'
            # partner has defected and cooperated an equal number of times
            else:
                if self.soft:
                    return 'C'
                else:
                    return 'D'


class TESTER(BotPlayer):
    def __init__(self):
        d = "TESTER initially defects to test what the other player will do. "+\
        "If the other player defects ever, TESTER apologizes by cooperating "+\
        "and then mirrors the partner's moves thereafter. If the other "+\
        "player does not retaliate, TESTER cooperates twice but then defects "+\
        "on and off every other turn."
        BotPlayer.__init__(self, "TESTER", description=d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Test the waters with initial defection, apologize if they ever defect,
        and if they do not, cooperate twice and then switch off between
        defection and cooperation every other turn.
        """
        if not pastMoves:
            # this is the first turn, default to defection
            return 'D'
        else:
            partner_moves = [move[1] for move in pastMoves]
            if 'D' not in partner_moves:
                # if they have not defected, alternate actions after
                if 0 < len(pastMoves) < 3:
                    # it is the second or third move and they have not defected
                    return 'C'
                # it is past the second or third move and they have not defected
                my_last_move = pastMoves[-1][0]
                if my_last_move == 'C':
                    return 'D'
                elif my_last_move == 'D':
                    return 'C'
            elif 'D' in partner_moves:
                # if they have defected, check when their first time was to see
                # if we need to apologize
                if 'D' not in partner_moves[:-1]:
                    # this is their first defection, so apologize
                    return 'C'
                elif 'D' in partner_moves[:-1]:
                    # if they defected more than a turn ago, we just mirror
                    # their most recent action
                    return partner_moves[-1]

class FRIEDMAN(BotPlayer):
    def __init__(self):
        d = "FRIEDMAN is the permanent retaliator. It cooperates until its "+\
        "partner defects, after which FRIEDMAN defects for the rest of the "+\
        "interaction."
        BotPlayer.__init__(self, "FRIEDMAN", description=d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Cooperate until they defect, then defect always.
        """
        if not pastMoves:
            # this is the first turn, default to cooperation
            return 'C'
        else:
            partner_moves = [move[1] for move in pastMoves]
            if 'D' in partner_moves:
                # defect if they have ever defected
                return 'D'
            elif 'D' not in partner_moves:
                # cooperate as long as they do
                return 'C'

class EATHERLY(BotPlayer):
    def __init__(self):
        d = "EATHERLY defaults to cooperation, but keeps track of how many "+\
        "times the other player has defected, so after a defection by the "+\
        "other player, EATHERLY can defect with probability equal to the "+\
        "ratio of its partner's defections to the total number of moves so far."
        BotPlayer.__init__(self, "EATHERLY", d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        if not pastMoves:
            # this is the first turn, default to cooperation
            return 'C'
        else:
            if pastMoves[-1][1] == 'C':
                # they cooperated last turn, so reciprocate cooperation
                return 'C'
            elif pastMoves[-1][1] == 'D':
                # they defected last turn, so defect with probability equal to
                # their defection ratio
                total_moves = len(pastMoves)
                their_defections =\
                 len([1 for turn in pastMoves if turn[1] == 'D'])
                defection_ratio = float(their_defections)/float(total_moves)
                r = random.random()
                if r < defection_ratio:
                    return 'D'
                else:
                    return 'C'

class CHAMPION(BotPlayer):
    def __init__(self, p_cooperate=0.5):
        d = "CHAMPION cooperates for about 1/20 of the expected length of "+\
        "interaction, mirrors its partner's previous move for about 3/40 of "+\
        "the expected length of interaction, and then cooperates unless all "+\
        "three of the following conditions are true: its partner defected "+\
        "last turn, its partner cooperated less than 60% of the time, and "+\
        "a randomly generated number between 0 and 1 is less than its "+\
        "partner's defection rate."
        BotPlayer.__init__(self, "CHAMPION", description=d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.9):
        """
        Cooperate for 1/20 the expected length of interaction, mirror partner's
        moves for 3/40 the expected length of interaction, then defect with
        probability equal to partner's defection rate and only after they
        defect and if their defection rate is above 40%.
        """
        num_turns = float(len(pastMoves))
        expected_length = 1.0/(1.0-w)
        if num_turns <= expected_length/20.0:
            # in unconditional cooperation phase
            return 'C'
        if expected_length/20.0 < num_turns < (5.0/40.0)*expected_length:
            # in pure reciprocation stage
            their_last_move = pastMoves[-1][1]
            return their_last_move
        elif num_turns >= (5.0/40.0)*expected_length:
            # in the judged phase (all of their actions come into play)
            their_last_move = pastMoves[-1][1]
            their_defections =\
                 len([1 for turn in pastMoves if turn[1] == 'D'])
            their_defection_rate = their_defections/num_turns
            r = random.random()
            if their_last_move == 'D' and their_defection_rate > max(0.4, r):
                # all conditions for the final phase are met
                return 'D'
            else:
                # at least one condition failed
                return 'C'


## TODO: design and implement more bots


## TODO: finish unfinished bots

### vvv Unfinished bots vvv ###

class TRANQUILIZER(BotPlayer):
    def __init__(self):
        ## TODO: read pages 45-46 of Axelrod and describe this
        d = None
        BotPlayer.__init__(self, "TRANQUILIZER", d)

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        ## TODO: read pages 45-46 of Axelrod and implement this
        return 'C'

class DOWNING(BotPlayer):
    def __init__(self, optimistic=True):
        d = "DOWNING tries to maximize expected gains by testing the water "+\
        "with its partner. The idea is that if its partner seems responsive "+\
        "to what DOWNING is doing, DOWNING will cooperate, but if the other "+\
        "player seems unresponsive, DOWNING will try to get away with "+\
        "whatever it can by defecting. DOWNING does this by keeping an "+\
        "estimate of the probability of the other player cooperating given "+\
        "DOWNING's last move. The initial estimates depend on DOWNING's "+\
        "outlook (optimistic or pessimistic)."
        if optimistic:
            name = "OPT_DOWNING"
        elif not optimistic:
            name = "PESS_DOWNING"
        BotPlayer.__init__(self, name, description=d)
        self.optimistic = optimistic

    def getNextMove(self, pastMoves,\
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Estimate the chance the other player cooperates after DOWNING cooperates
        or defects, and use these estimates to choose an action.
        """
        ## TODO: this is hard and needs more specification, ignore for now
        return 'C'

### ^^^ Unfinished bots ^^^ ###

if __name__ == "__main__":
    pass