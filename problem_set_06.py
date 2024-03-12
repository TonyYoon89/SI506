import csv
from pathlib import Path


def calculate_shot_conversion_rate(goals, shots, precision=2):
    """Calculates the shot conversion rate (goals divided by shots). The number
    of decimal places to retain when rounding the quotient is specified by the
    < precision > argument. If the < try > block raises an exception (i.e., a
    ZeroDivisionError) the function returns 0.0.

    Parameters:
        goals (int): number of goals scored
        shots (int): number of shots taken
        precision (int): number of decimal places to retain

    Returns:
        float: shot conversion rate
    """

    try:
        return round(goals / shots, precision)
    except ZeroDivisionError:
        return 0.0


def clean_squad(squad):
    """Converts a player's "Squad" value (e.g. "es Spain") to a two-item tuple
    comprising the following items:

    1  Upper case two-letter country abbreviation (e.g., "ES")
    2. squad name (e.g., "Spain")

    Parameters:
        squad (str): comprises a two-letter country abbreviation and squad name

    Returns:
        tuple: "Squad" element converted to a two-item tuple
    """
    return (squad[:2].upper(), squad[3:])


def format_player_position(position):
    """Reformats player's position string by converting the comma (",") delimiter that
    separates multiple positions to a pipe (|), e.g., "MF,DF" -> "MF|DF". This change
    eliminates the need to surround the position string with double quotes when writing the
    value to a CSV file.

    Parameters:
        position (str): player's position string

    Returns:
        str: reformatted position string
    """

    return position.replace(",", "|")


def get_multi_position_players(players, pos_idx):
    """Returns players who play multiple positions. Evaluates the "Pos" element
    for the presence of multiple positions (e.g., "DF", "FW", "GK", "MF").

    Parameters:
        players (list): nested list of player data
        pos_idx (int): index value of the "Pos" element

    Returns:
        list: nested list of players who play multiple positions
    """
    multi = []

    for player in players:
        position = player[pos_idx].split("|")
        if len(position) > 1:
            multi.append(player)
    return multi


def get_player_shooting_numbers(player, slice_):
    """Returns a player's shots, shots on target, and goals scored. All values
    are converted from strings to integers before being returned to the caller.

    Parameters:
        player (list): a list containing player data
        slice_ (slice): slice() instance required to access the shooting-related
                        elements in the player list.

    Returns:
        list: player's shooting statistics (shots, shots on target, and goals)
    """

    shooting_numbers = player[slice_]

    for i in range(len(shooting_numbers)):
        shooting_numbers[i] = int(shooting_numbers[i])

    return shooting_numbers


def get_team(players, squad_idx, squad):
    """Returns members of a country's team.

    Parameters:
        players (list): nested list of player data
        squad_idx (int): index value of the "Squad" element
        squad (str): country/squad name

    Returns:
        list: team members who represent the < squad >
    """

    team = []

    for player in players:
        if player[squad_idx].lower() == squad.lower():
            team.append(player)
    return team


def get_team_names(players, squad_idx):
    """Returns a list of team/squad names that correspond to the countries participating
    in the World Cup. Duplicate names are filtered out of the list returned to the caller.

    Parameters:
        players (list): nested list of player data
        squad_idx (int): index value of the "Squad" element

    Returns:
        list: countries represented by the players in the < players > list
    """

    teams = []
    for player in players:
        if player[squad_idx] not in teams:
            teams.append(player[squad_idx])
    return teams


def get_top_scorer(players, gls_idx):
    """Returns the top scorer from the < players > list. Filters out players
    that did not score a goal and excludes them from consideration. Ties between
    top scorers are accommodated.

    Parameters:
        players (list): nested list of player data
        gls_idx (int): index value of a nested list's "Gls" element

    Returns:
        list: nested list of one or more top scorers
    """
    top_scorers = []
    most_goals = 0

    for player in players:
        goals = int(player[gls_idx])
        if goals > 0 and goals > most_goals:
            most_goals = goals
            top_scorers.clear()
            top_scorers.append(player)
        elif goals > 0 and goals == most_goals:
            top_scorers.append(player)

    return top_scorers


def read_csv(filepath, encoding="utf-8", newline="", delimiter=","):
    """
    Reads a CSV file, parsing row values per the provided delimiter. Returns a list of lists,
    wherein each nested list represents a single row from the input file.

    WARN: If a byte order mark (BOM) is encountered at the beginning of the first line of decoded
    text, call < read_csv > and pass 'utf-8-sig' as the < encoding > argument.

    WARN: If newline='' is not specified, newlines '\n' or '\r\n' embedded inside quoted fields
    may not be interpreted correctly by the csv.reader.

    Parameters:
        filepath (str): The location of the file to read
        encoding (str): name of encoding used to decode the file
        newline (str): specifies replacement value for newline '\n'
                       or '\r\n' (Windows) character sequences
        delimiter (str): delimiter that separates the row values

    Returns:
        list: nested "row" lists
    """

    with open(filepath, "r", encoding=encoding, newline=newline) as file_obj:
        data = []
        reader = csv.reader(file_obj, delimiter=delimiter)
        for row in reader:
            data.append(row)
        return data


def write_csv(filepath, data, headers=None, encoding="utf-8", newline=""):
    """
    Writes data to a target CSV file. Column headers are written as the first
    row of the CSV file if optional headers are specified.

    WARN: If newline='' is not specified, newlines '\n' or '\r\n' embedded inside quoted
    fields may not be interpreted correctly by the csv.reader. On platforms that utilize
    `\r\n` an extra `\r` will be added.

    Parameters:
        filepath (str): path to target file (if file does not exist it will be created)
        data (list | tuple): sequence to be written to the target file
        headers (seq): optional header row list or tuple
        encoding (str): name of encoding used to encode the file
        newline (str): specifies replacement value for newline '\n'
                       or '\r\n' (Windows) character sequences

    Returns:
        None
    """

    with open(filepath, "w", encoding=encoding, newline=newline) as file_obj:
        writer = csv.writer(file_obj)
        if headers:
            writer.writerow(headers)
            for row in data:
                writer.writerow(row)
        else:
            writer.writerows(data)


def main():
    """Program entry point. Orchestrates workflow.

    Parameters:
        None

    Returns:
        None
    """

    # CHALLENGE 01

    # 1.1
    filepath = Path("data-2023-fifa_wwc-players.csv").resolve()
    print(f"1.1 {filepath}")

    # 1.2
    data = read_csv(filepath)
    
    # 1.3
    for i in range(len(data)):
        data[i] = data[i][:10]

    # 1.4
    print(f"\n1.4 data[0] = {data[0]}")  # headers
    print(f"\n1.4 data[-1] = {data[-1]}")  # last player
    assert data[0] == [
        "Rk",
        "Player",
        "Pos",
        "Squad",
        "Age",
        "Born",
        "90s",
        "Gls",
        "Sh",
        "SoT",
    ]
    assert data[-1] == [
        "619",
        "Claudia Zornoza",
        "MF",
        "es Spain",
        "32",
        "1990",
        "0.4",
        "0",
        "0",
        "0",
    ]

    # 1.5
    headers = data[0]
    players = data[1:]

    # CHALLENGE 02

    # 2.1
    assert "MF|DF" == format_player_position("MF,DF")
    assert "GK" == format_player_position("GK")

    # 2.2
    assert ("NG", "Nigeria") == clean_squad("ng Nigeria")
    assert ("ZA", "South Africa") == clean_squad("za South Africa")

    # CHALLENGE 03

    # 3.1
    pos_idx = headers.index("Pos")
    squad_idx = headers.index("Squad")

    # 3.2
    for player in players:
        player[pos_idx] = format_player_position(player[pos_idx])
        code, squad = clean_squad(player[squad_idx])
        player.insert(squad_idx, code)
        player[squad_idx + 1] = squad

    # 3.3
    headers.insert(squad_idx, "Country_Code")

    # 3.4
    squad_idx += 1

    # 3.5
    write_csv("./stu-players.csv", players, headers)

    # CHALLENGE 04

    # 4.2
    multi_position_players = get_multi_position_players(players, pos_idx)
    print(multi_position_players)

    # 4.3
    write_csv("stu-players-multi_position.csv", multi_position_players, headers)

    # CHALLENGE 05

    # 5.2
    team_china = get_team(players, squad_idx, "China PR")

    # 5.3
    write_csv("stu-team-china.csv", team_china, headers)

    # CHALLENGE 06

    # 6.2
    gls_idx = headers.index("Gls")

    # 6.3
    top_scorers = get_top_scorer(players, gls_idx)

    # 6.4
    print(f"\n6.4 top scorer(s) (n={len(top_scorers)}) = {top_scorers}")

    # CHALLENGE 07

    # 7.2
    countries = get_team_names(players, squad_idx)

    # 7.3
    countries.sort()

    # 7.4
    print(f"\n7.4 countries = {countries}")
    assert len(countries) == 32

    # 7.5-9
    team_top_scorers = []
    for country in countries:
        team = get_team(players, squad_idx, country)
        top_scorers = get_top_scorer(team, gls_idx)
        team_top_scorers.extend(top_scorers)

    # 7.10
    write_csv("stu-team-top_scorers.csv", team_top_scorers, headers)

    # CHALLENGE 08

    # 8.2 UNCOMMENT: built-in slice(< start >, < start >, < step >=None) object in action!
    slice_ = slice(gls_idx, len(headers))  #  equivalent to slice(8, 11)

    # 8.3
    goals, shots, shots_on_target = get_player_shooting_numbers(players[0], slice_)
    # 8.4
    print(
        f"\n8.4 goals = {goals}",
        f"shots = {shots}",
        f"shots_on_target = {shots_on_target}",
        sep="\n",
    )
    assert goals == 1
    assert shots == 10
    assert shots_on_target == 4

    # CHALLENGE 9

    # 9.2-4
    for player in players:
        goals, shots, shots_on_target = get_player_shooting_numbers(player, slice_)
        shots_conv_rate = calculate_shot_conversion_rate(goals, shots, 3)
        shots_on_target_conv_rate = calculate_shot_conversion_rate(goals=goals, shots=shots_on_target, precision=3)
        player.extend([shots_conv_rate, shots_on_target_conv_rate])

    # 9.5
    headers.extend(["shots_conv_rate", "shots_on_target_conv_rate"])
    # 9.6
    write_csv("stu-players-shooting_efficiency.csv", players, headers)


if __name__ == "__main__":
    main()
