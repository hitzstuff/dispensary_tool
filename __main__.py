import pathlib
import webbrowser
from json import (load as json_load, dump as json_dump)
import requests
import math
import bs4
import pandas as pd
import PySimpleGUIQt as sg
from __init__ import __VERSION__

# Global variables
THEME = 'LightGreen3'
DEFAULT_FONT = 'Open Sans'
DEFAULT_FONT_SIZE = 11
DEFAULT_TEXT_JUSTIFICATION = 'left'
DEFAULT_ELEMENT_SIZE = (15, 1)
DEFAULT_BUTTON_SIZE = (12, 1)
PROGRAM_NAME = 'Dispensary Tool'
GITHUB_LINK = 'https://github.com/hitzstuff/dispensary_tool'

# The directory that this file resides in
MAIN_DIRECTORY = str(pathlib.Path( __file__ ).parent.absolute())
PROGRAM_ICON = str(MAIN_DIRECTORY) + r'\mmj.ico'

# Structure of the menu bar
menu_bar = [
    ['File',
        ['Exit']
        ],
    ['Edit',
        ['Product Weights']
        ],
    ['Help',
        ['GitHub Page', 'Check for Updates', 'About']
        ]
    ]

# Version checking
request = requests.get(GITHUB_LINK, timeout=5)
parse = bs4.BeautifulSoup(request.text, 'html.parser')
parse_part = parse.select('div#readme p')
NEWEST_VERSION = str(parse_part[0])
NEWEST_VERSION = NEWEST_VERSION.split()[-1][:-4]
DOWNLOAD_LINK = str(parse_part[1])
DOWNLOAD_LINK = ((DOWNLOAD_LINK.split()[-1][:-4]).split('>')[1]).split('<')[0]

# Preformatted string for the 'About' menu
ABOUT = (
    f'Current Version:\t {__VERSION__}\n' +
    f'Newest Version:\t {NEWEST_VERSION}\n\n'
    +
    'Developed by:\t Aaron Hitzeman\n' +
    '\t\t aaron.hitzeman@gmail.com\n\n'
    +
    'Visit the GitHub page for more information.'
)

# Preformatted string for the 'About' menu when an update is available
ABOUT_UPDATE = (
    f'Current Version:\t {__VERSION__}\n' +
    f'Newest Version:\t {NEWEST_VERSION}\n\n'
    +
    'A newer version of this program is available!' +
    '  Please use the "Check for Updates" button to download the latest version.\n\n'
    +
    'Developed by:\t Aaron Hitzeman\n' +
    '\t\t aaron.hitzeman@gmail.com\n\n'
    +
    'Visit the GitHub page for more information.'
)

# Preformatted update messages
UPDATE_MSG_YES = (
    f'Current Version: {__VERSION__}\n' +
    f'Newest Version: {NEWEST_VERSION}\n\n'
    +
    'A newer version of this program is available!  Would you like to download it?'
)
UPDATE_MSG_NO = (
    f'Current Version: {__VERSION__}\n' +
    f'Newest Version: {NEWEST_VERSION}\n\n'
    +
    'There are currently no updates available.'
)

# Location of the settings file
SETTINGS_FILE = pathlib.PurePath(MAIN_DIRECTORY, 'config', 'settings.cfg')

# Default dictionary of products and their dispensation amounts (in grams)
DEFAULT_SETTINGS = {
    'Ground Flower': 7.0,
    'Whole Flower': 3.5,
    '10ct Pre-Rolls': 3.5,
    '5ct Pre-Rolls': 2.5,
    '2ct Pre-Rolls': 1.0
    }

# Global variable for the patient's current allotment amount
OZ = 2.5

# Global dictionary for products and their dispensation amounts
MMJ = DEFAULT_SETTINGS.copy()

# Maps products to their respective keys for GUI interaction
SETTINGS_KEYS_TO_ELEMENT_KEYS = {
    list(MMJ)[0]: '-PRODUCT_1-',
    list(MMJ)[1]: '-PRODUCT_2-',
    list(MMJ)[2]: '-PRODUCT_3-',
    list(MMJ)[3]: '-PRODUCT_4-',
    list(MMJ)[4]: '-PRODUCT_5-',
}

def update_check():
    '''Checks the program's version against the one on the GitHub page'''
    if __VERSION__ != NEWEST_VERSION:
        status = True
    else:
        status = False
    return status

def toggle(state=False):
    '''Quickly toggles between a True and False response'''
    if state is True:
        new_state = False
    else:
        new_state = True
    return new_state

def sort_dictionary(dictionary):
    '''Sorts a given dictionary by its values (high to low)'''
    dictionary = dict(
        sorted(
            dictionary.items(),
            key = lambda item: item[1],
            reverse = True
        )
    )
    return dictionary

def load_settings(settings_file, default_settings):
    '''Loads the settings file with products and dispensation amounts'''
    try:
        with open(settings_file, 'r', encoding='UTF-8') as file:
            settings = json_load(file)
    except FileNotFoundError as error:
        print(f'exception {error}', '\nNo settings file found...creating one now.')
        settings = default_settings
        save_settings(settings_file, settings, None)
    print('Settings loaded')
    return settings

def save_settings(settings_file, settings, values):
    '''Saves the current settings to the config file'''
    if values:
        # Update the window with values read from the settings file
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS.items():
            dict_key = key[0]
            try:
                settings[dict_key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[dict_key]]
            except KeyError:
                print(
                    'Problem updating settings from window values:\n' +
                    f'\tKey:\t{key[0]}\n\tValue:\t{key[1]}'
                    )
    # Opens the settings file and overwrites it with the new values
    with open(settings_file, 'w', encoding='UTF-8') as file:
        json_dump(settings, file)
        print('Settings saved')
    return None

def convert_weight(weight, unit_of_measurement='gram'):
    '''Converts product weight between grams and ounces'''
    if unit_of_measurement == 'gram':
        new_weight = weight / 28.34952
    elif unit_of_measurement == 'ounce':
        new_weight = round((weight * 28.34952) - 0.04, 1)
    else:
        new_weight = weight
    return new_weight

def maximize_allotment(ounces, prod_1=True, prod_2=True, prod_3=True, prod_4=True, prod_5=True):
    '''Tallies the maximum number of products until the allotment equals zero'''
    grams = round(convert_weight(ounces, 'ounce'), 1)
    products = sort_dictionary(MMJ)
    product_1 = list(products)[0]
    product_2 = list(products)[1]
    product_3 = list(products)[2]
    product_4 = list(products)[3]
    product_5 = list(products)[4]
    weight_1 = MMJ[product_1]
    weight_2 = MMJ[product_2]
    weight_3 = MMJ[product_3]
    weight_4 = MMJ[product_4]
    weight_5 = MMJ[product_5]
    minimum_allotment = MMJ[product_5]
    patient_order = []
    while (grams > 0) or (grams >= minimum_allotment):
        if (prod_1 is True) and (grams >= weight_1):
            patient_order.append(product_1)
            grams -= weight_1
        elif (prod_2 is True) and (grams >= weight_2):
            patient_order.append(product_2)
            grams -= weight_2
        elif (prod_3 is True) and (grams >= weight_3):
            patient_order.append(product_3)
            grams -= weight_3
        elif (prod_4 is True) and (grams >= weight_4):
            patient_order.append(product_4)
            grams -= weight_4
        elif (prod_5 is True) and (grams >= weight_5):
            patient_order.append(product_5)
            grams -= weight_5
        else:
            break
    ounces = convert_weight(grams, 'gram')
    patient_order = (pd.DataFrame(patient_order)).value_counts()
    products_2 = ['']
    quantities = ['']
    strings = ['']
    for i, _ in enumerate(patient_order):
        product = patient_order.index[i][0]
        quantity = patient_order[i]
        weight_g = MMJ[product]
        total_g = weight_g * quantity
        total_oz = convert_weight(total_g, 'gram')
        string = f'= {total_g:.1f} g / {total_oz:.3f} oz'
        products_2.append(product)
        quantities.append(quantity)
        strings.append(string)
    quantities.append('')
    quantities.append('')
    products_2.append('')
    products_2.append('Remaining:')
    strings.append('')
    strings.append(f'{grams:.1f} g / {ounces:.3f} oz')
    products_2 = pd.DataFrame(products_2, columns=[''])
    quantities = pd.DataFrame(quantities, columns=[''])
    strings = pd.DataFrame(strings, columns=[''])
    order_columns = [quantities, products_2, strings]
    patient_order = pd.concat(order_columns, axis=1)
    return patient_order, ounces

def text_label(text):
    '''Returns a text label'''
    return sg.Text(text+':', justification='l', size = (20, .5))

def settings_window(settings):
    '''Creates the window for changing the config file settings'''
    sg.theme(THEME)
    # Create the layout for the window
    layout = [
        [sg.Text(
            'Product Weights (grams)\n'
            )],
        [text_label(
            list(MMJ)[0]),
            sg.Input(
                key = '-PRODUCT_1-',
                size = (4, 0.75))
            ],
        [text_label(
            list(MMJ)[1]),
            sg.Input(
                key = '-PRODUCT_2-',
                size = (4, 0.75))
            ],
        [text_label(
            list(MMJ)[2]
            ),
            sg.Input(
                key = '-PRODUCT_3-',
                size = (4, 0.75)
                )
            ],
        [text_label(
            list(MMJ)[3]),
            sg.Input(
                key = '-PRODUCT_4-',
                size = (4, 0.75))
            ],
        [text_label(
            list(MMJ)[4]),
            sg.Input(
                key = '-PRODUCT_5-',
                size = (4, 0.75))
            ],
        [
            sg.Button(
                'Save',
                size = (10, 0.85),
                enable_events = True,
                button_type = sg.BUTTON_TYPE_CLOSES_WIN
                ),
            sg.Button(
                'Exit',
                size = (10, 0.85),
                enable_events = True,
                button_type = sg.BUTTON_TYPE_CLOSES_WIN
                )
            ]
        ]
    # Create the window
    window = sg.Window(
        'Settings',
        layout,
        keep_on_top = True,
        icon = PROGRAM_ICON,
        resizable = False,
        finalize = True
        )
    # Update the window with the values read from the settings file
    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS.items():
        dict_key = key[0]
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[dict_key]].update(value=settings[dict_key])
        except KeyError:
            print(f'Problem updating PySimpleGUI window from settings. Key = {key}')
    return window

def main_window():
    '''Creates the primary window for the program.'''
    # Set the theme
    sg.theme(THEME)
    # Configure the layout
    layout = [
        [sg.Menu(
            menu_bar,
            #background_color = 'LightGray'
            )],
        [sg.Text(
            '',
            key = '-OUTPUT-',
            size = (30, 3),
            enable_events = True,
            relief = 'sunken',
            background_color = '#FFF',
            text_color = '#000'
            )],
        [sg.Text(
            '[Categories]',
            )],
        [sg.Checkbox(
            list(MMJ)[0],
            key = '-PRODUCT_1-',
            enable_events = True,
            default = True
            )],
        [sg.Checkbox(
            list(MMJ)[1],
            key = '-PRODUCT_2-',
            enable_events = True,
            default = True
            )],
        [sg.Checkbox(
            list(MMJ)[2],
            key = '-PRODUCT_3-',
            enable_events = True,
            default = True
        )],
        [sg.Checkbox(
            list(MMJ)[3],
            key = '-PRODUCT_4-',
            enable_events = True,
            default = True
        )],
        [sg.Checkbox(
            list(MMJ)[4],
            key = '-PRODUCT_5-',
            enable_events = True,
            default = True
        )],
        [text_label(
            'Current Allotment (ounces)'
            ),
            sg.Input(
                key = '-OZ-',
                enable_events = True,
                size = (5, 0.75),
                background_color = '#FFF'
                )
            ],
        [sg.Text(
            ''
            )],
        [sg.Button(
            'Calculate',
            key = '-CALCULATE-',
            size = (15, 0.85),
            enable_events = True,
            tooltip = 'Calculate Maximized Allotment',
            bind_return_key = True
            )]
        ]
    # Configure the window
    window = sg.Window(
        'Dispensary Tool',
        layout,
        default_element_size = DEFAULT_ELEMENT_SIZE,
        text_justification = DEFAULT_TEXT_JUSTIFICATION,
        auto_size_text = False,
        auto_size_buttons = False,
        default_button_element_size = DEFAULT_BUTTON_SIZE,
        element_padding = (0, 0),
        #background_color = 'LightGray',
        icon = PROGRAM_ICON,
        resizable = False,
        finalize = True
        )
    return window

def main():
    '''Primary program functionality.'''
    window, settings = None, load_settings(SETTINGS_FILE, DEFAULT_SETTINGS)
    product_1 = True
    product_2 = True
    product_3 = True
    product_4 = True
    product_5 = True
    while True:
        try:
            # Create the main window
            if window is None:
                window = main_window()
            event, values = window.read()
            # Close the program
            if (event == sg.WIN_CLOSED) or (event == 'Exit'):
                break
            # Checks for updates, then asks the user if they want to download it
            if event == 'Check for Updates':
                new_version = update_check()
                if new_version is True:
                    answer = sg.popup_yes_no(
                        UPDATE_MSG_YES,
                        title = 'Update Available',
                        keep_on_top = True
                    )
                    if answer == 'Yes':
                        webbrowser.open(DOWNLOAD_LINK)
                else:
                    sg.popup(
                        UPDATE_MSG_NO,
                        title = 'No Updates Available',
                        keep_on_top = True                        
                    )
            # Load the 'About' message
            if event == 'About':
                new_version = update_check()
                if new_version is True:
                    sg.popup(
                        ABOUT_UPDATE,
                        title = f'{PROGRAM_NAME}  -  New Version Available',
                        keep_on_top = True
                    )
                else:
                    sg.popup(
                        ABOUT,
                        title = f'{PROGRAM_NAME}',
                        keep_on_top = True
                        )
            # Open a web browser to the GitHub page
            if event == 'GitHub Page':
                webbrowser.open(GITHUB_LINK)
            # Open a window for configuring product weights
            if event == 'Product Weights':
                event, values = settings_window(settings).read(close=True)
                if event == 'Save':
                    window.close()
                    save_settings(SETTINGS_FILE, settings, values)
                    window = None
            # Toggle between products
            if event == '-PRODUCT_1-':
                product_1 = toggle(product_1)
            if event == '-PRODUCT_2-':
                product_2 = toggle(product_2)
            if event == '-PRODUCT_3-':
                product_3 = toggle(product_3)
            if event == '-PRODUCT_4-':
                product_4 = toggle(product_4)
            if event == '-PRODUCT_5-':
                product_5 = toggle(product_5)
            if event == '-CALCULATE-':
                allotment = float(values['-OZ-'])
                try:
                    order, ounces = maximize_allotment(
                        ounces=allotment,
                        prod_1=product_1,
                        prod_2=product_2,
                        prod_3=product_3,
                        prod_4=product_4,
                        prod_5=product_5
                        )
                    order = order.to_string(index=False)
                    window['-OUTPUT-'].update(order)
                except ValueError as v_error:
                    sg.popup_error(
                    f'The value {v_error} was out of bounds.',
                    title = 'Value Error'
                    )
        except ValueError as v_error:
            sg.popup_error(
                f'The value {v_error} was out of bounds.',
                title = 'Value Error'
                )
        except TypeError as t_error:
            sg.popup_error(
                f'{t_error} was an improper data type.',
                title = 'Type Error'
                )
    window.close()

if __name__ == '__main__':
    main()
