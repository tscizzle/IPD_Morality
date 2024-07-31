########
##
## Make various morality related calculations on the results of an IPD
## tournament
##
########


import copy
import numpy as np


class MoralityCalculator(object):
    """
    Wraps up morality functions and calculations
    """
    def __init__(self, tourney_res):
        """
        Calculate the cooperation matrix of the given tournament results

        ARGS:
        - tourney_res: TournamentResults object holding the results of the
        tournament to be morally analyzed
        """
        self.tourney_res = tourney_res

        self.cooperation_matrix = None
        self.bigger_man_scores = None
        self.cooperation_rates = None
        self.calculate_cooperation_stuff()


        self.eigenjesus_scores = None
        self.eigenmoses_scores = None
        self.calculate_network_morality()

    def __str__(self):
        # get the bots in order of their score
        sorted_bots = self.tourney_res.get_sorted_bot_list()

        headers = [
            "Tournament ID",
            "Bot Name",
            "Cooperation Rate",
            "Not Worse Partner",
            "Recursive Jesus",
            "Recursive Moses"
        ]
        num_cols = len(headers)

        # find a good column width to use for formatting the output
        long_header = max([len(h) for h in headers])
        long_name = max(
            [len(bot.name) for bot in self.tourney_res.get_bot_list()]
        )+1
        col = max([long_header, long_name])
        col_str = str(col)
        format_str = (("{: <"+col_str+"} ")*num_cols)[:-1]
        hr = "-"*(num_cols*col)

        # construct output string
        headers_str = format_str.format(*headers)
        output = "\n"+hr+"\n"+headers_str+"\n"+hr+"\n"
        for bot in sorted_bots:
            t_id = bot.tournament_id
            name = self.tourney_res.get_name_by_id(t_id)
            coop_rate = self.cooperation_rates[t_id]
            big_man_score = self.bigger_man_scores[t_id]
            eigenjesus = self.eigenjesus_scores[t_id]
            eigenmoses = self.eigenmoses_scores[t_id]
            row = format_str.format(str(t_id), name,\
             str(coop_rate), str(big_man_score),
             str(eigenjesus), eigenmoses)
            output += row+"\n"
        return output


    #####
    # Initialization calculation methods
    #####

    def calculate_cooperation_stuff(self):
        """
        Calculate the cooperation rate for each bot in each bot pair and store
        these in an instance variable

        STORES:
        - cooperation_matrix: numpy array, cooperation_matrix[i][j] is i's
        cooperation rate when partnered with j
        - bigger_man_scores: a bot's bigger_man_score is the fraction of
        partnerships in which that bot cooperated at least as much as its
        partner
        - cooperation_rates: the fraction of each bot's total moves that are
        cooperations
        """
        tr = self.tourney_res
        bot_list = tr.get_bot_list()
        bot_id_list = [bot.tournament_id for bot in bot_list]
        num_bots = len(bot_list)
        coop_matrix = [[0 for _ in xrange(num_bots)] for _ in xrange(num_bots)]
        big_man_scores = {}
        for bot_id in bot_id_list:
            big_man_scores[bot_id] = 0.0
        coop_rates = {}
        # for each bot pair, count the times each bot cooperates and divide by
        # the total number of turns, and store this rate in coop_matrix
        for i in xrange(num_bots):
            bot1_id = bot_list[i].tournament_id
            for j in xrange(i, num_bots):
                bot2_id = bot_list[j].tournament_id
                interactions = tr.get_interactions(bot1_id, bot2_id)
                total_turns = sum([len(meeting) for meeting in interactions])
                bot1_coops, bot2_coops = 0.0, 0.0
                for meeting in interactions:
                    for turn in meeting:
                        if turn[0] == 'C':
                            bot1_coops += 1.0
                        if turn[1] == 'C':
                            bot2_coops += 1.0
                bot1_rate = bot1_coops/total_turns
                bot2_rate = bot2_coops/total_turns
                coop_matrix[bot1_id][bot2_id] = bot1_rate
                coop_matrix[bot2_id][bot1_id] = bot2_rate
                # don't include the case where a bot partners with its own clone
                if bot1_id != bot2_id:
                    if bot1_rate >= bot2_rate:
                        big_man_scores[bot1_id] += 1.0
                    if bot2_rate >= bot1_rate:
                        big_man_scores[bot2_id] += 1.0
        for i in xrange(num_bots):
            bot_id = bot_list[i].tournament_id
            bot_coop_rates = coop_matrix[bot_id]
            coop_rates[bot_id] = sum(bot_coop_rates)/len(bot_coop_rates)
            big_man_scores[bot_id] = big_man_scores[bot_id]/(num_bots-1)
        # save these cooperation rates per interaction and the overall
        # cooperation rate for each bot
        self.cooperation_matrix = np.array(coop_matrix)
        self.bigger_man_scores = big_man_scores
        self.cooperation_rates = coop_rates

    def principal_eigenvector(self, C, iters):
        """
        Starts with every node at a constant amount of 'worth' and iterates
        using C to update every node's 'worth' until converging on the principal
        eigenvector

        ARGS:
        - C: C is a numpy array in [0, 1]^(nxn) where values represent the
        'votes' between nodes like in PageRank

        RETURNS:
        - pev: pev is the principal eigenvector of C, representing the end
        values of each node. normalize to add to n
        """
        num_vals = len(C)
        current_vals = np.array([1 for _ in xrange(num_vals)])
        i = 0
        while i < iters:
            current_vals = C.dot(current_vals)
            i += 1
        total_val = float(sum(current_vals))
        pev = copy.copy(current_vals)
        for idx, v in enumerate(current_vals):
            try:
                pev[idx] = (num_vals/total_val)*v
            except ZeroDivisionError:
                pev[idx] = 1
        return pev

    def calculate_network_morality(self):
        """
        Calculate and store the morality metrics of network jesus and network
        moses for each bot

        ARGS:
        - coop_matrix: numpy array, coop_matrix[i][j] is i's cooperation rate
        when partnered with j

        STORES:
        - eigenjesus_scores: list of recursively defined morality scores
        (cooperating with cooperaters is worth more), cooperating always helps
        - eigenmoses_scores: list of recursively defined morality scores
        (cooperating with cooperaters is worth more), cooperating with a
        defector actually counts against you
        """
        ## TODO: come up with programmtic way of determining number of iters
        self.eigenjesus_scores =\
         self.principal_eigenvector(self.cooperation_matrix, 100)
        coop_def_matrix = (self.cooperation_matrix-0.5)*2
        self.eigenmoses_scores =\
         self.principal_eigenvector(coop_def_matrix, 100)


    ## TODO: design and implement more morality metrics


    #####
    # Getter methods
    #####

    def get_coop_rate_by_id(self, bot_id):
        return self.cooperation_rates[bot_id]

    def get_good_partner_by_id(self, bot_id):
        return self.bigger_man_scores[bot_id]

    def get_eigenjesus_by_id(self, bot_id):
        return self.eigenjesus_scores[bot_id]

    def get_eigenmoses_by_id(self, bot_id):
        return self.eigenmoses_scores[bot_id]

    def get_bots_sorted_by_coop_rate(self):
        bot_list = self.tourney_res.botList
        def get_coop_rate(bot):
            return self.get_coop_rate_by_id(bot.tournament_id)
        return sorted(bot_list, key=get_coop_rate, reverse=True)

    def get_bots_sorted_by_good_partner(self):
        bot_list = self.tourney_res.botList
        def get_good_partner(bot):
            return self.get_good_partner_by_id(bot.tournament_id)
        return sorted(bot_list, key=get_good_partner, reverse=True)

    def get_bots_sorted_by_eigenjesus(self):
        bot_list = self.tourney_res.botList
        def get_eigenjesus(bot):
            return self.get_eigenjesus_by_id(bot.tournament_id)
        return sorted(bot_list, key=get_eigenjesus, reverse=True)

    def get_bots_sorted_by_eigenmoses(self):
        bot_list = self.tourney_res.botList
        def get_eigenmoses(bot):
            return self.get_eigenmoses_by_id(bot.tournament_id)
        return sorted(bot_list, key=get_eigenmoses, reverse=True)


if __name__ == "__main__":
    pass
