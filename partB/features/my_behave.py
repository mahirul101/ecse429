import random
import sys

from behave.__main__ import Configuration, run_behave, Runner

class ShuffleRunner(Runner):

    def feature_locations(self):
        # Get the feature file locations
        locations = super().feature_locations()
        
        # Shuffle the locations to randomize the order
        random.shuffle(locations)
        
        # Return the shuffled list of feature files
        return locations

def main():
    # Configure Behave's settings
    config = Configuration()
    
    # Run Behave with the custom ShuffleRunner
    return run_behave(config, runner_class=ShuffleRunner)

if __name__ == '__main__':
    # Run the custom script
    sys.exit(main())