import copy
import pathlib
import five_oh_six_utils as utl

from pathlib import Path


# Constants
CACHE_FILEPATH = "./CACHE.json"
NONE_VALUES = ("", "n/a", "none", "unknown")
SWAPI_ENDPOINT = "https://swapi.py4e.com/api"
SWAPI_PEOPLE = f"{SWAPI_ENDPOINT}/people/"
SWAPI_PLANETS = f"{SWAPI_ENDPOINT}/planets/"
SWAPI_SPECIES = f"{SWAPI_ENDPOINT}/species/"
SWAPI_STARSHIPS = f"{SWAPI_ENDPOINT}/starships/"

# Create/retrieve cache
cache = utl.create_cache(CACHE_FILEPATH)


def board_ship(ship, crew_members, crew_positions, passengers=None):
    """Assigns < crew_members > and < passengers > to a starship. Crew size and passenger capacity
    is limited by the < ship >'s "crew_size" and "max_passengers" values. Boarding passengers is
    optional.

    The < crew_members > and < crew_positions > tuples must contain the same number of elements. The
    individual < crew_positions > and < crew_members > elements are then paired by index position and
    stored in a dictionary structured as follows:

    {< crew_positions[0] >: < crew_members[0] >, < crew_positions[1] >: < crew_members[1] >, ...}

    The number of crew positions/members is limited by the < crew size > value. No additional
    crew positions/members are permitted to be assigned to the crew members dictionary even if
    passed to the function. Crew positions/members are assigned to the dictionary as key-value pairs
    by index position (0, 1, ...).

    The number of passengers permitted to board a < ship > is limited by the < max_passengers > value.
    If the number of passengers attempting to board exceeds < max_passengers > only the first < n >
    passengers (where `n` = "max_passengers") are permitted to board the vessel.

    Parameters:
        starship (dict): represents a starship
        crew_members (tuple): crew members
        crew_positions (tuple): crew positions (e.g., 'pilot', 'copilot', etc.)
        passengers (list): passengers seeking permission to board

    Returns:
        dict: starship with crew members and passengers aboard the vessel
    """

    ship["crew_members"] = {crew_positions[i]: crew_members[i] for i in range(ship["crew_size"])}
    if passengers:
        ship["passengers_on_board"] = passengers[: ship["max_passengers"]]
    return ship


def convert_episode_values(episodes, none_values):
    """Converts select string values to either < int >, < float >, < list >, or < None >
    in the passed in list of nested dictionaries. The function delegates to the
    < utl.to_*() > functions the task of converting the specified strings to either
    an integer, float, list, or None.

    If a value is a member of < none_values > the value is replaced by < None >. Otherwise,
    various < utl.to_*() > functions are called as necessary in an attempt to convert
    certain episode values to more appropriate types per the "Type conversions" listed below.

    Type conversions:
        series_season_num (str) -> series_season_num (int | None)
        series_episode_num (str) -> series_episode_num (int | None)
        season_episode_num (str) -> season_episode_num (int | None)
        episode_prod_code (str) -> episode_prod_code (float | None)
        episode_us_viewers_mm (str) -> episode_us_viewers_mm (float | None)
        episode_writers (str) -> episode_writers (list | None)

    Parameters:
        episodes (list): nested episode dictionaries
        none_values (tuple): strings to convert to None

    Returns:
        list: nested episode dictionaries containing mutated key-value pairs
    """

    for episode in episodes:
        for key, value in episode.items():
            if value in none_values:
                episode[key] = None
            elif key in [
                "series_season_num",
                "series_episode_num",
                "season_episode_num",
            ]:
                episode[key] = utl.to_int(value)
            elif key in ["episode_prod_code", "episode_us_viewers_mm"]:
                episode[key] = utl.to_float(value)
            elif key == "episode_writers":
                episode[key] = utl.to_list(value, ", ")
            else:
                continue  # If no conversion is necessary, move to the next item

    return episodes


def get_most_viewed_episode(episodes):
    """Identifies and returns a list of one or more episodes with the highest recorded
    viewership. Ignores episodes with no viewship value. Includes in the list only those
    episodes that tie for the highest recorded viewership. If no ties exist only one
    episode will be returned in the list. Delegates to the function < has_viewer_data >
    the task of determining if the episode includes viewership "episode_us_viewers_mm"
    numeric data.

    Parameters:
        episodes (list): nested episode dictionaries

    Returns:
        list: episode(s) with the highest recorded viewership.
    """

    max_viewers = 0
    most_viewed_episodes = []

    for episode in episodes:
        # Check if the episode has viewership data
        if has_viewer_data(episode):
            viewers = float(episode["episode_us_viewers_mm"])
            # Compare with the maximum viewers found so far
            if viewers > max_viewers:
                max_viewers = viewers
                most_viewed_episodes = [episode]
            elif viewers == max_viewers:
                most_viewed_episodes.append(episode)

    return most_viewed_episodes


def get_news_desks(articles, none_values):
    """Returns a list of New York Times news desks sourced from the passed in
    < articles > list. Accesses the news desk name from each article's "news_desk"
    key-value pair. Filters out duplicates in order to guarantee uniqueness. The
    list sorted alphanumerically before being returned to the caller.

    Delegates to the function < utl.to_none > the task of converting "news_desk"
    values that equal "None" (a string) to None. Only news_desk values that are "truthy"
    (i.e., not None) are returned in the list.

    Parameters:
        articles (list): nested dictionary representations of New York Times articles
        none_values (tuple): strings to convert to None

    Returns:
        list: news desk strings (no duplicates) sorted alphanumerically
    """
    news_desks = []
    for article in articles:
        news_desk = utl.to_none(article.get("news_desk"), none_values)
        if (
            news_desk and news_desk not in news_desks
        ):  # Check for truthiness and uniqueness
            news_desks.append(news_desk)

    return sorted(news_desks)


def get_swapi_resource(url, params=None, timeout=10, verify=True):
    """Retrieves a deep copy of a SWAPI resource from either the local < cache >
    dictionary or from a remote API if no local copy exists. Delegates to the function
    < utl.create_cache_key > the task of minting a key that is used to identify a cached
    resource. If the desired resource is not located in the cache, delegates to the
    function < get_resource > the task of retrieving the resource from SWAPI.
    A deep copy of the resource retrieved remotely is then added to the local < cache > by
    mapping it to a new < cache[key] >. The mutated cache is written to the file
    system before a deep copy of the resource is returned to the caller.

    WARN: Deep copying is required to guard against possible mutatation of the cached
    objects when dictionaries representing SWAPI entities (e.g., films, people, planets,
    species, starships, and vehicles) are modified by other processes.

    Parameters:
        url (str): a uniform resource locator that specifies the resource.
        params (dict): optional dictionary of querystring arguments.
        timeout (int): timeout value in seconds
        verify (bool): verify server's TSL certificate

    Returns:
        dict|list: requested resource sourced from either the local cache or a remote API
    """

    key = utl.create_cache_key(url, params)
    if key in cache.keys():
        return copy.deepcopy(cache[key])  # recursive copy of objects
    else:
        resource = utl.get_resource(url, params, timeout, verify)
        cache[key] = copy.deepcopy(resource)  # recursive copy of objects
        utl.write_json(CACHE_FILEPATH, cache)  # persist mutated cache
        return resource


def group_articles_by_news_desk(news_desks, articles):
    """Returns a dictionary of "news desk" key-value pairs that group the passed in
    < articles > by their parent news desk. The passed in < news_desks > list provides
    the keys while each news desk's < articles > are stored in a list and assigned to
    the appropriate "news desk" key. Each key-value pair is structured as follows:

    {
        < news_desk_name_01 >: [{< article_01 >}, {< article_05 >}, ...],
        < news_desk_name_02 >: [{< article_20 >}, {< article_31 >}, ...],
        ...
    }

    Each dictionary that represents an article is a "thinned" version of the New York Times
    original and consists of the following key-value pairs ordered as follows:

    Key order:
        web_url
        headline_main (new name)
        news_desk
        byline_original (new name)
        document_type
        material_type (new name)
        abstract
        word_count
        pub_date

    Parameters:
        news_desks (list): list of news_desk names
        articles (list): nested dictionary representations of New York Times articles

    Returns
        dict: key-value pairs that group articles by their parent news desk
    """

    grouped_articles = {news_desk: [] for news_desk in news_desks}

    # Loop through each article
    for article in articles:
        # Extract the news desk of the article
        article_news_desk = article.get("news_desk")

        # If the article's news desk is in the list of news desks
        if article_news_desk in news_desks:
            # Create a thinned article dictionary
            thinned_article = {
                "web_url": article.get("web_url"),
                "headline_main": article.get("headline", {}).get("main"),
                "news_desk": article_news_desk,
                "byline_original": article.get("byline", {}).get("original"),
                "document_type": article.get("document_type"),
                "material_type": article.get("type_of_material"),
                "abstract": article.get("abstract"),
                "word_count": article.get("word_count"),
                "pub_date": article.get("pub_date"),
            }

            # Add this thinned article to the corresponding list in the dictionary
            grouped_articles[article_news_desk].append(thinned_article)

    return grouped_articles


def has_viewer_data(episode):
    """Checks the truth value of an episode's "episode_us_viewers_mm" key-value pair. Returns
    True if the truth value is "truthy" (e.g., numeric values that are not 0, non-empty sequences
    or dictionaries, boolean True); otherwise returns False if a "falsy" value is detected (e.g.,
    empty sequences (including empty or blank strings), 0, 0.0, None, boolean False)).

    Parameters:
        episode (dict): represents an episode

    Returns:
        bool: True if "episode_us_viewers_mm" value is truthy; otherwise False
    """

    return bool(episode.get("episode_us_viewers_mm"))


def transform_sentient_being(data, keys, none_values, planets=None, is_droid=False):
    """Returns a new "thinned" dictionary representation of both organic (i.e., person) and
    mechanical (i.e., droid) sentient beings based on the passed in < data > dictionary with
    string values converted to more appropriate types.

    The new dictionary is constructed by mapping a subset of the < data > dictionary's
    key-value pairs to the new dictionary based on the passed in < keys > dictionary. The truth
    value of < is_droid > determines whether the sentient being is a droid or a person and is
    used to select the appropriate nested "droid" or "person" dictionary in < keys >.

    The < keys > dictionary contains nested "droid" and "person" dictionaries that specify
    the following features of the new dictionary to be returned to the caller:

    * the subset of < data > key-value pairs to be mapped to the new dictionary.
    * the order in which the < data > key-value pairs are mapped to the new dictionary.
    * the key names to be used in the new dictionary. Each key in < keys > corresponds to
      a key in < data >. Each value in < keys > represents the (new) key name to be used
      in the new dictionary.

    < data > values are converted to more appropriate types as outlined below under "Mappings".
    Strings found in < none_values > are converted to < None > irrespective of case. Type
    conversions are delegated to the various < utl.to_*() > functions. If a new key lacks a
    corresponding < data > value < None > is assigned.

    Each targeted < data > value is then mapped to the new key when assigning the new key-value
    pair to the new "person" dictionary. Some overlap exists between droid and person keys
    but certain keys are not shared. For unshared keys < is_droid > is used in certain conditional
    statements as an additional filtering expression.

    Additionally, a person's "homeworld" and "species" key-value pairs require special handling.

    Retrieving a dictionary representation of the person's home planet is delegated to the
    function < get_swapi_resource() >. If the caller passes in a Wookieepedia-sourced
    < planets > list this function delegates to the function < utl.get_nested_dict() > the task
    of retrieving the Wookieepedia representation of the homeworld from < planets >.
    If the homeworld is found in < planets > the SWAPI and Wookieepedia dictionaries are
    combined. Cleaning the homeworld dictionary is delegated to the function < transform_planet() >.

    Likewise, retrieving a representation of the person's species is delegated to the function
    < get_swapi_resource() >. From the dictionary returned the "name" value is accessed and mapped
    to the new dictionary's "species" key.

    Person mappings (old key -> new key):
        url (str) -> url (str)
        name (str) -> name (str | None)
        birth_year (str) -> birth_date (dict | None)
        height (str) -> height_cm (float | None)
        mass (str) -> mass_kg (float | None)
        homeworld (str) -> homeworld (dict | None)
        species (list) -> species (str | None)
        force_sensitive (str) -> force_sensitive (str | None)

    Droid mappings (old key -> new key):
        url (str) -> url (str)
        name (str) -> name (str | None)
        model (str) -> model (str | None)
        manufacturer (str) -> manufacturer (str | None)
        create_year (str) -> create_date (dict | None)
        height (str) -> height_cm (float | None)
        mass (str) -> mass_kg (float | None)
        equipment (str) -> equipment (list | None)
        instructions (str) -> instructions (list | None)

    Parameters:
        data (dict): source data
        keys (dict): old key to new key mappings
        none_values (tuple): strings to convert to None
        planets (list): Supplementary planet data
        is_droid (bool): True if the sentient being is a droid

    Returns:
        dict: new dictionary representation of a person
    """

    new_entity = {}
    entity_keys = keys["droid"] if is_droid else keys["person"]

    for old_key, new_key in entity_keys.items():
        original_value = data.get(old_key)

        if old_key in ["url", "name"]:
            new_entity[new_key] = utl.to_none(original_value, none_values)
        elif old_key in ["height", "mass"]:
            new_entity[new_key] = utl.to_none(utl.to_float(original_value), none_values)
        elif old_key in ["model", "manufacturer"] and is_droid:
            new_entity[new_key] = utl.to_none(original_value, none_values)
        elif old_key in ["equipment"] and is_droid:
            new_entity[new_key] = utl.to_list(original_value, delimiter="|")
        elif old_key in ["instructions"] and is_droid:
            new_entity[new_key] = utl.to_list(original_value, delimiter=",")
        elif old_key in ["create_year"] and is_droid:
            new_entity[new_key] = utl.to_none(utl.to_year_era(original_value), none_values)
        elif old_key in ["force_sensitive"] and not is_droid:
            new_entity[new_key] = utl.to_none(original_value, none_values)
        elif old_key in ["birth_year"] and not is_droid:
            new_entity[new_key] = utl.to_none(utl.to_year_era(original_value), none_values)
        elif old_key in ["homeworld"] and original_value:
            homeworld = get_swapi_resource(original_value)
            if planets:
                wookiee_homeworld = utl.get_nested_dict(planets, "name", homeworld["name"])
                if wookiee_homeworld:
                    homeworld["url"] = wookiee_homeworld.get("url", homeworld.get("url"))
                    homeworld.update(wookiee_homeworld)
            new_entity[new_key] = transform_planet(homeworld, keys, none_values) 
        elif old_key == "species" and not is_droid:
            species_info = get_swapi_resource(original_value[0])
            new_entity[new_key] = species_info["name"] if species_info else None
        else:
            new_entity[new_key] = original_value

    return new_entity


def transform_planet(data, keys, none_values):
    """Returns a new "thinned" dictionary representation of a planet based on the passed in
    < data > dictionary with string values converted to more appropriate types.

    The new dictionary is constructed by mapping a subset of the < data > dictionary's
    key-value pairs to the new dictionary based on the passed in < keys >
    dictionary. The < keys > dictionary contains a nested "planet" dictionary that specifies
    the following features of the new dictionary to be returned to the caller:

    * the subset of < data > key-value pairs to be mapped to the new dictionary.
    * the order in which the < data > key-value pairs are mapped to the new dictionary.
    * the key names to be used in the new dictionary. Each key in < keys > corresponds to
      a key in < data >. Each value in < keys > represents the (new) key name to be used
      in the new dictionary.

    < data > values are converted to more appropriate types as outlined below under "Mappings".
    Strings found in < none_values > are converted to < None > irrespective of case. Type
    conversions are delegated to the various < utl.to_*() > functions. If a new key lacks a
    corresponding < data > value < None > is assigned.

    Each targeted < data > value is then mapped to the new key when assigning the new
    key-value pair to the new "planet" dictionary.

    Mappings (old key -> new key):
        url (str) -> url (str)
        name (str) -> name (str | None)
        region (str) -> region (str | None)
        sector (str) -> sector (str | None)
        suns (str) -> suns (int | None)
        moons (str) -> moons (int | None)
        orbital_period (str) -> orbital_period_days (float | None)
        diameter (str) -> diameter_km (int | None)
        atmosphere (str) -> atmosphere (str | None)
        climate (str) -> climate (list | None)
        terrain (str) -> terrain (list | None)
        population (str) -> population (int | None)

    Parameters:
        data (dict): source data
        keys (dict): old key to new key mappings
        none_values (tuple): strings to convert to None

    Returns:
        dict: new dictionary representation of a planet
    """
    transformed_planet = {}

    for old_key, new_key in keys["planet"].items():
        value = data.get(old_key)

        # Use utl.to_none for converting values in none_values to None
        value = utl.to_none(value, none_values)

        if value is not None:
            if old_key in ["suns", "moons", "population", "diameter"]:
                value = utl.to_int(value)
            elif old_key == "gravity":
                value = utl.to_gravity_value(value)
            elif old_key == "orbital_period":
                value = utl.to_float(value)
            elif old_key in ["climate", "terrain"]:
                value = utl.to_list(value, ", ")

        transformed_planet[new_key] = value

    return transformed_planet


def transform_starship(data, keys, none_values):
    """Returns a new "thinned" dictionary representation of a starship based on the passed in
    < data > dictionary with string values converted to more appropriate types.

    The new dictionary is constructed by mapping a subset of the < data > dictionary's
    key-value pairs to the new dictionary based on the passed in < keys >
    dictionary. The < keys > dictionary contains a nested "starship" dictionary that specifies
    the following features of the new dictionary to be returned to the caller:

    * the subset of < data > key-value pairs to be mapped to the new dictionary.
    * the order in which the < data > key-value pairs are mapped to the new dictionary.
    * the key names to be used in the new dictionary. Each key in < keys > corresponds to
      a key in < data >. Each value in < keys > represents the (new) key name to be used
      in the new dictionary.

    < data > values are converted to more appropriate types as outlined below under "Mappings".
    Strings found in < none_values > are converted to < None > irrespective of case. Type
    conversions are delegated to the various < utl.to_*() > functions. If a new key lacks a
    corresponding < data > value < None > is assigned.

    Each targeted < data > value is then mapped to the new key when assigning the new
    key-value pair to the new "starship" dictionary.

    Assigning crew members and passengers constitute separate operations.

    Mappings (old key -> new key):
        url (str) -> url (str)
        name (str) -> name (str | None)
        model (str) -> model (str | None)
        starship_class (str) -> starship_class (str | None)
        manufacturer (str) -> manufacturer (str | None)
        length (str) -> length_m (float | None)
        hyperdrive_rating (str) -> hyperdrive_rating (float | None)
        MGLT (str) -> max_megalight_hr (int | None)
        max_atmosphering_speed (str) -> max_atmosphering_speed_kph (int | None)
        crew (str) -> crew_size (int | None)
        crew_members (dict) -> crew_members (dict | None)
        passengers (str) -> max_passengers (int | None)
        passengers_on_board (list) -> passengers_on_board (list | None)
        cargo_capacity (str) -> cargo_capacity_kg (int | None)
        consumables (str) -> consumables (str | None)
        armament (list) -> armament (list | None)

    Parameters:
        data (dict): source data
        keys (dict): old key to new key mappings
        none_values (tuple): strings to convert to None

    Returns:
        dict: new dictionary representation of a planet
    """

    starship = {}

    for old_key, new_key in keys["starship"].items():
        value = data.get(old_key)

        value = utl.to_none(value, none_values)

        if old_key in ["length", "hyperdrive_rating"]:
            value = utl.to_float(value)
        elif old_key == "max_atmosphering_speed":
            value = utl.to_int(value.replace(",", ""))
        elif old_key in ["crew", "passengers", "cargo_capacity"]:
            value = utl.to_int(value)
        elif old_key == "armament":
            value = utl.to_list(value, ",")

        starship[new_key] = value

    return starship


def main():
    """Entry point for program.

    Parameters:
        None

    Returns:
        None
    """

    # 3.1 CHALLENGE 01

    assert utl.to_float("4") == 4.0
    assert utl.to_float("506,000,000.9999") == 506000000.9999
    assert utl.to_float("Darth Vader") == "Darth Vader"

    assert utl.to_int("506") == 506
    assert utl.to_int("506,000,000.9999") == 506000000
    assert utl.to_int("Ahsoka Tano") == "Ahsoka Tano"

    # 3.2 CHALLENGE 02

    assert utl.to_list("Use the Force") == ["Use", "the", "Force"]
    assert utl.to_list("X-wing|Y-wing", "|") == ["X-wing", "Y-wing"]
    assert utl.to_list([506, 507], ", ") == [506, 507]

    assert utl.to_none("", NONE_VALUES) is None
    assert utl.to_none("N/A ", NONE_VALUES) is None
    assert utl.to_none(" unknown", NONE_VALUES) is None
    assert utl.to_none("Yoda", NONE_VALUES) == "Yoda"
    assert utl.to_none(("41BBY", "19BBY"), NONE_VALUES) == ("41BBY", "19BBY")

    # 3.3 CHALLENGE 03
    clone_wars_episodes = utl.read_csv_to_dicts("./data-clone_wars_episodes.csv")

    count = 0
    for episode in clone_wars_episodes:
        if has_viewer_data(episode):
            count += 1
    assert count == 88

    # 3.4 CHALLENGE 04
    clone_wars_episodes = convert_episode_values(clone_wars_episodes, NONE_VALUES)
    utl.write_json("stu-clone_wars-episodes_converted.json", clone_wars_episodes)

    # 3.5 CHALLENGE 05
    most_viewed_episode = get_most_viewed_episode(clone_wars_episodes)
    print(most_viewed_episode)

    # 3.6 CHALLENGE 06
    articles = utl.read_json("./data-nyt_star_wars_articles.json")
    news_desks = get_news_desks(articles, NONE_VALUES)
    utl.write_json("stu-nyt_news_desks.json", news_desks)

    # 3.7 CHALLENGE 07
    news_desk_articles = group_articles_by_news_desk(news_desks, articles)
    utl.write_json("stu-nyt_news_desk_articles.json", news_desk_articles)

    # 3.8 CHALLENGE 08
    wookiee_planets = utl.read_csv_to_dicts("data-wookieepedia_planets.csv")
    wookiee_dagobah = utl.get_nested_dict(wookiee_planets, "name", "Dagobah")
    utl.write_json("stu-wookiee_dagobah.json", wookiee_dagobah)

    wookiee_haruun_kal = utl.get_nested_dict(wookiee_planets, "system", "Al'Har system")
    utl.write_json("stu-wookiee_haruun_kal.json", wookiee_haruun_kal)

    # 3.9 CHALLENGE 09
    assert utl.to_year_era("1032BBY") == {"year": 1032, "era": "BBY"}
    assert utl.to_year_era("19BBY") == {"year": 19, "era": "BBY"}
    assert utl.to_year_era("0ABY") == {"year": 0, "era": "ABY"}
    assert utl.to_year_era("Chewbacca") == "Chewbacca"

    # 3.10 CHALLENGE 10
    keys_path = Path("data-key_mappings.json").absolute()
    keys = utl.read_json(keys_path)
    harunn_kal = transform_planet(wookiee_haruun_kal, keys, NONE_VALUES)
    # print(harunn_kal)
    # print(type(harunn_kal))
    utl.write_json("stu-haruun_kal.json", harunn_kal)

    # 3.11 CHALLENGE 11
    planets = [transform_planet(planet, keys, NONE_VALUES) for planet in wookiee_planets]
    planets.sort(key=lambda x: x["name"], reverse=True)
    utl.write_json("stu-planets_sorted_name.json", planets)
    planets_diameter_km = sorted(planets, key=lambda x: (-x["diameter_km"] if x["diameter_km"] else 0, x["name"]))
    utl.write_json("stu-planets_sorted_diameter.json", planets_diameter_km)

    # 3.12 CHALLENGE 12
    wookiee_starships = utl.read_csv_to_dicts("data-wookieepedia_starships.csv")
    wookiee_twilight = utl.get_nested_dict(wookiee_starships, "name", "Twilight")
    twilight = transform_starship(wookiee_twilight, keys, NONE_VALUES)
    utl.write_json("stu-twilight.json", twilight)

    # 3.13 CHALLENGE 13
    wookiee_people = utl.read_json("data-wookieepedia_people.json")
    wookiee_droids = utl.read_json("data-wookieepedia_droids.json")

    # Fetch SWAPI data and combine it with Wookieepedia data
    swapi_anakin = get_swapi_resource(SWAPI_PEOPLE, {"search": "Anakin Skywalker"})["results"][0]
    wookiee_anakin = utl.get_nested_dict(wookiee_people, "name", swapi_anakin["name"])
    swapi_anakin.update(wookiee_anakin)
    anakin = transform_sentient_being(swapi_anakin, keys, NONE_VALUES, planets, is_droid=False)
    utl.write_json("stu-anakin_skywalker.json", anakin)

    swapi_r2_d2 = get_swapi_resource(SWAPI_PEOPLE, {"search": "R2-D2"})["results"][0]
    wookiee_r2_d2 = utl.get_nested_dict(wookiee_droids, "name", swapi_r2_d2["name"])
    swapi_r2_d2.update(wookiee_r2_d2)
    r2_d2 = transform_sentient_being(swapi_r2_d2, keys, NONE_VALUES, planets, is_droid=True)
    utl.write_json("stu-r2_d2.json", r2_d2)

    swapi_obi_wan = get_swapi_resource(SWAPI_PEOPLE, {"search": "Obi-Wan Kenobi"})["results"][0]
    wookiee_obi_wan = utl.get_nested_dict(wookiee_people, "name", swapi_obi_wan["name"])
    swapi_obi_wan.update(wookiee_obi_wan)
    obi_wan = transform_sentient_being(swapi_obi_wan, keys, NONE_VALUES, planets, is_droid=False)
    utl.write_json("stu-obi_wan_kenobi.json", obi_wan)

    # 3.14 CHALLENGE 14

    # Test board_ship() function
    # Retrieve and transform Padmé Amidala's data
    swapi_padme = get_swapi_resource(SWAPI_PEOPLE, {"search": "Padmé Amidala"})["results"][0]
    wookiee_padme = utl.get_nested_dict(wookiee_people, "name", swapi_padme["name"])
    swapi_padme.update(wookiee_padme)
    padme = transform_sentient_being(swapi_padme, keys, NONE_VALUES, planets, is_droid=False)
    utl.write_json("stu-padme_amidala.json", padme)

    # Retrieve and transform C-3PO's data
    swapi_c_3po = get_swapi_resource(SWAPI_PEOPLE, {"search": "C-3PO"})["results"][0]
    wookiee_c_3po = utl.get_nested_dict(wookiee_droids, "name", swapi_c_3po["name"])
    swapi_c_3po.update(wookiee_c_3po)
    c_3po = transform_sentient_being(swapi_c_3po, keys, NONE_VALUES, planets, is_droid=True)
    utl.write_json("stu-c_3po.json", c_3po)

    # Load Jedi data from JSON
    jedi_path = Path("data-jedi.json").absolute()
    jedi = utl.read_json(jedi_path)
    ahsoka_tanu, mace_windu, plo_koon, shaak_ti, yoda = jedi

    # Prepare test data for boarding the ship
    test_crew_members = (anakin, obi_wan, mace_windu)
    test_crew_positions = ("pilot", "copilot", "navigator")
    test_passengers = [padme, c_3po, r2_d2, ahsoka_tanu, plo_koon, shaak_ti, yoda]

    test_ship = {
        "crew_size": 2,
        "crew_members": None,
        "max_passengers": 6,
        "passengers_on_board": None,
    }

    test_ship = board_ship(test_ship, test_crew_members, test_crew_positions, test_passengers)
    #print(test_ship["crew_members"])
    #print(test_ship["passengers_on_board"])
    #print([
    #    padme,
    #    c_3po,
    #    r2_d2,
    #    ahsoka_tanu,
    #    plo_koon,
    #    shaak_ti,
    #])

    assert test_ship["crew_members"] == {
        "pilot": anakin,
        "copilot": obi_wan,
    }
    assert test_ship["passengers_on_board"] == [
        padme,
        c_3po,
        r2_d2,
        ahsoka_tanu,
        plo_koon,
        shaak_ti,
    ]

    twilight = board_ship(twilight, (anakin, obi_wan), ("pilot", "copilot"), [padme, c_3po, r2_d2])
    r2_d2["instructions"] = ["Power up the engines"]

    # 3.15 CHALLENGE 15
    naboo = utl.get_nested_dict(planets, "diameter_km", 12120)
    r2_d2["instructions"].append(f"Plot course for Naboo, {naboo['region']}, {naboo['sector']}")
    # "Plot course for Naboo, Mid Rim Territories, Chommell sector"
    # "Plot course for Naboo, Mid Rim Territories, Chommell sector"
    r2_d2["instructions"].append("Release the docking clamp")
    utl.write_json("stu-twilight_departs.json", twilight)


if __name__ == "__main__":
    main()
