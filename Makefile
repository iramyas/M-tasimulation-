# Makefile pour le projet Métasimulation L3 Info UVSQ 2024-2025
# Auteur: BRULU Thomas, MADANI-FOUATIH Iram (Based on user provided structure)

# --- Variables ---

PYTHON = python3
# Command to run unit tests in verbose mode (if used without discover)
UNITTEST = $(PYTHON) -m unittest -v

# Command to run test discovery with verbose mode
# FIX: Ensure 'discover' is immediately after 'unittest'
UNITTEST_DISCOVER_VERBOSE = $(PYTHON) -m unittest discover -v

# The name of your main script
MAIN_SCRIPT = main.py # Ensure this matches the exact name of your script

# Example files and directories
AUTOMATES_DIR = automates
TURING_DIR = machines_turing
TESTS_DIR = tests # Define the tests directory
DEFAULT_AUTOMATE_FILE = $(AUTOMATES_DIR)/regle110.txt
DEFAULT_TURING_FILE = $(TURING_DIR)/incrementeur.txt
DEFAULT_INPUT_AC = 0001000
DEFAULT_INPUT_MT = 101
DEFAULT_OUTPUT_DIR = output
DEFAULT_OUTPUT_AC = $(DEFAULT_OUTPUT_DIR)/simulation_ac.txt
DEFAULT_OUTPUT_MT = $(DEFAULT_OUTPUT_DIR)/simulation_mt.txt
DEFAULT_OUTPUT_SIMU = $(DEFAULT_OUTPUT_DIR)/simulation_mt_via_ac.txt

# --- Main Targets ---

# Declares targets that don't correspond to files
# Added new run targets for Q7 automata examples
# Added TESTS_DIR to .PHONY if you don't intend to create it via Make
.PHONY: all help clean \
        run run_automate run_turing run_simulate \
        run_cycle_mod3 run_propagation_infini run_pattern_switch \
        test test_automate test_turing test_simulateur \
        test_q1 test_q2 test_q3 test_q4 test_q5 \
        test_q8 test_q9 test_q10 test_q11 test_q12 test_q13 \
        create_output_dir \
        $(TESTS_DIR)

# Default target - runs a standard simulation or shows help
# Changed default to run default examples
all: create_output_dir run_automate run_turing run_simulate

# Help
help:
	@echo "==========================================================="
	@echo " Makefile for the Metasimulation Project "
	@echo "==========================================================="
	@echo "Available run targets:"
	@echo "  make all              - Launches default simulations (Regle 110, Incrementeur MT, MT via AC)"
	@echo "  make run_automate   - Launches an example cellular automaton simulation (Regle 110)"
	@echo "  make run_turing     - Launches an example Turing machine simulation (Incrementeur)"
	@echo "  make run_simulate   - Launches an example MT via AC simulation (Incrementeur)"
	@echo "  make run_cycle_mod3   - Launches example AC simulation (cycle_mod3)" # Added Q7 target
	@echo "  make run_propagation_infini - Launches example AC simulation (propagation_infini)" # Added Q7 target
	@echo "  make run_pattern_switch - Launches example AC simulation (pattern_switch)" # Added Q7 target
	@echo ""
	@echo "Available test targets:"
	@echo "  make test             - Launches ALL unit tests"
	@echo "  make test_automate  - Launches tests for automate.py"
	@echo "  make test_turing    - Launches tests for turing.py"
	@echo "  make test_simulateur - Launches tests for simulateur.py"
	@echo ""
	@echo "  make test_q<N>        - Launches tests specific to question N (N={1,2,3,4,5,8,9,10,11,12,13})"
	@echo "     (ex: make test_q3)"
	@echo ""
	@echo "Other target:"
	@echo "  make clean            - Removes generated files (*.pyc, __pycache__, $(DEFAULT_OUTPUT_DIR)/*.txt)"
	@echo ""
	@echo "Note: Ensure example files exist in the specified directories."
	@echo "Note: Ensure test files are in the $(TESTS_DIR) directory."
	@echo "==========================================================="

# --- Helper Target for Directory ---
# Ensure the output directory exists before attempting to write to it
create_output_dir:
	@mkdir -p $(DEFAULT_OUTPUT_DIR)
	@echo "Ensure output directory $(DEFAULT_OUTPUT_DIR) exists."

# --- Run Targets ---

# Run default Cellular Automaton simulation (Q5, part of Q6)
# The target is the output file itself
$(DEFAULT_OUTPUT_AC): $(MAIN_SCRIPT) automate.py $(AUTOMATES_DIR)/regle110.txt create_output_dir
	@echo "\n--- Launching example simulation: Automaton ($(AUTOMATES_DIR)/regle110.txt) -> $@ ---"
	$(PYTHON) $(MAIN_SCRIPT) automate \
		--input-word $(DEFAULT_INPUT_AC) \
		--mode steps \
		--value 20 \
		--output_file $@ \
		$(AUTOMATES_DIR)/regle110.txt  
	@echo "Output in $@"

# Run default Turing Machine simulation (Q12)
# The target is the output file itself
$(DEFAULT_OUTPUT_MT): $(MAIN_SCRIPT) turing.py $(TURING_DIR)/incrementeur.txt create_output_dir
	@echo "\n--- Launching example simulation: Turing Machine ($(TURING_DIR)/incrementeur.txt) -> $@ ---"
	$(PYTHON) $(MAIN_SCRIPT) turing \
		--turing_file $(TURING_DIR)/incrementeur.txt \
		--input-word $(DEFAULT_INPUT_MT) \  # <--- CORRECTED ARGUMENT NAME
		--max_steps 50 \
		--output_file $@ \
		--quiet
	@echo "Output in $@"
	@echo "(To see steps, re-run the python command without --quiet)"

# Run default MT via AC simulation (Q13)
# The target is the output file itself
$(DEFAULT_OUTPUT_SIMU): $(MAIN_SCRIPT) simulateur.py automate.py turing.py $(TURING_DIR)/incrementeur.txt create_output_dir
	@echo "\n--- Launching example simulation: MT via AC ($(TURING_DIR)/incrementeur.txt}) -> $@ ---"
	$(PYTHON) $(MAIN_SCRIPT) simulate \
		--turing_file $(TURING_DIR)/incrementeur.txt \
		--input_word $(DEFAULT_INPUT_MT) \
		--max_steps 100 # Adjusted max steps, might need tuning
		# --compare # Add --compare flag here if your simulate command handles it
		--output_file $@
	@echo "Output of AC simulation in $@"


# Wrapper targets to easily run the default examples by name
run_automate: $(DEFAULT_OUTPUT_AC)
run_turing: $(DEFAULT_OUTPUT_MT)
run_simulate: $(DEFAULT_OUTPUT_SIMU)

# --- Targets for Q7 Automaton Examples ---

# Define paths for the Q7 example files
RUN_CYCLE_MOD3_FILE = $(AUTOMATES_DIR)/cycle_mod3.txt
RUN_PROPAGATION_INFINI_FILE = $(AUTOMATES_DIR)/propagation_infini.txt
RUN_PATTERN_SWITCH_FILE = $(AUTOMATES_DIR)/pattern_switch.txt

# Define example initial configurations for Q7 automata if needed
DEFAULT_INPUT_CYCLE = 012012 # Example input
DEFAULT_INPUT_PROPAGATION = □1□ # Example input
DEFAULT_INPUT_PATTERN = 10101 # Example input

# Define output file names for these examples
OUTPUT_CYCLE_MOD3 = $(DEFAULT_OUTPUT_DIR)/simulation_cycle_mod3.txt
OUTPUT_PROPAGATION_INFINI = $(DEFAULT_OUTPUT_DIR)/simulation_propagation_infini.txt
OUTPUT_PATTERN_SWITCH = $(DEFAULT_OUTPUT_DIR)/simulation_pattern_switch.txt


$(OUTPUT_CYCLE_MOD3): $(MAIN_SCRIPT) automate.py $(RUN_CYCLE_MOD3_FILE) create_output_dir
	@echo "\n--- Launching Example Automaton Simulation: cycle_mod3 ($(RUN_CYCLE_MOD3_FILE}) -> $@ ---"
	$(PYTHON) $(MAIN_SCRIPT) automate \
		--automate_file $(RUN_CYCLE_MOD3_FILE) \
		--input_config $(DEFAULT_INPUT_CYCLE) \
		--mode steps --value 10 # Adjust mode/value as needed
		--output_file $@

$(OUTPUT_PROPAGATION_INFINI): $(MAIN_SCRIPT) automate.py $(RUN_PROPAGATION_INFINI_FILE) create_output_dir
	@echo "\n--- Launching Example Automaton Simulation: propagation_infini ($(RUN_PROPAGATION_INFINI_FILE}) -> $@ ---"
	$(PYTHON) $(MAIN_SCRIPT) automate \
		--automate_file $(RUN_PROPAGATION_INFINI_FILE) \
		--input_config $(DEFAULT_INPUT_PROPAGATION) \
		--mode steps --value 10 # Adjust mode/value as needed
		--output_file $@

$(OUTPUT_PATTERN_SWITCH): $(MAIN_SCRIPT) automate.py $(RUN_PATTERN_SWITCH_FILE) create_output_dir
	@echo "\n--- Launching Example Automaton Simulation: pattern_switch ($(RUN_PATTERN_SWITCH_FILE}) -> $@ ---"
	$(PYTHON) $(MAIN_SCRIPT) automate \
		--automate_file $(RUN_PATTERN_SWITCH_FILE) \
		--input_config $(DEFAULT_INPUT_PATTERN) \
		--mode steps --value 10 # Adjust mode/value as needed
		--output_file $@

# Wrapper targets for Q7 examples
run_cycle_mod3: $(OUTPUT_CYCLE_MOD3)
run_propagation_infini: $(OUTPUT_PROPAGATION_INFINI)
run_pattern_switch: $(OUTPUT_PATTERN_SWITCH)


# --- General Test Targets ---

# Dependencies on test files added
# Use discover command to find tests in the tests/ directory
test: test_automate test_turing test_simulateur

# Define paths to the test files (assuming they are in TESTS_DIR relative to Makefile)
TEST_AUTOMATE_FILE_PATH = $(TESTS_DIR)/test_automate.py
TEST_TURING_FILE_PATH = $(TESTS_DIR)/test_turing.py
TEST_SIMULATEUR_FILE_PATH = $(TESTS_DIR)/test_simulateur.py


# Run tests for automate module using discover in the tests directory
test_automate: $(TEST_AUTOMATE_FILE_PATH) automate.py
	@echo "\n--- Launching tests for automate.py ---"
	# Use the UNITTEST_DISCOVER_VERBOSE variable with directory and pattern
	$(UNITTEST_DISCOVER_VERBOSE) -s $(TESTS_DIR) -p test_automate.py

# Run tests for turing module using discover in the tests directory
test_turing: $(TEST_TURING_FILE_PATH) turing.py
	@echo "\n--- Launching tests for turing.py ---"
	# Use the UNITTEST_DISCOVER_VERBOSE variable with directory and pattern
	$(UNITTEST_DISCOVER_VERBOSE) -s $(TESTS_DIR) -p test_turing.py

# Run tests for simulateur module using discover in the tests directory
test_simulateur: $(TEST_SIMULATEUR_FILE_PATH) simulateur.py automate.py turing.py
	@echo "\n--- Launching tests for simulateur.py ---"
	# Use the UNITTEST_DISCOVER_VERBOSE variable with directory and pattern
	$(UNITTEST_DISCOVER_VERBOSE) -s $(TESTS_DIR) -p test_simulateur.py


# --- Test Targets by Question ---
# Each target executes the relevant unit test(s) for the question
# Added dependencies on the relevant source/test files and main script
# Use PYTHONPATH to allow unittest to import test modules from the tests directory
# Keep the specific test calls as provided by the user, assuming this structure is correct

test_q1: $(TEST_AUTOMATE_FILE_PATH) automate.py $(MAIN_SCRIPT)
	@echo "\n--- Test Q1 : AutomateCellulaire Structure ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_automate.TestAutomateStructures.test_creation_automate
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_automate.TestAutomateStructures.test_automate_symbole_defaut_manquant_ajoute

test_q2: $(TEST_AUTOMATE_FILE_PATH) automate.py $(MAIN_SCRIPT)
	@echo "\n--- Test Q2 : Configuration (Automate) Structure ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_automate.TestAutomateStructures.test_creation_configuration
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_automate.TestAutomateStructures.test_configuration_vide
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_automate.TestAutomateStructures.test_configuration_eq
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_automate.TestAutomateStructures.test_configuration_noyau

test_q3: $(TEST_AUTOMATE_FILE_PATH) automate.py $(MAIN_SCRIPT) $(AUTOMATES_DIR)/regle110.txt
	@echo "\n--- Test Q3 : Automaton Reading (lire_automate) ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_automate.TestAutomateLecture

test_q4: $(TEST_AUTOMATE_FILE_PATH) automate.py $(MAIN_SCRIPT) $(AUTOMATES_DIR)/regle110.txt # Dependency on example file needed by some tests
	@echo "\n--- Test Q4 : Automaton Calculation Step (pas_de_calcul) ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_automate.TestAutomateCalcul

test_q5: $(TEST_AUTOMATE_FILE_PATH) automate.py $(MAIN_SCRIPT) $(AUTOMATES_DIR)/regle110.txt # Dependency on example file needed by some tests
	@echo "\n--- Test Q5 : Automaton Simulation (simuler_automate) ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_automate.TestAutomateSimulation

# Q6 (Display) and Q7 (Examples) are demonstrated by the run_* targets and implicitly tested if simuler_automate works.

test_q8: $(TEST_TURING_FILE_PATH) turing.py $(MAIN_SCRIPT)
	@echo "\n--- Test Q8 : MachineTuring Structure ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_turing.TestTuringStructures.test_creation_machine_ok
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_turing.TestTuringStructures.test_creation_machine_erreurs_validation

test_q9: $(TEST_TURING_FILE_PATH) turing.py $(MAIN_SCRIPT)
	@echo "\n--- Test Q9 : ConfigurationTuring Structure ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_turing.TestTuringStructures.test_creation_config
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_turing.TestTuringStructures.test_config_lire_ecrire_deplacer

test_q10: $(TEST_TURING_FILE_PATH) turing.py $(MAIN_SCRIPT) $(TURING_DIR)/incrementeur.txt # Dependency on example file
	@echo "\n--- Test Q10 : Turing Machine Reading (lire_turing) ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_turing.TestTuringLecture

test_q11: $(TEST_TURING_FILE_PATH) turing.py $(MAIN_SCRIPT)
	@echo "\n--- Test Q11 : Turing Calculation Step (pas_turing) ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_turing.TestTuringCalcul

test_q12: $(TEST_TURING_FILE_PATH) turing.py $(MAIN_SCRIPT) $(TURING_DIR)/incrementeur.txt # Dependency on example file
	@echo "\n--- Test Q12 : Turing Simulation (simuler_turing) ---"
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_turing.TestTuringSimulation

test_q13: $(TEST_SIMULATEUR_FILE_PATH) simulateur.py automate.py turing.py $(MAIN_SCRIPT) $(TURING_DIR)/incrementeur.txt # Dependency on example file
	@echo "\n--- Test Q13 : MT via AC Simulation (build/simulate/compare) ---"
	# Assuming TestSimulateurConstruction and TestSimulateurIntegration cover Q13
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_simulateur.TestSimulateurConstruction
	PYTHONPATH=$(TESTS_DIR) $(UNITTEST) test_simulateur.TestSimulateurIntegration


# Q14 is theoretical (answer in README.md)

# --- Clean Target ---

clean:
	@echo "\n--- Cleaning generated files ---"
	# Remove Python bytecode files
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +
	# Remove output files in the output directory
	# Use -f to avoid error if directory or files don't exist
	rm -rf $(DEFAULT_OUTPUT_DIR) # Use rm -rf to remove the directory and its contents
	@echo "Cleaning complete."

# --- Example File Verification (used as dependencies) ---
# These targets now just exist to ensure Make checks for the file.
$(AUTOMATES_DIR)/regle110.txt: ;
$(TURING_DIR)/incrementeur.txt: ;
$(RUN_CYCLE_MOD3_FILE): ;
$(RUN_PROPAGATION_INFINI_FILE): ;
$(RUN_PATTERN_SWITCH_FILE): ;

# Add dependencies for the main Python files for consistency
$(MAIN_SCRIPT): ;
automate.py: ;
turing.py: ;
simulateur.py: ;

# Add dependencies for the test files for consistency
$(TEST_AUTOMATE_FILE_PATH): ;
$(TEST_TURING_FILE_PATH): ;
$(TEST_SIMULATEUR_FILE_PATH): ;