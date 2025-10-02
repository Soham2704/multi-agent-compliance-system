class InteriorDesignAgent:
    def __init__(self):
        print("InteriorDesignAgent initialized.")

    def calculate_carpet_area(self, total_bua: float):
        """
        Calculates the estimated maximum carpet area based on the total 
        permissible built-up area (BUA).
        
        A common industry rule of thumb is that carpet area is ~70% of BUA.
        """
        carpet_area = total_bua * 0.70
        
        breakdown = {
            "input_total_bua_sqm": round(total_bua, 2),
            "formula": "estimated_carpet_area = total_bua * 0.70",
            "result_carpet_area_sqm": round(carpet_area, 2)
        }
        return breakdown