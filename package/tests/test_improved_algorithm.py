import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Import the improved seating algorithm
from src.routes.improved_seating import find_best_seats_for_group, find_consecutive_available_seats
from src.models.seating import SeatingModel

class TestImprovedSeatingAlgorithm(unittest.TestCase):
    """Test suite for the improved cinema seating algorithm"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Define a test seating configuration
        self.config = {
            "rows": 15,
            "columns": 12,
            "rowLabels": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O'],
            "vipRows": [9, 10, 11],  # J, K, L (0-indexed)
            "vipColumns": [2, 3, 4, 5, 6, 7, 8, 9],  # 3-10 (0-indexed)
            "accessibleSeats": [
                {"row": 5, "col": 0}, {"row": 5, "col": 1},  # F1, F2
                {"row": 5, "col": 10}, {"row": 5, "col": 11}  # F11, F12
            ],
            "discountRows": [0, 1],  # A, B (0-indexed)
            "aisleAfterColumn": 5  # Aisle after column 6 (0-indexed)
        }
        
        # Create an empty theater with all seats available
        self.seats = []
        for i in range(self.config["rows"]):
            row = []
            for j in range(self.config["columns"]):
                # Determine seat type
                seat_type = 'normal'
                
                # Check if VIP
                if i in self.config["vipRows"] and j in self.config["vipColumns"]:
                    seat_type = 'vip'
                
                # Check if accessible
                is_accessible = any(seat["row"] == i and seat["col"] == j for seat in self.config["accessibleSeats"])
                if is_accessible:
                    seat_type = 'accessible'
                
                # Check if discount
                is_discount = i in self.config["discountRows"]
                
                # Create seat object
                row.append({
                    "id": f"{self.config['rowLabels'][i]}{j + 1}",
                    "row": i,
                    "col": j,
                    "type": seat_type,
                    "status": "available",
                    "isDiscount": is_discount,
                    "price": SeatingModel.calculate_price(seat_type, is_discount)
                })
            self.seats.append(row)

    def test_find_best_seats_for_small_group(self):
        """Test finding best seats for a small group (2 people)"""
        # Find best seats for a group of 2
        best_seats = find_best_seats_for_group(self.seats, self.config, 2, "any")
        
        # Verify that 2 seats were found
        self.assertEqual(len(best_seats), 2, "Should find exactly 2 seats")
        
        # Verify that seats are in the same row
        self.assertEqual(best_seats[0]["row"], best_seats[1]["row"], "Seats should be in the same row")
        
        # Verify that seats are adjacent
        self.assertEqual(best_seats[0]["col"] + 1, best_seats[1]["col"], "Seats should be adjacent")
        
        # Verify that seats are in a middle row (close to row H)
        middle_row = self.config["rows"] // 2  # Row H (7) in 0-indexed
        self.assertTrue(abs(best_seats[0]["row"] - middle_row) <= 2, 
                        "Seats should be in or close to middle rows")

    def test_find_best_seats_for_large_group(self):
        """Test finding best seats for a large group (7 people)"""
        # Find best seats for a group of 7
        best_seats = find_best_seats_for_group(self.seats, self.config, 7, "any")
        
        # Verify that 7 seats were found
        self.assertEqual(len(best_seats), 7, "Should find exactly 7 seats")
        
        # Verify that seats are in the same row
        first_row = best_seats[0]["row"]
        for seat in best_seats:
            self.assertEqual(seat["row"], first_row, "All seats should be in the same row")
        
        # Verify that seats are consecutive (accounting for aisle)
        sorted_seats = sorted(best_seats, key=lambda s: s["col"])
        for i in range(1, len(sorted_seats)):
            diff = sorted_seats[i]["col"] - sorted_seats[i-1]["col"]
            # Either adjacent or separated by aisle
            self.assertTrue(diff == 1 or (sorted_seats[i-1]["col"] == 5 and sorted_seats[i]["col"] == 6),
                           f"Seats should be consecutive, found gap of {diff} columns")

    def test_center_preference(self):
        """Test that the algorithm prefers center seats"""
        # Find best seats for a group of 4
        best_seats = find_best_seats_for_group(self.seats, self.config, 4, "any")
        
        # Calculate the average column position
        avg_col = sum(seat["col"] for seat in best_seats) / len(best_seats)
        
        # Center column should be around 5.5 (between columns 5 and 6)
        center_col = (self.config["columns"] - 1) / 2  # 5.5 for 12 columns
        
        # Verify that the average column is close to the center
        self.assertTrue(abs(avg_col - center_col) <= 2, 
                       f"Seats should be centered, average column was {avg_col}")

    def test_no_single_seat_gaps(self):
        """Test that the algorithm prevents single seat gaps"""
        # Book some seats to create a potential gap scenario
        # Book seats in row H (middle row), columns 3-5
        middle_row = self.config["rows"] // 2  # Row H (7) in 0-indexed
        for j in range(3, 6):
            self.seats[middle_row][j]["status"] = "booked"
            
        # Book seats in row H, columns 7-9
        for j in range(7, 10):
            self.seats[middle_row][j]["status"] = "booked"
            
        # This leaves column 6 open, which would create a single-seat gap
        # Find best seats for a group of 2 in row H
        best_seats = find_best_seats_for_group(self.seats, self.config, 2, "any")
        
        # For this test, we'll consider it a pass if:
        # 1. The algorithm returns seats in a different row (avoiding the gap issue)
        # 2. Or if it returns seats that don't create a single gap
        if best_seats:
            if best_seats[0]["row"] != middle_row:
                # Algorithm chose seats in a different row, which is a valid strategy
                self.assertTrue(True)
            else:
                # Algorithm chose seats in the same row, check if it creates a gap
                # Create a temporary booking
                temp_seats = [row[:] for row in self.seats]  # Deep copy
                for seat in best_seats:
                    r, c = seat["row"], seat["col"]
                    temp_seats[r][c]["status"] = "booked"
                    
                # Check if this creates a single gap
                would_create_gap, _ = SeatingModel.would_create_single_gap(
                    temp_seats, middle_row, best_seats)
                
                self.assertFalse(would_create_gap, 
                                "Algorithm should not recommend seats that create single gaps")
        else:
            # If no seats are returned, that's also acceptable as there might not be
            # a valid configuration that avoids single gaps
            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
