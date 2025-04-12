import pygame
import os
import sys

class MenuView:
    """
    Hiển thị màn hình bắt đầu game cờ vua với tùy chọn chọn quân đen hoặc trắng.
    """
    def __init__(self, screen_width=800, screen_height=600):
        # Khởi tạo pygame
        pygame.init()
        pygame.display.set_caption("Chess Game")
        
        # Tạo màn hình
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.width = screen_width
        self.height = screen_height
        
        # Màu sắc
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (100, 100, 100)
        self.LIGHT_BLUE = (173, 216, 230)
        self.GREEN = (144, 238, 144)  # Light green
        self.DARK_GREEN = (0, 100, 0)  # Dark green
        
        # Font chữ
        self.title_font = pygame.font.SysFont('Arial', 60, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 30)
        
        # Tạo các nút chọn
        self.white_button = pygame.Rect(self.width//4 - 75, self.height//2, 150, 150)
        self.black_button = pygame.Rect(3*self.width//4 - 75, self.height//2, 150, 150)
        self.start_button = pygame.Rect(self.width//2 - 100, self.height*3//4, 200, 60)
        
        # Tạo các nút chọn thời gian
        button_width = 100
        button_height = 40
        button_spacing = 20
        total_width = 3 * button_width + 2 * button_spacing
        start_x = (self.width - total_width) // 2
        
        self.time_buttons = {
            "5": pygame.Rect(start_x, self.height//2 - 100, button_width, button_height),
            "10": pygame.Rect(start_x + button_width + button_spacing, self.height//2 - 100, button_width, button_height),
            "15": pygame.Rect(start_x + 2 * (button_width + button_spacing), self.height//2 - 100, button_width, button_height)

        }
        
        # Tạo hình ảnh cho vua trắng và đen
        self.white_king_img = pygame.image.load(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'white_king.png'))
        self.black_king_img = pygame.image.load(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'black_king.png'))
        
        # Trạng thái chọn
        self.selected_color = None
        self.selected_time = None
        
    def show(self):
        """Hiển thị màn hình chính và xử lý tương tác"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Kiểm tra nút quân trắng
                    if self.white_button.collidepoint(mouse_pos):
                        self.selected_color = "white"
                    
                    # Kiểm tra nút quân đen
                    elif self.black_button.collidepoint(mouse_pos):
                        self.selected_color = "black"
                    
                    # Kiểm tra các nút thời gian
                    for time, button in self.time_buttons.items():
                        if button.collidepoint(mouse_pos):
                            self.selected_time = time
                    
                    # Kiểm tra nút bắt đầu
                    if self.start_button.collidepoint(mouse_pos) and self.selected_color and self.selected_time:
                        return {"color": self.selected_color, "time": self.selected_time}
            
            # Vẽ nền
            self.screen.fill(self.LIGHT_BLUE)
            
            # Vẽ tiêu đề
            title_text = self.title_font.render("CHESS GAME", True, self.BLACK)
            self.screen.blit(title_text, (self.width//2 - title_text.get_width()//2, 50))
            
            # Vẽ nút chọn quân trắng
            pygame.draw.rect(self.screen, 
                            self.WHITE if self.selected_color != "white" else self.GRAY, 
                            self.white_button)
            pygame.draw.rect(self.screen, self.BLACK, self.white_button, 2)
            self.screen.blit(self.white_king_img, 
                            (self.white_button.x + 15, self.white_button.y + 15))
            
            # Vẽ nút chọn quân đen
            pygame.draw.rect(self.screen, 
                            self.DARK_GRAY if self.selected_color != "black" else self.GRAY, 
                            self.black_button)
            pygame.draw.rect(self.screen, self.BLACK, self.black_button, 2)
            self.screen.blit(self.black_king_img, 
                            (self.black_button.x + 15, self.black_button.y + 15))
            
            # Vẽ các nút chọn thời gian
            time_label = self.button_font.render("Choose time (minute)", True, self.BLACK)
            self.screen.blit(time_label, (self.width//2 - time_label.get_width()//2, self.height//2 - 150))
            
            for time, button in self.time_buttons.items():
                pygame.draw.rect(self.screen,
                               self.DARK_GREEN if self.selected_time == time else self.GREEN,
                               button)
                pygame.draw.rect(self.screen, self.BLACK, button, 2)
                
                time_text = self.button_font.render(f"{time}", True, self.BLACK)
                self.screen.blit(time_text,
                               (button.x + button.width//2 - time_text.get_width()//2,
                                button.y + button.height//2 - time_text.get_height()//2))

            # Vẽ nút bắt đầu
            pygame.draw.rect(self.screen, 
                            self.GRAY if self.selected_color and self.selected_time else self.DARK_GRAY, 
                            self.start_button)
            pygame.draw.rect(self.screen, self.BLACK, self.start_button, 2)
            
            start_text = self.button_font.render("START", True, self.BLACK)
            self.screen.blit(start_text, 
                            (self.start_button.x + self.start_button.width//2 - start_text.get_width()//2, 
                             self.start_button.y + self.start_button.height//2 - start_text.get_height()//2))
            
            pygame.display.flip() 