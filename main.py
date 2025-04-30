from copy import deepcopy
from enum import Enum
from json import dumps

from selenium import webdriver
from selenium.webdriver.common.by import By

DEAL = 148042
MODE = "turn-one"
SOLITAIRE_LINK = f"https://freesolitaire.win/{MODE}#{DEAL}"

STOCK = "#stock"
WASTE = "#waste"
FOUND_CLASS = "#foundations .pile"
COLS = "#tableau .pile"


# unsure if this is useful, at least it can be a reference
class Suit(Enum):
    UNKNOWN = 0
    SPADE = 1
    HEART = 2
    CLUB = 3
    DIAMOND = 4


board = {
    "stock": True,  # whether or not there's a card
    "waste": None,  # what card is here?
    "foundation_1": [],  # Piles for cards to be in
    "foundation_2": [],  # Piles for cards to be in
    "foundation_3": [],  # Piles for cards to be in
    "foundation_4": [],  # Piles for cards to be in
    "tableau_1": [],  # Piles for cards to be in
    "tableau_2": [],  # Piles for cards to be in
    "tableau_3": [],  # Piles for cards to be in
    "tableau_4": [],  # Piles for cards to be in
    "tableau_5": [],  # Piles for cards to be in
    "tableau_6": [],  # Piles for cards to be in
    "tableau_7": [],  # Piles for cards to be in
}

cards = {}


def get_card_name_by_value(suit, rank):
    for key, val in cards.items():
        if val == [suit, rank]:
            return key
    return None


# this follows freesolitaire.win's setup
def set_up_cards():
    iter = 0
    for rank in range(1, 14):
        for suit in range(1, 5):
            cards[f"card{iter}"] = [suit, rank]
            iter += 1


def driver_setup() -> webdriver:
    driver = webdriver.Firefox()
    driver.implicitly_wait(0.5)
    return driver


def get_board_state(driver) -> dict:
    # get a fresh copy of the blank board
    board_state = deepcopy(board)

    # get stock state
    # true if there's something in the stock, otherwise false
    stock = driver.find_element(by=By.CSS_SELECTOR, value=STOCK)
    stock_elems = stock.find_elements(by=By.CSS_SELECTOR, value=".card")
    board_state["stock"] = (
        True if stock_elems else False
    )  # probably a better way of doing this

    # get waste state
    # stock = [suit, rank] if there's a card, else None
    waste = driver.find_element(by=By.CSS_SELECTOR, value=WASTE)
    waste_elems = waste.find_elements(by=By.CSS_SELECTOR, value=".card")

    board_state["waste"] = (
        cards[waste_elems[-1].get_property("id")] if waste_elems else None
    )  # probably a better way of doing this

    # get foundation states
    # foundation is a list of objects
    # those objects are "card" if they're not visible, else [suit, rank]
    foundations = driver.find_elements(by=By.CSS_SELECTOR, value=FOUND_CLASS)
    for foundation_i, foundation in enumerate(foundations):
        f_cards = foundation.find_elements(by=By.CSS_SELECTOR, value=".card")
        current_foundation = f"foundation_{foundation_i + 1}"

        for card in f_cards:
            visible = "card_visible" in card.get_attribute("class")
            id = card.get_property("id")
            card_slot = cards[id] if visible else "card"
            board_state[current_foundation].append(card_slot)

    # get tableau states
    # foundation is a list of objects
    # those objects are "card" if they're not visible, else [suit, rank]
    tableaus = driver.find_elements(by=By.CSS_SELECTOR, value=COLS)
    for tableau_i, tableau in enumerate(tableaus):
        t_cards = tableau.find_elements(by=By.CSS_SELECTOR, value=".card")
        current_tableau = f"tableau_{tableau_i + 1}"

        for card in t_cards:
            visible = "card_visible" in card.get_attribute("class")
            id = card.get_property("id")
            card_slot = cards[id] if visible else "card"
            board_state[current_tableau].append(card_slot)

    return board_state


def draw_from_stock(stock):
    stock.click()


def check_foundation_empty(foundation_num):
    pass


def get_tableau_elements(tableau_num):
    pass


def check_tableaus_empty() -> list[bool]:
    tableaus = range(1, 5)
    return [check_tableau_empty(tableau_num) for tableau_num in tableaus]


def check_tableau_empty(tableau_num):
    board
    pass


def get_card_color(suit: int) -> str:
    """
    Get the rank of the given card object. Returns "unknown" if unknown.
    """

    if suit <= 0:
        return "unknown"
    return "black" if suit % 2 else "red"


def get_rank_of_card(card_list: list) -> int:
    """
    Get the rank of the given card object. Returns 0 if unknown.
    """
    if type(card_list) is str:
        return 0
    return card_list[1]


def get_suit_of_card(card_list: list) -> int:
    """
    Get the suit of the given card object. Returns 0 if unknown.
    """
    if type(card_list) is str:
        return 0
    return card_list[0]


def get_all_possible_actions(board_state) -> list:
    pass


def get_card_actions(board_state, card) -> list:
    """iterate through all the cards in the board state and see where this one card can go

    Parameters
    ----------
    board_state : _type_
        _description_
    card : _type_
        _description_

    Returns
    -------
    list
        list of actions that can be taken, ideally in the format of "move card here"
    """
    pass


def main():
    set_up_cards()
    driver = driver_setup()

    driver.get("https://freesolitaire.win/turn-one#148042")

    stock = driver.find_element(by=By.CSS_SELECTOR, value=STOCK)
    waste = driver.find_element(by=By.CSS_SELECTOR, value=WASTE)
    foundation1, foundation2, foundation3, foundation4 = driver.find_elements(
        by=By.CSS_SELECTOR, value=FOUND_CLASS
    )
    (
        tableau1,
        tableau2,
        tableau3,
        tableau4,
        tableau5,
        tableau6,
        tableau7,
    ) = driver.find_elements(by=By.CSS_SELECTOR, value=COLS)

    board_state = get_board_state(driver)
    print(dumps(board_state, indent=2))

    # stock.click()
    # print("-" * 40)

    # board_state = get_board_state(driver)
    # print(dumps(board_state, indent=2))

    # x = input("Press Enter to check next board state")

    # board_state = get_board_state(driver)
    # print(dumps(board_state, indent=2))
    print(get_card_color(board_state["tableau_6"][-1][0]))
    print(get_card_color(board_state["tableau_7"][-1][0]))

    x = input("Press Enter to exit")

    driver.quit()


if __name__ == "__main__":
    main()
