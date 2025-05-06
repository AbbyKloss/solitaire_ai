from copy import deepcopy
from enum import Enum
from json import dumps
from sys import exit

from selenium import webdriver
from selenium.common.exceptions import NoSuchDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

DEAL = 148042
# DEAL = 131986
# DEAL = 124149

MODE = "turn-one"
SOLITAIRE_LINK = f"https://freesolitaire.win/{MODE}"  # #{DEAL}"

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


# A dictionary representation of a blank board state
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

# global elements to be used in other functions
board_state = {}
cards = {}
driver = None
board_elements = {key: None for key in board.keys()}


def get_card_name_by_value(suit: int, rank: int) -> str | None:
    """Generates the freesolitaire.win card name for the given suit and rank

    Parameters
    ----------
    suit : int
        The suit of the card. Typically the first object in the card list object
    rank : int
        The rank of the card. Should be the second/last object in the card list object

    Returns
    -------
    str or None
        Valid card name if there is one, otherwise returns None
    """
    for key, val in cards.items():
        if val == [suit, rank]:
            return key
    return None


# this follows freesolitaire.win's setup
def set_up_cards():
    """Initializes the global cards"""
    iter = 0
    for rank in range(1, 14):
        for suit in range(1, 5):
            cards[f"card{iter}"] = [suit, rank]
            iter += 1


def set_up_board_elements():
    """Initializes the global board elements"""
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


def driver_setup():
    """initializes the global driver"""
    global driver
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    driver.implicitly_wait(0.5)
    driver.get(SOLITAIRE_LINK)


def get_board_state():
    """Sets the global board state based on information from the global driver"""
    global driver
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


def draw_from_stock():
    """Clicks the stock element"""
    stock = board_elements["stock"]
    stock.click()


def check_loc_empty(loc: str) -> bool:
    """Checks whether or not the given location is empty

    Parameters
    ----------
    loc : string
        String representation of the location, as described in `board_state` or `board`

    Returns
    -------
    bool
        True if empty, else False
    """
    return not board_state[loc]


def check_tableau_empty(tableau_num: int) -> bool:
    """Checks whether or not the given tableau is empty

    Parameters
    ----------
    loc : string
        String representation of the tableau, as described in `board_state` or `board`

    Returns
    -------
    bool
        True if empty, else False
    """

    tab_str = f"tableau_{tableau_num}"
    return check_loc_empty(tab_str)


def check_foundation_empty(foundation_num: int) -> bool:
    """Checks whether or not the given tableau is empty

    Parameters
    ----------
    loc : string
        String representation of the tableau, as described in `board_state` or `board`

    Returns
    -------
    bool
        True if empty, else False
    """
    found_str = f"foundation_{foundation_num}"
    return check_loc_empty(found_str)


def check_tableaus_empty() -> list[bool]:
    """Checks whether or not each tableau is empty

    Returns
    -------
    list[bool]
        List of booleans, which are True if empty, else False. List is in order of the tableaus from left to right
    """
    tableaus = range(1, 8)
    return [check_tableau_empty(tableau_num) for tableau_num in tableaus]


def check_foundations_empty() -> list[bool]:
    """Checks whether or not each foundation is empty

    Returns
    -------
    list[bool]
        List of booleans, which are True if empty, else False. List is in order of the foundations from left to right
    """
    foundations = range(1, 5)
    return [check_foundation_empty(foundation_num) for foundation_num in foundations]


def check_foundation_movement_possible(card: list[int], dest: str) -> bool:
    """Checks to see if movement of a card to the given foundation is possible

    Parameters
    ----------
    card : list[int]
        Card representation (i.e. [suit, rank])
    dest : str
        String representation of the desired foundation (i.e. "foundation_x")

    Returns
    -------
    bool
        True if possible, else False
    """
    if card == "card":
        return False
    suit = card[0]
    rank = card[1]

    # if Ace
    if rank == 1:
        return check_loc_empty(dest)

    if check_loc_empty(dest):
        return False

    dest_card = board_state[dest][-1]

    dst_suit = dest_card[0]
    dst_rank = dest_card[1]

    return suit == dst_suit and dst_rank == rank - 1


def check_tableau_movement_possible(card: list[int], dest: str):
    """Checks to see if movement of a card to the given tableau is possible

    Parameters
    ----------
    card : list[int]
        Card representation (i.e. [suit, rank])
    dest : str
        String representation of the desired tableau (i.e. "tableau_x")

    Returns
    -------
    bool
        True if possible, else False
    """
    if card == "card":
        return False

    suit = card[0]
    rank = card[1]

    # if King
    if rank == 13:
        return check_loc_empty(dest)

    if check_loc_empty(dest):
        return False

    dst_card = board_state[dest][-1]

    dst_suit = dst_card[0]
    dst_rank = dst_card[1]

    src_col = get_card_color(suit)
    dst_col = get_card_color(dst_suit)

    return src_col != dst_col and dst_rank == rank + 1


def check_card_movement_possible(card: list[int], dest: str):
    """Checks to see if movement of a card to the given location is possible

    Parameters
    ----------
    card : list[int]
        Card representation (i.e. [suit, rank])
    dest : str
        String representation of the desired location (i.e. "location_x")

    Returns
    -------
    bool
        True if possible, else False
    """

    if "foundation" in dest:
        return check_foundation_movement_possible(card, dest)

    return check_tableau_movement_possible(card, dest)


def get_card_color(suit: int) -> str:
    """Get the rank of the given card object. Returns "unknown" if unknown.

    Parameters
    ----------
    suit : int
        Representation of the given card's suit. See the Suit class as a reference.

    Returns
    -------
    str
        "black", "red", or "unknown"
    """

    if suit <= 0:
        return "unknown"
    return "black" if suit % 2 else "red"


# I don't use these next two super often. I should.
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


def get_src_cards(src_loc: str) -> list[int]:
    """gets the list of cards in the board state at the source location (src_loc)

    Parameters
    ----------
    src_loc : string
        A location a card can reasonably be taken from within the board state object

    Returns
    -------
    list[list[int]]
        The list of cards. Can be an empty list.

    """

    bs_loc = board_state[src_loc]
    if bs_loc == None or not bs_loc:
        return []

    if src_loc == "waste":
        return [bs_loc]

    return bs_loc


def get_all_possible_actions() -> [list, list]:
    """Gets a list of all possible actions.

    Returns
    -------
    list
        List contains all possible actions in the format of [[source_card, dest], ..., "stock"]
    """
    src_locations = [
        "waste",
        "tableau_1",
        "tableau_2",
        "tableau_3",
        "tableau_4",
        "tableau_5",
        "tableau_6",
        "tableau_7",
    ]

    dst_locations = [
        "foundation_1",
        "foundation_2",
        "foundation_3",
        "foundation_4",
        "tableau_1",
        "tableau_2",
        "tableau_3",
        "tableau_4",
        "tableau_5",
        "tableau_6",
        "tableau_7",
    ]

    ret_obj = []
    #source and destination decide proper order of moves
    source_dest_obj = []

    for src_loc in src_locations:
        cards = get_src_cards(src_loc)
        print("cards: ", end="")
        print(cards)

        for card in cards:
            if card is None:
                continue

            for dst_loc in dst_locations:
                if check_card_movement_possible(card, dst_loc):
                    ret_obj.append([card, dst_loc])
                    source_dest_obj.append({"card_value":card[1], "source":src_loc, "card_pos":cards.index(card),
                                            "destination":dst_loc})
                    print(source_dest_obj)

    if STOCK:
        ret_obj.append("stock")
        source_dest_obj.append({"card_value":"card", "source":"stock", "card_pos":-1, "destination":"waste"})

    return ret_obj, source_dest_obj


def perform_action(action: list[int, str] | str) -> None:
    """Performs the given action.

    Parameters
    ----------
    action : list[int, str] | str
        Action to be performed. Either a representation of a card and a destination to move it to or "stock".
    """
    if action == "stock":
        return draw_from_stock()

    move_card(*action)


def move_card(card, dest) -> bool:
    """Moves the given card to the given destination.

    Parameters
    ----------
    card : list[int, int]
        Representation of a card
    dest : str
        Representation of a location within the `board_state` object

    Returns
    -------
    bool
        Whether or not the given movement was possible within solitaire rules.
    """
    if not check_card_movement_possible(card, dest):
        return False

    card_name = get_card_name_by_value(*card)
    card_elem = driver.find_element(by=By.CSS_SELECTOR, value=f"#{card_name}")
    dest_elem = board_elements[dest]

    print(f"Moving Card '{card_name}' to '{dest}'")

    # ActionChains(driver).drag_and_drop(card_elem, dest_elem).perform()
    ActionChains(driver).move_to_element_with_offset(
        card_elem, xoffset=0, yoffset=-55
    ).click_and_hold().move_to_element(dest_elem).release().perform()
    return True

def get_foundation_lengths():
    foundations = ["foundation_1", "foundation_2", "foundation_3", "foundation_4"]
    length_list = []
    for foundation in foundations:
        length = len(get_src_cards(foundation))
        length_list.append(length)
    return length_list

def get_num_unknowns(location):
    cards = get_src_cards(location)
    unknown_count = 0
    for card in cards:
        if card == "card":
            unknown_count += 1
    return unknown_count

def check_if_king_available(action_info_list):
    check = False
    for action_dict in action_info_list:
        #print(action_dict)
        if action_dict["card_value"] == 13:
            check = True
    return check

def move_ranker(action_info_list):
    #lower ranks are better
    foundation_sizes = get_foundation_lengths()
    foundation_avg = sum(foundation_sizes)/4
    king_check = check_if_king_available(action_info_list)
    best_move = {"index":999, "rank":999} #placeholder
    i = 0
    for action_dict in action_info_list:
        if action_dict["source"] == "stock":
            rank = 5
        elif "foundation" in action_dict["destination"]:
            if len(get_src_cards(action_dict["destination"])) < foundation_avg+2:
                rank = 1
            elif king_check and "tableau" in action_dict["source"]:
                rank = 3.75
            else:
                if action_dict["card_pos"] > 0: #if the move will reveal a card
                    rank = 2.5
                else:
                    rank = 4.5
        elif "tableau" in action_dict["source"] and "tableau" in action_dict["destination"]:
            if get_num_unknowns(action_dict["source"]) > get_num_unknowns(action_dict["destination"]):
                rank = 2
            elif king_check:
                if action_dict["card_value"] == 13: #moves king to empty foundation
                    rank = 3
                if action_dict["card_pos"] == 0: #moves anything that will empty a foundation
                    rank = 3.5
            else:
                rank = 6
        elif action_dict["source"] == "waste" and "tableau" in action_dict["destination"]:
            rank = 4
        else:
            print(f"ERROR: UNRANKABLE ACTION: {action_dict}")
        if rank < best_move["rank"]:
            best_move = {"index":i,"rank":rank}

        i += 1

    return best_move["index"]

def main():
    """Main function, plays solitaire"""
    set_up_cards()
    driver_setup()
    global board_state

    driver.get("https://freesolitaire.win/turn-one#148042")
    set_up_board_elements()

    while True:
        get_board_state()
        actions, action_info_dict = get_all_possible_actions()
        print("actions:", end="")
        print(actions)
        #pause = input("input anything to continue")
        if not actions:
            break
        best_action_index = move_ranker(action_info_dict)
        print(f"Best Action: {action_info_dict[best_action_index]}")
        perform_action(actions[best_action_index])

    x = input("Press Enter to exit")

    driver.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        driver.quit()
        raise e
