########
##
## The arena which runs tournaments of bots
##
########


import random

import bot_player as bp
import tournament_results as tr
import morality_calculator as mc


class Arena(object):
    """
    Hosts tournaments of bots
    """
    def __init__(self):
        pass

    def generate_interaction_lengths(self, w, numMeetings):
        """
        Based on a probability of continuing each step, generate
        interaction lengths for the bot pairs

        ARGS:
        - w: probability of interaction continuing at each step
        - numMeetings: number of interaction_lengths needed to be
        generated

        RETURNS:
        - interaction_lengths: a list of integers representing how
        long each meeting between bots will be (if the list is n
        long, it is because each bot pair meets n times)
        """
        interaction_lengths = []
        i = 0
        while i < numMeetings:
            meeting_length = 1
            while True:
                r = random.random()
                if r > w:
                    break
                else:
                    meeting_length += 1
            interaction_lengths.append(meeting_length)
            i += 1
        return interaction_lengths

    def bot_interaction(self, bot1, bot2, interaction_length,
                    payoffs={'T': 5,'R': 3,'P': 1,'S': 0}, w=0.995):
        """
        Two bots paired together interacting

        ARGS:
        - bot1, bot2: instances of BotPlayer (presumably subclasses
        of BotPlayer), representing the two participating bots
        - interaction_length: how many turns bot1 and bot2 play in
        this interaction

        RETURNS:
        - past_moves: list of every move that occurred during the
        interaction
        """
        past_moves_1 = []
        past_moves_2 = []
        i = 0
        while i < interaction_length:
            bot1_move = bot1.getNextMove(past_moves_1,
                payoffs=payoffs, w=w)
            bot2_move = bot2.getNextMove(past_moves_2,
                payoffs=payoffs, w=w)
            next_moves_1 = (bot1_move, bot2_move)
            next_moves_2 = (bot2_move, bot1_move)
            past_moves_1.append(next_moves_1)
            past_moves_2.append(next_moves_2)
            i += 1
        return past_moves_1

    def validate_tournament_inputs(self, botList, numMeetings, payoffs, w):
        """
        Make sure the inputs to runTournament make sense and if they do not,
        say why in the list 'errors'

        ARGS:
        - botList: list of bots to participate in the tournament
        - w: probability of interaction continuing at each step
        - numMeetings: number of times each bot is paired with each
        other bot
        - payoffs: defines the scores for each Prisoner's Dilemma situation

        RETURNS:
        - errors: list or error messages to let the user know what is wrong
        with the inputs, if anything
        """
        errors = []
        # botList has to be a list of BotPlayer instances
        for bot in botList:
            if not isinstance(bot, bp.BotPlayer):
                errors.append("botList must be a list of BotPlayer objects")
                break
        if int(numMeetings) != numMeetings:
            errors.append("numMeetings must represent an integer")
        if numMeetings < 1:
            errors.append("numMeetings must be at least 1")
        if not (payoffs['T'] > payoffs['R'] > payoffs['P'] > payoffs['S']):
            errors.append("payoffs must obey T > R > P > S")
        if not (2*payoffs['R'] > payoffs['T'] + payoffs['S']):
            errors.append("payoffs must obey 2*R > T + S")
        if not (0 < w < 1):
            errors.append("w must be a number between 0 and 1")
        return errors

    def runTournament(self, botList, numMeetings,
                    payoffs={'T':5,'R':3,'P':1,'S':0}, w=0.995):
        """
        Main method, partners each bot with each other bot with
        w probability of ending each turn (length of interactions
        is determined (using w) before any pairings, so all
        pairings use the same list of interaction lengths)
        
        ARGS:
        - botList: list of bots to participate in the tournament
        - w: probability of interaction continuing at each step
        - numMeetings: number of times each bot is paired with each
        other bot
        - payoffs: defines the scores for each Prisoner's Dilemma situation

        RETURNS:
        - tourney_res: TournamentResults object with all the info
        """

        # validate inputs 
        error_messages =\
         self.validate_tournament_inputs(botList, numMeetings, payoffs, w)
        if error_messages:
            print(error_messages)
            return -1

        # dictionary of interactions to pass to TournamentResults
        interactions = {}

        # determine length of each interaction based on w
        interaction_lengths =\
         self.generate_interaction_lengths(w, numMeetings)

        # assign each bot a tournament id number
        for t_id, bot in enumerate(botList):
            bot.tournament_id = t_id

        # pair each bot with each other bot and save the results
        num_bots = len(botList)
        for i in xrange(num_bots):
            for j in xrange(i, num_bots):
                bot1 = botList[i]
                bot2 = botList[j]
                meeting_results_list = []
                for m in xrange(numMeetings):
                    interaction_length = interaction_lengths[m]
                    meeting_results =\
                     self.bot_interaction(bot1, bot2, interaction_length,\
                     payoffs=payoffs, w=w)
                    meeting_results_list.append(meeting_results)
                interactions[(bot1.tournament_id, bot2.tournament_id)] =\
                 meeting_results_list
        tourney_res = tr.TournamentResults(botList, interactions, payoffs)
        return tourney_res


## TODO: add capability for error/noise


## TODO: extend to ecological (evolutionary) environment


if __name__ == "__main__":
    
    import the_bots
    
    a = Arena()

    #----------#

    num_meetings = 5

    b1 = the_bots.ALL_D()
    b2 = the_bots.ALL_C()
    b3 = the_bots.RANDOM(p_cooperate=0.5)
    b4 = the_bots.PAVLOV()
    b5 = the_bots.TIT_FOR_TAT()
    b6 = the_bots.TIT_FOR_TWO_TATS()
    b7 = the_bots.TWO_TITS_FOR_TAT()
    b8 = the_bots.SUSPICIOUS_TIT_FOR_TAT()
    b9 = the_bots.GENEROUS_TIT_FOR_TAT(p_generous=0.1)
    b10 = the_bots.GENEROUS_TIT_FOR_TAT(p_generous=0.3)
    b11 = the_bots.JOSS(p_sneaky=0.1)
    b12 = the_bots.JOSS(p_sneaky=0.3)
    b13 = the_bots.MAJORITY(soft=True)
    b14 = the_bots.MAJORITY(soft=False)
    b15 = the_bots.TESTER()
    b16 = the_bots.FRIEDMAN()
    b17 = the_bots.EATHERLY()
    b18 = the_bots.CHAMPION()
    b19 = the_bots.RANDOM(p_cooperate=0.8)
    b20 = the_bots.RANDOM(p_cooperate=0.2)
    bot_list = [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13,\
     b14, b15, b16, b17, b18, b19, b20]

    t = a.runTournament(bot_list, num_meetings)
    print(t)

    mc = mc.MoralityCalculator(t)
    print(mc)

    #----------#
