import configparser
import os
import sys

config = configparser.ConfigParser()
config.read('config.cfg')

default_way = '\\'.join(str(os.path.abspath(__file__)).split('\\')[:-1]) + '\\'
need_ways = ['way_to_default_classes', 'way_to_default_classes', 'way_to_gui', 'way_to_obj_classes',
             'way_to_nps_classes', 'way_to_wall_classes', 'way_to_save_load_and_location']

for i in need_ways:
    sys.path.append(default_way + config.get("ways", i))


import pygame
import random
from my_hero import *
from inventory import *
from chest import *
from gui import *
import save_lode
from kit_obj import *
from army_kit_obj import *
from scientific_kit_obj import *
from lollipop_obj import *
from lollipop_heard_obj import *
from mellon_ice_cream_obj import *
from cherry_obj import *
from hamburger_obj import *
from pizza_obj import *
from donat_obj import *
from brick_wall import *
from janitor_armor_obj import *
from brick_obj import *
from default_instrument import *
from inventory_sprites_class import *

NAME_OF_SAVES = ['inventory_test', 'test', 'test_1', 'empty_test']  # special for presentation
# NUMBER_OF_SAVE = int(input('Какое сохранение нужно загрузить? \n'))  # I comment it because i don't want to click
# it every launch
NUMBER_OF_SAVE = 2


WIDTH = 800
HEIGHT = 800
FPS = 75
COLOR = (10, 255, 0)

toolbar = ['', '', '', '', '', '']
load_obj = []
load_chests = []

keys = {
    '119': '', '115': '', '100': '', '97': '', '27': '', '101': '', '105': ''
}

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My_game")
clock = pygame.time.Clock()

arm_sprites = pygame.sprite.Group()
gui_sprites = pygame.sprite.Group()
gui = gui(0, 0, toolbar, gui_sprites, arm_sprites)

player_sprites = pygame.sprite.Group()
inventory_sprites = inventory_sprites()
inventory = Inventory(inventory_sprites)
ground_sprites = pygame.sprite.Group()
wall_sprites = pygame.sprite.Group()
relocatable_sprites = pygame.sprite.Group()


# TODO lode
player = save_lode.lode(NAME_OF_SAVES[NUMBER_OF_SAVE], load_obj, inventory_sprites, gui_sprites, ground_sprites,
                        toolbar, inventory, gui, player_sprites, load_chests, wall_sprites, relocatable_sprites,
                        keys)

background = pygame.image.load(default_way + config.get("ways",
                                                        'way_to_save_load_and_location')
                               + '\\' + 'test_fon.png').convert()
background_rect = background.get_rect()

running = True
while running:
    clock.tick(FPS)
    event = pygame.event.poll()

    if event.type == 2:  # key pressed
        keys[str(event.key)] = 'pressed'
        if event.key == 27 and not inventory.is_open():
            if any([i.is_open() for i in load_chests]):
                for i in load_chests:
                    if i.is_open():
                        i.close()
                        break
            else:
                # TODO
                print('exit')
        else:
            if not any([i.is_open() for i in load_chests]):
                inventory.update(keys)

    if event.type == 3:  # key unpressed
        keys[str(event.key)] = 'unpressed'

    if event.type == 4:
        # update cords if something obj is move
        if inventory.is_open():
            if inventory.obj_is_moved != '':
                inventory.obj_is_moved.update(x_m=event.pos[0], y_m=event.pos[1])
        elif any([i.is_open() for i in load_chests]):
            for i in load_chests:
                if i.is_open():
                    if i.obj_is_moved != '':
                        i.obj_is_moved.update(x_m=event.pos[0], y_m=event.pos[1])
                    break
        else:
            if toolbar[gui.get_window_pos()] != '' and toolbar[gui.get_window_pos()].parent.is_work():
                toolbar[gui.get_window_pos()].parent.update(cords=event.pos)
                
    if event.type == 5:  # mouse click on
        if event.button == 1:  # click on left mouse button
            if gui.text_info.open():  # special for close open info, if it open
                gui.text_info.kill()
            elif inventory.is_open():  # if inventory open we return info about event to inventory obj
                inventory.click_1_on(*event.pos)
            elif any([i.is_open() for i in load_chests]):  # if any chest are open we return
                # info about event to chest obj
                for i in load_chests:
                    if i.is_open():
                        i.click_1_on(*event.pos)
                        break
            else:
                if toolbar[gui.get_window_pos()] != '':
                    toolbar[gui.get_window_pos()].in_arms_click_1_on(*event.pos)
        elif event.button == 3:  # click on right mouse button
            if inventory.is_open() or any([i.is_open() for i in load_chests]):
                if inventory.is_open():
                    is_none = inventory.click_2_on(*event.pos)
                else:
                    for i in load_chests:
                        if i.is_open():
                            is_none = i.click_2_on(*event.pos)
                            break
                if is_none:
                    a, count = is_none
                    name = a.parent.file_name
                    a = a.parent.copy()
                    a = save_lode.definition_that_obj_is_it(name, load_obj, *a[0], count, *a[1])
                    # the magic function that spawn a new obj
                    if any([i.is_open() for i in load_chests]):
                        x, y = a.obj_in_inventory.get_cords()
                        if 407 <= x <= 757 and 150 <= y <= 650:
                            a.put_in_the_chest(i)

            else:
                for i in ground_sprites:
                    if str(i) == '<obj_on_ground sprite(in 1 groups)>':
                        i.click_2(*event.pos)
                for i in wall_sprites:
                    i.click_in_wall(*event.pos, player)

        elif event.button == 4:  # mouse wheel move
            count = gui.get_window_pos() + 1
            if count > 5:
                count = 0
            gui.toolbar_window_changes(count)

        elif event.button == 5:  # mouse wheel move
            count = gui.get_window_pos() - 1
            if count < 0:
                count = 5
            gui.toolbar_window_changes(count)

    if event.type == 6:
        if event.button == 1:  # click on left mouse button
            if gui.text_info.open():  # special for close open info, if it open
                gui.text_info.kill()
            elif inventory.is_open():  # if inventory open we return info about event to inventory obj
                inventory.click_1_off(*event.pos)
            elif any([i.is_open() for i in load_chests]):  # if any chest are open we return
                # info about event to chest obj
                for i in load_chests:
                    if i.is_open():
                        i.click_1_off(*event.pos)
                        break
            else:
                if toolbar[gui.get_window_pos()] != '':
                    toolbar[gui.get_window_pos()].in_arms_click_1_on(*event.pos)
        elif event.button == 3:  # click on right mouse button
            if inventory.is_open() or any([i.is_open() for i in load_chests]):
                if inventory.is_open():
                    inventory.click_2_off(*event.pos)

        if event.button == 1:  # un click on left mouse button
            if inventory.is_open():  # if inventory open we return info about event to inventory obj
                inventory.click_1_off(*event.pos)
            elif any([i.is_open() for i in load_chests]):  # if any chest are open we return
                # info about event to chest obj
                for i in load_chests:
                    if i.is_open():
                        i.click_1_off(*event.pos)
                        break
            else:
                if toolbar[gui.get_window_pos()] != '':
                    toolbar[gui.get_window_pos()].in_arms_click_1_off(*event.pos)

        elif event.button == 3:  # un click on right mouse button
            if inventory.is_open() or any([i.is_open() for i in load_chests]):
                if inventory.is_open():
                    inventory.click_2_off(*event.pos)
                else:
                    for i in load_chests:
                        if i.is_open():
                            i.click_2_off(*event.pos)
                            break
            else:
                for i in ground_sprites:
                    if str(i) == '<obj_on_ground sprite(in 1 groups)>':
                        i.click_2(*event.pos)
                for i in wall_sprites:
                    i.click_in_wall(*event.pos, player)

    if event.type == pygame.QUIT:
        for i in load_chests:
            if i.is_open():
                i.close()
        running = False

    # update all sprites and gui
    player_sprites.update()
    gui_sprites.update()
    arm_sprites.update()
    gui.update()
    if toolbar[gui.get_window_pos()] != '' and toolbar[gui.get_window_pos()].parent.is_work():
        toolbar[gui.get_window_pos()].parent.update()

    # render
    screen.blit(background, background_rect)
    ground_sprites.draw(screen)
    player_sprites.draw(screen)
    arm_sprites.draw(screen)
    wall_sprites.draw(screen)
    gui_sprites.draw(screen)

    if inventory.is_open():
        screen.blit(*inventory.image())
        inventory_sprites.draw(screen)
        relocatable_sprites.draw(screen)
    else:
        for i in load_chests:
            if i.is_open():
                screen.blit(*i.image())
                inventory_sprites.draw(screen)
                i.chest_sprites.draw(screen)
                relocatable_sprites.draw(screen)
                break

    pygame.display.flip()  # flipping the screen

# kill the window
pygame.quit()

# save the game
# TODO
if input('Сохранить игру? (yes or no) \n') == 'yes':
    save_lode.save(NAME_OF_SAVES[NUMBER_OF_SAVE], load_obj, load_chests, player, wall_sprites)
