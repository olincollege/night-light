import os

# Paths configuration
test_dir = "../../tests"
output_dir = "./tests"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Iterate over tests files in the tests directory
for filename in os.listdir(test_dir):
    if filename.startswith("test_") and filename.endswith(".py"):
        module_name = filename.replace(".py", "")

        # Create an .rst file for each test module
        with open(os.path.join(output_dir, f"{module_name}.rst"), "w") as rst_file:
            rst_file.write(f"{module_name}\n")
            rst_file.write("=" * len(module_name) + "\n\n")
            rst_file.write(f".. automodule:: {module_name}\n")
            rst_file.write("    :members:\n")
            rst_file.write("    :undoc-members:\n")
            rst_file.write("    :show-inheritance:\n")
