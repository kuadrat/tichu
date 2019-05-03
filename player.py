
import logging
#import watchdog

from combination import Combination
from kustom.cards import deck

logger = logging.getLogger('tichu.' + __name__)

class PlayerAction() :
    name = 'generic PlayerAction'

    def __str__(self) :
        return '<PlayerAction {}>'.format(self.name)

    def __repr__(self) :
        return self.__str__()

class PassAction(PlayerAction) :
    name = 'pass'

class PlayAction(PlayerAction) :
    name = 'play'
    
    def __init__(self, combination) :
        self.combination = combination

class RageQuitAction(PlayerAction) :
    """ For debug purposes. """
    name = 'ragequit'

class Player() :

    play_lock = True
    next_action = None

    def __init__(self, name) :
        self.name = name

    def draw_cards(self, deck, n=14) :
        self.hand = Hand(deck.draw(n))

    def release_play_lock(self) :
        """ Release the play_lock, allowing this player to take action. """
        self.play_lock = False

    def close_play_lock(self) :
        """ Prevent the player from doing anything by closing his play_lock. 
        """ 
        self.play_lock = True

    def pass_(self) :
        self.next_action = PassAction()

    def play(self, cards) :
        """
        =====  =================================================================
        cards  list of int or list of :class: `Card <cards.deck.Card>`s
        =====  =================================================================
        """
        if self.play_lock :
            logger.info('%s cannot play now, has play_lock.', self.name)
            return

        combination = self.hand.play(cards)
        self.next_action = PlayAction(combination)

    def ragequit(self) :
        """ For debug only. """
        self.next_action = RageQuitAction()

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

        return combination

