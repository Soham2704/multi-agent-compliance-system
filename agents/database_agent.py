from sqlalchemy.orm import Session
from database_setup import Rule

class DatabaseQueryAgent:
    def __init__(self, db_session: Session):
        self.db = db_session
        print("DatabaseQueryAgent initialized with aggregation logic.")

    def find_matching_rules(self, city: str, parameters: dict):
        """
        Finds all rules that match the given case parameters by aggregating results
        from multiple, independent queries.
        """
        all_matching_rules = []
        
        # --- Perform separate, targeted queries for each relevant parameter ---

        # Query 1: Find rules based on road width
        if "road_width_m" in parameters:
            width = parameters["road_width_m"]
            # This powerful JSONB-like query checks inside the JSON `conditions` column
            width_rules = self.db.query(Rule).filter(
                Rule.city == city,
                Rule.conditions['road_width_m']['min'].as_float() <= width,
                Rule.conditions['road_width_m']['max'].as_float() > width
            ).all()
            all_matching_rules.extend(width_rules)

        # Query 2: Find rules based on plot area
        if "plot_area_sqm" in parameters:
            area = parameters["plot_area_sqm"]
            area_rules = self.db.query(Rule).filter(
                Rule.city == city,
                Rule.conditions['plot_area_sqm']['min'].as_float() <= area,
                Rule.conditions['plot_area_sqm']['max'].as_float() >= area
            ).all()
            all_matching_rules.extend(area_rules)
            
        # Query 3: Find rules based on location (if provided)
        if "location" in parameters:
            loc = parameters["location"]
            # This powerful query checks if the input `loc` is IN the JSON list
            loc_rules = self.db.query(Rule).filter(
                Rule.city == city,
                Rule.conditions['location'].as_string().contains(f'"{loc}"') # Search for the string within the JSON array
            ).all()
            all_matching_rules.extend(loc_rules)

        # --- De-duplicate the final list ---
        # A rule might have matched multiple queries (e.g., both road width and plot area).
        # This ensures we only return each unique rule once.
        final_rules = list({rule.id: rule for rule in all_matching_rules}.values())
        
        return final_rules