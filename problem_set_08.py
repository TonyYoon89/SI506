import json
from pathlib import Path

# SETUP FOR PROBLEM SET 08

rank_1_avg_test = 24.97
rank_10_avg_test = 23.96

first_doubleday_book_title_test = "LESSONS IN CHEMISTRY"
first_doubleday_book_score_test = 10

penultimate_doubleday_book_title_test = "LESSONS IN CHEMISTRY"
penultimate_doubleday_book_score_test = 10

doubleday_score_test = 105

# fmt: off
fiction_publishers_test = ["St. Martin's", 'Putnam', 'Del Rey', 'Red Tower', 'Riverhead', 'Knopf', 'Bloomsbury', 'Pamela Dorman', 'Doubleday', 'Random House', 'Ecco', 'Bramble', 'Little, Brown', 'Harper', 'Berkley', 'Celadon', 'Grand Central', 'Grove', 'Tor Nightfire', 'Ballantine', 'Tor', 'Delacorte']
# fmt: on

fiction_publishers_scoreboard_test = {
    "St. Martin's": 80,
    "Putnam": 20,
    "Del Rey": 25,
    "Red Tower": 265,
    "Riverhead": 115,
    "Knopf": 30,
    "Bloomsbury": 70,
    "Pamela Dorman": 90,
    "Doubleday": 105,
    "Random House": 5,
    "Ecco": 65,
    "Bramble": 65,
    "Little, Brown": 65,
    "Harper": 80,
    "Berkley": 10,
    "Celadon": 55,
    "Grand Central": 5,
    "Grove": 20,
    "Tor Nightfire": 10,
    "Ballantine": 5,
    "Tor": 10,
    "Delacorte": 5,
}

# PROBLEM SET 08


def clean_book(book, desired_keys=None):
    """Accepts a dictionary representation of a book. Creates an empty dictionary.
    Loops through the keys and values of < book >.

    If < desired_keys > is not None, check if each key is in < desired_keys >.
    If it is, add that key and its value to the new dictionary. At the same time,
    call < convert_to_float > to make that value a float, if possible.

    If < desired_keys > is None, add each key and its value to the new dictionary
    while calling < convert_to_float > to make that value a float, if possible.

    Parameters:
        book (dict): dictionary representation of a book on the NYT bestsellers list
        desired_keys (list): represents which keys should still be in the cleaned book dictionary

    Returns:
        dict: a new, cleaned dictionary representation of the book with only the desired
                keys and "price" now a float
    """
    cleaned_book = {}
    for key, value in book.items():
        if desired_keys is None or key in desired_keys:
            cleaned_value = convert_to_float(value) if key == "price" else value
            cleaned_book[key] = cleaned_value
    return cleaned_book


def convert_to_float(value):
    """Implements error handling to check if the passed-in value is a NON-INTEGER
    that can be converted to a float.
    If possible, the non-integer value is converted and assigned back to its
    variable.

    Parameters:
        value (any): a value that may be able to be converted to a float. In this
                        case, these are the values from a single book dictionary.
    Returns:
        value (float|any): value will be float, if possible. Otherwise it will returned unchanged.
    """
    try:
        if isinstance(value, int):
            return value
        else:
            return float(value)
    except:
        return value


def create_scoreboard(bestseller_lists):
    """Creates a new, empty dictionary. Given eight weeks of bestseller lists,
    this function calls < find_publishers > to find all unique publisher names
    from the lists. Then, using < score_publisher > assigns a "publisher name",
    "score" key-value pair to the new dictionary for each publisher. Returns the
    dictionary with publisher names and scores.

    Parameters:
        bestseller_lists (list): list of dictionaries, each dictionary represents
                                a weekly bestseller list and contains the key "books"
                                with a value that is a list of book dictionaries.

    Returns:
        dict: a "scoreboard" of each publisher that appears on the bestseller
                lists and their total scores based on the rankings of their
                books. The keys are strings of publisher's names and the
                values are integer scores.
    """
    publishers = find_publishers(bestseller_lists)
    scoreboard = {
        publisher: score_publisher(bestseller_lists, publisher)
        for publisher in publishers
    }
    return scoreboard


def find_publishers(bestseller_lists):
    """Creates a list of the unique publisher names (no repeats) that appear
    throughout the weekly bestseller lists.

    Parameters:
        bestseller_lists (list): list of dictionaries, each dictionary represents
                                a weekly bestseller list and contains the key "books"
                                with a value that is a list of book dictionaries.

    Returns:
        list: list of strings; the names of all the publishers that have at least
            one book on a bestseller list for these 8 weeks.
    """
    publishers = []
    for week in bestseller_lists:
        for book in week["books"]:
            publisher = book["publisher"]
            if (
                publisher not in publishers
            ):  # Check if the publisher is already in the list
                publishers.append(
                    publisher
                )  # Add the publisher to the list if not already included
    return publishers


def get_average_price_by_rank(bestseller_lists, rank):
    """Given a list of bestseller lists and a rank, finds the average price of
    the books of that rank over the 8 weeks of lists. Includes duplicates of
    the same book if that book ranked in the same position multiple times over
    the eight weeks.

    Parameters:
        bestseller_lists (list): list of dictionaries, each dictionary represents
                                a weekly bestseller list and contains the key "books"
                                with a value that is a list of book dictionaries.
        rank (int): an integer 1-10 representing the rank of the books of interest
                    such as No. 1 bestsellers (1) or No. 5 bestsellers (5).

    Returns:
        float: the average price (rounded to nearest cent) for all books (including
                repeats) of the given rank over the eight weeks of lists
    """

    total_price = 0.0
    for week in bestseller_lists:
        for book in week["books"]:
            if book["rank"] == rank:
                total_price += book["price"]
    return round(total_price / 8, 2)


def get_books_by_publisher(bestseller_lists, publisher):
    """Given a publisher and eight weeks of bestseller lists, finds all of the
    books published by the publisher on those eight lists and returns the books
    as a list of dictionaries. Includes repeats if a book remained on the list for
    multiple weeks.

    Parameters:
        bestseller_lists (list): list of dictionaries, each dictionary represents
                                a weekly bestseller list and contains the key "books"
                                with a value that is a list of book dictionaries.
        publisher (str): the name of a book publisher that has a book on at least one
                        of the eight weekly bestseller lists.

    Returns:
        list : list of dictionaries, each representing a book published by the given
                publisher, includes repeats if a book remained on the list for
                multiple weeks
    """
    books = []
    for week in bestseller_lists:
        for book in week["books"]:
            if book["publisher"].lower() == publisher.lower():
                books.append(book)
    return books


def score_book(book):
    """Checks the rank of a book. If the book is rank 1-5, assigns a score
    of 15. If the book rank is 6-10, assigns a score of 10. Rank 11-15, score of 5.

    Parameter:
        book (dict): dictionary representation of a book on the NYT bestsellers list

    Returns:
        int: a score of 15, 10, or 5, depending on the rank of the book.
    """
    rank = book["rank"]
    if rank <= 5:
        return 15
    elif rank <= 10:
        return 10
    else:
        return 5


def score_publisher(bestseller_lists, publisher):
    """Scores a publisher based on the rank of its books on the 8 weekly
    bestseller lists. Calls < get_books_by_publisher > to find the publisher's
    books, uses < score_book > to find the score for each book and adds that
    to the publisher score. This includes repeat books so that a publisher
    gets credit for a book remaining on the bestseller list for multiple
    weeks.

    Parameters:
        bestseller_lists (list): list of dictionaries, each dictionary represents
                                a weekly bestseller list and contains the key "books"
                                with a value that is a list of book dictionaries.
        publisher (str): the name of a book publisher that has a book on at least one
                        of the eight weekly bestseller lists.

    Returns:
        int: the total scores of all the publisher's books (including repeats) over
        the 8 weeks of bestseller lists
    """
    books = get_books_by_publisher(bestseller_lists, publisher)
    total_score = sum(score_book(book) for book in books)
    return total_score


def read_json(filepath, encoding="utf-8"):
    """Reads a JSON file and converts it to a Python dictionary.

    Parameters:
        filepath (str): a path to the JSON file
        encoding (str): name of encoding used to decode the file

    Returns:
        dict/list: dict or list representations of the decoded JSON document
    """
    with open(filepath, "r", encoding=encoding) as file_obj:
        data = json.load(file_obj)
    return data


def write_json(filepath, data, encoding="utf-8", indent=2):
    """Serializes object as JSON. Writes content to the provided filepath.

    Parameters:
        filepath (str): the path to the file

        data (dict)/(list): the data to be encoded as JSON and written to
        the file

        encoding (str): name of encoding used to encode the file

        indent (int): number of "pretty printed" indention spaces applied to
        encoded JSON

    Returns:
        None
    """

    with open(filepath, "w", encoding=encoding) as file_obj:
        json.dump(data, file_obj, indent=indent)


def main():
    """Program entry point.

    Parameters:
        None

    Returns:
        None
    """

    # PROBLEM 1
    filepath_young_adult = Path("data-young_adult_bestsellers-2024.json").resolve()

    # TODO 1.2 & 1.3
    young_adult_bestsellers = read_json(filepath_young_adult)
    young_adult_bestsellers_week_1 = young_adult_bestsellers[0]

    print(f"\nYoung Adult Bestsellers Week 1: {young_adult_bestsellers_week_1}")

    # TODO 1.4
    filepath_fiction = Path("data-fiction_bestsellers-2024.json").resolve()

    # TODO 1.5 & 1.6
    fiction_bestsellers = read_json(filepath_fiction)
    fiction_bestsellers_week_8 = fiction_bestsellers[-1]

    print(f"\nFiction Bestsellers Week 8: {fiction_bestsellers_week_8}")

    # PROBLEM 2

    assert convert_to_float("5") == 5
    assert convert_to_float("NYT Books of the Year") == "NYT Books of the Year"
    assert convert_to_float("24.57") == 24.57

    # PROBLEM 3

    keep_keys = [
        "rank",
        "rank_last_week",
        "isbns",
        "publisher",
        "description",
        "price",
        "title",
        "author",
    ]
    # TODO 3.3

    for week in young_adult_bestsellers:
        for i in range(len(week["books"])):
            week["books"][i] = clean_book(week["books"][i], desired_keys=keep_keys)

    print(f"\nCleaned Young Adult Bestsellers Week 1: {young_adult_bestsellers_week_1}")

    # TODO 3.4
    filepath = "stu-clean_young_adult_bestsellers-2024.json"
    write_json(filepath, young_adult_bestsellers)

    # PROBLEM 4

    # TODO 4.3
    rank_1_avg = get_average_price_by_rank(young_adult_bestsellers, 1)

    print(f"\nAverage Price of No. 1 Young Adult Books: ${rank_1_avg}")
    assert rank_1_avg == rank_1_avg_test

    # TODO 4.4
    rank_10_avg = get_average_price_by_rank(rank=10, bestseller_lists=young_adult_bestsellers)

    print(f"\nAverage Price of No. 10 Young Adult Books: ${rank_10_avg}")
    assert rank_10_avg == rank_10_avg_test

    # PROBLEM 5

    # TODO 5.3
    doubleday_books = get_books_by_publisher(fiction_bestsellers, "Doubleday")
    
    # TODO Uncomment and replace question marks with correct expressions
    # TODO 5.4
    for book in doubleday_books:
        print(f"\nTitle: {book['title']}")
        print(f"Rank: {book.get('rank')}")

    # PROBLEM 6
    first_book_score = score_book(doubleday_books[0])

    # TODO Uncomment and replace "?first book title?" and "?penultimate book title?" with the correct expressions

    # fmt: off
    print(f"\nFirst Doubleday Book: {doubleday_books[0]['title']}; Score: {first_book_score}")
    # fmt: on

    assert doubleday_books[0]["title"] == first_doubleday_book_title_test
    assert first_book_score == first_doubleday_book_score_test

    penultimate_book_score = score_book(doubleday_books[-2])

    # fmt: off
    print(f"\nPenultimate Doubleday Book: {doubleday_books[-2]['title']}; Score: {penultimate_book_score}")
    # fmt: on

    assert doubleday_books[-2]["title"] == penultimate_doubleday_book_title_test
    assert penultimate_book_score == penultimate_doubleday_book_score_test

    # PROBLEM 7

    # TODO 7.3

    # fmt: off
    doubleday_score = score_publisher(publisher="Doubleday", bestseller_lists=fiction_bestsellers)

    # fmt: on

    print(f"\nDoubleday Publisher Score: {doubleday_score}")
    assert doubleday_score == doubleday_score_test

    # PROBLEM 8

    # TODO 8.3
    fiction_publishers = find_publishers(fiction_bestsellers)
    print(f"\nFiction Publishers: {fiction_publishers}")
    assert fiction_publishers == fiction_publishers_test

    # PROBLEM 9

    # TODO 9.3
    fiction_publishers_scoreboard = create_scoreboard(fiction_bestsellers)

    print(f"\nScoreboard of Fiction Publishers: {fiction_publishers_scoreboard}")
    assert fiction_publishers_scoreboard == fiction_publishers_scoreboard_test

    filepath = "stu-fiction_publishers_scoreboard-2024.json"
    write_json(filepath, fiction_publishers_scoreboard)


# Do not modify or remove this if statement
if __name__ == "__main__":
    main()
