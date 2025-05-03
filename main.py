from copy import deepcopy
from enum import Enum
from json import dumps

from selenium import webdriver
from selenium.webdriver import ActionChains
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

board_state = {}
cards = {}

driver = None
board_elements = {key: None for key in board.keys()}


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


def set_up_board_elements():
    global board_elements

    board_elements["stock"] = driver.find_element(by=By.CSS_SELECTOR, value=STOCK)
    board_elements["waste"] = driver.find_element(by=By.CSS_SELECTOR, value=WASTE)
    (
        board_elements["foundation_1"],
        board_elements["foundation_2"],
        board_elements["foundation_3"],
        board_elements["foundation_4"],
    ) = driver.find_elements(by=By.CSS_SELECTOR, value=FOUND_CLASS)
    (
        board_elements["tableau_1"],
        board_elements["tableau_2"],
        board_elements["tableau_3"],
        board_elements["tableau_4"],
        board_elements["tableau_5"],
        board_elements["tableau_6"],
        board_elements["tableau_7"],
    ) = driver.find_elements(by=By.CSS_SELECTOR, value=COLS)


def driver_setup() -> webdriver:
    global driver
    driver = webdriver.Firefox()
    driver.implicitly_wait(0.5)


def get_board_state(driver) -> dict:
    # get a fresh copy of the blank board
    global board_state
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


def get_tableau_elements(tableau_num):
    pass


def check_loc_empty(loc):
    return not board_state[loc]


def check_tableau_empty(tableau_num):
    tab_str = f"tableau_{tableau_num}"
    return check_loc_empty(tab_str)


def check_foundation_empty(foundation_num):
    found_str = f"foundation_{foundation_num}"
    return check_loc_empty(found_str)


def check_tableaus_empty() -> list[bool]:
    tableaus = range(1, 8)
    return [check_tableau_empty(tableau_num) for tableau_num in tableaus]


def check_foundations_empty() -> list[bool]:
    foundations = range(1, 5)
    return [check_foundation_empty(foundation_num) for foundation_num in foundations]


def check_foundation_movement_possible(card, dest):
    pass


def check_card_movement_possible(card: list[int], dest: str):
    return True
    suit = card[0]
    rank = card[1]

    # if Ace
    if rank == 1:
        if "foundation" in dest and check_loc_empty(dest):
            return True
        return False

    if rank == 13:
        if "tableau" in dest and check_loc_empty(dest):
            return True

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


def get_all_possible_actions() -> list:
    pass


def get_card_actions(card) -> list:
    """iterate through all the locations in the board state and see where this one card can go
    locations are all the tableaus and foundations

    Parameters
    ----------
    board_state : _type_
        _description_
    card : _type_
        _description_

    Returns
    -------
    list
        list of actions that can be taken, ideally in the format of "move card here" (i.e. [card, dest])
    """
    pass


def move_card(card, dest):
    if not check_card_movement_possible(card, dest):
        return False

    card_name = get_card_name_by_value(*card)
    card_elem = driver.find_element(by=By.CSS_SELECTOR, value=f"#{card_name}")
    dest_elem = board_elements[dest]

    print(f"Moving Card '{card_name}' to '{dest}'")

    ActionChains(driver).drag_and_drop(card_elem, dest_elem).perform()
    return True


def main():
    set_up_cards()
    driver_setup()
    global board_state

    driver.get("https://freesolitaire.win/turn-one#148042")
    set_up_board_elements()

    board_state = get_board_state(driver)
    print(dumps(board_state, indent=2))

    print(check_foundations_empty())
    print(check_tableaus_empty())

    move_card([2, 8], "tableau_7")

    # stock.click()
    # print("-" * 40)

    # board_state = get_board_state(driver)
    # print(dumps(board_state, indent=2))

    # x = input("Press Enter to check next board state")

    # board_state = get_board_state(driver)
    # print(dumps(board_state, indent=2))
    # print(get_card_color(board_state["tableau_6"][-1][0]))
    # print(get_card_color(board_state["tableau_7"][-1][0]))

    x = input("Press Enter to exit")

    driver.quit()


if __name__ == "__main__":
    main()
