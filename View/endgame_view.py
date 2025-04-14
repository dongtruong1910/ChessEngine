import pygame
import sys
from typing import Optional

# Màn hình kết thúc game
class EndgameView:

    def __init__(self, screen, winner: Optional[str] = None):
        self.screen = screen
        self.winner = winner
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Font cho text
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 28)

        # Màu sắc
        self.text_color = (255, 255, 255)
        self.button_color = (106, 168, 79)
        self.button_hover_color = (129, 194, 97)
        self.button_text_color = (255, 255, 255)

        # Các button
        self.continue_button = pygame.Rect(self.screen_width // 2 - 150, self.screen_height // 2 + 80, 120, 40)
        self.exit_button = pygame.Rect(self.screen_width // 2 + 30, self.screen_height // 2 + 80, 120, 40)

    # Vẽ Overlay và các button
    def draw(self):
        # Tạo lớp overlay mờ
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))  # Màu đen với độ trong suốt
        self.screen.blit(overlay, (0, 0))

        # Hiển thị kết quả
        if self.winner:
            title_text = f"{self.winner.capitalize()} wins!"
        else:
            title_text = "Draw!"

        title_surface = self.title_font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 60))
        self.screen.blit(title_surface, title_rect)

        # Hiển thị câu hỏi
        question = "Do you want to continue?"
        question_surface = self.text_font.render(question, True, self.text_color)
        question_rect = question_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(question_surface, question_rect)

        # Vẽ buttons
        self.draw_button(self.continue_button, "Yes")
        self.draw_button(self.exit_button, "No")

        # Cập nhật màn hình
        pygame.display.flip()

        return self.handle_events()

    # Vẽ button với hiệu ứng hover
    def draw_button(self, button_rect, text):
        # Kiểm tra hover
        mouse_pos = pygame.mouse.get_pos()
        color = self.button_hover_color if button_rect.collidepoint(mouse_pos) else self.button_color

        # Vẽ button
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)  # Viền

        # Vẽ text
        text_surface = self.text_font.render(text, True, self.button_text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

    # Xử lý sự kiện click chuột
    def handle_events(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.continue_button.collidepoint(event.pos):
                        # Return "restart" signal to main game loop
                        return "restart"

                    if self.exit_button.collidepoint(event.pos):
                        # Thoát game
                        pygame.quit()
                        sys.exit()

            # Cập nhật hiệu ứng hover
            mouse_pos = pygame.mouse.get_pos()
            if self.continue_button.collidepoint(mouse_pos) or self.exit_button.collidepoint(mouse_pos):
                # Vẽ lại nếu hover trên button
                self.draw_button(self.continue_button, "Yes")
                self.draw_button(self.exit_button, "No")
                pygame.display.update([self.continue_button, self.exit_button])