import sys
import random

import pygame

from spritesheet import Spritesheet


pygame.init()
screen = pygame.display.set_mode((600, 800))
clock = pygame.time.Clock()
FPS = 60

background = pygame.image.load("assets/background.png")
number_spritesheeet = Spritesheet("assets/numbers.png")


class Game:
    def __init__(self, guesses):
        self.ANSWER = [random.randint(1, 9)] + [random.randint(0, 9) for i in range(guesses-2)]
        print("".join(map(str, self.ANSWER)))
        self.MAX_GUESSES = guesses
        self.current_guess = 0
        
        self.guess_table = [
            [None for _ in range(5)] for _ in range(self.MAX_GUESSES)
        ]
    

        self.numbers = [
            pygame.transform.scale(
                number_spritesheeet.load_sprite(
                    f"numbers{number}.png", 
                    colourkey=(255, 0, 0)
                ), 
                (70, 70)
            ) for number in range(10)
        ]
        
        self.base = self.numbers[0].copy()
        self.base.set_colorkey((0, 0, 0))
        self.IMAGE_SIZE = self.base.get_width()
        self.images = [self._convert(guess) for guess in self.guess_table]
        
        self.current_key = 0
  
        
    def _is_valid_guess(self, guess):
        return None not in guess and guess[0] != 0
    

    def _convert(self, guess):
        image_array = []
        for number in guess:
            if type(number) == int:
                
                image = self.numbers[number]               
                image_array.append(image)
                
            else:
                image_array.append(self.base)

        return image_array
    

    def _set_colour(self, surface, colour):
        width, height = surface.get_size()

        for x in range(width):
            for y in range(height):
                current_colour = surface.get_at((x, y))
                if current_colour == (0, 0, 0, 255):
                    surface.set_at((x, y), (255, 255, 255, 255)) 
                       
                                
                elif current_colour == (255, 255, 255, 255) or current_colour == (164, 164, 164, 255):
                    surface.set_at((x, y), colour)
                    
        return surface
        
        
    def _submit(self, index):
        count = {digit: 0 for digit in self.ANSWER.copy()}
        checked = [False for i in self.ANSWER.copy()]
        colours = [(85, 85, 85, 255) for _ in self.ANSWER.copy()]

      
        for i, number in enumerate(self.guess_table[index]):
            answer_digit = self.ANSWER[i]
            if number == answer_digit:
                count[answer_digit] += 1
                colours[i] = (106, 170, 100, 255)
                checked[i] = True
                
                if count[answer_digit] >= self.ANSWER.count(number):
                    count[answer_digit] = float("inf")
                    
        
        for i, number in enumerate(self.guess_table[index]):
            answer_digit = self.ANSWER[i]
            
            if number in self.ANSWER and count[number] < self.ANSWER.count(number) and not checked[i]:
                count[number] += 1
                colours[i] = (201, 180, 88, 255)
            
        return colours
    
    
    def _play_win_animation(self, surface):
        f = lambda x: -x ** 2 + 30.25
        
        for i, image in enumerate(self.images[self.current_guess]):
            x_pos, y_pos = 114 + i * (self.IMAGE_SIZE + 6), 125 + self.current_guess * (self.IMAGE_SIZE + 10)
            
            for j in range(-55, 55):
                surface.fill((255, 255, 255))
                surface.blit(background, (100, 25))
                self._draw(surface)
                pygame.draw.rect(surface, (255, 255, 255), (x_pos, y_pos, self.IMAGE_SIZE, self.IMAGE_SIZE))
                surface.blit(image, (x_pos, y_pos - f(j/10)))
                pygame.display.flip()
                
        surface.fill((255, 255, 255))
        surface.blit(background, (100, 25))
        self._draw(surface)
        pygame.display.flip()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    
    def _play_valid_guess_animation(self, surface):
        def play(axis): 
            for rotation in axis:
                self._draw(surface)
                pygame.draw.rect(surface, (255, 255, 255), (x, y, self.IMAGE_SIZE, self.IMAGE_SIZE))
                surface.blit(pygame.transform.scale(image, (self.IMAGE_SIZE, self.IMAGE_SIZE - rotation)),  (x, rotation/2 + y))
                pygame.time.delay(2)
                pygame.display.flip()
            
        colours = self._submit(self.current_guess)
        
        for i, image in enumerate(self.images[self.current_guess]):
            x, y = 114 + i * (self.IMAGE_SIZE + 6), 125 + self.current_guess * (self.IMAGE_SIZE + 10)
            play(range(self.IMAGE_SIZE)) 
            self._draw(surface)
            image = self._set_colour(image.copy(), colours[i])
            self.images[self.current_guess][i] = image
            play(range(self.IMAGE_SIZE, 0, -1))
            
            
        if self.guess_table[self.current_guess] == self.ANSWER:
            surface.fill((255, 255, 255))
            self._draw(surface)
            self._play_win_animation(surface)
                        
        return surface  
    
 
    def _play_invalid_guess_animation(self, surface):
        def draw():
            surface.fill((255, 255, 255))
            surface.blit(background, (100, 25))
            
            for i, row in enumerate(self.images):    
                image_y = 125 + i * (self.IMAGE_SIZE + 10)
                
                for j, image in enumerate(row):
                    image_x = 114 + j * (self.IMAGE_SIZE + 6)
                
                    if i == self.current_guess:
                        surface.blit(image,  (offset + image_x, image_y))
                        
                    else:
                        surface.blit(image,  (image_x, image_y))
                        
                pygame.time.delay(2)   
            
            pygame.display.flip()
            
        offset = 1
        
        for _ in range(4):
            offset *= -2
            draw()
            
        for _ in range(4):
            offset /= -2
            draw()
            
            
    def _animate_guess(self, surface):
        if not self._is_valid_guess(self.guess_table[self.current_guess]):
            self._play_invalid_guess_animation(surface)
            
        else:
            self._play_valid_guess_animation(surface)


    def _draw(self, surface): 
        for i, row in enumerate(self.images):
            for j, image in enumerate(row):
                surface.blit(image,  (114 + j * (self.IMAGE_SIZE + 6), 125 + i * (self.IMAGE_SIZE + 10)))
          
                
    def update_guesses(self, surface, event):
        # 13 = ENTER
        if event.key == 13:
            self._animate_guess(surface)
        
            if self._is_valid_guess(self.guess_table[self.current_guess]):
                if self.current_guess >= len(self.guess_table) - 1:
                    self.guess_table.pop(0)
                    self.guess_table.append([None for _ in range(5)])
                    self.images.pop(0)
                    self.images.append(self._convert([None for _ in range(5)]))
    
                    
                else:
                    self.current_guess += 1
                    self._draw(surface)
                    
                self.current_key = 0


        
        elif event.key == pygame.K_BACKSPACE:
            self.current_key = max(0, self.current_key-1)
            self.guess_table[self.current_guess][self.current_key] = None
            self.images[self.current_guess] = self._convert(self.guess_table[self.current_guess])

        else:
            number = event.unicode
            
            if number.isdigit() and self.current_key < 5:  
                self.guess_table[self.current_guess][self.current_key] = int(number)
                self.current_key = self.current_key + 1
                self.images[self.current_guess] = self._convert(self.guess_table[self.current_guess])
                                  

    def update(self, surface):
        self._draw(surface)


game = Game(6)

while True:
    screen.fill((255, 255, 255))
    screen.blit(background, (100, 25))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
           
        if event.type == pygame.KEYDOWN:
            game.update_guesses(screen, event)
           
    
    game.update(screen)
    pygame.display.flip()
    clock.tick(FPS)
