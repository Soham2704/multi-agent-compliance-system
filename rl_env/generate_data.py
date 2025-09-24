import json

print("Generating a representative set of synthetic cases...")

synthetic_cases = []

# Define a representative set of values for each parameter
plot_sizes = [500, 1500, 3000, 4500]
locations = ["urban", "suburban", "rural"]
road_widths = [6, 9, 12, 18, 24, 30]

for size in plot_sizes:
    for loc in locations:
        for width in road_widths:
            case = {
                "plot_size": size,
                "location": loc,
                "road_width": width
            }
            synthetic_cases.append(case)

output_path = "io/synthetic_cases.json"
with open(output_path, "w") as f:
    json.dump(synthetic_cases, f, indent=4)

print(f"Successfully generated and saved {len(synthetic_cases)} representative cases to {output_path}")