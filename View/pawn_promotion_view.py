import pygame
import os
from typing import Optional

# Giao diện phong cấp
class PawnPromotionView:

    def __init__(self, screen, square_size):
        self.screen = screen
        self.square_size = square_size

        # Màu sắc
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.HIGHLIGHT = (173, 216, 230)  # Light blue

        # Load hình ảnh quân cờ
        self.piece_images = {}
        self.load_piece_images()

        # Các loại quân phong cấp
        self.promotion_pieces = ["queen", "rook", "bishop", "knight"]

    def load_piece_images(self):
        pieces = ["queen", "rook", "bishop", "knight"]
        colors = ["white", "black"]

        for color in colors:
            for piece in pieces:
                image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                          'assets', 'images', f'{color}_{piece}.png')
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path)
                    image = pygame.transform.scale(image, (self.square_size, self.square_size))
                    self.piece_images[f"{color}_{piece}"] = image

    # Hiển thị hộp phong cấp
    def display_pawn_promotion(self, color: str, col: int) -> Optional[str]:
        width, height = self.screen.get_size()
        x = max(0, min(col * self.square_size, width - 4 * self.square_size))
        y = height // 2 - self.square_size // 2

        # Tạo các ô vuông cho từng quân cờ phong cấp
        piece_rects = []
        for i in range(4):
            piece_rects.append(pygame.Rect(
                x + i * self.square_size,
                y,
                self.square_size,
                self.square_size
            ))

        # Vẽ hộp phong cấp
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        # Vẽ các ô vuông và quân cờ
        for i, (piece_type, rect) in enumerate(zip(self.promotion_pieces, piece_rects)):
            # Vẽ ô vuông
            pygame.draw.rect(self.screen, self.WHITE, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2)

            # Vẽ quân cờ
            image_key = f"{color}_{piece_type}"
            if image_key in self.piece_images:
                self.screen.blit(self.piece_images[image_key], rect)

        pygame.display.flip()

        # Xử lý tương tác
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "queen"  # Mặc định là hậu

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Kiểm tra xem người dùng click vào quân cờ nào
                    for i, rect in enumerate(piece_rects):
                        if rect.collidepoint(mouse_pos):
                            return self.promotion_pieces[i]

        return "queen"  # Mặc định là hậu

    def get_pawn_promotion_choice(self, color: str, col: int) -> str:
        return self.display_pawn_promotion(color, col)