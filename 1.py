from google_play_scraper import search, app
import pandas as pd
import re
import time
import random
from datetime import datetime


# ============================================================
# US GOOGLE PLAY APP FINDER
# 10K TO BELOW 50K INSTALLS
# FREE APPS ONLY
# ============================================================
#
# ONLY FILTERS:
#
#   1. Available/searchable in US Google Play Store
#   2. >= 10,000 installs
#   3. < 50,000 installs
#   4. FREE
#
# NO:
#   - Category restriction
#   - Permission restriction
#   - Update-date restriction
#   - Existing-app exclusion
#   - Developer-country restriction
#   - Game exclusion
#   - Shopping exclusion
#   - Government exclusion
#
# INSTALL:
#   pip install google-play-scraper pandas openpyxl
#
# ============================================================


# ============================================================
# SETTINGS
# ============================================================

COUNTRY = "us"
LANG = "en"

MIN_INSTALLS = 10_000
MAX_INSTALLS_EXCLUSIVE = 50_000

SEARCH_RESULTS_PER_TERM = 100

MAX_SEARCH_RETRIES = 3
MAX_APP_RETRIES = 2

SEARCH_DELAY = 0.4
APP_DELAY = 0.25
RETRY_DELAY = 4

broken_searches = []
search_stats = []
skipped_apps = []


# ============================================================
# VERY BROAD SEARCH TERMS
# ============================================================

BASE_SEARCH_TERMS = [

    # GENERAL
    "app",
    "apps",
    "tool",
    "tools",
    "utility",
    "utilities",
    "assistant",
    "manager",
    "tracker",
    "monitor",
    "helper",
    "viewer",
    "scanner",
    "converter",
    "controller",
    "organizer",
    "planner",
    "dashboard",
    "service",

    # PRODUCTIVITY
    "productivity",
    "notes",
    "notepad",
    "memo",
    "todo",
    "to do list",
    "task manager",
    "task tracker",
    "reminder",
    "calendar",
    "schedule",
    "planner",
    "daily planner",
    "habit tracker",
    "time tracker",
    "focus timer",
    "pomodoro",
    "document scanner",
    "PDF reader",
    "PDF editor",
    "OCR",
    "clipboard",
    "keyboard",

    # BUSINESS
    "business",
    "business tools",
    "invoice",
    "invoice maker",
    "receipt",
    "receipt scanner",
    "inventory",
    "inventory manager",
    "POS",
    "employee tracker",
    "shift tracker",
    "work tracker",
    "attendance",
    "field service",
    "delivery driver",
    "courier",
    "fleet",
    "warehouse",
    "barcode scanner",
    "QR scanner",

    # FINANCE
    "finance",
    "money",
    "money manager",
    "budget",
    "budget planner",
    "expense tracker",
    "income tracker",
    "savings",
    "investment",
    "stock tracker",
    "crypto tracker",
    "currency converter",
    "calculator",
    "loan calculator",
    "tax calculator",

    # COMMUNICATION
    "communication",
    "messenger",
    "chat",
    "SMS",
    "dialer",
    "caller id",
    "call blocker",
    "call recorder",
    "contacts",
    "phone",
    "video call",
    "voice chat",

    # SOCIAL
    "social",
    "social network",
    "community",
    "friends",
    "group chat",
    "social media",
    "status saver",

    # PHOTO
    "photo",
    "photo editor",
    "image editor",
    "photo filters",
    "photo collage",
    "collage maker",
    "camera",
    "selfie camera",
    "photo effects",
    "photo enhancer",
    "AI photo",
    "background remover",
    "photo scanner",

    # VIDEO
    "video",
    "video editor",
    "video maker",
    "video player",
    "media player",
    "screen recorder",
    "screen capture",
    "video downloader",
    "video compressor",
    "video converter",
    "video effects",
    "subtitle editor",

    # MUSIC / AUDIO
    "music",
    "music player",
    "audio player",
    "audio recorder",
    "voice recorder",
    "equalizer",
    "bass booster",
    "volume booster",
    "sound meter",
    "podcast",
    "radio",
    "ringtones",
    "music tools",

    # PERSONALIZATION
    "personalization",
    "wallpaper",
    "live wallpaper",
    "4K wallpaper",
    "HD wallpaper",
    "themes",
    "icons",
    "icon pack",
    "launcher",
    "lock screen",
    "home screen",
    "widgets",
    "clock widget",
    "weather widget",
    "edge lighting",
    "dynamic island",
    "always on display",

    # UTILITIES
    "device tools",
    "phone tools",
    "system tools",
    "system monitor",
    "device info",
    "CPU monitor",
    "RAM monitor",
    "battery monitor",
    "battery saver",
    "storage manager",
    "file manager",
    "file explorer",
    "phone cleaner",
    "WiFi tools",
    "WiFi analyzer",
    "network monitor",
    "internet speed",
    "internet speed meter",
    "Bluetooth tools",
    "sensor tools",

    # SCREEN / ACCESSIBILITY
    "screen tools",
    "screen dimmer",
    "screen filter",
    "brightness",
    "rotation control",
    "navigation bar",
    "assistive touch",
    "floating button",
    "floating window",
    "floating tools",
    "magnifier",
    "accessibility",
    "auto clicker",

    # WEATHER
    "weather",
    "weather forecast",
    "weather radar",
    "weather alerts",
    "local weather",
    "temperature",
    "rain radar",
    "storm tracker",

    # CLOCK
    "clock",
    "alarm",
    "alarm clock",
    "timer",
    "stopwatch",
    "countdown",
    "world clock",
    "world time",
    "time zone",
    "time zone converter",

    # TRAVEL
    "travel",
    "travel planner",
    "trip planner",
    "travel guide",
    "city guide",
    "tour guide",
    "flight tracker",
    "hotel",
    "packing list",
    "travel diary",
    "translator",

    # GPS / MAP
    "GPS",
    "GPS tools",
    "navigation",
    "maps",
    "location",
    "location tracker",
    "GPS tracker",
    "compass",
    "speedometer",
    "altimeter",
    "distance tracker",
    "route planner",

    # AUTOMOTIVE
    "car",
    "car tools",
    "car maintenance",
    "vehicle",
    "vehicle tracker",
    "OBD",
    "OBD scanner",
    "car diagnostic",
    "HUD",
    "parking",
    "EV charging",
    "fuel tracker",

    # EDUCATION
    "education",
    "learning",
    "study",
    "study tools",
    "homework",
    "quiz",
    "flashcards",
    "dictionary",
    "language learning",
    "English learning",
    "Spanish learning",
    "Korean learning",
    "Japanese learning",
    "math",
    "math solver",
    "science",
    "history",
    "geography",

    # BOOKS
    "books",
    "ebook",
    "ebook reader",
    "reading",
    "novel",
    "stories",
    "audiobook",
    "book tracker",

    # HEALTH / FITNESS
    "health",
    "health tracker",
    "wellness",
    "fitness",
    "fitness tracker",
    "workout",
    "workout tracker",
    "exercise",
    "step counter",
    "pedometer",
    "running",
    "walking",
    "cycling",
    "sleep tracker",
    "water reminder",
    "meditation",
    "breathing",

    # FOOD
    "food",
    "recipe",
    "recipes",
    "cooking",
    "meal planner",
    "grocery list",
    "restaurant",
    "food diary",

    # LIFESTYLE
    "lifestyle",
    "daily life",
    "home",
    "home management",
    "cleaning",
    "garden",
    "gardening",
    "pet",
    "pet care",
    "dog",
    "cat",
    "fashion",
    "beauty",

    # SHOPPING
    "shopping",
    "shopping list",
    "price comparison",
    "price tracker",
    "deals",
    "coupons",
    "marketplace",

    # ENTERTAINMENT
    "entertainment",
    "movies",
    "movie tracker",
    "TV",
    "TV guide",
    "anime",
    "manga",
    "comics",
    "K-pop",
    "K-drama",
    "celebrity",
    "fan app",

    # NEWS
    "news",
    "breaking news",
    "local news",
    "world news",
    "technology news",
    "sports news",
    "finance news",
    "news reader",
    "RSS reader",

    # SPORTS
    "sports",
    "football",
    "soccer",
    "basketball",
    "baseball",
    "tennis",
    "golf",
    "cricket",
    "sports scores",
    "live scores",
    "sports tracker",

    # EVENTS
    "events",
    "event planner",
    "event calendar",
    "festival",
    "concert",
    "tickets",

    # SECURITY
    "security",
    "privacy",
    "app lock",
    "app locker",
    "app hider",
    "password manager",
    "authenticator",
    "VPN",
    "antivirus",

    # SMART HOME
    "smart home",
    "IoT",
    "smart devices",
    "remote control",
    "TV remote",
    "universal remote",
    "Bluetooth controller",

    # ART / DESIGN
    "art",
    "drawing",
    "painting",
    "sketch",
    "graphic design",
    "logo maker",
    "poster maker",
    "design tools",
    "color picker",

    # PARENTING
    "parenting",
    "baby",
    "baby tracker",
    "family",
    "family organizer",
    "kids",

    # DATING
    "dating",
    "dating app",
    "meet people",
    "friend finder",

    # HOUSE
    "real estate",
    "property",
    "rent",
    "house",
    "apartment",
    "roommate",
    "home search",

    # JOBS
    "jobs",
    "job search",
    "career",
    "resume",
    "resume builder",
    "CV maker",

    # MEDICAL
    "medical",
    "medicine",
    "medication reminder",
    "pill reminder",
    "health diary",

    # REWARDS
    "rewards",
    "reward app",
    "cash rewards",
    "earn money",
    "earn points",
    "cashback",

    # OTHER UTILITIES
    "measurement",
    "ruler",
    "level",
    "decibel meter",
    "light meter",
    "unit converter",
    "barcode",
    "QR code",
    "random generator",
    "decision maker",

    # GAMES - INCLUDED
    "game",
    "games",
    "puzzle game",
    "casual game",
    "arcade game",
    "strategy game",
    "simulation game",
    "sports game",
    "racing game",
    "card game",
    "board game",
    "word game",
    "trivia game",
    "educational game",
    "adventure game",
    "role playing game",
]


# ============================================================
# GENERATE MORE LONG-TAIL QUERIES
# ============================================================

PREFIXES = [
    "simple",
    "easy",
    "smart",
    "quick",
    "mini",
    "daily",
    "personal",
    "mobile",
    "Android",
    "digital",
    "modern",
    "basic",
    "advanced",
]


TOPICS = [
    "alarm clock",
    "world clock",
    "weather",
    "calculator",
    "notes",
    "todo list",
    "habit tracker",
    "expense tracker",
    "budget planner",
    "currency converter",
    "photo editor",
    "video editor",
    "screen recorder",
    "voice recorder",
    "music player",
    "file manager",
    "QR scanner",
    "barcode scanner",
    "document scanner",
    "PDF reader",
    "GPS tracker",
    "speedometer",
    "compass",
    "fitness tracker",
    "step counter",
    "workout timer",
    "study timer",
    "flashcards",
    "dictionary",
    "translator",
    "wallpaper",
    "launcher",
    "lock screen",
    "battery monitor",
    "network monitor",
    "WiFi analyzer",
    "Bluetooth tools",
    "app lock",
    "remote control",
    "car tools",
    "travel planner",
    "meal planner",
    "shopping list",
    "calendar",
    "reminder",
    "clipboard",
    "keyboard",
    "news reader",
    "sports tracker",
    "recipe",
    "pet care",
    "drawing",
    "scanner",
    "timer",
    "stopwatch",
]


SUFFIXES = [
    "app",
    "tool",
    "utility",
    "manager",
    "tracker",
    "assistant",
    "widget",
]


def generate_search_terms():

    terms = set(BASE_SEARCH_TERMS)

    # Prefix + topic
    for prefix in PREFIXES:

        for topic in TOPICS:

            terms.add(
                f"{prefix} {topic}"
            )


    # Topic + suffix
    for topic in TOPICS:

        for suffix in SUFFIXES:

            terms.add(
                f"{topic} {suffix}"
            )


    terms = list(terms)

    random.shuffle(terms)

    return terms


# ============================================================
# INSTALL COUNT
# ============================================================

def parse_installs(value):

    if value is None:
        return 0


    if isinstance(value, (int, float)):
        return int(value)


    digits = re.sub(
        r"[^\d]",
        "",
        str(value)
    )


    try:
        return int(digits)

    except Exception:
        return 0


# ============================================================
# SAFE SEARCH
# ============================================================

def safe_search(term):

    last_error = None


    for attempt in range(
        1,
        MAX_SEARCH_RETRIES + 1
    ):

        try:

            results = search(
                term,
                lang=LANG,
                country=COUNTRY,
                n_hits=SEARCH_RESULTS_PER_TERM
            )


            if results is None:
                raise ValueError(
                    "Search returned None"
                )


            return results


        except Exception as e:

            last_error = (
                f"{type(e).__name__}: {e}"
            )


            print(
                f"   Search attempt "
                f"{attempt}/{MAX_SEARCH_RETRIES} "
                f"failed: {last_error}",
                flush=True
            )


            if attempt < MAX_SEARCH_RETRIES:
                time.sleep(RETRY_DELAY)


    broken_searches.append({
        "Search Term": term,
        "Error": last_error
    })


    return []


# ============================================================
# SAFE APP DETAILS
# ============================================================

def safe_app(package_id):

    last_error = None


    for attempt in range(
        1,
        MAX_APP_RETRIES + 1
    ):

        try:

            result = app(
                package_id,
                lang=LANG,
                country=COUNTRY
            )


            return result, None


        except Exception as e:

            last_error = (
                f"{type(e).__name__}: {e}"
            )


            print(
                f"      Detail attempt "
                f"{attempt}/{MAX_APP_RETRIES} "
                f"failed: {last_error}",
                flush=True
            )


            if attempt < MAX_APP_RETRIES:
                time.sleep(RETRY_DELAY)


    return None, last_error


# ============================================================
# DISCOVERY
# ============================================================

def discover_candidates():

    search_terms = generate_search_terms()

    candidates = {}


    print()
    print("=" * 60)
    print(" US GOOGLE PLAY 10K - BELOW 50K FINDER")
    print("=" * 60)

    print(
        f"Search terms: {len(search_terms):,}"
    )

    print(
        f"Install range: "
        f">= {MIN_INSTALLS:,} and < {MAX_INSTALLS_EXCLUSIVE:,}"
    )

    print(
        "Free apps only: YES"
    )

    print(
        "Category restriction: NONE"
    )

    print(
        "Update restriction: NONE"
    )

    print(
        "Permission restriction: NONE"
    )

    print("=" * 60)


    for number, term in enumerate(
        search_terms,
        start=1
    ):

        print()
        print(
            f"[SEARCH {number}/{len(search_terms)}] "
            f"{term}",
            flush=True
        )


        results = safe_search(term)


        new_count = 0
        duplicate_count = 0


        for position, item in enumerate(
            results,
            start=1
        ):

            if not isinstance(item, dict):
                continue


            package_id = item.get("appId")


            if not package_id:
                continue


            package_id = (
                package_id
                .strip()
                .lower()
            )


            # -----------------------------------------------
            # CURRENT-RUN DEDUPLICATION ONLY
            # -----------------------------------------------

            if package_id in candidates:

                duplicate_count += 1


                if term not in candidates[
                    package_id
                ]["search_terms"]:

                    candidates[
                        package_id
                    ]["search_terms"].append(
                        term
                    )


                if position < candidates[
                    package_id
                ]["best_position"]:

                    candidates[
                        package_id
                    ]["best_position"] = position


                continue


            # -----------------------------------------------
            # NEW CANDIDATE
            # -----------------------------------------------

            candidates[package_id] = {

                "search_terms": [term],

                "best_position": position,

                "search_title": item.get(
                    "title",
                    ""
                ),
            }


            new_count += 1


        search_stats.append({

            "Search Term":
                term,

            "Returned":
                len(results),

            "New Unique Apps":
                new_count,

            "Duplicate Apps":
                duplicate_count,

            "Total Unique Candidates":
                len(candidates),
        })


        print(
            f"   Returned: {len(results)}"
        )

        print(
            f"   New unique: {new_count}"
        )

        print(
            f"   Duplicates: {duplicate_count}"
        )

        print(
            f"   Total unique candidates: "
            f"{len(candidates):,}"
        )


        time.sleep(
            SEARCH_DELAY
        )


    return candidates


# ============================================================
# EVALUATE
# ============================================================

def evaluate_candidate(
    package_id,
    candidate_data
):

    result, error = safe_app(
        package_id
    )


    if result is None:

        skipped_apps.append({

            "Package ID":
                package_id,

            "Reason":
                f"App detail error: {error}"
        })

        return None


    title = result.get(
        "title",
        ""
    )


    developer = result.get(
        "developer",
        ""
    )


    installs_text = result.get(
        "installs",
        ""
    )


    # Prefer realInstalls when available.
    real_installs = result.get(
        "realInstalls"
    )


    if real_installs is not None:

        try:
            installs_number = int(
                real_installs
            )

        except Exception:
            installs_number = parse_installs(
                installs_text
            )

    else:

        installs_number = parse_installs(
            installs_text
        )


    # ========================================================
    # FILTER 1: FREE
    # ========================================================

    if not result.get(
        "free",
        False
    ):

        return None


    # ========================================================
    # FILTER 2: >= 10K
    # ========================================================

    if installs_number < MIN_INSTALLS:

        return None


    # ========================================================
    # FILTER 3: < 50K
    # ========================================================

    if installs_number >= MAX_INSTALLS_EXCLUSIVE:

        return None


    print()
    print(
        "      >>> QUALIFIED <<<",
        flush=True
    )

    print(
        f"      {title}",
        flush=True
    )

    print(
        f"      Developer: {developer}",
        flush=True
    )

    print(
        f"      Installs: {installs_number:,}",
        flush=True
    )

    print(
        f"      Category: "
        f"{result.get('genre', '')}",
        flush=True
    )


    return {

        "App Name":
            title,

        "Package ID":
            package_id,

        "Developer":
            developer,

        "Developer Email":
            result.get(
                "developerEmail",
                ""
            ),

        "Developer Website":
            result.get(
                "developerWebsite",
                ""
            ),

        "Developer Address":
            result.get(
                "developerAddress",
                ""
            ),

        "Category":
            result.get(
                "genre",
                ""
            ),

        "Category ID":
            result.get(
                "genreId",
                ""
            ),

        "Installs Display":
            installs_text,

        "Install Count":
            installs_number,

        "Free":
            "YES",

        "Price":
            result.get(
                "price",
                0
            ),

        "Rating":
            result.get(
                "score",
                ""
            ),

        "Ratings Count":
            result.get(
                "ratings",
                ""
            ),

        "Reviews":
            result.get(
                "reviews",
                ""
            ),

        "Contains Ads":
            result.get(
                "adSupported",
                ""
            ),

        "In-App Purchases":
            result.get(
                "offersIAP",
                ""
            ),

        "Last Updated":
            result.get(
                "updated",
                ""
            ),

        "Released":
            result.get(
                "released",
                ""
            ),

        "Content Rating":
            result.get(
                "contentRating",
                ""
            ),

        "Search Match Count":
            len(
                candidate_data[
                    "search_terms"
                ]
            ),

        "Found By Search":
            ", ".join(
                candidate_data[
                    "search_terms"
                ]
            ),

        "Market":
            "United States",

        "Play Store URL":
            (
                "https://play.google.com/"
                "store/apps/details?id="
                f"{package_id}"
                "&hl=en&gl=US"
            ),
    }


# ============================================================
# CHECK ALL CANDIDATES
# ============================================================

def find_apps():

    candidates = discover_candidates()


    # Apps appearing in multiple searches first
    candidate_items = list(
        candidates.items()
    )


    candidate_items.sort(

        key=lambda x: (

            -len(
                x[1]["search_terms"]
            ),

            x[1]["best_position"]
        )
    )


    qualified = []


    print()
    print("=" * 60)

    print(
        f"CHECKING {len(candidate_items):,} UNIQUE APPS"
    )

    print("=" * 60)


    for index, (
        package_id,
        candidate_data
    ) in enumerate(
        candidate_items,
        start=1
    ):

        print(
            f"[APP {index}/{len(candidate_items)}] "
            f"{package_id}",
            flush=True
        )


        result = evaluate_candidate(
            package_id,
            candidate_data
        )


        if result:
            qualified.append(result)


        time.sleep(
            APP_DELAY
        )


    return qualified


# ============================================================
# EXPORT RESULTS
# ============================================================

def export_results(results):

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    if not results:

        print()
        print(
            "No qualified apps found."
        )

        return


    df = pd.DataFrame(
        results
    )


    df = df.drop_duplicates(
        subset=["Package ID"]
    )


    df = df.sort_values(

        by=[
            "Install Count",
            "Search Match Count"
        ],

        ascending=[
            False,
            False
        ]
    )


    excel_file = (
        f"US_FREE_APPS_10K_TO_BELOW_50K_{today}.xlsx"
    )


    csv_file = (
        f"US_FREE_APPS_10K_TO_BELOW_50K_{today}.csv"
    )


    df.to_excel(
        excel_file,
        index=False
    )


    df.to_csv(
        csv_file,
        index=False,
        encoding="utf-8-sig"
    )


    print()
    print("=" * 60)
    print(" RESULTS")
    print("=" * 60)

    print(
        f"Qualified unique apps: "
        f"{len(df):,}"
    )


    print()
    print("CATEGORY BREAKDOWN:")


    for category, count in (
        df["Category"]
        .value_counts()
        .items()
    ):

        print(
            f"   {category}: {count:,}"
        )


    print()
    print(
        f"Excel: {excel_file}"
    )

    print(
        f"CSV: {csv_file}"
    )


# ============================================================
# EXPORT SEARCH STATS
# ============================================================

def export_search_stats():

    if not search_stats:
        return


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    df = pd.DataFrame(
        search_stats
    )


    df = df.sort_values(
        "New Unique Apps",
        ascending=False
    )


    file_name = (
        f"US_10K_50K_SEARCH_STATS_{today}.xlsx"
    )


    df.to_excel(
        file_name,
        index=False
    )


    print(
        f"Search statistics: {file_name}"
    )


# ============================================================
# EXPORT BROKEN SEARCHES
# ============================================================

def export_broken_searches():

    if not broken_searches:
        return


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    df = pd.DataFrame(
        broken_searches
    )


    df = df.drop_duplicates(
        subset=["Search Term"]
    )


    file_name = (
        f"US_10K_50K_BROKEN_SEARCHES_{today}.xlsx"
    )


    df.to_excel(
        file_name,
        index=False
    )


    print(
        f"Broken searches: {file_name}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    results = find_apps()

    export_results(
        results
    )

    export_search_stats()

    export_broken_searches()


    print()
    print("=" * 60)
    print(" FINISHED")
    print("=" * 60)

    print(
        "Google Play market: UNITED STATES"
    )

    print(
        "Free apps only: YES"
    )

    print(
        f"Minimum installs: {MIN_INSTALLS:,}"
    )

    print(
        f"Maximum installs: "
        f"BELOW {MAX_INSTALLS_EXCLUSIVE:,}"
    )

    print(
        "Category restriction: NONE"
    )

    print(
        "Update restriction: NONE"
    )

    print(
        "Permission restriction: NONE"
    )

    print(
        "Existing app exclusion: NONE"
    )

    print(
        "Games: INCLUDED"
    )

    print(
        "Shopping: INCLUDED"
    )

    print(
        "Government: INCLUDED"
    )

    print(
        "Paid apps: EXCLUDED"
    )

    print("=" * 60)