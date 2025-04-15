import pygame
import sys
from View.menu_view import MenuView
from Controller.game_controller import GameController


class ChessGame:
    def __init__(self, screen_width=800, screen_height=600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.board_size = min(screen_width, screen_height) - 100
        self.margin = 30
        pygame.init()  # Initialize pygame once at startup

    def run(self):
        # Main application loop that continues until the user quits
        while True:
            # Show menu and get player info
            menu = MenuView(self.screen_width, self.screen_height)
            player_info = menu.show()

            if not player_info:  # If player exits menu
                pygame.quit()
                sys.exit()

            # Initialize controller with player info
            controller = GameController(
                player_color=player_info['color'],
                time_limit=int(player_info['time'])
            )
            controller.init_view(self.board_size, self.margin)

            # Game loop
            running_game = True
            while running_game:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        controller.handle_click(pygame.mouse.get_pos())

                # Update display
                controller.run()

                # Check if game is over
                if controller.game_over:
                    result = controller.board_view.show_game_over(controller.winner)
                    if result == "restart":
                        # Exit game loop to return to menu
                        running_game = False
                        break

                pygame.display.flip()


# Launch game
if __name__ == "__main__":
    game = ChessGame()
    game.run()