# NCSG

- Required python version >= 3.6

## Usage
- Use the config file to change the settings of the program
- Example config file:
```
{
  "algorithms_available": ["BFSGraphletCounter", "DPGraphletCounter", "BruteForceGraphletCounter"],
  "algorithms_to_run": ["DPGraphletCounter"],
  "graphlet_size": 4,
  "input_file": "tests/df_subti.csv",
  "use_user_input": false,
  "sample_size": 2000,
  "use_sampling": false,
  "markov_steps": 100,
  "use_markov_graph_generation": false,
  "num_of_markov_graphs": 100,
  "output": {
    "csv_output": {
      "generate": true,
      "folder": "graph_output"
    },
    "visualizations": {
      "generate": true,
      "folder": "graph_output",
      "graph_size": 50
    }
  }
}
```
- Install required packages and run in terminal or your favorite IDE