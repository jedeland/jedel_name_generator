import pandas as pd
import numpy as np
import requests
import os
import re
from bs4 import BeautifulSoup
from transliterate import translit, detect_language
import time
from unidecode import unidecode
#from Name_Gen import addon_wiktionary
import sqlite3; import random

# This addon pack focuses on the application of current and historic data to create more organic naming conventions for NPC's
# The following dataset will act as an anchor for this https://www.ssb.no/en/navn#renderAjaxBanner
# https://www.europeandataportal.eu/data/datasets?locale=en&tags=vornamen&keywords=vornamen
# Changed idea to read wikipedia pages eg. https://en.wikipedia.org/w/index.php?title=Category:German-language_surnames&pagefrom=Eschenbach%0AEschenbach+%28surname%29#mw-pages
# https://archaeologydataservice.ac.uk/archives/view/atlas_ahrb_2005/datasets.cfm?CFID=331341&CFTOKEN=70517262
# Any information taken from https://www.europeandataportal.eu is being used under the Creative Commons Share-Alike Attribution Licence (CC-BY-SA), none is currently being used.
# Arcane name set seems like a useful idea, see text below
# Look into GeoNames dataset found here, https://github.com/awesomedata/awesome-public-datasets , could be used for expanded town name generator
# Possible use argument for this dataset https://github.com/smashew/NameDatabases/tree/master/NamesDatabases
# Use in conjunction with the place names loaded by geonames
'''
Courtesy of u/Alazypanda -
If need random fantastical sounding names I quite literally take the "generic" or chemical names of medication
Like the leader of the mafia my players are working with, Levo Thyroxine.
Might be worth adding some to the data base, but then its up to you to find where to split the word for first/lastname to make it sound right.

Wikientries are now being used to form "organic" lists, the problem with these entries is that they are usually using seperate formats from 
one another, meaning that there is no standardised function that i can create to pass each link through
'''


def find_town_names():
    df = pd.read_csv("name_data/cities1000.txt", sep="\t", header=None)
    df.columns = ["geonameid", "name", "asciiname", "alternatenames", "lat", "lon",
                  "class", "code", "country_code", "cc2", "admin1", "admin2", "admin3",
                  "admin4", "pop", "elevation", "dem_el", "timezone", "mod_date"]
    print(df)
    df = df[~df["timezone"].str.contains('America|Australia|Atlantic|Africa|Pacific')]
    print(df)
    print(pd.unique(df["country_code"]))
    codes = pd.unique(df["country_code"])
    long_string = "AM|AL|AT|AZ|BE|BG|BY|CH|CN|CZ|DE|EE|ES|FI|FR|GB|GE|GR|" \
                  "HR|HU|IE|IL|IN|IQ|IR|IT|JP|KR|KZ|LI|LK|LU|LV|MK|MT|NL|" \
                  "NO|NP|PH|PL|PT|RO|RS|RU|SA|SE|SI|SK|SY|TR|TW|UA|UZ|VN|XK"
    df = df[df["country_code"].str.contains(long_string)]
    df_names_temp = pd.read_excel("surnames_cleaned.xlsx")

    df.to_excel("town_names.xlsx", index=False)


def soup_surnames():
    # is_valid = False
    if os.path.exists("name_data/surnames_cleaned.xlsx"):
        # Implements checks
        df = pd.read_excel("surnames_cleaned.xlsx")
        print(df)
        print(pd.unique(df["name"]))
        return df
    else:
        print("Starting Soup")
        df = pd.DataFrame(columns=["name", "tag", "origin"])
        surname_urls = read_surnames()
        for key, value in surname_urls.items():
            try:
                if "-" in key:
                    nationality = key.split("-")[0]
                else:
                    nationality = key.split(" ")[0]
            except:
                pass
            print(key, value)
            if value == 'https://en.wiktionary.org/wiki/Category:Surnames_by_language':
                # Wiktionary names are in their original language, need to follow deeper to find the english prounouncation
                key_format = "https://en.wiktionary.org/wiki/Category:{}".format(key)
                wiktionary_page = "https://en.wiktionary.org"
                # if key == "Arabic surnames" or key == "Persian surnames":
                df = read_wiki(df, key_format, nationality.strip(), wiktionary_page)
            elif value == 'https://en.wikipedia.org/wiki/Category:Surnames_by_language':
                key_format = "https://en.wikipedia.org/wiki/Category:{}".format(key)
                wiki_page = "https://en.wikipedia.org"
                df = read_wiki(df, key_format, nationality.strip(), wiki_page)
        # Clean out dataframe

        print("Printing dataframe: \n\n\n", df.head(20))
        df = translate_names(df)
        # print(df)
        df = df[~df.isin(['None', None]).any(axis=1)]
        df.dropna(axis=0, how='any', thresh=None, subset=None, inplace=False)
        df.to_excel("surnames_cleaned.xlsx", index=False)
        # print(pd.unique(df["origin"])) big_list = pd.unique(df["origin"]) print(list(big_list))
        return df


def read_wiki(df, key, origins, page_type):
    print(page_type)
    if page_type == "https://en.wiktionary.org":
        problem_list = ["Arabic", "Hindi", "Persian", "Hebrew", "Telugu", "Punjabi", "Yiddish"]
        print("Value is from Wiktionary")
        print("Looking for english variatey")
        file = requests.get(key)
        soup = BeautifulSoup(file.content, "lxml")
        div_tag = soup.find_all("div", {"id": "mw-pages"})
        for tag in div_tag:
            list_tag = tag.find_all("li")
            for name in list_tag:

                print(name.string)
                print(origins)
                if origins not in problem_list:
                    split_name = name.string.split("(")[0]  # Incase of any disambiguations or other issues
                    print(split_name)
                    if any(re.findall(r"Appendix|learn more|previous|List|Surnames|surnames|name|names", split_name,
                                      re.IGNORECASE)):
                        print("Invalid name: ", split_name)
                    else:
                        df = df.append({"name": split_name, "tag": "N", "origin": origins}, ignore_index=True)
                elif origins in problem_list:
                    problem_name = name.string.split("(")[0]  # Incase of any disambiguations or other issues
                    print(problem_name)
                    if any(re.findall(r"Appendix|learn more|previous|List|Surnames|surnames|name|names|", problem_name,
                                      re.IGNORECASE)):
                        print("Invalid name: ", problem_name)
                    else:
                        split_name = find_latin_name(page_type, name.a["href"])

                        df = df.append({"name": split_name, "tag": "N", "origin": origins}, ignore_index=True)
            a_tag = tag.find_all("a", href=True)
            for a_link in a_tag:
                if "next page" in a_link.string:
                    print("There is a page in the tag: {}".format(page_type + a_link["href"]))
                    df = read_wiki(df, page_type + a_link["href"], origins, page_type)
                    break
                    # df = df.append({"name": split_name, "tag": "N", "origin": origins}, ignore_index=True)
        return df
    elif page_type == "https://en.wikipedia.org":

        print("Value is from Wikipedia")
        file = requests.get(key)
        soup = BeautifulSoup(file.content, "lxml")
        # First things first the soup needs to search if there is a next page
        div_tag = soup.find_all("div", {"id": "mw-pages"})
        for tag in div_tag:
            list_tag = tag.find_all("li")
            for name in list_tag:
                name = name.string.split("(")[0]  # Incase of any disambiguations or other issues
                print(name, "\n", origins)
                if any(re.findall(r"Appendix|learn more|previous|List|Surnames|name", name, re.IGNORECASE)):
                    print("Invalid name: ", name)
                else:
                    df = df.append({"name": name, "tag": "N", "origin": origins}, ignore_index=True)
            a_tag = tag.find_all("a", href=True)
            for a_link in a_tag:
                if "next page" in a_link.string:
                    print("There is a page in the tag: {}".format(page_type + a_link["href"]))
                    df = read_wiki(df, page_type + a_link["href"], origins, page_type)
                    break

        return df


def translate_names(df_in):
    df_in["origin"] = np.where((df_in["origin"] == "Surnames"), "African", df_in["origin"])
    df_in["origin"] = np.where((df_in["origin"] == "Low"), "German", df_in["origin"])
    find_town_names()

    print("Translating names using python libraries")

    def translate_to_latin(df_latin):
        print("Translating to latin using unidecode")
        asian_languages = ["Chinese", "Korean", "Japanese"]  # Relevant Asian Language Tags
        for i in asian_languages:
            df_temp = df_latin.loc[df_latin["origin"] == i]
            for index, row in df_temp.iterrows():
                print(row["name"])
                latin_name = unidecode(row["name"])
                latin_nopunct = re.sub(r'[^\w\s]', '', latin_name)
                latin_nopunct = latin_nopunct.capitalize()
                print(latin_name)
                df_latin.replace(row["name"], latin_nopunct, inplace=True)
        cyrillic_languages = ["Armenian", "Bulgarian", "Georgian", "Greek", "Russian", "Serbo"]
        for g in cyrillic_languages:
            df_temp = df_latin.loc[df_latin["origin"] == g]

            for index, row in df_temp.iterrows():
                print(row["name"])
                test_string = row["name"]
                res = all(ord(c) < 128 for c in test_string)
                try:
                    latin_name = translit(row["name"], reversed=True)
                    latin_nopunct = re.sub(r'[^\w\s]', '', latin_name)
                    latin_nopunct = latin_nopunct.capitalize()
                    print(latin_name)
                    df_latin.replace(row["name"], latin_nopunct, inplace=True)
                except:
                    pass
        # for language in
        return df_latin

    def assign_possible_family_affix(df_affix):

        # This needs to relate to the town names excel, so the "names" of the nations are related to the capital
        # print("Creating new last names, using the rules proscribed here: https://en.wikipedia.org/wiki/List_of_family_name_affixes")
        name_affixes = {"Bet": ["Riyadh", "Baghdad"], "Al'": ["Riyadh", "Baghdad"],
                        "von": ["Vienna", "Zurich", "Berlin"], "zu": ["Vienna", "Zurich", "Berlin"],
                        "De": ["Brussels", "Luxembourg", "Amsterdam", "Paris", "Rome", "Malta", "Madrid", "Manilla",
                               "Lisbon"],
                        "Van": ["Brussels", "Luxembourg", "Amsterdam"], "Del": ["Paris", "Manilla"], "Della": ["Rome"],
                        "Du": ["Paris"],
                        "Af": ["Stockholm", "Oslo"], "Di": ["Rome", "Madrid"], "of": ["London"]}
        location_df = pd.read_excel("town_names.xlsx")
        single_names = location_df[~location_df["asciiname"].str.contains(" ", na=False)]
        print(single_names)
        for k, arg in name_affixes.items():
            print(k, arg)
            for i in arg:
                i_location = single_names[single_names["timezone"].str.contains(i, na=False)]
                i_location = i_location[i_location["pop"] > 7000]
                print(i_location)
                for index, row in i_location.iterrows():
                    location = row["asciiname"]
                    print(k + " " + location)
                    df_affix = df_affix.append({"name": k + " " + location, "tag": "N", "origin": i}, ignore_index=True)
        print(df_affix)
        return df_affix

    def standarise_names(df_standard):
        print("This function will standardise the name tags")
        # df = pd.read_excel("names_merged.xlsx")
        name_dict = {"Arabic": "Arabia", "Arabia/Persia": "Arabia", "French": "France", "Spanish": "Spain",
                     "Indian": "India", "Finnish": "Finland", "Riyadh": "Arabia", "Montenegrin": "Balkan",
                     "Turkish": "Turkey", "Swedish": "Sweden", "German": "Germany", "Georgian": "Georgia",
                     "Japanese": "Japan", "USA": "England", "English": "England", "Great Briton": "England",
                     "Estonian": "Estonia", "Baghdad": "Arabia", "Vienna": "Germany", "Zurich": "Swiss",
                     "Berlin": "Germany", "Amsterdam": "Dutch", "Paris": "France", "Rome": "Italy",
                     "Lisbon": "Portugal",
                     "Stockholm": "Sweden", "Oslo": "Norway", "Norwegian": "Norway", "London": "England",
                     "Portuguese": "Portugal", "Irish": "Celtic", "Scottish Gaelic": "Celtic", "Welsh": "Celtic",
                     "Serbo": "Balkan", "Germanyic": "German",
                     "Madrid": "Spain", "Brussels": "Belgium", "Bengali": "India", "Punjabi": "India",
                     "Iranian": "Persian", "Hindi": "India", "Cornish": "Celtic", "Catalan": "Spain",
                     "Bosnian": "Balkan", "Slovene": "Balkan",
                     "Serbia": "Balkan", "Serbian": "Balkan", "Afrikaans": "Dutch", "Belarusian": "Russia",
                     "Chichewa": "Bantu", "Galician": "Spain", "Hiligaynon": "Philippines", "Ilocano": "Philippines",
                     "Kapampangan": "Philippines",
                     "Tagalog": "Philippines", "Telugu": "India", "Maltese": "Malta", "Armenian": "Armenia",
                     "Azerbaijani": "Azerbaijan", "Bulgarian": "Bulgaria", "Bosnia and Herzegovina": "Balkan",
                     "Croatia": "Balkan", "Croatian": "Balkan", "Danish": "Denmark", "Faroese": "Norway",
                     "Germanyy": "Germany", "Great Britain": "England", "Hungarian": "Hungary", "Korean": "Korea",
                     "Italian": "Italy",
                     "India/Sri Lanka": "India", "Icelandic": "Iceland", "Latvian": "Latvia", "Lithuanian": "Lithuania",
                     "Macedonian": "Macedonia", "Kosovo": "Balkan", "Montenegro": "Balkan", "Polish": "Poland",
                     "Romanian": "Romania",
                     "Tamil": "India", "Ukrainian": "Ukraine", "Vietnamese": "Vietnam", "Albanian": "Albania",
                     "Belarus": "Russia", "Russian": "Russia", "Kazakhstan/Uzbekistan": "Kazakhstan",
                     "Amharic": "Ethiopia",
                     "Bosniak": "Balkan", "Balkann": "Balkan", "Slovak": "Slovakia", "Slovakiaia": "Slovakia",
                     "Filipino": "Philippines", "Greek": "Greece", "Chinese": "China", "Sinhalese": "Srilanka",
                     "Ireland": "Celtic",
                     "Hebrew": "Israel", "Yiddish": "Israel", "Scottish": "Celtic", "Tatar": "Kazakhstan",
                     "Norman": "France", "Occitan": "France", "Breton": "France", "Cebuano": "Philippines",
                     "Moldova": "Romania",
                     "Nepali": "India", "Urdu": "Pakistani", "Yoruba": "African"}
        for k, v in name_dict.items():
            try:
                df_standard["origin"] = df_standard["origin"].str.replace(k, v)
                print(k, v)
            except:
                pass
        print(sorted(pd.unique(df_standard["origin"])))

    df_in = translate_to_latin(df_in)
    df_in = assign_possible_family_affix(df_in)
    standarise_names(df_in)

    return df_in


def find_latin_name(page, link):
    name = ""
    possible_tags = ["headword-tr manual-tr tr Latn", "headword-tr tr Latn"]
    file = requests.get(page + link)
    soup = BeautifulSoup(file.content, "lxml")

    for i in possible_tags:
        try:
            span_tag = soup.find_all("span", {"class": i})
            text_arg = span_tag[0].string.strip("()")
            print(text_arg)

            if text_arg == "transliteration needed":
                pass
            else:
                text_arg = text_arg.split(",")[0]
                text_modified = re.sub(r'[^\w\s]', '', text_arg)
                text = text_modified.capitalize()
                name = text_modified
                if name[0] == "ʾ|ʿ":
                    name = name[1:]
                print("---000---", name)
                return name
        except:
            pass


def read_surnames():
    # https://en.wiktionary.org/wiki/Category:Surnames_by_language
    # This function aims to go through each of the catagories listed in the above link, goes through each entry and tries to assign them to one of the pre existing lists
    print("Attempting to webscrape surnames, along with some straggeler forenames")
    # The following names are relatively populated
    valid_names = {}
    total_names = 0
    files = ["https://en.wiktionary.org/wiki/Category:Surnames_by_language",
             "https://en.wikipedia.org/wiki/Category:Surnames_by_language"]
    for file_url in files:
        file = requests.get(file_url)
        print(file_url)
        soup = BeautifulSoup(file.content, "lxml")
        div_tag = soup.find_all("div", {"class": "CategoryTreeItem"})
        for article in div_tag:
            # print(article)
            # print(file_url)
            span_tag = article.find_all("span", {"dir": "ltr"})[
                0]  # The first span element with this tag holds the length of the article
            if "," in span_tag.string:
                span_checker = span_tag.string.split(",", 1)[1]
            else:
                span_checker = span_tag.string

            span_checker = re.sub('[^0-9]', '', span_checker)
            if int(span_checker) >= 25:
                total_names = total_names + int(span_checker)
                print(article, total_names)
                valid_names.update({article.a.text: file_url})
                # print("Valid names include: ", valid_names)
            # print(span_checker)
            # print(article, article.a, "\n\n{}".format(article.a.text))
        # print(valid_names)
    print(valid_names, "\n\n\n", int(total_names))
    return valid_names


def splice_names():
    # Please note that most of the names involved in this function are infact latin-ised names, and cover countries that have already been found via web scraping
    df = form_international_names()
    # Check why some types are not assigning most as men or "M"
    df_bs4 = soup_names()
    print(df_bs4, pd.unique(df_bs4["origin"]))
    df_surnames = soup_surnames()
    df_fantasy = pd.read_csv("name_data/fantasy.csv")

    frames = [df, df_bs4, df_surnames, df_fantasy]
    df_full = pd.concat(frames, ignore_index=True)
    df_full["name"] = df_full["name"].str.replace("\w{L}+", "")
    df_full["name"] = df_full["name"].replace("", np.nan)
    df_full["name"] = df_full["name"].str.replace("[", "")
    df_full = df_full.sort_values(["origin"])
    df_full.dropna(axis=0, how='any', thresh=None, subset=["name"], inplace=True)
    df_full = translate_names(df_full)

    print(df_full)
    print(df_full[df_full["name"] == ""])
    df_full.to_excel("names_merged.xlsx", na_rep="0", index=False)
    # print(df_merge)

    print("Checking if name exists more than once")
    counts = df_full["origin"].value_counts()
    counts = df_full[df_full["origin"].isin(counts.index[counts.gt(2)])]
    # print(counts)
    print(counts.tail(40))

    return df_full


def form_international_names():  # add npc_df as argument
    # Due to a distinct lack of international names, outside of europe from the previous sources
    # This function will use the first name database provided by Matthias Winkelmann and Jörg MICHAEL at the following address
    # https://github.com/MatthiasWinkelmann/firstname-database
    exists = check_if_exists()
    add_files = False  # Default value
    decision = start_soup(add_files)
    print(decision)

    if exists and decision is False:
        print(
            "This file already exists in the a already created CSV folder, this function will use this version instead of creating a new file")
        df = pd.read_excel("firstnames_cleaned.xlsx")
        new_df = df
        make_cross_compatible(new_df)

        print(pd.unique(new_df["tag"]))
        return new_df
    elif not exists or decision is True:
        print("Splicing previous dataframe with international dataframe")
        df_target = pd.read_csv("name_data/firstnames_matthiaswinkelmann.csv")
        print("This is the original CSV file, in a dataframe format \n", df_target)
        col = df_target.columns  # Columns are made up of 2 strings that are ineffecient
        new_cols = refactor_columns(col)
        print("Creating new file")

        df_target = format_df_target(df_target)
        new_df = pd.DataFrame(columns=["name", "tag", "origin"])
        # need to put in argument for new_columns checker, could assign numbers and change after
        start = time.time()
        for i in range(len(df_target)):
            print("Testing second iterration")
            text_arg = df_target.loc[i, "text"].split(",")
            text_arg[-1] = "0"
            text_temp = text_arg[2:]
            for p in range(len(text_temp)):
                if text_temp[p] != "0":
                    origins = new_cols[p + 2]  # The +2 Counteracts the slice action
                    # print(text_arg, origins, "\n", new_cols)
                    print("Testing aspects:", len(text_arg), len(new_cols))
                    new_df = new_df.append({"name": text_arg[0], "tag": text_arg[1], "origin": origins},
                                           ignore_index=True)
                    # By placing the DF assignment here the file should create multiple versions of the same name with individual origins assigned to them, which will speed up later search functions
                    print(p)

            # Although inline text version is quicker, there are issues with duplicate values origins = [new_cols[text_arg.index(b)] for b in text_arg[2:] if b != "0"]
            # This should eliminate any duplicate values inside of the list
        end = time.time()
        print(new_df, pd.unique(new_df["tag"]))
        make_cross_compatible(new_df)
        print("Time elapsed: ", start - end)
        print(pd.unique(new_df["tag"]))
        new_df.to_excel("firstnames_cleaned.xlsx", index=False)
        return new_df


def make_cross_compatible(new_df):
    new_df["name"] = new_df["name"].str.replace("+", "-")
    new_df["tag"] = new_df["tag"].str.replace("1F", "WF").replace("?F",
                                                                  "WF")  # Weighted Female - most likely to be female
    new_df["tag"] = new_df["tag"].str.replace("1M", "?M").replace("?M", "WM")  # Weighted Male - most likely to be male
    new_df["tag"] = new_df["tag"].str.replace("?", "NN")  # name is neutral, non last name


def add_stragglers(df, file_arg, name_fin):  # Can add gender argument, only applicable locations are gender neutral
    print("Adding stragglers, see addon_pack_interface.create_duplicate_names() for more details")
    files = file_arg.values()
    origin = list(file_arg.keys())
    gender = ["NN", "NN", "NN", "M", "F"]
    i = 0
    for file_url in files:
        file = requests.get(file_url)
        # print(file_url)
        if str(file) == "<Response [404]>":
            pass
        elif str(file) == "<Response [200]>":
            print("Starting up Beautiful Soup, adding leftover names, this may take some time ...")
            soup = BeautifulSoup(file.content, "lxml")
            lst_tag = soup.find_all("li")
            for item in lst_tag:
                # print(article)
                # print(file_url)
                item_txt = item.string
                item_txt = re.sub(r'[^\w\s]', '', str(item_txt))
                origins = origin[i]
                if origins == "Yoruba":
                    origins = "African"
                if origins == "Hawf":
                    origins = "Hawaiian"
                if item_txt is None:
                    # print(item.text)
                    item_split = item.text.split(" ")
                    item_txt = item_split[0]
                    item_txt = re.sub(r"([A-Z])", r" \1", item_txt).split()
                    item_txt = item_txt[0]
                    item_txt = item_txt.strip()
                # print(item.text)
                # print("Divided text: ", item_txt)
                # if item_txt == name_div[i - 1]:  # First female entry
                #    divide = True
                if item_txt == name_fin[i]:  # Last acceptable entry
                    adder = str(item_txt)
                    df = df.append({"name": adder, "tag": gender[i], "origin": origins},
                                   ignore_index=True)
                    break
                if item_txt is not None and str(item_txt) != "None":
                    adder = str(item_txt)
                    parts = re.split(r'[;,\s]\s*', adder)  # removes any double names that are not hyphinated
                    # print(parts)
                    adder = parts[0]
                    if not adder.strip():
                        print("Not Found")
                        pass
                    print("Adding... ", adder, " - Origin: {}".format(origins))

                    df = df.append({"name": adder, "tag": gender[i], "origin": origins},
                                   ignore_index=True)
        i += 1

    print(df)
    conn = sqlite3.connect("name_data/names_merged.db")
    df.to_sql
    return df


def check_if_exists():
    outcome = False
    if os.path.exists("name_data/firstnames_cleaned.xlsx"):
        test_df = pd.read_excel("firstnames_cleaned.xlsx")
        sample = test_df.sample(20)
        print(sample)
        # print(test_df[50:80], test_df[4000:4001])
        case1, case2, case3, case4 = test_df.iloc[60], test_df.iloc[70], test_df.iloc[80], test_df.iloc[4000]
        print(case1["name"], case2["name"], case3["name"], case4["name"])
        if case1["name"] == "Aart" and case2["name"] == "Aatu" \
                and case3["name"] == "Abaz" and case4["name"] == "Annamarie":
            print("The cleaned file is valid")
            outcome = True

    return outcome


def format_df_target(df_target):
    a, b = df_target.columns[0], df_target.columns[1]
    df_target = df_target.rename(columns={a: "text", b: "na"})
    df_target["text"] = df_target["text"].str.replace(";;", ",0,0")  # Crude fix, bad data to blame
    df_target["text"] = df_target["text"].str.replace(";", ",")
    df_target["text"] = df_target["text"].str.replace(",,", ",")
    df_target = df_target.drop(columns=["na"])
    return df_target


def refactor_columns(col):
    new_columns = []
    for i in range(len(col)):
        line = col[i]
        out = line.split(";")
        new_columns = new_columns + out
    nations = new_columns

    nations[4], nations[12], nations[26] = "USA", "Dutch", "Czech"
    nations.pop(-1)
    print(nations)
    nations.remove("etc.")
    return nations


def soup_names():
    test_case = False
    test_decision = True
    name_dict = {}
    nations = ["French", "Italian", "Spanish", "Turkish", "Dutch", "Swedish", "Polish", "Serbian", "Irish",
               "Czech", "Hungarian", "Russian", "Persian", "Basque", "Armenian",
               "German"]  # Test cases to see if wiktionary will take these as a real argument
    nation_abrev = ["France", "Italy", "Spain", "Turkey", "Dutch", "Sweden", "Poland", "Serbia", "Ireland",
                    "Czech", "Hungary", "Russia", "Persian", "Basque", "Armenia", "German"]
    probable_formats = ["dd", "dd", "dd", "dd", "li", "dd", "td", "li", "li", "dd", "dd", "td", "li", "dd",
                        "li", "dd"]
    name_div = ["Abbée", "Abbondanza" "Abdianabel", "Abay", "Aafke", "Aagot", "Adela", "Anica",
                "Aengus", "Ada", "Adél", "Авдотья", "Aban", "Abarrane", "Akabi", "Aaltje"]
    name_fin = ["Zoëlle", "Zelmira", "Zulema", "Zekiye", "Zjarritjen", "Öllegård", "Żywia",
                "Vida", "Nóra", "Zorka", "Zseraldin", "Ярослава", "Yasmin", "Zuriňe", "Zoulal", "Zwaantje"]
    if os.path.exists("npcs.csv") or os.path.exists("npcs.xlsx"):
        print("File already exists")
        try:
            # print("We're getting there")
            df_csv, df_xlsx = pd.read_csv("npcs.csv"), pd.read_excel("npcs.xlsx")
            file_list = [df_csv, df_xlsx]
            # print("Starting the soup is recommended before taking the test\nIf you wish to skip this step please ensure that everything is working in order...")

            # If you decide you need to add new names, please ensure you have added the following things
            # 1. The nations name, relative to the wikipedia article, for instance https://en.wiktionary.org/wiki/Appendix:Russian_given_names
            # 2. The nations abreviation, eg ENG for english
            # 3. The format of the HTML that is being used to hold the names
            # 4. The first female name to change the gender type from male to female
            # 5. The last name needed, as an end point (As wikipedia often adds extra things to the end of a file using
            # The HTML type that is being read by BS4)
            test_case = start_soup(test_case)
            # form_non_latin(file_list)
            df_csv = clean_df(df_csv)
            df_stable = translit_non_latin(df_csv)

            if test_case == True:
                # Move function here
                print("Starting up Beautiful Soup")

                df = pd.DataFrame(columns=["name", "tag", "origin"])
                print("adding wikipedia names")
                #df = addon_wiktionary.add_wiktionary_names()
                df_unmerged = add_wiki_names(df)
                con_frames = [df, df_unmerged]
                df = pd.concat(con_frames, ignore_index=True)
                df = translit_non_latin(df)
                print("Forming files ...")
                # form_files(df)
                print("Printing Tail", df.tail(60))

                return df
            else:
                print("Printing df_xlsx", df_xlsx)
                return df_xlsx
        except:
            print("An error occured")
            pass
    else:
        print("File does not exist, starting up Beautiful Soup and creating files")
        df = pd.DataFrame(columns=["name", "tag", "origin"])
        #df = addon_wiktionary.add_wiktionary_names()
        df_unmerged = add_wiki_names(df)
        con_frames = [df, df_unmerged]
        df = pd.concat(con_frames, ignore_index=True)
        df = translit_non_latin(df)
        # form_files(df)
        print(df.tail(60))

        return df

def start_soup(add_decision):
    input_finish = False
    while not input_finish:
        print("add new names: [y/n?]")

        answer = input("\n\n\n")
        if answer.lower() == "y" or answer.lower() == "yes":
            print("Adding new files")
            add_decision = True
            input_finish = True
        elif answer.lower() == "n" or answer.lower() == "no":
            print("Returing Dataframe")
            add_decision = False
            input_finish = True
        else:
            print("That is an invalid input, please type either Y or N")
    return add_decision

def add_wiki_names(df_temp):
        names_urls = read_wiki_names()
        for key, value in names_urls.items():
            try:
                if "-" in key:
                   nationality = key.split("-")[0]
                else:
                    nationality = key.split(" ")[0]
            except:
                pass
            print(key, value)
            if value == 'https://en.wikipedia.org/wiki/Category:Feminine_given_names':
                # Wiktionary names are in their original language, need to follow deeper to find the english prounouncation
                key_format = "https://en.wikipedia.org/wiki/Category:{}".format(key)
                gender = "F"
                # if key == "Arabic surnames" or key == "Persian surnames":
                df_temp = read_category_names(df_temp, key_format, nationality.strip(), gender)
            elif value == 'https://en.wikipedia.org/wiki/Category:Masculine_given_names':
                key_format = "https://en.wikipedia.org/wiki/Category:{}".format(key)
                gender = "M"
                df_temp = read_category_names(df_temp, key_format, nationality.strip(), gender)
        return df_temp

def add_names(df, name_div, name_fin, nation_abrev, nations, probable_formats):
    for i in range(len(nations)):
        divide = False
        argument = "https://en.wiktionary.org/wiki/Appendix:{}_given_names".format(nations[i])
        print(argument)
        file = requests.get(argument)
        print(str(file), "Iteration is {}".format(i), nations[i])
        #print("This has updated")
        #print(str(file))
        if str(file) == "<Response [404]>":
            pass
        elif str(file) == "<Response [200]>":
            #print("Also updated")
            soup = BeautifulSoup(file.content, "lxml")

            rec_data = soup.find_all(probable_formats)
            item_txt = ""
            for item in rec_data:
                item_txt = item.string
                origins = nation_abrev[i]
                print(origins)

                if item_txt is None:
                    # print(item.text)
                    item_split = item.text.split(" ")
                    item_txt = item_split[0]
                    item_txt = re.sub(r"([A-Z])", r" \1", item_txt).split()
                    item_txt = item_txt[0]
                    item_txt = item_txt.strip()
                print(item.string)
                print("Divided text: ", item_txt)
                print(name_div, item_txt)
                if item_txt == name_div:  # First female entry
                    divide = True
                if item_txt == name_fin[i]:  # Last acceptable entry
                    adder = str(item_txt)

                    df = df.append({"name": adder, "tag": "F", "origin": origins},
                                   ignore_index=True)
                    break

                if item_txt is not None:
                    adder = str(item_txt)
                    parts = re.split(r'[;,\s]\s*', adder)  # removes any double names that are not hyphinated
                    print(parts)
                    adder = parts[0]
                    if not adder.strip():
                        print("Not Found")
                        pass
                    print(adder)
                    if adder == name_div[-1]:
                        # Had to add this to fix the polish names set, should rework later
                        divide = True
                    if not divide:
                        df = df.append({"name": adder, "tag": "M", "origin": origins},
                                       ignore_index=True)
                    else:
                        df = df.append({"name": adder, "tag": "F", "origin": origins},
                                       ignore_index=True)
            print(df)
    for e in nations:
        print(e)
        g = df.loc[df["origin"] == e]
        print("DF IS + {}".format(g), g)
        print(g, g["tag"].value_counts())

    df_clean = clean_df(df)
    return df_clean


def read_category_names(df_category, key, origins, gender):
    print("Value is from Wikipedia")
    file = requests.get(key)
    soup = BeautifulSoup(file.content, "lxml")
    # First things first the soup needs to search if there is a next page
    div_tag = soup.find_all("div", {"id": "mw-pages"})
    for tag in div_tag:
        list_tag = tag.find_all("li")
        for name in list_tag:
            name = name.string.split("(")[0]  # Incase of any disambiguations or other issues
            print(name, "\n", origins, gender)
            if any(re.findall(r"Appendix|learn more|previous|List|Surnames|name", name, re.IGNORECASE)):
                print("Invalid name: ", name)
            else:
                print(name, gender, origins)
                df_category = df_category.append({"name": name, "tag": gender, "origin": origins}, ignore_index=True)
        a_tag = tag.find_all("a", href=True)
        for a_link in a_tag:
            if "next page" in a_link.string:
                print("There is a page in the tag: {}".format("https://en.wikipedia.org" + a_link["href"]))
                df_category = read_category_names(df_category, "https://en.wikipedia.org" + a_link["href"], origins,
                                                  gender)
                break
    print(df_category)
    return df_category


def read_wiki_names():
    total_names = 0
    valid_names = {}
    print("Hello")
    files = ["https://en.wikipedia.org/wiki/Category:Feminine_given_names",
             "https://en.wikipedia.org/wiki/Category:Masculine_given_names"]
    # Would be possible to add the following links, but i have decided against it "https://en.wiktionary.org/wiki/Category:Female_given_names_by_language", "https://en.wiktionary.org/wiki/Category:Male_given_names_by_language"
    for file_url in files:
        file = requests.get(file_url)
        print(file_url)
        soup = BeautifulSoup(file.content, "lxml")
        div_tag = soup.find_all("div", {"class": "CategoryTreeItem"})
        for article in div_tag:
            print(article.text)
            try:
                span_tag = article.find_all("span", {"dir": "ltr"})[
                    0]  # The first span element with this tag holds the length of the article
                print(span_tag)
                if "," in span_tag.string:
                    span_checker = span_tag.string.split(",", 1)[1]
                else:
                    span_checker = span_tag.string

                span_checker = re.sub('[^0-9]', '', span_checker)
                if int(span_checker) >= 25:
                    total_names = total_names + int(span_checker)
                    print(article, total_names)
                    valid_names.update({article.a.text: file_url})
            except:
                pass

    print(valid_names, "\n\n\n", int(total_names))
    return valid_names


def clean_df(df):
    df["name"] = df["name"].str.replace("[^\w\s]", "")
    df["name"] = df["name"].str.replace("[\b\d+(?:\.\d+)?\s+]", "")
    df = df.dropna(axis=0, how='any', thresh=None, subset=None, inplace=False)
    df = df.drop_duplicates(subset="name", keep="first")
    return df


def start_tests(file_in, nation):
    print("Starting test case ...\nUsing the following values", file_in, nation)
    nation_abrev = nation
    correct_responses = []
    for i in range(len(file_in)):  # Goes through both files (csv and excel)
        df_arg = file_in[i]  # Created dataframe
        for i in range(len(nation_abrev)):  # Goes through each nationality present

            # print(i) Test
            df_temp = df_arg.loc[df_arg["origin"] == nation_abrev[i]]  # Loads temp dataframe filled with nationality
            if df_temp.size > 99:  # If the temp file is bigger than 10, assume the DF is correctly loaded
                print("Size of names relating to : {} is adequate".format(nation_abrev[i]))
                correct_responses.append(i)  # adds to list
            else:
                print("Origin is missing names, would recommend adding files")
                return False

    if len(correct_responses) == len(nation_abrev) * 2:
        print("Tests appear to be fine, you can skip the BS4 implementation")
        return True
    else:
        return False


def translit_non_latin(df):
    # This function will first add names that are in non latin cases, eg. russian names and
    # Will translate them along with any other names that already exist in the DF
    non_latin_languages = ["Russia", "Serbia"]
    print("*\n*\n*\n*\n*\n")
    for column in df.columns:
        df_copy = df.loc[(df["origin"] == "Serbia") | (
                    df["origin"] == "Russia")]  # Add any other languages that may use Cyrillic Script
        for index, row in df_copy.iterrows():
            name = row[0]
            language_code = detect_language(name)
            if language_code is not None:
                print("Translating ...")
                print(language_code)
                print(row)
                print(translit(name, "{}".format(language_code), reversed=True))
                latin_name = translit(name, "{}".format(language_code), reversed=True)
                df.at[index, "name"] = latin_name
    print("New Dataframe using translated names", df)
    return df


def generate_city_input():
    # Function will use DCGAN with geonames to create plausible settlement / city names along side NPC generator
    # https://www.geonames.org/
    print("This function has not been implemented yet")


def form_files(data):
    # Aims to create an SQL version of the dataframe
    data.to_sql("")
    data.to_excel("npcs.xlsx", index=False)
    data.to_csv("npcs.csv", index=False)
    print("Not implemented yet")
    # Continue Later
    # data.to_sql()

def check_counts():
    if os.path.exists("name_data/names_merged.xlsx"):
        print("Final output exists, proceeding")
        df = pd.read_excel("names_merged.xlsx")
        tags = list(pd.unique(df["origin"]))
        for g in tags:
            nation_df = df[df["origin"] == g]
            print("Nationality: {0} \nContains: {1} Values\n {2}".format(g, nation_df.size, nation_df["tag"].value_counts()))

    else:
        print("Final output does not exist, please create the file using splice names function")

def move_to_sql():
    if os.path.exists("name_data/names_merged.xlsx"):
        #print("Final output exists, proceeding")
        df = pd.read_excel("names_merged.xlsx")
        #print(df)
        conn = sqlite3.connect("name_data/names_merged.db")
        c = conn.cursor()
        c.execute('CREATE TABLE NAMES (name text, tag text, origin text)')
        conn.commit()
        df.to_sql('NAMES', conn, if_exists='replace', index = False)
        new_df = pd.read_sql(sql='SELECT * FROM NAMES', con=conn)
        #print(new_df)

def get_sql_names():
    try:
        conn = sqlite3.connect("name_data/names_merged.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(cursor.fetchall())
        new_df = pd.read_sql_query(sql="SELECT * FROM 'NAMES'", con=conn)
        return new_df
    except Exception as e:
        print("Something went wrong", e)

def find_location_names(number_of_values=10, user_arg="France"):
    #TODO: Create alternative that copies the gen_townnames_.db from this directory to the history gen directoy, using try and except
    conn = sqlite3.connect('C://Users//jedel//PycharmProjects//Lorem_Ipsum_Gen//Name_Gen//gen_townnames_.db')
    c = conn.cursor()
    df = pd.read_sql(sql='SELECT * FROM NAMES', con=conn)
    #Left out austria because there is somethign wrong with it atm
    european_group = ['Albania', 'Belarus', 'Belgium', 'Bulgaria', 'Croatia', 'Czech Republic', 'Estonia', 'Finland', 'France',
    'Germany', 'Greece', 'Hungary','Ireland',
    'Italy', 'Kosovo', 'Latvia', 'Luxembourg', 'Macedonia',
    'Malta', 'Netherlands', 'Norway','Poland', 'Portugal',
    'Romania', 'Russia', 'Serbia', 'Slovakia', 'Slovenia',
    'Spain', 'Sweden', 'Switzerland','Turkey',
    'Ukraine', 'United Kingdom']
    #df = df[df["Origin"].isin(european_group)]

    #df_culture = df[df["Origin"] == random.choice(pd.unique(df["Origin"]))]
    df_culture = df[df["Origin"] == user_arg]
    out_value = df_culture.sample(number_of_values)

    location_dict = {"{}".format(df_culture["Origin"].iloc[0]) : out_value["Name"].to_list()}

    return location_dict


locations = find_location_names(20, "France")
print(locations)