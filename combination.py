"""
In Tichu, one usually does not play single cards but rather combinations of 
several cards. These are:
    
    - single cards
    - pairs
    - three of a kind (triplets)
    - full houses (three of a kind + a pair)
    - straights (sequence of at least 5 consecutive cards)
    - straights of pairs (sequence of at least 2 consecutive pairs)
    - four of a kind (bomb)
    - straights of one suit (straight bomb)

These combinations are implemeneted in this submodule.
"""

from kustom.cards.deck import Card, tichu_deck

# Define some special cards for comparisons
Dog = Card(rank=0, suit='Special', name='Dog', shortname='Dog')
Mahjongg = Card(rank=1, suit='Special', name='Mahjongg')
Phoenix = Card(rank=14.5, suit='Special', name='Phoenix')
Dragon = Card(rank=15, suit='Special', name='Dragon', shortname='Dragon')

class Combination() :

    # The names of the possible combinations here must match the respective 
    # methods `is_xxx`!
    combinations = ['single', 'pair', 'triplet', 'straight', 'full_house', 
                    'straight_of_pairs', 'bomb', 'straight_bomb']

    with_phoenix = False

    def __init__(self, cards) :
        """ 
        =====  =================================================================
        cards  list of :class: `Card <cards.deck.Card>` objects.
        =====  =================================================================
        """
        self.cards = cards
        # The number of cards is frequently used in determining the combo 
        # type, so a shorthand is useful
        self.N = len(self.cards)
        # Same argument for the list of ranks
        self.ranks = [card.rank for card in self.cards]
        if Phoenix in self :
            self.ranks.remove(Phoenix.rank)
            self.with_phoenix = True

        self.determine_combination()

    def __iter__(self) :
        """ Iterate over the cards in this combo. """
        return (card for card in self.cards)

    def __str__(self) :
        res = '<Combination> {}: '.format(self.combo_type)
        for card in self.cards :
            res += '{}, '.format(card)
        return res

    def __repr__(self) :
        return self.__str__()

    def determine_combination(self) :
        """ Go through all possible combinations and verify whether these 
        cards fulfill the requirements for one them.
        """
        # Call all functions that go by the name `is_xxx` where `xxx` is a 
        # name of a possible combination
        combo_determined = False
        for combination in self.combinations :
            fcn_name = 'is_{}'.format(combination)
            is_this_combo = self.__getattribute__(fcn_name)()
            # Set the combination type and rank, if a match was found
            # (The rank is set in the `is_xxx` functions since it differs 
            # slightly for different combinations)
            if is_this_combo :
                # Special case for straights
                if 'straight' in combination :
                    self.combo_type = '{}-{}'.format(len(self.cards), combination)
                else :
                    self.combo_type = combination
                combo_determined = True
                break
        if not combo_determined :
            msg = 'Could not determine valid combination: '
            for card in self.cards :
                msg += '{}, '.format(card)
            raise ValueError(msg)

    def is_single(self) :
        """ All single cards are valid. """
        if self.N == 1 :
            self.rank = self.cards[0].rank
            return True
        else :
            return False

    def is_pair(self) :
        """ Two cards of the same rank qualify as a pair. """
        if not self.N == 2 : return False

        # Dogs and Dragons may not appear in a pair (due to the phoenix they 
        # would be playable)
        if Dog in self or Dragon in self : return False

        return self.have_equal_ranks()
        
    def is_triplet(self) :
        """ Three cards of the same rank. """
        if not self.N == 3 : return False

        return self.have_equal_ranks()

    def is_straight(self) :
        """ 5 or more consecutive cards of non-equal suit (equal suits is a 
        straight bomb).
        """
        if not self.are_subsequent_singles() : return False
        if not self.are_same_suit() : return True
        return False

    def are_subsequent_singles(self) :
        """ Test if *self.cards* consist of at least 5 subsequent cards, 
        paying no mind to the suits.
        Also set the rank if subsequency is detected.
        """
        if self.N < 5 : return False

        # Dogs and Dragons may not appear in a straight
        if Dog in self or Dragon in self : return False

        res = self.is_subsequent_list(self.ranks, self.with_phoenix)
        if res :
            self.rank = min(self.ranks)
        return res

    def is_subsequent_list(self, my_list, with_phoenix=False) :
        """ Check whether *my_list* contains only subsequent values (or 
        maximally 1 step of 2, if *with_phoenix* is True.
        """
        # Sort the ranks and verify that they are subsequent
        ordered = sorted(my_list)
        for i in range(len(ordered) - 1) :
            delta = ordered[i+1] - ordered[i]
            if delta == 1 :
                continue
            elif delta == 2 and with_phoenix :
                # "Use" the phoenix
                with_phoenix = False
            else :
                return False

        return True

    def are_same_suit(self) :
        """ Return True if all cards in *self.cards* are of one suit. """
        suits = [card.suit for card in self]
        if len(set(suits)) == 1 :
            return True
        else :
            return False

    def is_full_house(self) :
        """ Exactly 5 cards, consisting of a triplet and a pair. """
        if self.N != 5 : return False

        # Dogs and Dragons may not appear in a full_house
        if Dog in self or Dragon in self : return False

        # Ensure that there are only 2 different ranks
        rank_set = set(self.ranks)
        if not len(rank_set) == 2 : return False

        # Determine which rank corresponds to the triplet
        for rank in rank_set :
            if self.ranks.count(rank) == 3 :
                self.rank = rank
                return True

        # With the phoenix, assume the higher cards as the triplet
        # TODO In rare cases it might make strategic sense to use the lower 
        # rank as the triplet -> user interaction
        if self.with_phoenix :
            self.rank = max(self.ranks)
            return True


    def is_straight_of_pairs(self) :
        """ At least 4 cards, where every rank has to occur exactly twice AND 
        has to be subsequent to another rank.
        """ 
        # Need at least 4 cards and it has to be an even number
        if self.N < 4 or self.N%2 : return False

        rank_set = set(self.ranks)

        # Verify that each rank appears twice, unless the phoenix is present, 
        # in which case one element may occur once
        counts = set([self.ranks.count(rank) for rank in rank_set])
        if self.with_phoenix :
            if not counts == set([1, 2]) : return False
        else :
            if not counts == set([2]) : return False

        # Check if the cards are subsequent
        res = self.is_subsequent_list(list(rank_set), self.with_phoenix)
        if res :
            self.rank = min(rank_set)
        return res

    def is_bomb(self) :
        """ Four of a kind without the help of the phoenix"""
        if not self.N == 4 : return False

        # No phoenix
        if Phoenix in self : return False

        return self.have_equal_ranks()

    def have_equal_ranks(self) :
        """ Returns True if all *self.cards* have the same rank. """
        # If all ranks are equal, the resulting set will have len(1)
        if len(set(self.ranks)) == 1 :
            self.rank = self.ranks[0]
            return True
        else :
            return False

    def is_straight_bomb(self) :
        """ Min. 5 subsequent cards of the same suit. """
        if not self.are_subsequent_singles() : return False
        if self.are_same_suit() : return True
        return False

# Testing
if __name__ == '__main__' :
    td = tichu_deck
    # Create some combinations
    full_house = [td[0], td[13], td[24], td[11], Phoenix]
    Full_house = Combination(full_house)
    print(Full_house)
    print(Full_house.rank)
 
    pair_straight = [td[1], td[2], td[14], Phoenix]
    Pair_straight = Combination(pair_straight)
    print(Pair_straight)
    print(Pair_straight.rank)

    bomb = [td[12], td[25], td[38], td[51]]
    Bomb = Combination(bomb)
    print(Bomb)
    print(Bomb.rank)

    straight_bomb5 = td[:5]
    Straight_bomb5 = Combination(straight_bomb5)
    print(Straight_bomb5)
    print(Straight_bomb5.rank)

    no_bomb = [td[12], td[25], td[38], Phoenix]
    No_bomb = Combination(no_bomb)
    print(No_bomb)
    print(No_bomb.rank)


