import requests
import json
import time
import re
import shutil
from pathlib import Path
from datetime import datetime
import os.path
from math import floor

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf

start = time.time()

api_key = ""

if api_key == "":
    print("You have to supply your own api_key from https://tarkov-market.com")
    exit()

api_bsg = {}
api_market = {}
ids = []

PRICETOGET = "price"

slot_type_translator = {'mod_scope': 'Sights',
                        'mod_tactical_000': 'Tactical Mod',
                        'mod_handguard': 'Handguard',
                        'mod_sight_front': 'Front Sights',
                        'mod_mount_000': 'Mount',
                        'mod_mount_001': 'Mount',
                        'mod_mount_002': 'Mount',
                        'mod_foregrip': 'Foregrip',
                        'mod_tactical': 'Tactical Mod',
                        'mod_muzzle': 'Muzzle device',
                        'mod_muzzle_000': 'Muzzle device',
                        'mod_muzzle_001': 'Muzzle device',
                        'mod_sight_rear': 'Rear Sights',
                        'mod_mount': 'Mount',
                        'launcher_0_grenade': 'Launcher',
                        'mod_nvg': 'Sights',
                        'mod_tactical_001': 'Tactical Mod',
                        'mod_tactical_002': 'Tactical Mod',
                        'mod_tactical_003': 'Tactical Mod',
                        'mod_flashlight': 'Flashlight',
                        'mod_scope_000': 'Sights',
                        'mod_scope_001': 'Sights',
                        'mod_stock': 'Stock',
                        'mod_scope_002': 'Sights',
                        'mod_scope_003': 'Sights',
                        'mod_stock_000': 'Stock',
                        'mod_pistolgrip': 'Pistol grip',
                        'mod_pistol_grip': 'Pistol grip',
                        'mod_stock_axis': 'Stock',
                        'mod_mount_003': 'Mount',
                        'mod_gas_block': 'Gas block',
                        'mod_bipod': 'Bipod',
                        'mod_tactical001': 'Tactical Mod',
                        'mod_tactical002': 'Tactical Mod',
                        'mod_tactical_2': 'Tactical Mod',
                        'mod_mount_004': 'Mount',
                        'mod_mount_005': 'Mount',
                        'mod_mount_006': 'Mount',
                        'mod_tactical_004': 'Tactical Mod',
                        'mod_barrel': 'Barrel',
                        'mod_magazine': 'Magazine',
                        'mod_reciever': 'Receiver',
                        'mod_charge': 'Charging handle',
                        'mod_launcher': 'UBGL',
                        'mod_pistol_grip_akms': 'Pistol grip',
                        'mod_stock_akms': 'Stock',
                        'mod_stock_001': 'Stock'}

with open('nodeid.json') as json_file:
    ids = json.load(json_file)


my_file = Path('bsg.json')
if my_file.is_file() and (datetime.now() - datetime.fromtimestamp(os.path.getmtime('bsg.json'))).total_seconds() <= 24 * 60 * 60:
    with open('bsg.json', "r") as json_file:
        api_bsg = json.load(json_file)
else:
    p = requests.get("https://tarkov-market.com/api/v1/bsg/Items/all?x-api-key=" + api_key)
    api_bsg = json.loads(p.content)
    with open('bsg.json', 'w+') as outfile:
        outfile.truncate(0)
        json.dump(api_bsg, outfile)

my_file = Path('tk market.json')
if my_file.is_file() and (datetime.now() - datetime.fromtimestamp(os.path.getmtime('bsg.json'))).total_seconds() <= 60 * 60:
    with open('tk market.json', "r") as json_file:
        api_market = json.load(json_file)
else:
    while True:
        p = requests.get("https://tarkov-market.com/api/v1/Items/all?x-api-key=" + api_key)
        if p.status_code == 200:
            break
        print(p.status_code)
        time.sleep(5)
    p = requests.get("https://tarkov-market.com/api/v1/Items/all?x-api-key=" + api_key)
    r = json.loads(p.content)
    for i in r:
        api_market[str(i["bsgId"])] = i
    with open('tk market.json', 'w+') as outfile:
        outfile.truncate(0)
        json.dump(api_market, outfile)


print(f"Temps écoulé : {round(time.time()-start,1)}s")


def download(item_id):
    if not wait_dl.is_visible():
        wait_dl.show_all()
        wait_dl.get_window().set_decorations(Gdk.WMDecoration.BORDER)
        while Gtk.events_pending():
            Gtk.main_iteration()
    for key in ["icon", "img", "imgBig"]:
        if key not in api_market[item_id] or api_market[item_id][key] == "":
            continue
        reg = re.search("\.png|\.gif|\.jpg", api_market[item_id][key].lower())
        if reg is None:
            print("Erreur avec " + api_market[item_id][key])
            continue
        path = "Images/" + key + "/" + item_id + reg.group(0)
        my_file = Path(path)
        if not my_file.is_file():
            try:
                r = requests.get(api_market[item_id][key], stream=True)
                # Check if the image was retrieved successfully
                if r.status_code == 200:
                    # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                    r.raw.decode_content = True

                    # Open a local file with wb ( write binary ) permission.
                    with open(path, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)

                    print('DL:', path)
                else:
                    time.sleep(5)
            except requests.exceptions.MissingSchema:
                print(api_market[item_id][key])


def get_path_img(folder, id):
    for fix in [".png", ".jpg", ".gif"]:
        path = f"Images/{folder}/{id}{fix}"
        my_file = Path(path)
        if my_file.is_file():
            return path
    return ""


def get_path_first_img(item_id, folders=["imgBig", "img", "icon"]):
    for f in folders:
        p = get_path_img(f, item_id)
        if p != "":
            return p
    download(item_id)
    return get_path_first_img(item_id, folders)


def download_all_img():
    for item_id, dict in api_bsg.items():
        if item_id in api_market and (dict["_parent"] in ids["Weapon"] or dict["_parent"] in ids["Mod"]) and dict["_type"] == "Item":
            download(item_id)


def space(name):
    return re.sub(r"([a-z])([A-Z])", "\\1 \\2", name)


def generate_id():
    mod = ""
    for id, dict in api_bsg.items():
        if dict["_type"] == "Node":
            if dict["_name"] == "Mod":
                print("Mod : " + id)
                mod = id
                break

    print("----")
    modcat = []
    for id, dict in api_bsg.items():
        if dict["_parent"] == mod and dict["_type"] == "Node":
            print(dict["_name"] + " : " + id)
            modcat.append(id)
    modtype = {}
    print("----")
    for id, dict in api_bsg.items():
        if dict["_parent"] in modcat and dict["_type"] == "Node":
            print(dict["_name"] + " : " + id)
            modtype[id] = space(dict["_name"])
    print("----")
    for id, dict in api_bsg.items():
        if dict["_parent"] in modtype and dict["_type"] == "Node":
            print(dict["_name"] + " : " + id)
            modtype[id] = space(dict["_name"])
    weapon = ""
    for id, dict in api_bsg.items():
        if dict["_type"] == "Node":
            if dict["_name"] == "Weapon":
                weapon = id
    print("----")
    weaponcat = {}
    for id, dict in api_bsg.items():
        if dict["_parent"] == weapon:
            print(dict["_name"] + " : " + id)
            weaponcat[id] = space(dict["_name"])

    print("----")
    slot_dict = {}
    for id, dict in api_bsg.items():
        if dict["_parent"] in modtype or dict["_parent"] in weaponcat:
            if "Slots" in dict["_props"]:
                for s in dict["_props"]["Slots"]:
                    if "mod_mount" in s["_name"]:
                        slot_dict[s["_name"]] = "Mount"
                    elif "mod_tactical" in s["_name"]:
                        slot_dict[s["_name"]] = "Tactical Mod"
                    elif s["_name"] not in slot_dict:

                        mid = s["_props"]["filters"][0]["Filter"][0]

                        maxid = "5448fe124bdc2da5018b4567"
                        pid = api_bsg[mid]["_parent"]

                        path = []
                        while pid != maxid:
                            if pid == "":
                                break
                            path = [pid] + path
                            pid = api_bsg[pid]["_parent"]
                        txt = dict["_props"]["Name"] + " : "
                        for p in path:
                            if "Name" in api_bsg[p]["_props"]:
                                txt += api_bsg[p]["_props"]["Name"] + " (" + api_bsg[p]["_name"] + "), "
                        print(txt)
                        if "Name" in api_bsg[path[1]]["_props"]:
                            slot_dict[s["_name"]] = api_bsg[path[1]]["_props"]["Name"]

    print(slot_dict)

    with open('nodeid.json', 'w') as outfile:
        outfile.truncate(0)
        json.dump({"Mod": modtype, "Weapon": weaponcat}, outfile)


stats = {"RecoilForceUp": True, "RecoilForceBack": True, "Ergonomics": False, "Velocity": True, "Cost": False}


def mod_to_list(id):
    l = [api_market[id]["name"]]
    for x in stats:
        l.append(api_bsg[id]['_props'][x])
    l.append(api_market[id][PRICETOGET])

    return l


class Item():
    def __init__(self, id):
        self.id = id
        self.name = api_market[id]["name"]
        self.mods = {}
        for s in api_bsg[id]["_props"]["Slots"]:
            self.mods[s["_name"]] = None

    def add_mod(self, idmod, slotname, mainitem):
        if idmod not in api_bsg or mainitem.conflicting(idmod):
            return 0
        if slotname in self.mods:
            imod = Item(idmod)
            self.mods[slotname] = imod
            return imod
        else:
            print("wrong slot")
            print(self.mods)
            return -1

    def rem_mod(self, slotname):
        if slotname in self.mods and self.mods[slotname] is not None:
            self.mods[slotname] = None
            return 1
        else:
            print("wrong slot")
            print(self.mods)
            return -1

    def get_stat_array(self, tab_sname):
        row = []
        row.append(self.id)
        row.append(GdkPixbuf.Pixbuf.new_from_file(get_path_first_img(self.id, ["icon", "img"])))
        row.append(self.name)
        for statname in tab_sname:
            if "RecoilForce" in statname:
                statname = "Recoil"
            if statname == "Cost" and PRICETOGET in api_market[self.id]:
                row.append(api_market[self.id][PRICETOGET])
            else:
                row.append(api_bsg[self.id]["_props"][statname])

        return row

    def get_conflingting_list(self):
        customlist = []
        if "ConflictingItems" in api_bsg[self.id]["_props"]:
            for x in api_bsg[self.id]["_props"]["ConflictingItems"]:
                customlist.append(x)
        childlist = []
        for slot, item_mod in self.mods.items():
            if item_mod is not None:
                childlist = childlist + item_mod.get_conflingting_list()
        return customlist + childlist

    def get_item_list(self):
        list = []
        for slot, item_mod in self.mods.items():
            if item_mod is not None and item_mod.id not in list:
                list.append(item_mod.id)
                list = list + item_mod.get_item_list()
        return list

    def conflicting(self, itemid):
        conflingting_list = self.get_conflingting_list()
        if itemid in conflingting_list:
            return True
        item_list = self.get_item_list()
        if "ConflictingItems" in api_bsg[itemid]["_props"]:
            for x in api_bsg[itemid]["_props"]["ConflictingItems"]:
                if x in item_list:
                    return True
        return False

    def stat(self, statname, percent=False, mainstat=0):
        if statname == "Cost" and PRICETOGET in api_market[self.id]:
            modif = api_market[self.id][PRICETOGET]
        elif statname not in api_bsg[self.id]["_props"]:
            print("stat not found : " + statname)
            return 0
        else:
            modif = api_bsg[self.id]["_props"][statname]
        if mainstat == 0:
            mainstat = modif
        elif percent:
            modif = floor(modif * mainstat / 100)

        if "RecoilForce" in statname:
            statname = "Recoil"

        if self.mods == {}:
            return modif

        for slot, item in self.mods.items():
            if item is not None:
                modif += item.stat(statname, percent, mainstat)

        return modif

    def show_stats(self):
        txt = "Stats:\n"
        for s, p in stats.items():
            if s == "Cost":

                txt += f"{s} : ₽{self.stat(s, p)}\n"
            else:
                txt += f"{s} : {self.stat(s, p)}\n"
        txt += f"Cost without weapon: ₽{self.stat(s, p)-api_market[self.id][PRICETOGET]}\n"
        return txt

    def print_mod(self, tab=""):
        txt = f"{self.name}\n"
        if self.mods == {} or self.mods is None:
            return txt
        for slot, mod in self.mods.items():
            txt += tab + slot + " : "
            if mod is None:
                txt += "Vide\n"
            else:
                txt += mod.print_mod(tab + "  ")
        return txt

    def build_basic(self, mainitem=None):
        if mainitem is None:
            mainitem = self
        if self.mods == {}:
            return
        for s in api_bsg[self.id]["_props"]["Slots"]:
            if len(s["_props"]["filters"][0]["Filter"]) > 0:
                item = self.add_mod(s["_props"]["filters"][0]["Filter"][0], s["_name"], mainitem)

                if item == 0:
                    i = 1
                    while item == 0 and i < len(s["_props"]["filters"][0]["Filter"]):
                        item = self.add_mod(s["_props"]["filters"][0]["Filter"][i], s["_name"], mainitem)
                        i += 1
        for slot, i in self.mods.items():
            if i is not None:
                i.build_basic(mainitem)


def tests():
    # id_weapon = "5c07c60e0db834002330051f" #adar
    # id_weapon = "5926bb2186f7744b1c6c6e60"  # mp5
    id_weapon = "58948c8e86f77409493f7266"  # mpx
    weapon = Item(id_weapon)

    tab = {}
    for s in api_bsg["5c0e2f26d174af02a9625114"]["_props"]["Slots"]:

        name = s["_name"]

        type = api_bsg[api_bsg[s["_props"]["filters"][0]["Filter"][0]]["_parent"]]["_props"]["Name"]
        tab[type] = []
        print(name)
        # print(s["_props"]["filters"])
        # print(" " + api_market[s["_props"]["filters"][0]["Filter"][0]]["name"] + " : " + s["_props"]["filters"][0]["Filter"][0])
        for m in s["_props"]["filters"][0]["Filter"]:
            print(" " + api_market[m]["name"] + " : " + m)
            tab[type].append(mod_to_list(m))

    print(weapon.stat("RecoilForceUp", percent=True))
    # weapon.add_mod("5c0e2ff6d174af02a1659d4a", "mod_pistol_grip")
    # weapon.add_mod("55d4887d4bdc2d962f8b4570", "mod_magazine")
    # weapon.add_mod("5c0e2f26d174af02a9625114", "mod_reciever")
    # weapon.add_mod("5649be884bdc2d79388b4577", "mod_stock")
    # weapon.add_mod("5c0faf68d174af02a96260b8", "mod_charge")
    weapon.build_basic()
    print(weapon.print_mod())
    print(weapon.stat("RecoilForceUp", percent=True))
    print(weapon.stat("RecoilForceBack", percent=True))
    print(weapon.stat("Ergonomics"))


class WaitingWindow(Gtk.Window):
    def __init__(self, message, title="Wait please"):
        Gtk.Window.__init__(self, title=title)
        self.set_border_width(5)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        label = Gtk.Label(label=message)
        label.set_name("label_wait")
        self.add(label)


class ChooseWeaponWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Choose Weapon")
        self.set_border_width(10)
        self.windowbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hmenubox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.windowbox.add(hmenubox)
        self.type_store = Gtk.ListStore(str, str)
        self.weapon_store = Gtk.ListStore(str, str)

        self.type_combo = Gtk.ComboBox.new_with_model(self.type_store)
        hmenubox.pack_start(self.type_combo, True, False, True)

        self.weapon_combo = Gtk.ComboBox.new_with_model(self.weapon_store)
        hmenubox.pack_start(self.weapon_combo, True, False, True)

        for t in sorted(ids["Weapon"].items(), key=lambda item: item[1]):
            self.type_store.append([t[1], t[0]])

        self.type_combo.connect("changed", self.on_type_combo_changed)
        renderer_text = Gtk.CellRendererText()
        self.type_combo.pack_start(renderer_text, True)
        self.type_combo.add_attribute(renderer_text, "text", 0)
        self.type_combo.set_active(1)
        self.curr_type = self.type_combo.get_model()[self.type_combo.get_active_iter()][1]
        self.curr_weapon = self.generate_weapon_combo()

        self.weapon_combo.connect("changed", self.on_weapon_combo_changed)
        renderer_text = Gtk.CellRendererText()
        self.weapon_combo.pack_start(renderer_text, True)
        self.weapon_combo.add_attribute(renderer_text, "text", 0)
        self.img = Gtk.Image()
        self.img.set_from_file(get_path_first_img(self.curr_weapon))
        self.windowbox.add(self.img)
        button = Gtk.Button.new_with_label("Create Weapon")
        button.connect("clicked", self.select_weapon)
        button.set_name("chooseweapon")
        self.windowbox.pack_start(button, False, False, 0)
        self.add(self.windowbox)
        wait_dl.hide()

    def generate_weapon_combo(self):
        self.weapon_store.clear()
        d = {}
        for id, w in api_bsg.items():
            if id not in api_market:
                continue
            if w["_parent"] == self.curr_type:
                d[id] = api_market[id]["name"]
        d = sorted(d.items(), key=lambda item: item[1])
        for t in d:
            self.weapon_store.append([t[1], t[0]])
        self.weapon_combo.set_active(0)
        return d[0][0]

    def on_type_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self.curr_type = model[tree_iter][1]
            print(f"Selected: {self.curr_type}")
            self.generate_weapon_combo()

    def on_weapon_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            row = [model[tree_iter][0], model[tree_iter][1]]
            if row[1] != self.curr_weapon:
                self.curr_weapon = row[1]
                self.weapon_store.remove(tree_iter)
                self.weapon_store.prepend(row)
                self.weapon_combo.set_active(0)
                self.img.set_from_file(get_path_first_img(self.curr_weapon))
                # print(f"Selected: {self.curr_weapon}")
        wait_dl.hide()

    def select_weapon(self, event):
        wmw = WeaponModWindow(self.curr_weapon)
        wmw.show_all()

    # def resize(self):
    #     while Gtk.events_pending():
    #         Gtk.main_iteration()
    #     w = self.windowbox.get_allocation().width
    #     h = self.windowbox.get_allocation().height
    #     # if w > 1000:
    #     #     w = 1000
    #     # if h > 700:
    #     #     h = 700
    #     print(f"{w}x{h}")
    #     self.windowbox.set_size_request(w, h)


class ChooseModWindow(Gtk.Window):
    def __init__(self, item: Item, itemslot, window):
        if item is None:
            return
        self.window = window
        Gtk.Window.__init__(self, title="Choose a mod")
        self.set_border_width(10)

        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        self.sw = Gtk.ScrolledWindow(hexpand=True, vexpand=True, hadjustment=None, vadjustment=None)
        self.sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        button = Gtk.Button.new_with_label("Remove Current Mod")
        button.connect("clicked", self.select_mod, item, itemslot)
        self.vbox.add(button)
        tab = ["Recoil", "Ergonomics", "Cost"]
        headertab = []
        for i in range(len(tab)):
            headertab.append(int)
        store = Gtk.ListStore(*[str, GdkPixbuf.Pixbuf, str] + headertab + [str])
        sorted_model = Gtk.TreeModelSort(model=store)
        sorted_model.set_sort_column_id(len(headertab) + 2, Gtk.SortType.ASCENDING)
        self.tree = Gtk.TreeView(model=sorted_model)

        self.add(self.sw)
        self.vbox.add(self.tree)
        slot = None
        for slot in api_bsg[item.id]["_props"]["Slots"]:
            if slot["_name"] == itemslot:
                break
        if slot is None:
            return
        conftab = window.weapon.get_conflingting_list()
        itemtab = window.weapon.get_item_list()
        for mod in slot["_props"]["filters"][0]["Filter"]:
            if mod in conftab:
                continue
            found = False
            if "ConflictingItems" in api_bsg[mod]["_props"]:
                for x in api_bsg[mod]["_props"]["ConflictingItems"]:
                    if x in itemtab:
                        found = True
                        break
            if found:
                continue
            imod = Item(mod)
            store.append(imod.get_stat_array(tab) + ["₽"])

        column_img = Gtk.TreeViewColumn("Icon", Gtk.CellRendererPixbuf(), pixbuf=1)
        self.tree.append_column(column_img)
        column_name = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=2)
        self.tree.append_column(column_name)
        i = 3
        for x in tab:
            if x == "Cost":
                column = Gtk.TreeViewColumn(x)
                prefix = Gtk.CellRendererText()
                cost = Gtk.CellRendererText()

                column.pack_start(prefix, True)
                column.pack_start(cost, True)

                column.add_attribute(prefix, "text", i + 1)
                column.add_attribute(cost, "text", i)
                column.set_sort_column_id(i)
                self.tree.append_column(column)
                i += 1
            else:
                column = Gtk.TreeViewColumn(x, Gtk.CellRendererText(), text=i)
                column.set_sort_column_id(i)
                self.tree.append_column(column)
            i += 1
        self.sw.add(self.vbox)
        select = self.tree.get_selection()
        select.connect("changed", self.select_mod, item, itemslot)
        wait_dl.hide()

    def select_mod(self, event, item, itemslot):
        if type(event) == Gtk.Button:
            item.rem_mod(itemslot)
        else:
            model, treeiter = event.get_selected()
            if treeiter is not None:
                item.add_mod(model[treeiter][0], itemslot, self.window.weapon)
        self.window.update()
        self.destroy()

    def resize(self):
        while Gtk.events_pending():
            Gtk.main_iteration()
        w = self.vbox.get_allocation().width
        h = self.vbox.get_allocation().height
        if w > 1000:
            w = 1000
        if h > 700:
            h = 700
        self.sw.set_size_request(w, h)


def selectModMenuClick(event, window, item, slot):
    smm = ChooseModWindow(item, slot, window)
    if smm is None:
        return
    smm.show_all()
    smm.resize()


def build_mod_showcase(window, parent, item: Item):
    for slot, mod in item.mods.items():
        showcase = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        parent.add(showcase)
        showcase.add(Gtk.Label(label=slot_type_translator[slot]))
        if mod is None:
            button = Gtk.Button.new_with_label("None")
            button.connect("clicked", selectModMenuClick, window, item, slot)
            showcase.add(button)
        else:
            button = Gtk.Button()
            button.connect("clicked", selectModMenuClick, window, item, slot)
            img = Gtk.Image()
            path = get_path_first_img(mod.id, ["img", "icon"])
            img.set_from_file(path)
            button.set_image(img)
            showcase.add(button)
            showcase.add(Gtk.Label(label=mod.name))
            showcase.add(Gtk.Label(label=f"₽{api_market[mod.id][PRICETOGET]}"))
            undermods = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            showcase.add(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
            showcase.add(undermods)
            build_mod_showcase(window, undermods, mod)
        parent.add(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
    return None


class WeaponModWindow(Gtk.Window):
    def __init__(self, weaponid):
        Gtk.Window.__init__(self, title="Main Window")
        self.set_border_width(10)
        self.weapon = Item(weaponid)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.add(hbox)
        self.img = Gtk.Image()
        self.img.set_from_file(get_path_first_img(self.weapon.id))
        hbox.pack_start(self.img, False, False, 0)
        self.labelS = Gtk.Label(label=self.weapon.show_stats())
        hbox.pack_start(self.labelS, False, False, 0)
        vbox.add(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.showcase = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        vbox.add(self.showcase)
        build_mod_showcase(self, self.showcase, self.weapon)
        wait_dl.hide()

    def update(self):
        self.labelS.set_text(self.weapon.show_stats())
        self.showcase.foreach(Gtk.Widget.destroy)
        build_mod_showcase(self, self.showcase, self.weapon)
        self.showcase.show_all()
        wait_dl.hide()


css_provider = Gtk.CssProvider()
css_provider.load_from_path("style.css")
context = Gtk.StyleContext()
screen = Gdk.Screen.get_default()
context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
wait_dl = WaitingWindow("Downloading images, please wait")
win = ChooseWeaponWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
