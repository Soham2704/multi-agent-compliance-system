from database_setup import SessionLocal, Rule

# --- 1. Define the Expanded, Structured Rule Data ---
# This new set includes specific rules that will match our case studies.
RULES_DATA = [
    # --- Mumbai Rules (DCPR 2034) ---
    {
        "id": "MUM-FSI-SUBURBS-R18-27",
        "city": "Mumbai",
        "rule_type": "FSI",
        "conditions": {
            # --- THE FIX: Make the location condition more general ---
            "location": ["urban", "suburban"], 
            "road_width_m": {"min": 18, "max": 27}
        },
        "entitlements": {
            "base_fsi": 1.0,
            "premium_fsi": 0.5,
            "tdr_fsi": 0.9,
            "total_fsi": 2.4
        },
        "notes": "FSI for Residential/Commercial zones in urban/suburban areas on 18m-27m roads."
    },
    {
        "id": "MUM-LOS-1001-2500",
        "city": "Mumbai",
        "rule_type": "LayoutOpenSpace",
        "conditions": {
            "plot_area_sqm": {"min": 1001, "max": 2500}
        },
        "entitlements": {
            "los_percentage": 15,
            "min_area_sqm": 125,
            "min_dimension_m": 7.5
        },
        "notes": "Layout Open Space requirement for plots between 1001 and 2500 sq.m."
    },

   {
        "id": "PUNE-SETBACK-001",
        "city": "Pune",
        "rule_type": "Setback",
        "conditions": {
            "plot_area_sqm": {"min": 501, "max": 1000},
            "road_width_m": {"min": 9, "max": 15},
            "building_use": "Residential"
        },
        "entitlements": {
            "front_margin_m": 3.0,
            "side_margin_m": 1.5,
            "rear_margin_m": 1.5
        },
        "notes": "Setbacks for residential plots 501-1000sqm on 9m-15m roads."
    },
    {
        "id": "PUNE-FSI-001",
        "city": "Pune",
        "rule_type": "FSI",
        "conditions": {}, # Generic base FSI
        "entitlements": {
            "base_fsi": 1.1
        },
        "notes": "Standard base FSI for PMRDA region."
    },

    # --- Ahmedabad Rules (AUDA DCR) ---
    {
        "id": "AHM-HEIGHT-001",
        "city": "Ahmedabad",
        "rule_type": "BuildingHeight",
        "conditions": {
            "road_width_m": {"min": 12, "max": 18}
        },
        "entitlements": {
            "max_height_m": 25.0
        },
        "notes": "Maximum permissible building height for plots on 12m-18m roads."
    }
]

# --- 2. Database Population Logic (Now with Update logic) ---
def populate_database():
    print("--- Connecting to the database to populate/update rules... ---")
    db = SessionLocal()
    try:
        for rule_data in RULES_DATA:
            existing_rule = db.query(Rule).filter(Rule.id == rule_data["id"]).first()
            if existing_rule:
                # If it exists, update it to ensure our data is fresh
                print(f"  - Updating rule '{rule_data['id']}' for {rule_data['city']}.")
                existing_rule.city = rule_data["city"]
                existing_rule.rule_type = rule_data["rule_type"]
                existing_rule.conditions = rule_data["conditions"]
                existing_rule.entitlements = rule_data["entitlements"]
                existing_rule.notes = rule_data["notes"]
            else:
                # If it doesn't exist, create it
                print(f"  - Adding new rule '{rule_data['id']}' for {rule_data['city']}.")
                new_rule = Rule(**rule_data)
                db.add(new_rule)
        
        db.commit()
        print("--- Successfully committed all rules to the database. ---")
    except Exception as e:
        print(f"!!! An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()