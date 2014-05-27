########
##
## Wrapper to hold results of a tournament
##
########

import copy

class TournamentResults():
    """
    Calculates and wraps results of tournaments
    """
    def __init__(self, botList, interactions, payoffs):
        """
        Calculate the scores of the interactions and the total scores for the
        bots using the specified payoffs.

        ARGS:
        - botList: a list of BotPlayer objects where the index of botX in the
        list is the tournament id used in the argument interactions. basically,
        botList maps tournament id to bot
        - interactions: a dictionary with
            keys => (tournament_id1, tournament_id2)
            values => [meeting1, meeting2, ...]
        where meetingX is a list of tuples (bot1_move, bot2_move).
        For example:
        interactions = {
            (0, 1): [
                [('C', 'D'), ('D', 'D')],
                [('C', 'C'), ('C', 'D'), ('D', 'D')]
            ],
            ...
        }
        - payoffs: defines the scores for each Prisoner's Dilemma situation,
        which TournamentResults needs to correctly score each interaction
        """
        self.botList = botList
        self.interactions = interactions
        self.payoffs = payoffs

        self.numBots = len(self.botList)

        # to allow lookup for bot name and description by tournament id
        self.bot_info_by_id = {}
        for bot in botList:
            self.bot_info_by_id[bot.tournament_id] =\
            {'name': bot.name, 'description': bot.description, 'total': 0}

        self.interaction_lengths = []
        some_pair = self.interactions.keys()[0]
        for interaction in self.interactions[some_pair]:
            self.interaction_lengths.append(len(interaction))

        self.total_interactions = float(
            self.numBots*sum(self.interaction_lengths)
        )

        # to be filled with scores for each bot in each interaction
        self.interaction_scores = {}

        # calculate and store interaction and total scores
        self.calculate_scores()

    def __str__(self):
        # sort the bots for printing output
        def get_score(bot):
            return self.bot_info_by_id[bot.tournament_id]['total']
        sorted_bots = sorted(self.botList, key=get_score, reverse=True)

        headers = [
            "Tournament ID",
            "Bot Name",
            "Total Score",
            "Avg Score Per Turn"
        ]
        num_cols = len(headers)

        # find a good column width to use for formatting the output
        long_header = max([len(h) for h in headers])
        long_name = max([len(bot.name) for bot in self.botList])+1
        col = max([long_header, long_name])
        col_str = str(col)
        format_str = (("{: <"+col_str+"} ")*num_cols)[:-1]
        hr = "-"*(num_cols*col)

        # construct output string
        output = "\n***\n"
        output += "Interaction Lengths: "+str(self.interaction_lengths)
        output += "\n***\n"
        headers_str = format_str.format(*headers)
        output += "\n"+hr+"\n"+headers_str+"\n"+hr+"\n"
        for bot in sorted_bots:
            t_id = bot.tournament_id
            name = self.get_name_by_id(t_id)
            score = self.get_score_by_id(t_id)
            avg = self.get_avg_score_by_id(t_id)
            row = format_str.format(str(t_id), name, str(score), avg)
            output += row+"\n"
        return output


    ## TODO: make pretty printing for interactions


    #####
    # Initialization calculation methods
    #####

    def score_turn(self, actions):
        """
        Get the scores for each bot for a single turn

        ARGS:
        - actions: tuple (bot1_move, bot2_move)

        RETURNS:
        - scores: the score for each bot (bot1_score, bot2_score)
        """
        scores = -1

        if actions[0] == 'C':
            if actions[1] == 'C':
                scores = (self.payoffs['R'], self.payoffs['R'])
            elif actions[1] == 'D':
                scores = (self.payoffs['S'], self.payoffs['T'])
            else:
                print("actions[1] is not a valid move, must be 'C' or 'D'")
                return -1
        elif actions[0] == 'D':
            if actions[1] == 'C':
                scores = (self.payoffs['T'], self.payoffs['S'])
            elif actions[1] == 'D':
                scores = (self.payoffs['P'], self.payoffs['P'])
            else:
                print("actions[1] is not a valid move, must be 'C' or 'D'")
                return -1
        else:
            print("actions[0] is not a valid move, must be 'C' or 'D'")
            return -1

        return scores

    def calculate_scores(self):
        """
        Get the scores for each bot pair meetings list and store in
        self.interaction_scores. Tally up the total score for each bot and store
        in self.bot_info_by_id['total']
        """
        for bot_pair in self.interactions:
            self.interaction_scores[bot_pair] = []
            for meeting in self.interactions[bot_pair]:
                meeting_scores = [0, 0]
                for turn in meeting:
                    turn_scores = self.score_turn(turn)
                    # accumulate scores for meeting
                    meeting_scores[0] += turn_scores[0]
                    meeting_scores[1] += turn_scores[1]
                meeting_scores = tuple(meeting_scores)
                # add scores for meeting to list of meeting scores for this pair
                self.interaction_scores[bot_pair].append(meeting_scores)
                # also add to total for each bot, but only once if this is a bot
                # paired with its clone
                if bot_pair[0] == bot_pair[1]:
                    self.bot_info_by_id[bot_pair[0]]['total']\
                     += meeting_scores[0]
                else:
                    for idx, bot_id in enumerate(bot_pair):
                        self.bot_info_by_id[bot_id]['total']\
                         += meeting_scores[idx]


    #####
    # Getter methods
    #####

    def get_name_by_id(self, t_id):
        return self.bot_info_by_id[t_id]['name']

    def get_description_by_id(self, t_id):
        return self.bot_info_by_id[t_id]['description']

    def get_score_by_id(self, t_id):
        return self.bot_info_by_id[t_id]['total']

    def get_avg_score_by_id(self, t_id):
        return self.get_score_by_id(t_id)/self.total_interactions

    def get_winning_id(self):
        id_list = [bot.tournament_id for bot in self.botList]
        return max(id_list, key=self.get_score_by_id)

    def get_winning_name(self):
        return self.get_name_by_id(self.get_winning_id())

    def get_interaction_score(self, id_1, id_2, meeting):
        return self.interaction_scores[(id_1, id_2)][meeting]

    def get_interaction_scores(self, id_1, id_2):
        return self.interaction_scores[(id_1, id_2)]

    def get_interaction(self, id_1, id_2, meeting):
        return self.interactions[(id_1, id_2)][meeting]

    def get_interactions(self, id_1, id_2):
        return self.interactions[(id_1, id_2)]

    def get_bot_list(self):
        return self.botList

    def get_sorted_bot_list(self):
        def get_score(bot):
            return self.get_score_by_id(bot.tournament_id)
        return sorted(self.botList, key=get_score, reverse=True)


if __name__ == "__main__":
    pass
