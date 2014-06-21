########
##
## Class to represent a bot in an IPD tournament
##
########


class BotPlayer(object):
    """
    This class should be inherited from by bots who define their
    own getNextMove method. That is how bots have their own strategy.
    self.name is the name of the strategy employed
    self.description is an explanation of the strategy
    self.tournament_id can be assigned upon beginning each tournament
    """
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        if not self.description:
            self.description = self.name
        self.tournament_id = None

    def __str__(self):
        return self.name

    def getNextMove(self, pastMoves, payoffs, w):
        """
        Given the history of interactions with another bot,
        output the next move, either cooperate or defect

        This method is to be overridden by bots and should use only static
        initialization variables, randomness, and past moves in order to make
        a decision. No other state should be updated/saved/taken into account.

        TODO: Is that 'no other state' thing valid? What if a bot wants to
        do some behavior only once, but when exactly it does so is randomly
        determined? I believe this could require some saved information besides
        the history of moves, but this seems like a valid strategy.

        ARGS:
        pastMoves: array of tuples, where each tuple is the pair
            of choices made that turn by this bot and its partner
            [(myMove1, hisMove1), (myMove2, hisMove2), ...] and
            the moves are represented by 'C' for "Cooperate" or 'D'
            for "Defect". For example, [('C', 'D'), ('D', 'D'), ...]

        RETURNS:
        nextMove: 'C' for "Cooperate" or 'D' for "Defect"
        """

        ## this method should be overridden, so this return value
        ## doesn't matter
        return 'D'
