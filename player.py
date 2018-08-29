
import watchdog

from kustom.cards import deck

class Player() :

    pass

class Hand() :
    """ The cards a player holds in his hand. Takes care of the actions a 
    player can take, like playing cards and combinations, passing, drawing 
    cards, etc. 
    """
    def __init__(self, cards) :
        """ 
        =====  =================================================================
        cards  list of :class: `Card <cards.deck.Card>` objects.
        =====  =================================================================
        """
        self.cards = cards

    def play(self, indices) :
        """ Play the combination of cards defined by the given *indices*.

        =======  ===============================================================
        indices  list of int; the indices of the cards to play as they appear 
                 in *self.cards*
        =======  ===============================================================
        """
        cards = [self.cards[i] for i in indices]
        combination = Combination(cards)

