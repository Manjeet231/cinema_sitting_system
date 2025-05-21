from flask import Blueprint, jsonify, request
import json
import os

seating_bp = Blueprint('seating', __name__)

# In-memory storage for seating data
# In a production app, this would be stored in a database
SEATING_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'seating.json')

# Ensure data directory exists
os.makedirs(os.path.dirname(SEATING_DATA_FILE), exist_ok=True)

# Initialize seating data if it doesn't exist
def initialize_seating_data():
    if not os.path.exists(SEATING_DATA_FILE):
        # Default seating configuration
        seating_config = {
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
        
        # Pricing
        pricing = {
            "normal": 10.00,
            "vip": 15.00,
            "accessible": 10.00,
            "discount": 7.50
        }
        
        # Generate seats
        seats = []
        for i in range(seating_config["rows"]):
            row = []
            for j in range(seating_config["columns"]):
                # Determine seat type
                seat_type = 'normal'
                
                # Check if VIP
                if i in seating_config["vipRows"] and j in seating_config["vipColumns"]:
                    seat_type = 'vip'
                
                # Check if accessible
                is_accessible = any(seat["row"] == i and seat["col"] == j for seat in seating_config["accessibleSeats"])
                if is_accessible:
                    seat_type = 'accessible'
                
                # Check if discount
                is_discount = i in seating_config["discountRows"]
                
                # Calculate price
                price = pricing["normal"]
                if is_discount and seat_type == 'normal':
                    price = pricing["discount"]
                elif seat_type == 'vip':
                    price = pricing["vip"]
                elif seat_type == 'accessible':
                    price = pricing["accessible"]
                
                # Create seat object
                row.append({
                    "id": f"{seating_config['rowLabels'][i]}{j + 1}",
                    "row": i,
                    "col": j,
                    "type": seat_type,
                    "status": "available",
                    "isDiscount": is_discount,
                    "price": price
                })
            seats.append(row)
        
        # Save to file
        with open(SEATING_DATA_FILE, 'w') as f:
            json.dump({
                "config": seating_config,
                "pricing": pricing,
                "seats": seats
            }, f)

# Initialize seating data
initialize_seating_data()

# Get seating data
def get_seating_data():
    try:
        with open(SEATING_DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        initialize_seating_data()
        with open(SEATING_DATA_FILE, 'r') as f:
            return json.load(f)

# Save seating data
def save_seating_data(data):
    with open(SEATING_DATA_FILE, 'w') as f:
        json.dump(data, f)

@seating_bp.route('/config', methods=['GET'])
def get_config():
    """Get seating configuration"""
    data = get_seating_data()
    return jsonify({
        "config": data["config"],
        "pricing": data["pricing"]
    })

@seating_bp.route('/seats', methods=['GET'])
def get_seats():
    """Get all seats"""
    data = get_seating_data()
    return jsonify(data["seats"])

@seating_bp.route('/seats', methods=['POST'])
def update_seats():
    """Update seats (used for booking or admin changes)"""
    data = get_seating_data()
    request_data = request.json
    
    # Update seats based on request
    for seat_update in request_data:
        row = seat_update.get("row")
        col = seat_update.get("col")
        status = seat_update.get("status")
        
        if row is not None and col is not None and status is not None:
            data["seats"][row][col]["status"] = status
    
    # Save updated data
    save_seating_data(data)
    return jsonify({"success": True})

@seating_bp.route('/best-seats', methods=['POST'])
def find_best_seats():
    """Find best seats for a group"""
    data = get_seating_data()
    request_data = request.json
    
    group_size = request_data.get("groupSize", 1)
    seat_type = request_data.get("seatType", "any")
    
    # Call the seating algorithm to find best seats
    best_seats = find_best_seats_for_group(data["seats"], data["config"], group_size, seat_type)
    
    return jsonify(best_seats)

def find_best_seats_for_group(seats, config, group_size, seat_type):
    """Algorithm to find best seats for a group"""
    # Priority: middle rows, consecutive seats, centered
    middle_row = config["rows"] // 2
    row_priority = sorted(range(config["rows"]), key=lambda i: abs(middle_row - i))
    
    # Check each row for consecutive available seats
    for row_index in row_priority:
        row = seats[row_index]
        
        # Skip if we're looking for specific seat types that don't match this row
        if seat_type == 'vip' and row_index not in config["vipRows"]:
            continue
        if seat_type == 'accessible' and not any(seat["row"] == row_index for seat in config["accessibleSeats"]):
            continue
        
        # Find consecutive available seats in this row
        available_groups = find_consecutive_available_seats(row, config, group_size, seat_type)
        
        if available_groups:
            # Sort groups by distance from center
            center_col = config["columns"] // 2
            available_groups.sort(key=lambda group: abs(sum(seat["col"] for seat in group) / len(group) - center_col))
            
            # Return the best group (closest to center)
            return available_groups[0]
    
    # If no consecutive seats found, try to find any available seats
    if seat_type != 'any':
        return find_best_seats_for_group(seats, config, group_size, 'any')
    
    # If still no seats found, return empty array
    return []

def find_consecutive_available_seats(row, config, group_size, seat_type):
    """Find consecutive available seats in a row"""
    groups = []
    current_group = []
    
    # Account for aisle
    row_with_aisle = list(row)
    row_with_aisle.insert(config["aisleAfterColumn"] + 1, None)
    
    for i, seat in enumerate(row_with_aisle):
        # Skip aisle
        if seat is None:
            if len(current_group) >= group_size:
                groups.append(current_group.copy())
            current_group = []
            continue
        
        is_available = seat["status"] == "available"
        matches_type = seat_type == 'any' or seat["type"] == seat_type
        
        if is_available and matches_type:
            current_group.append(seat)
        else:
            if len(current_group) >= group_size:
                groups.append(current_group.copy())
            current_group = []
    
    # Check the last group
    if len(current_group) >= group_size:
        groups.append(current_group.copy())
    
    # For each group, take exactly the number of seats needed
    result = []
    for group in groups:
        # If group is larger than needed, take seats from the middle
        if len(group) > group_size:
            start_index = (len(group) - group_size) // 2
            result.append(group[start_index:start_index + group_size])
        else:
            result.append(group)
    
    return result

@seating_bp.route('/reset', methods=['POST'])
def reset_seats():
    """Reset all seats to available (admin function)"""
    data = get_seating_data()
    
    # Reset all seats to available
    for row in data["seats"]:
        for seat in row:
            seat["status"] = "available"
    
    # Save updated data
    save_seating_data(data)
    return jsonify({"success": True})

@seating_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get seating statistics"""
    data = get_seating_data()
    
    total_seats = 0
    available_seats = 0
    booked_seats = 0
    
    # Count seats by status
    for row in data["seats"]:
        for seat in row:
            total_seats += 1
            if seat["status"] == "available":
                available_seats += 1
            elif seat["status"] == "booked":
                booked_seats += 1
    
    # Calculate occupancy rate
    occupancy_rate = (booked_seats / total_seats) * 100 if total_seats > 0 else 0
    
    return jsonify({
        "totalSeats": total_seats,
        "availableSeats": available_seats,
        "bookedSeats": booked_seats,
        "occupancyRate": round(occupancy_rate, 1)
    })
