import random
import sqlite3
import os
from pprint import pprint

import pandas as pd; import numpy as np
import requests; import os; import re; import addon_namegen

from unidecode import unidecode



jobs = """
Baker; Brewer; Butcher; Distiller; Farmer; Fisherman; Fruit Picker; Gatherer; Grocer; Peasant; Miller; Shepherd; Smoker; Falconer; Farrier; Groom; Houndsman; Stablehand; Artist; 
Jester; Minstrel; Performer; Crier; Envoy; Herald; Messenger;
Architect; Carpenter; Cooper; Mason; Painter; Roofer; Shipbuilder; Thatcher; Wheelwright; Atilliator (Crossbow Maker); Bookbinder; Bowyer; Brazier; 
Candlemaker; Cobbler; Currier; Draper; Dyer; Fletcher; Furrier; Glassblower; Jeweller; Knitter; Leatherworker; Potter; Roper; Sailmaker; Sewer; Sculptor; 
Shoemaker; Cordwainer; Smelter; Smith; Blacksmith; Swordsmith; Armoursmith; Goldsmith; Silversmith; Spinner; Tailor; Tanner; Weaver; Woodcarver; Woodcrafter;
Calligrapher; Cartographer; Librarian; Printer; Scholar; Scribe; Tutor;
Chef; Cook; Innkeeper; Scullion; Servant; Wench; Whore (Escort);
Banker (Moneylender); Baron; Guard; Inquisitor; Judge; Knight; Lawyer; Marshal; Priest (Canon); Reeve; Sexton; Sheriff; Taxer; Theologian; Warden;
Miner; Woodcutter; Alchemist; Apothecary; Cultist; Herbalist; Physician; Shaman; Soothsayer; Street Magician; Surgeon; Wiseman; Witch;
Archer; Barber; Beggar; Bottler; Charcoal Burner; Ditcher; Drayman; Ewerer (Water Boiler); Executioner; Gardener; 
Gamekeeper; Hunter; Mercenary; Mercer; Navigator; Night Soil Man; Ranger; Sailor; Shoveler; Thief; Merchant
"""
job_cleaned = re.sub("\n", "", jobs)
job_choice = job_cleaned.split(";")
yes_list, no_list, quit_list = ["y", "yeh", "yes", "yep", "ye"], ["n", "no", "nah", "nope"], ["q", "quit", "exit"]



def npc_options():
    try:
        #TODO: Implement way to read from SQL instead of XLSX, as the constant interaction can lead to corruption

        console_running = True
        while console_running is True:
            npc_data_exists(True)
            try:

                conn = sqlite3.connect("names_merged_test.db")
                print("Connected to ", conn)
                df_arg = pd.read_sql_query(sql="SELECT * FROM NAMES", con=conn)
            except Exception as e:
                print("SQL file didnt work, using backup", e)
                df_arg = pd.read_excel("names_merged.xlsx")
            #print(df_arg, pd.unique(df_arg["origin"]))
            #print(df_arg)
            #Use this to reset fantasy tags to reapply with console
            # try:
            #     df_arg = df_arg.drop(df_arg[(df_arg["origin"] == "Tiefling") |  (df_arg["origin"] == "Half-Orc")
            #                                 | (df_arg["origin"] == "Halfling") | (df_arg["origin"] == "Gnome")
            #                                 | (df_arg["origin"] == "Elf") | (df_arg["origin"] == "Dwarf") | (df_arg["origin"] == "Dragonborn")].index)
            # except:
            #     pass

            print("Loading NPC options ...")
            culture_list = pd.unique(df_arg["origin"])
            culture_list = culture_list.tolist()
            #do_enum(culture_list)
            non_relevant = []
            for i in culture_list:
                df_temp = df_arg.loc[df_arg["origin"] == i]
                #print(df_temp)
                if any(df_temp["tag"] != "N"):
                    pass
                    #print("This dataframe has regular names")
                else:
                    non_relevant.append(i)

                    #print("This dataframe has no regular names")
                    #print(pd.unique(df_temp["tag"]))
            non_relevant_last = []
            for g in culture_list:
                df_temp_g = df_arg.loc[df_arg["origin"] == g]
                #print(df_temp_g)
                if any(df_temp_g["tag"] == "N"):
                    pass
                    #print("This DF contains last names")
                else:
                    non_relevant_last.append(g)

                    #print("This DF contains no last names")


            africa = ["African", "Ethiopia"]
            arb_tag = ['Arabia', 'Armenia', 'Azerbaijan', 'Israel', 'Persian', 'Kazakhstan', 'Turkey']
            arabia = arb_tag
            asia = sorted(['Philippines', 'China', 'India', 'Persian', 'Japan', 'Kazakhstan', 'Korea', 'Pakistani', 'Srilanka', 'Vietnam', "Hawaiian"])
            europe = sorted(['Albania', 'Armenia', 'Austria', 'Azerbaijan', 'Balkan', 'Basque', 'Russia', 'Belgium', 'France', 'Bulgaria', 'Celtic', 'Czech', 'Denmark', 'Dutch', 'East Frisia', 'England',
                        'Estonia', 'Norway', 'Finland', 'Georgia', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Italy', 'Latin', 'Latvia', 'Lithuania',
                        'Luxembourg', 'Macedonia', 'Malta', 'Romania', 'Poland', 'Portugal', 'Scandinavian', 'Slavic', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Swiss', 'Turkey', 'Ukraine'])

            fantasy = sorted(["Tiefling", "Half-Orc", "Halfling", "Gnome", "Elf", "Dwarf", "Dragonborn"])

            #Fantasy genders are assorted into NN and N
            union_list = [arabia, asia, europe, fantasy]
            #union_text_list = [af_tag, arb_tag, as_tag, euro_tag, fantasy_tag]
            drop_list = []
            for i in union_list:

                for item in i:
                    df_temp = df_arg.loc[df_arg["origin"] == item]
                    #print(df_temp)
                    if len(pd.unique(df_temp["tag"])) == 1:
                        drop_list.append(item)
                        i.remove(item)
                    else:
                        pass
            #print("Printing Drop List: ", drop_list)


            #Clean dataframe to remove "does not exist" issues
            if not drop_list:
                print("All entries are complete, no need to add any new names ...")
                #print(df_arg[df_arg.duplicated(subset=None, keep="first")])
                df_duplicates = df_arg.duplicated()
                #print(df_duplicates)
                if df_duplicates.size >= 1:
                    df_arg.drop_duplicates(keep="first", inplace=True)
                    #print(df_arg)
                    df_arg.to_excel("names_merged.xlsx", index=False)
                #df_arg = df_arg.drop_duplicates(keep="first")
                #print(pd.unique(df_arg["origin"]))
            elif len(drop_list) > 0:
                print("There are names missing, adding new names using BS4, this may take a minute ...")
                print(drop_list)
                print(non_relevant)
                df_arg = create_duplicate_names(df_arg, non_relevant_last, non_relevant)
                temp = df_arg[(df_arg["origin"] == "Ethiopia")]
                print(pd.unique(temp["tag"]))
            #Used later to ensure there is always a quit option
            #Assigns cultural lists to regions

            regions = {"African": africa, "Europe": europe,"Near East": arabia, "Asia": asia, "Experimental: Fantasy": fantasy}

            print("Type the number of NPC's you wish to create: ")
            npc_num = None
            while npc_num is None:
                try:
                    num_arg = int(input(""))
                    if str(num_arg).lower() in quit_list:
                        npc_num = num_arg
                        console_running = False
                    elif num_arg >= 501 or num_arg <= 0:
                        print("The program can only create between 1 and 100 npc's, please ensure you type a number between these two values, try again")
                    else:
                        npc_num = num_arg
                except:
                    print("There was an error, please ensure the input is a valid whole number")

            print("Are the NPC's the same culture as each other? [y/n]")
            single_culture = None

            while single_culture is None:
                try:
                    culture_arg = input("")
                    if culture_arg.lower() in yes_list:
                        print("Creating NPC's with the same culture")
                        single_culture = True
                    elif culture_arg.lower() in no_list:
                        print("Creating NPC's with different cultures")
                        single_culture = False
                    elif culture_arg.lower() in quit_list:
                        console_running = False
                    else:
                        print("There was an error, please ensure the input corresponds to yes or no")
                except:
                    print("There was an error, please ensure the input corresponds to yes or no")

            origin_list = list(regions.keys())
            if single_culture is True or int(npc_num) == 1:
                selected_nation = select_group(origin_list, regions)
                out_df = show_npc(df_arg, selected_nation, npc_num)

                #show_table(out_df)

                pprint(out_df)
                download_excel([out_df])
            elif single_culture is False:
                print("Please type the number of different NPC groups you wish to create, each with their own culture")
                groups = non_single_culture(df_arg, origin_list, regions, npc_num)

                download_excel(groups)

                # Previous implementation
                # while group_iter != npc_out:
                #     npc_out = divide_npc_multiculture(npc_num, group_iter)
                #     print("Group sizes are", npc_out)
                #     for i in npc_out:
                #         print("Selecting NPC's for the Group with size {}".format(npc_out))
                #         selected_nation = select_group(origin_list, regions)
                #         out_df = show_npc(df_arg, selected_nation, int(i))
                #         #show_table(out_df)
                # print("Creating temporary excel file, set to user downloads")
                # #Source of code snippet found here - https://www.reddit.com/r/learnpython/comments/4dfh1i/how_to_get_the_downloads_folder_path_on_windows/
                # #out_df.to_excel("generated-names-multiple.xlsx")
                # #os.remove("generated-names-multiple.xlsx")
                # print(out_df)
                # #print(groupings)
            console_running = False

        print("Program Finished | Press anything to end")
        input()


        # else:
        #     npc_data_exists(False)

    except FileNotFoundError:
        print("The file may be corrupted, creating new file ...")
        npc_data_exists(False)


def download_excel(groups):
    print("Would you like to download the names as a file [y/n]? This will be stored in your Downloads under {}".format(
        os.path.join(os.getenv('USERPROFILE'), 'Downloads')))
    deciding = True
    # TODO: Add an option to use a CSV file format, as more people have word documents and it may be objectively better than Excel
    while deciding:
        download_arg = input("")
        if download_arg.lower() in yes_list:
            print("Downloading Excel file")
            from datetime import datetime
            now = datetime.now()
            date_string = now.strftime("%d-%m-%Y-%H%M")
            print(r"Argument: {0}\fluffys_generated_names_{1}.xlsx".format(
                os.path.join(os.getenv('USERPROFILE'), 'Downloads'), date_string))
            argument = r"{0}\fluffys_generated_names_{1}.xlsx".format(
                os.path.join(os.getenv('USERPROFILE'), 'Downloads'), date_string)
            writer = pd.ExcelWriter(argument, engine='xlsxwriter')

            g = 0
            for x in groups:
                g += 1
                print(x)
                x.to_excel(writer, sheet_name="Group {} names".format(g))
            writer.save()
            print("Done")
            os.system('start "excel" {}'.format(argument))
            deciding = False
        elif download_arg.lower() in no_list:
            print("Skipping Download")
            deciding = False
        elif download_arg.lower() in quit_list:
            console_running = False
            break
        else:
            print("There was an error, please ensure the input corresponds to yes or no")


def non_single_culture(df_arg, origin_list, regions, npc_num):
    group_iter = int(input("Groups: "))
    print("Groups amount to ", group_iter)
    groups = []
    print("NPC Total: {}".format(npc_num))
    npc_calc = npc_num
    i = 0
    while i <= group_iter - 1:
        try:
            print("Please type the size of Group {}".format(i + 1))
            size_arg = input("Size: ")
            npc_calc = npc_calc - int(size_arg)
            print("NPC's Remaining: {}".format(npc_calc))
            if npc_calc >= 0 and int(size_arg) > 0:
                i += 1
                groups.append(size_arg)
                #print(i)
            elif npc_calc < 0:
                print("Too many NPC's, ensure your input does not exceed the maximum")
                npc_calc = npc_calc + int(size_arg)
                print("NPC's Remaining: {}".format(npc_calc))
            elif npc_calc == 0 and i < group_iter-1:
                print("You have reached the maximum NPC limit, without filling out all of your groups, would you like to continue anyway? [y/n]")
                user_in = input("")
                if user_in.lower() in yes_list:
                    groups.append(size_arg)
                    break
                elif user_in.lower() in no_list:
                    npc_calc = npc_calc + int(size_arg)
                    pass
            else:
                print("Please ensure your input is a number")
        except:
            pass
    print(groups)
    frames = []
    for g in range(len(groups)):


        print("Selecting NPC's for Group {0} with size {1}".format(g+1, groups[g]))
        selected_nation = select_group(origin_list, regions)
        #TODO: Add version of show NPC's where the origin is displayed
        out_df = show_npc(df_arg, selected_nation, int(groups[g]))

        frames.append(out_df)
        #show_table(out_df)
    for k in frames:
        print(k)
    return frames







def select_group(origin_list, regions):
    print("Please select the NPC('s) culture region")
    uncompleted = True
    while uncompleted:
        try:
            do_enum(regions)
            choice = int(input("Number: "))  # Ensures input is int
            dict_arg = origin_list[choice - 1]  # Lists start at 0
            regions_refined = regions.get(dict_arg)

            do_enum(regions_refined)
            choice = int(input("Number: "))
            selected_nation = regions_refined[choice - 1]
            uncompleted = False
            return selected_nation
        except:
            print("Please ensure your selection is a valid number")

def divide_npc_multiculture(npc_num, group_iter):

    print("NPC Total: {}".format(npc_num))
    groupings = []
    npc_calc = npc_num
    for i in range(group_iter):
        print(groupings)
        try:

            print("Please type the size of Group {}".format(i + 1))
            size_arg = input("Size: ")
            npc_calc = npc_calc - int(size_arg)
            if npc_calc >= 0:

                groupings.append(int(size_arg))
                print("{} NPC's remaining".format(npc_calc))
                print(groupings)
            elif npc_calc < 0:
                print("\n\n\nOne of your groups is invalid, restarting selection"
                      "\nPlease ensure that your groups do not exceed the NPC total of {0}".format(npc_num))
                divide_npc_multiculture(npc_num, group_iter)

        except:
            print("There are still NPC's remaining, please ensure your groups fill the NPC requirements")

    #Play around with the idea that groupings should equal length of npc groups
    return groupings


def show_npc(df, nations, num_npcs):
    #Add information about gender of NPC, as some languages are hard to see the difference between
    print("Taking random value from data, returning {0} NPC names from {1} culture group".format(num_npcs, nations))
    df = df.loc[df["origin"] == nations]
    df_num = df["name"].str.contains("[0-9]+", regex=True, na=False) #Simple way to filter out any results with numbers in
    df = df[~df_num] #Returns all non-valid results, aka ones that dont fit the regex pattern
    rand_name, rand_surname = df.loc[df["tag"] != "N"], df.loc[df["tag"] == "N"]
    gender_tags, neutral_genders = { "WM": ["Male", "Female"], "WF": ["Female", "Male"]},  ["Female", "Male"]
    pyside_df = pd.DataFrame(columns=["Gender", "Name", "Job"])
    npc_division = round(num_npcs / 2)
    print("Num is ", npc_division)
    over_num, counter = npc_division + npc_division, 0

    for i in range(num_npcs):
        if counter % 2 == 0:
            counter += 1
            rand_name = df.loc[(df["tag"] == "M") | (df["tag"] == "NN") | (df["tag"] == "WM")]
            gender_in = "M"
            pyside_df = append_npc(gender_tags, neutral_genders, pyside_df, rand_name, rand_surname, gender_in)
        else:
            counter += 1
            rand_name = df.loc[(df["tag"] == "F") | (df["tag"] == "NN") | (df["tag"] == "WF")]
            gender_in = "F"
            pyside_df = append_npc(gender_tags, neutral_genders, pyside_df, rand_name, rand_surname, gender_in)
    pprint(pyside_df)
    return pyside_df







def append_npc(gender_tags, neutral_genders, pyside_df, rand_name, rand_surname, gender_in):
    f_name, l_name, job = np.random.choice(rand_name["name"], 1), np.random.choice(rand_surname["name"],
                                                                                   1), np.random.choice(
        job_choice, 1)
    job = re.sub(r'[^\w\s]', '', str(job))
    gender_name = re.sub(r'[^\w\s]', '', str(f_name))
    try:
        new = re.findall('[A-Z][^A-Z]*', gender_name)
        if len(new) > 1:
            gender_name = "-".join(new)
        else:
            gender_name = "".join(new)
    except:
        pass
    f_gender = rand_name.loc[rand_name["name"] == str(gender_name)]
    f_gender = f_gender["tag"].values
    f_gender = re.sub(r'[^\w\s]', '', str(f_gender))
    # name_group = re.findall('[A-Z][^A-Z]*', str(l_name))
    # if len(name_group) > 1:
    #     print(name_group)
    #     l_name = "-".join(name_group)
    # Cases NN, WF, WM
    f_gender = find_gender(gender_in, gender_tags, neutral_genders)
    print(f_gender)
    # Verifies if names are made up of char's
    gender = str(f_gender)
    name = str(f_name + " " + l_name)
    name = str(name.title())
    # Investigate numeric names in arabic name list, should of been fixed using the str.contains line above
    # print(name)
    name = re.sub(r'[^\w\s-]', '', name)
    pprint("{0} NPC: {1}".format(gender, name))
    pyside_arg = {"Gender": "{}".format(gender), "Name": "{}".format(name), "Job": "{}".format(str(job))}
    pyside_df = pyside_df.append(pyside_arg, ignore_index=True)
    #pyside_arg = {"NPC Data": "{0} NPC: {1}".format(gender, name)}
    #pyside_df = pyside_df.append(pyside_arg, ignore_index=True)
    return pyside_df


def find_gender(f_gender, gender_tags, neutral_genders):
    rand_num = random.randint(0, 100)
    if rand_num < 70 and f_gender in gender_tags.keys():
        f_gender = gender_tags.get(f_gender[0])
    elif rand_num >= 70 and f_gender in gender_tags.keys():
        f_gender = gender_tags.get(f_gender[1])
    elif "NN" in f_gender:#Strange issue with newly added files, adding the tag "NN NN"
        f_gender = neutral_genders[random.randint(0, 1)]
    elif "M" in f_gender:
        f_gender = "Male"
    elif "F" in f_gender:
        f_gender = "Female"
    return f_gender


def do_enum(args):
    for number, origin in enumerate(args, start=1): #cleaner that using enumerate constantly
        print(number, " ", origin)

def create_duplicate_names(df, add_last_names, remove_or_add):
    print("Dataframe argument: ", df)

    print("Names to add last names to, please implement these names in the addon_pack_namegen.py file if any adequate data sources are found: ", add_last_names)
    #https://fr.wiktionary.org/wiki/Cat%C3%A9gorie:Pr%C3%A9noms_masculins_en_pirah%C3%A3 - Native american
    #https://fr.wiktionary.org/wiki/Annexe:Liste_de_pr%C3%A9noms_b%C3%A9t%C3%A9 - African
    #https://en.wikipedia.org/wiki/Category:Yoruba_given_names - African
    #The URL's below are ones that where non valid, but i found over time new information to make them usable, add any other non valid files here, this could be done in the namegen file
    #But since it is so few results currently it seems like a waste to restart the entire creation process
    url_dict = {"African": "https://fr.wiktionary.org/wiki/Annexe:Liste_de_pr%C3%A9noms_b%C3%A9t%C3%A9", "Yoruba": "https://en.wikipedia.org/wiki/Category:Yoruba_given_names",
                "Ethiopia": "https://en.wikipedia.org/wiki/Category:Ethiopian_given_names", "Hawaiian": "https://en.wiktionary.org/wiki/Category:Hawaiian_male_given_names",
                "Hawf": "https://en.wiktionary.org/w/index.php?title=Category:Hawaiian_female_given_names&pageuntil=POLI%CA%BBAHU%0APoli%CA%BBahu#mw-pages"}
    name_fin = ["Zobe", "Yinka", "Zewde", "ʻŌpūnui", "Piʻilani"]
    df = addon_namegen.add_stragglers(df, url_dict, name_fin)
    if "Unisex" in add_last_names:
        add_last_names.remove("Unisex")
    print("Lists to remove or add first names to, if has not already been done via\nadd_stragglers(): ", remove_or_add)
    #Add new elemnt to last_name_donor if the add_last_names list expands, uses and copies pre existing last names for values without last names
    last_name_donor = ["Germany", "Dutch", "Norway", "Balkan"]
    print(len(add_last_names), add_last_names)
    for i in range(len(add_last_names)):
        print(i, last_name_donor[i])
        df_temp = df[(df["origin"] == last_name_donor[i]) & (df["tag"] == "N")]
        df_x = df_temp.copy() #Supresses copy warning, otherwise useless
        #Replaces value I with value I from both lists, for instance if I = 0 then the copied Germany values will be replaced with Austria
        df_x["origin"] = df_x["origin"].replace(str(last_name_donor[i]), str(add_last_names[i]))
        #print(df_x.tail(10))
        frames = [df, df_x]
        #Merges copied values into existing dataframes
        df = pd.concat(frames, ignore_index=True)
        #print(df)
        #print(pd.unique(df.columns))
        #for g in df.columns:
            #print(pd.unique(df[g]))
    try:
        df = df.drop(columns=['Unnamed: 0'])
    except:
        pass
    #print(df)
    #TODO: update to work with SQL
    #New dataframe is called to replace old dataframe that
    #df.to_excel("names_merged.xlsx", index=False)

    return df
#yes

def npc_data_exists(exists):
    if exists:
        print("Retrieving NPC's ...")
        #Passes through to main function
    elif exists is not True:
        print("'Names_merged' does not currently exist\n"
              "Creating new file, this may take a while....")
        df = addon_namegen.splice_names()
        npc_options()

#TODO: Add option importing names from addon_namegen.py using find location names function
npc_options()