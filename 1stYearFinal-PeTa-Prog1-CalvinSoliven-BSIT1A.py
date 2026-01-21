import pygame
import sys
import random

pygame.init()

# Screen setup (fullscreen)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Last Seen")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WINDOWS95_GREEN = (0, 128, 128)
WINDOWS95_GRAY = (192, 192, 192)

# Fonts
title_font = pygame.font.SysFont("Lucida Console", 48, bold=True)   
menu_font = pygame.font.SysFont("Lucida Console", 28)
small_font = pygame.font.SysFont("Lucida Console", 22)

# Game states
STATE_MENU = "menu"
STATE_CHATROOM = "chatroom"
STATE_CONVO = "conversation"
state = STATE_MENU
STATE_END = "end"


selected_chat = None
line_index = 0
player_input = ""

typing = False
typing_start = 0
typing_delay = 1500 
pending_response = None

# Conversations 
conversations = {
    "Luna": [
        {"text": "Luna: hey {user}, it's been a while :)", "choices": [
            ("Hey! Missed chatting with you.", 
             "Luna: aww, that's sweet. I was worried you forgot about me."),
            ("Yo, what's up?", 
             "Luna: not much, just thinking about old times. Feels weird being back here."),
            ("Oh hey. Been busy.", 
             "Luna: oh, right. I get it. Life gets in the way sometimes.")
        ]},
        {"text": "Luna: remember our old group chats, {user}?", "choices": [
            ("Yeah, those were fun.", 
             "Luna: haha, nostalgia hits. I miss how simple things felt."),
            ("Not really.", 
             "Luna: ouch, harsh. Guess I cared more than you did.")
        ]},
        {"text": "Luna: sometimes I scroll back through old messages.", "choices": [
            ("Haha, I do that too.", 
             "Luna: glad I’m not the only one. It’s like reliving a piece of us."),
            ("Nah, I don’t really look back.", 
             "Luna: fair, moving forward is good. But I still like remembering.")
        ]},
        {"text": "Luna: things feel so different now, don’t they {user}?", "choices": [
            ("Yeah, everyone’s changed a lot.", 
             "Luna: true, but that’s life. Still, I’m glad we reconnected."),
            ("Not really, feels the same to me.", 
             "Luna: interesting perspective. Maybe I’m just overthinking.")
        ]},
        {"text": "Luna: anyway, gotta go soon, {user}!", "choices": [
            ("Okay, talk later.", 
             "Luna: bye! Don’t be a stranger."),
            ("See ya.", 
             "Luna: take care. I’ll be around.")
        ]}
    ],

    "Kai": [
        {"text": "Kai: sup {user}, long time no talk!", "choices": [
            ("Yeah, been busy with school.", 
             "Kai: same here, finals are killing me. Feels like we’re both drowning."),
            ("I missed this chatroom vibe.", 
             "Kai: haha, nostalgia hits hard. Glad you came back.")
        ]},
        {"text": "Kai: do you still play games, {user}?", "choices": [
            ("Yeah, sometimes.", 
             "Kai: nice, me too. I still stay up way too late."),
            ("Not really.", 
             "Kai: ah, I see. Guess I’m the only one still hooked.")
        ]},
        {"text": "Kai: I’ve been grinding late nights, feels like old times.", "choices": [
            ("Haha, classic you.", 
             "Kai: some things never change. I still get carried away."),
            ("You should rest more.", 
             "Kai: yeah, maybe you’re right. I’ll try to chill.")
        ]},
        {"text": "Kai: anyway, I gotta bounce soon, {user}.", "choices": [
            ("Alright, catch you later.", 
             "Kai: peace! Don’t disappear again."),
            ("Take care, man.", 
             "Kai: you too. Stay safe.")
        ]}
    ],

    "Mira": [
        {"text": "Mira: hey {user}, remember me?", "choices": [
            ("Of course, how could I forget?", 
             "Mira: haha, smooth. Glad you still remember."),
            ("Not really, sorry.", 
             "Mira: ouch, that hurts. Guess I meant more to you back then.")
        ]},
        {"text": "Mira: we used to chat every night, {user}!", "choices": [
            ("Yeah, I remember.", 
             "Mira: good times. I miss those late night talks."),
            ("I barely recall.", 
             "Mira: wow, okay. Guess I was more invested.")
        ]},
        {"text": "Mira: sometimes I miss those days.", "choices": [
            ("Me too, things felt simpler.", 
             "Mira: exactly, life was easier. Now everything feels complicated."),
            ("I’ve moved on.", 
             "Mira: fair enough. I should probably do the same.")
        ]},
        {"text": "Mira: guess we’re both different now, {user}.", "choices": [
            ("Yeah, but it’s nice reconnecting.", 
             "Mira: agreed, glad we talked. Feels like closure."),
            ("True, people change.", 
             "Mira: yeah, that’s life. Still, it’s bittersweet.")
        ]},
        {"text": "Mira: anyway, I should get going. Talk again soon, {user}?", "choices": [
            ("Sure, I’d like that.", 
             "Mira: great, see you around! Don’t vanish again."),
            ("Maybe, we’ll see.", 
             "Mira: alright, take care. I’ll be here if you want.")
        ]}
    ]
}


chat_active = True


def draw_text(text, y, font, color=WHITE):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH//2, y))
    screen.blit(surface, rect)

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width - 40:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines

def draw_chatbox():
    box_size = min(WIDTH, HEIGHT) // 2
    box_x = (WIDTH - box_size) // 2
    box_y = (HEIGHT - box_size) // 2

    
    pygame.draw.rect(screen, (50, 50, 50), (box_x + 5, box_y + 5, box_size, box_size))

    
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_size, box_size))
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_size, box_size), 3)
    return box_x, box_y, box_size, box_size

def draw_chat_text(text, font, box_x, box_y, box_width, box_height, color=WHITE):
    lines = wrap_text(str(text), font, box_width)
    start_y = box_y + 60
    for i, line in enumerate(lines):
        surface = font.render(line, True, color)
        rect = surface.get_rect(midtop=(box_x + box_width//2, start_y + i*26))
        screen.blit(surface, rect)
    return start_y + len(lines)*26



def draw_choices(choices, font, box_x, box_y, box_width, box_height, text_bottom, color=WINDOWS95_GREEN):
    start_y = text_bottom + 40
    for i, choice in enumerate(choices):
        lines = wrap_text(f"{i+1}. {choice[0]}", font, box_width)
        for j, line in enumerate(lines):
            surface = font.render(line, True, color)
            rect = surface.get_rect(midtop=(box_x + box_width//2, start_y + i*90 + j*24))
            screen.blit(surface, rect)


def draw_player_input(player_input, font, box_x, box_y, box_width, box_height, color=WHITE):
    show_cursor = (pygame.time.get_ticks() // 500) % 2 == 0
    display_input = player_input + ("_" if show_cursor else "")
    surface = font.render(display_input, True, color)
    rect = surface.get_rect(midleft=(box_x + 20, box_y + box_height - 40))
    screen.blit(surface, rect)


def draw_header(selected_chat, typing, chat_active=True):
    header_height = 40
    header_width = min(WIDTH, HEIGHT) // 2
    header_x = (WIDTH - header_width) // 2
    header_y = (HEIGHT // 2) - (header_width // 2) - 60

    
    pygame.draw.rect(screen, WINDOWS95_GREEN, (header_x, header_y, header_width, header_height))
   
    pygame.draw.rect(screen, (50, 50, 50), (header_x, header_y, header_width, header_height), 2)

    if typing and chat_active:
        dot_count = (pygame.time.get_ticks() // 250) % 4
        dots = "." * dot_count
        status_text = f"{selected_chat} is typing{dots}"
        color = WHITE
        dot_color = (255, 255, 255)  
    else:
        if chat_active:
            status_text = f"{selected_chat} is online"
            color = (0, 200, 0)  
            dot_color = (0, 200, 0)  
        else:
            status_text = f"{selected_chat} is offline"
            color = (0, 0, 0)  
            dot_color = (100, 100, 100)  

    
    surface = small_font.render(status_text, True, color)
    rect = surface.get_rect(center=(header_x + header_width//2, header_y + header_height//2))
    screen.blit(surface, rect)

    
    dot_radius = 6
    dot_x = rect.left - 15
    dot_y = rect.centery
    pygame.draw.circle(screen, dot_color, (dot_x, dot_y), dot_radius)

username = ""
typing_text = ""       
typing_index = 0       
char_delay = 85        
post_typing_pause = 700   
pause_start = 0
completed_chats = set()

running = True
while running:
    screen.fill(WINDOWS95_GRAY)

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # MENU state input
        if state == STATE_MENU and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and username.strip() != "":
                state = STATE_CHATROOM
            elif event.key == pygame.K_BACKSPACE:
                username = username[:-1]
            else:
                username += event.unicode

        # CHATROOM state input
        elif state == STATE_CHATROOM and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and "Luna" not in completed_chats:
                selected_chat = "Luna"
                state = STATE_CONVO
                line_index = 0
                chat_active = True
                conversation_ended = False   # reset flag
                current_line = conversations[selected_chat][line_index]
                if "choices" in current_line and len(current_line["choices"]) > 0:
                    random.shuffle(current_line["choices"])
            elif event.key == pygame.K_2 and "Kai" not in completed_chats:
                selected_chat = "Kai"
                state = STATE_CONVO
                line_index = 0
                chat_active = True
                conversation_ended = False   # reset flag
                current_line = conversations[selected_chat][line_index]
                if "choices" in current_line and len(current_line["choices"]) > 0:
                    random.shuffle(current_line["choices"])
            elif event.key == pygame.K_3 and "Mira" not in completed_chats:
                selected_chat = "Mira"
                state = STATE_CONVO
                line_index = 0
                chat_active = True
                conversation_ended = False   # reset flag
                current_line = conversations[selected_chat][line_index]
                if "choices" in current_line and len(current_line["choices"]) > 0:
                    random.shuffle(current_line["choices"])

        # CONVO state input
        elif state == STATE_CONVO and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if player_input.isdigit() and not typing and len(current_line["choices"]) > 0:
                    choice_num = int(player_input) - 1
                    if 0 <= choice_num < len(current_line["choices"]):
                        pending_response = current_line["choices"][choice_num][1]
                        player_input = ""
                        typing = True
                        typing_start = pygame.time.get_ticks()
                        typing_text = ""
                        typing_index = 0
                        current_line["choices"] = []
                elif conversation_ended and not typing and pending_response is None:
                    state = STATE_CHATROOM
                    player_input = ""
                    chat_active = True
                    conversation_ended = False
            elif event.key == pygame.K_BACKSPACE:
                player_input = player_input[:-1]
            elif event.unicode.isdigit():
                player_input += event.unicode

        # END state input
        elif state == STATE_END and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                state = STATE_MENU
                completed_chats.clear()   # reset progress
                username = ""
            elif event.key == pygame.K_ESCAPE:
                running = False


    
    if typing and pygame.time.get_ticks() - typing_start >= char_delay:
        typing_start = pygame.time.get_ticks()
        if typing_index < len(pending_response):
            typing_text += pending_response[typing_index]
            typing_index += 1
        else:
            # Finished typing, start pause
            typing = False
            pause_start = pygame.time.get_ticks()
            current_line = {"text": typing_text.replace("{user}", username), "choices": []}
            pending_response = None
            typing_text = ""
            typing_index = 0


    if not typing and pause_start > 0 and pygame.time.get_ticks() - pause_start >= post_typing_pause:
        pause_start = 0
        line_index += 1
        if line_index < len(conversations[selected_chat]):
            current_line = conversations[selected_chat][line_index]
            if "choices" in current_line and len(current_line["choices"]) > 0:
                random.shuffle(current_line["choices"])
        else:
            current_line = {"text": f"{selected_chat}: chat ended.", "choices": []}
            chat_active = False
            conversation_ended = True
            completed_chats.add(selected_chat)   
            if len(completed_chats) == 3:        #  all three finished
                state = STATE_END


    
    if state == STATE_MENU:
        # Independent title banner at the top
        pygame.draw.rect(screen, (75, 0, 130), (WIDTH//2 - 300, 40, 600, 80))  
        pygame.draw.rect(screen, BLACK, (WIDTH//2 - 300, 40, 600, 80), 3)
        draw_text("Last Seen", 80, title_font, WHITE)

        
        box_size = min(WIDTH, HEIGHT) // 2
        box_x = (WIDTH - box_size) // 2
        box_y = (HEIGHT - box_size) // 2
        pygame.draw.rect(screen, (30, 30, 30), (box_x, box_y, box_size, box_size))
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_size, box_size), 3)

        
        pygame.draw.rect(screen, BLACK, (box_x + 50, box_y + 80, box_size - 100, 40))
        pygame.draw.rect(screen, WHITE, (box_x + 50, box_y + 80, box_size - 100, 40), 2)
        show_cursor = (pygame.time.get_ticks() // 500) % 2 == 0
        display_name = username + ("_" if show_cursor else "")
        username_surface = menu_font.render(display_name, True, WHITE)
        screen.blit(username_surface, (box_x + 60, box_y + 85))

        draw_text("Username:", box_y + 60, menu_font, WHITE)

        
        draw_text("Press ENTER to enter chatroom", box_y + 150, menu_font, (255, 215, 0))
        

    elif state == STATE_CHATROOM:
        box_size = min(WIDTH, HEIGHT) // 2
        box_x = (WIDTH - box_size) // 2
        box_y = (HEIGHT - box_size) // 2
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_size, box_size))
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_size, box_size), 3)

        draw_text("Choose who to chat with:", box_y + 60, menu_font, WHITE)

        
        if "Luna" in completed_chats:
            draw_text("1. Luna (completed)", box_y + 140, small_font, (150, 150, 150))  
        else:
            draw_text("1. Luna", box_y + 140, small_font, WINDOWS95_GREEN)

        if "Kai" in completed_chats:
            draw_text("2. Kai (completed)", box_y + 180, small_font, (150, 150, 150))  
        else:
            draw_text("2. Kai", box_y + 180, small_font, WINDOWS95_GREEN)

        if "Mira" in completed_chats:
            draw_text("3. Mira (completed)", box_y + 220, small_font, (150, 150, 150))  
        else:
            draw_text("3. Mira", box_y + 220, small_font, WINDOWS95_GREEN)

    elif state == STATE_CONVO:
        draw_header(selected_chat, typing, chat_active)
        box_x, box_y, box_width, box_height = draw_chatbox()

        
        if typing:
            text_to_show = typing_text.replace("{user}", username)
        else:
            text_to_show = str(current_line.get("text", "")).replace("{user}", username)

        text_bottom = draw_chat_text(text_to_show, small_font, box_x, box_y, box_width, box_height)

        draw_choices(current_line.get("choices", []), small_font, box_x, box_y, box_width, box_height, text_bottom)

        draw_player_input(player_input, small_font, box_x, box_y, box_width, box_height)

        if conversation_ended and not typing:
            draw_text("Press ENTER to return to chatroom", box_y + box_height + 30, small_font, WINDOWS95_GREEN)
    elif state == STATE_END:
        box_size = min(WIDTH, HEIGHT) // 2
        box_x = (WIDTH - box_size) // 2
        box_y = (HEIGHT - box_size) // 2
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_size, box_size))
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_size, box_size), 3)

        draw_text("All conversations complete.", box_y + 100, menu_font, WHITE)
        draw_text("Press ENTER to restart", box_y + 160, small_font, WINDOWS95_GREEN)
        draw_text("Press ESC to quit", box_y + 200, small_font, WINDOWS95_GREEN)


    
    pygame.display.flip()

pygame.quit()
sys.exit()
