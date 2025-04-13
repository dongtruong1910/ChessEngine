from typing import Tuple, List, Optional
from Model.board import Board
from Model.piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King

class ChessAI:
    def __init__(self, color: str, depth: int = 3):
        self.color = color  # Màu quân của AI
        self.depth = depth  # Độ sâu tìm kiếm

        self.CHECK_MATE = 12000  # Giá trị đánh giá cho chiếu tướng
        self.STALE_MATE = 0  # Giá trị đánh giá cho hòa


        # Tham khảo hàm đánh giá https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function

        """
            Đây là giá trị cho white, nếu là black thì sẽ lấy giá trị âm
        """

        # Giá trị của từng loại quân cho midgame và endgame
        self.midgame_value = [82,337,365,477,1025,0]  # Tốt, Mã, Tượng, Xe, Hậu, Vua
        self.endgame_value = [94,281,297,512,936,0]  # Tốt, Mã, Tượng, Xe, Hậu, Vua


        """
            PST (Piece Square Table) - Bảng giá trị vị trí cho từng quân cờ. 
            Đây là cho white, nếu black thì sẽ đảo ngược hàng row = 7 - row
        """

        # Update midgame and endgame position values for each piece
        self.midgame_position_value = {
            Pawn: [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [98, 134, 61, 95, 68, 126, 34, -11],
                [-6, 7, 26, 31, 65, 56, 25, -20],
                [-14, 13, 6, 21, 23, 12, 17, -23],
                [-27, -2, -5, 12, 17, 6, 10, -25],
                [-26, -4, -4, -10, 3, 3, 33, -12],
                [-35, -1, -20, -23, -15, 24, 38, -22],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            Knight: [
                [-167, -89, -34, -49, 61, -97, -15, -107],
                [-73, -41, 72, 36, 23, 62, 7, -17],
                [-47, 60, 37, 65, 84, 129, 73, 44],
                [-9, 17, 19, 53, 37, 69, 18, 22],
                [-13, 4, 16, 13, 28, 19, 21, -8],
                [-23, -9, 12, 10, 19, 17, 25, -16],
                [-29, -53, -12, -3, -1, 18, -14, -19],
                [-105, -21, -58, -33, -17, -28, -19, -23]
            ],
            Bishop: [
                [-29, 4, -82, -37, -25, -42, 7, -8],
                [-26, 16, -18, -13, 30, 59, 18, -47],
                [-16, 37, 43, 40, 35, 50, 37, -2],
                [-4, 5, 19, 50, 37, 37, 7, -2],
                [-6, 13, 13, 26, 34, 12, 10, 4],
                [0, 15, 15, 15, 14, 27, 18, 10],
                [4, 15, 16, 0, 7, 21, 33, 1],
                [-33, -3, -14, -21, -13, -12, -39, -21]
            ],
            Rook: [
                [32, 42, 32, 51, 63, 9, 31, 43],
                [27, 32, 58, 62, 80, 67, 26, 44],
                [-5, 19, 26, 36, 17, 45, 61, 16],
                [-24, -11, 7, 26, 24, 35, -8, -20],
                [-36, -26, -12, -1, 9, -7, 6, -23],
                [-45, -25, -16, -17, 3, 0, -5, -33],
                [-44, -16, -20, -9, -1, 11, -6, -71],
                [-19, -13, 1, 17, 16, 7, -37, -26]
            ],
            Queen: [
                [-28, 0, 29, 12, 59, 44, 43, 45],
                [-24, -39, -5, 1, -16, 57, 28, 54],
                [-13, -17, 7, 8, 29, 56, 47, 57],
                [-27, -27, -16, -16, -1, 17, -2, 1],
                [-9, -26, -9, -10, -2, -4, 3, -3],
                [-14, 2, -11, -2, -5, 2, 14, 5],
                [-35, -8, 11, 2, 8, 15, -3, 1],
                [-1, -18, -9, 10, -15, -25, -31, -50]
            ],
            King: [
                [-65, 23, 16, -15, -56, -34, 2, 13],
                [29, -1, -20, -7, -8, -4, -38, -29],
                [-9, 24, 2, -16, -20, 6, 22, -22],
                [-17, -20, -12, -27, -30, -25, -14, -36],
                [-49, -1, -27, -39, -46, -44, -33, -51],
                [-14, -14, -22, -46, -44, -30, -15, -27],
                [1, 7, -8, -64, -43, -16, 9, 8],
                [-15, 36, 12, -54, 8, -28, 24, 14]
            ]
        }

        # Add endgame position values
        self.endgame_position_value = {
            Pawn: [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [178, 173, 158, 134, 147, 132, 165, 187],
                [94, 100, 85, 67, 56, 53, 82, 84],
                [32, 24, 13, 5, -2, 4, 17, 17],
                [13, 9, -3, -7, -7, -8, 3, -1],
                [4, 7, -6, 1, 0, -5, -1, -8],
                [13, 8, 8, 10, 13, 0, 2, -7],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            Knight: [
                [-58, -38, -13, -28, -31, -27, -63, -99],
                [-25, -8, -25, -2, -9, -25, -24, -52],
                [-24, -20, 10, 9, -1, -9, -19, -41],
                [-17, 3, 22, 22, 22, 11, 8, -18],
                [-18, -6, 16, 25, 16, 17, 4, -18],
                [-23, -3, -1, 15, 10, -3, -20, -22],
                [-42, -20, -10, -5, -2, -20, -23, -44],
                [-29, -51, -23, -15, -22, -18, -50, -64]
            ],
            Bishop: [
                [-14, -21, -11, -8, -7, -9, -17, -24],
                [-8, -4, 7, -12, -3, -13, -4, -14],
                [2, -8, 0, -1, -2, 6, 0, 4],
                [-3, 9, 12, 9, 14, 10, 3, 2],
                [-6, 3, 13, 19, 7, 10, -3, -9],
                [-12, -3, 8, 10, 13, 3, -7, -15],
                [-14, -18, -7, -1, 4, -9, -15, -27],
                [-23, -9, -23, -5, -9, -16, -5, -17]
            ],
            Rook: [
                [13, 10, 18, 15, 12, 12, 8, 5],
                [11, 13, 13, 11, -3, 3, 8, 3],
                [7, 7, 7, 5, 4, -3, -5, -3],
                [4, 3, 13, 1, 2, 1, -1, 2],
                [3, 5, 8, 4, -5, -6, -8, -11],
                [-4, 0, -5, -1, -7, -12, -8, -16],
                [-6, -6, 0, 2, -9, -9, -11, -3],
                [-9, 2, 3, -1, -5, -13, 4, -20]
            ],
            Queen: [
                [-9, 22, 22, 27, 27, 19, 10, 20],
                [-17, 20, 32, 41, 58, 25, 30, 0],
                [-20, 6, 9, 49, 47, 35, 19, 9],
                [3, 22, 24, 45, 57, 40, 57, 36],
                [-18, 28, 19, 47, 31, 34, 39, 23],
                [-16, -27, 15, 6, 9, 17, 10, 5],
                [-22, -23, -30, -16, -16, -23, -36, -32],
                [-33, -28, -22, -43, -5, -32, -20, -41]
            ],
            King: [
                [-74, -35, -18, -18, -11, 15, 4, -17],
                [-12, 17, 14, 17, 17, 38, 23, 11],
                [10, 17, 23, 15, 20, 45, 44, 13],
                [-8, 22, 24, 27, 26, 33, 26, 3],
                [-18, -4, 21, 24, 27, 23, 9, -11],
                [-19, -3, 11, 21, 23, 16, 7, -9],
                [-27, -11, 4, 13, 14, 4, -5, -17],
                [-53, -34, -21, -11, -28, -14, -24, -43]
            ]
        }

        # Game phase increments for each piece (used for tapered evaluation)
        self.gamephase_inc = {
            Pawn: 0,
            Knight: 1,
            Bishop: 1,
            Rook: 2,
            Queen: 4,
            King: 0
        }
    def get_piece_index(self,piece_type):
        """Maps piece type to index for value arrays"""
        if piece_type == Pawn:
            return 0
        elif piece_type == Knight:
            return 1
        elif piece_type == Bishop:
            return 2
        elif piece_type == Rook:
            return 3
        elif piece_type == Queen:
            return 4
        elif piece_type == King:
            return 5
        return 0  # Default case

    def evaluate_board(self, board: Board) -> int:
        """
        Evaluate the board using piece values and position tables with tapered evaluation.
        Combines midgame and endgame scores based on the game phase.
        Returns a score from the perspective of the AI's color.
        """
        mg_score = {"white": 0, "black": 0}
        eg_score = {"white": 0, "black": 0}
        game_phase = 0

        # Evaluate each piece on the board
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece:
                    # Get basic piece value and position value
                    piece_type = type(piece)
                    color = piece.color

                    # Get the position value, flip row for black pieces
                    pos_row = row if color == "white" else 7 - row

                    piece_index = self.get_piece_index(piece_type)

                    # Add midgame and endgame values
                    mg_score[color] += self.midgame_value[piece_index] + \
                                       self.midgame_position_value[piece_type][pos_row][col]
                    eg_score[color] += self.endgame_value[piece_index] + \
                                       self.endgame_position_value[piece_type][pos_row][col]

                    # Update game phase
                    game_phase += self.gamephase_inc[piece_type]

        # Calculate total scores for midgame and endgame
        mg_total = mg_score["white"] - mg_score["black"]
        eg_total = eg_score["white"] - eg_score["black"]

        # Calculate tapered score based on game phase
        # Max phase value is 24 (1 point for knights/bishops, 2 for rooks, 4 for queens)
        mg_phase = min(game_phase, 24)
        eg_phase = 24 - mg_phase

        # Calculate final score
        score = (mg_total * mg_phase + eg_total * eg_phase) // 24

        # Return score from AI's perspective
        return score if self.color == "white" else -score

    def minimax_alpha_beta(self, board: Board, depth: int, alpha: float, beta: float,
                           is_maximizing: bool) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Thuật toán alpha-beta pruning để tìm nước đi tốt nhất.
        """
        # # Increment position counter
        # if not hasattr(self, 'positions_evaluated'):
        #     self.positions_evaluated = 0
        # self.positions_evaluated += 1

        # Kiểm tra điều kiện dừng
        if depth == 0:
            return self.evaluate_board(board), None

        # Kiểm tra chiếu tướng hoặc hòa cờ
        if board.is_checkmate("white"):
            return -self.CHECK_MATE if self.color == "white" else self.CHECK_MATE, None
        elif board.is_checkmate("black"):
            return self.CHECK_MATE if self.color == "white" else -self.CHECK_MATE, None
        elif board.is_stalemate():
            return self.STALE_MATE, None

        # Lấy màu quân hiện tại
        current_color = self.color if is_maximizing else ("black" if self.color == "white" else "white")

        # Lấy tất cả các nước đi có thể
        possible_moves = self.get_all_possible_moves(board, current_color)

        # Nếu không có nước đi nào
        if not possible_moves:
            return self.STALE_MATE, None

        best_move = None
        if is_maximizing:
            best_score = float('-inf')
            for start, end in possible_moves:
                # # Thực hiện nước đi
                # board.move_piece(start, end)

                # Tạo bản sao của bàn cờ để thử nước đi
                board_copy = board.clone()
                board_copy.move_piece(start, end)

                # Đệ quy với độ sâu giảm 1
                score, _ = self.minimax_alpha_beta(board_copy, depth - 1, alpha, beta, False)

                # # Hoàn tác nước đi
                # board.undo_move()

                # Cập nhật nước đi tốt nhất
                if score > best_score:
                    best_score = score
                    best_move = (start, end)

                # Cập nhật alpha
                alpha = max(alpha, best_score)

                # Cắt tỉa beta
                if beta <= alpha:
                    break
        else:
            best_score = float('inf')
            for start, end in possible_moves:
                # # Thực hiện nước đi
                # board.move_piece(start, end)

                # Tạo bản sao của bàn cờ để thử nước đi
                board_copy = board.clone()
                board_copy.move_piece(start, end)

                # Đệ quy với độ sâu giảm 1
                score, _ = self.minimax_alpha_beta(board_copy, depth - 1, alpha, beta, True)

                # # Hoàn tác nước đi
                # board.undo_move()

                # Cập nhật nước đi tốt nhất
                if score < best_score:
                    best_score = score
                    best_move = (start, end)

                # Cập nhật beta
                beta = min(beta, best_score)

                # Cắt tỉa alpha
                if beta <= alpha:
                    break

        return best_score, best_move

    def get_best_move(self, board: Board, use_alpha_beta: bool = True) -> Optional[
        Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Tìm nước đi tốt nhất cho AI dựa trên thuật toán minimax với alpha-beta pruning.
        """
        # # Reset the position counter
        # self.positions_evaluated = 0

        # Kiểm tra xem có phải lượt của AI không
        if board.current_turn != self.color:
            return None

        # Khởi tạo các giá trị alpha và beta cho alpha-beta pruning
        alpha = float('-inf')
        beta = float('inf')

        # # Get all possible moves for AI
        # possible_moves = self.get_all_possible_moves(board, self.color)
        #
        # # # Debug: Print all moves and their evaluations
        # # print(f"Evaluating {len(possible_moves)} possible moves for {self.color}")
        #
        # # best_score = float('-inf')
        # # best_move = None
        #
        # # # Evaluate each move directly
        # # for start, end in possible_moves:
        # #     # Make move on a copy of the board
        # #     board_copy = board.clone()
        # #     board_copy.move_piece(start, end)
        # #
        # #     # Evaluate the resulting position
        # #     evaluation = self.evaluate_board(board_copy)
        # #
        # #     # Debug output
        # #     print(f"Move {start} -> {end}: Score = {evaluation}")
        # #
        # #     # Keep track of best move
        # #     if evaluation > best_score:
        # #         best_score = evaluation
        # #         best_move = (start, end)
        #
        # # print(f"Best move: {best_move} with score {best_score}")
        #
        # # Alternatively, use the original minimax
        _, minimax_move = self.minimax_alpha_beta(
            board=board,
            depth=self.depth,
            alpha=alpha,
            beta=beta,
            is_maximizing=True
        )

        # print(f"Minimax suggested move: {minimax_move}")

        # Return the original minimax move
        return minimax_move

    def get_all_possible_moves(self, board: Board, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Lấy tất cả các nước đi có thể cho một bên
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece and piece.color == color:
                    valid_moves = board.get_valid_moves((row, col))
                    for move in valid_moves:
                        moves.append(((row, col), move))
        return moves
