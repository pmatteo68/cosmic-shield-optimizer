# CSS (Cosmic Shield Simulator) OPTIMIZER

## Software metadata

|Attribute|Value|
|:-|:-|
|Version|1.1.0|
|Date|Sep. 10, 2025|
|Author|Matteo Picciau|

## Credits
* Filippo M. Soccorsi (Astrophysics researcher at "La Sapienza" University of Rome, Italy), whom I thank for his priceless contribution as it relates to:
  * Functional requirements definition
  * Discovering high quality objective functions
  * Output results set definition
  * Testing
  * Issue troubleshooting
  * Sharing thoughts throughout the entire lifetime of the optimizer, being constant inspiration for enhancement and improvement

## Abstract
Python optimization engine, based on [Scikit-Optimize / gp_minimize][wr_gp_minimize] that iteratively runs a cosmic shield simulator (ref. my other repository, 'cosmic-shield-simulator', aka CSS) to identify shielding configurations meeting defined energy, protection efficiency, and constraint criteria.

## Simulation scenario
We defer the reader to the CSS project's README file for all the aspects pertaining the physics simulation in itself.

## Prerequisites
* [Python][wr_python] v. 3.9.21 (extensively tested) or sup. Dependencies: ref. `requirements.txt` file for 100% accurate detail, and also the table below.
* [CSS] Ver. 5.1.3 or sup.

## Python dependencies

|Package|Version|
|:-|:-|
|joblib|1.5.1|
|numpy|2.0.2|
|packaging|25.0|
|pip|25.2|
|pyaml|25.7.0|
|PyYAML|6.0.2|
|scikit-learn|1.6.1|
|scikit-optimize|0.10.2|
|scipy|1.13.1|
|setuptools|53.0.0|
|threadpoolctl|3.6.0|

### Tested Combinations

We have successfully executed this application on the following HW/SW combinations:
* ref. same section in the CSS project's README, they are the same, PLUS
* HP ZBook Fury G10, CPU: 13gen Intel Core i7-13850HX 3.80 GHz, Turbo Boost up to 5.30 GHz, RAM: 64 Gb, Storage: SSD 512 Gb, OS: Windows 11 Enterprise (where CSS was stubbed, as no Windows version of CSS exists)

## Optimization engine architecture overview
* Optimization strategy: based on [Scikit-Optimize / gp_minimize][wr_gp_minimize], a Python library for sequential optimization of expensive black-box functions. It uses Bayesian Optimization (an AI-based method) to choose the next best point to evaluate.
* Configurable constraints as of this version: max attempts, materials among which pick up layers, max number of layers, max shield thickness, max shield weight, min-max layer thickness
* History management: the engine persists the history of its attempts, so that a second run will leverage the findings in the first, etc. In order to start from scratch, the history file `css_optimizer_state.pkl` can be deleted.
* The tool is designed assuming that ONLY the geometry configuration file is being varied, moving through various tests. i.e., ALL the other CSS configurations are steady, where they have always been (i.e. in the CSS project directories as usual: scripts, macros, json files).
* For the reasons explained in the point above, the geometry json configuration file, for each run, is stored in each test's OUTPUT directory.
* So, all in all, in this tool model the function to maximize is SUM(energy eff + protection eff), with the following constraints and goals:
** number of layers has to fall in a (configurable) range
** each layer's thickness has to be within (configurable) limits
** shield's thickness has to be within (configurable) limits
** [1.0.10] shield's stiffness (thickness-weighted average of the young modulus of each layer, multiplied by a reduction safety factor called CF, typically around 0.9, and all of this is configurable in the command line)
** shield's normalized weight has to be within (configurable) limits
** TARGET: energy efficiency has to be equal or above a (configurable) threshold
** TARGET: protection efficiency has to be equale or above a (configurable) threshold
** Maximum number of attempts. If exceeded, the best result so far is shown.
* A key component of this architecture is the domain data, i.e. the set of independent variables that gp_minimize will determine upon each iteration, also known as SEARCH SPACE.
* [1.0.6] This architecture provides for isolation and modularization of the search data builder, which is pluggable. Refer. to the `Search Space Architecture and Search Space Builders` for additional details as to which builders are available, and what functionalities they offer.

## Optimization main loop
In light of what outlined in the previous section, it is now easy to make sense of the following main loop algorithm, which describes the optimizer operations.

```
                       (BEGIN)
                          │
                          ▼
                   ┌──────────────┐
                   │ Load History │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Loop Start  │
                   └──────┬───────┘
                          │
                          ▼
                ┌──────────────────┐
   ┌───────────►│ Define Geometry  │
   │            └─────────┬────────┘
   │                      │
   │                      ▼
   │            ┌──────────────────┐
   │            │  Run Simulation  │
   │            └─────────┬────────┘
   │                      │
   │                      ▼
   │                      │
   └───────────◄──────────┤
  (efficiency targets     │
   not met AND            │
   attempts available)    │
                          │
                          │
                          │ (efficiency targets met OR
                          │  max attempts reached)
                          │
                          ▼
                        (END)
```

## Constraint enforcement and simulation (CSS)

The following pseudo-code describes in some more detail what happens upon each and every iteration of the optimization loop.

```pseudocode
function objective_function(parameters):
    # Step 1: Build geometry
    shield = ShieldGeometry(parameters)

    # Step 2: Check pre-simulation constraints
    if not shield.geometry_constraints_ok():
        return HIGH_PENALTY   # skip costly simulation

    # Step 3: Run simulation (expensive step)
    results = run_simulation(shield)

    # Step 4: Check post-simulation constraints
    if not results.constraints_ok():
        return HIGH_PENALTY

    # Step 5: Compute objective value (lower is better)
    score = evaluate_protection(results)
    return score


# Optimization loop driven by gp_minimize
best_solution = gp_minimize(
    func = objective_function,
    space = parameter_space,
    n_calls = MAX_ITERATIONS,
    random_state = SEED
)

return best_solution
```

Note that the protections above are necessary as long as the search space `gp_minimize` operates on does not guaranteed a valid sample upon each iteration. Many new features in the v. 1.0.6 (shield thickness trimming, protection from same material in adjacent shield layers) address this need at the source, i.e. with those in place no more objective function penalization should occur because of the max_shield_thickness or max_layer_thickness violation. But we will keep them there, just in case.

Of course all constraint checkings could be removed on the day a "structurally" protected search space will be designed, i.e. on that CANNOT generate invalid tuples.

## Notes about stiffness

[1.0.10] Violation of the threshold will not result in any objective function penalization, they will be just visible in the log as warnings:

`WARNING (...) Shield stiffness out of range: ... (range: ...)`

IMPORTANT: if you are working with a JSON materials database older than v. 1.0.9, you need to UPGRADE it. Read notes in the change log entry for v. 1.0.10.

## Search Space Architecture and Search Space Builders

[1.0.6] As over time evolving the search space structure became imperative, starting from v. 1.0.6 this component has been made pluggable. Usually, the default (i.e. the latest search space builder) is recommended. The following table lists them all.

|Search Space Builder|First Rel.|Shield trimming (thickness)|Shield trimming (weight)|Protection from same material in adjacent shield layers|
|:-|:-|:-|:-|:-|
|`searchsp_adv250814.SearchSpaceBuilderAdv250814` (*)|1.0.6|Y|Y|Y|
|`searchsp_adv250813.SearchSpaceBuilderAdv250813`|1.0.6|Y|Y|N|
|`searchsp_base250801.SearchSpaceBuilderBase250801`|1.0.0|N|N|N|

(*) _Default, and recommended_

Although it is a little challenging, you can also write a custom search space builder by yourself, ref. guidelines below in this document.

## Objective Function and Objective Function Evaluators

[1.0.8] As over time trying new objective functions became imperative, starting from v. 1.0.8 the logic for evaluating the objective function is pluggable. The following table lists the available ones:

|Objective Function Evaluator|First Rel.|Uses configuration file|Features|
|:-|:-|:-|:-|
|`objfun_adv250817fms.ObjFEval_AdvFMS250817` (**)|1.0.8|Y|Weighted, based on many indicators and quantities, with scores and mild/hard penalties, with logarithmic modulations as appropriate|
|`objfun_base250801.ObjFEval_Base250801` (*)|1.0.0|N|Simplest logic, just based on the sum of the defined KPIs|

(*) _Default_

(**) _Credits: F. M. Soccorsi_

You can also write a custom objective function evaluator by yourself, ref. guidelines below in this document.

## Targets and Target Reached Assessors

[1.0.8] As over time trying new criteria for assessing whether or not the target is reached became imperative, starting from v. 1.0.8 the logic for assessing this is pluggable. The following table lists the available target reached assessors:

|Target Reached Assessor|First Rel.|Features|
|:-|:-|:-|
|`trgeval_base250801.TargetEval_Base250801` (*)|1.0.0|Simplest logic, just based on independent thresholds for the identified KPIs|

(*) _Default

You can also write a custom target reached assessor by yourself, ref. guidelines below in this document.

### Notes about `searchsp_adv250814.SearchSpaceBuilderAdv250814` (default search builder)

* [1.0.6] The randomic variables used to determine the materials are encoded/asymmetric numerical indexes, no more material names. Specifically:

|Shield Layer Position|min_material_index|max_material_index|Purpose|
|:-|:-|:-|:-|
|1|0|num. of materials - 1|The material for the first layer is picked up ordinarily, eg if we have FIVE materials, this will be a random integer between 0 and 4.
|>1|0|num. of materials - 2|The material for any layer following the first is picked up first by _rotating_ the materials list so that the material in the previous layer is placed in LAST position, and then by picking a random number between 0 and (num. of materials - 2). This will protect from having adjacent layers having the same material (so avoiding the case in which many consecutive layers made of the same material end up accidentally violating the per-layer max_thickness constraint), yet keeping the variables independent, which is needed by the `gp_minimize`. Note that in this case the raw data, i.e. the indexes actually utilized in the optimization, will not be humanly readable. Proper encoding and decoding functions have been implemented to make sure that, in all circumstances, the user is exposed to understandable information: raw (i.e. with rotation-based indexes for all the layers starting from the 2nd) and decoded/readable (material names).

* It is worth noting that the shield trimming (by thickness) can be enabled/disabled with the `CSS_OPT_SHIELD_TRIMMING` environment variable, ref. editable section in the scripts. It is generally recommended to keep this enabled to stop at the source any generation of shields exceeding the max_total_thickness limit.

* It is worth noting that the shield trimming (by weight) can be enabled/disabled with the `CSS_OPT_SHIELD_WGT_TRIMMING` environment variable, ref. editable section in the scripts. It is generally recommended to keep this enabled to stop at the source any generation of shields exceeding the max_total_weight limit.

* It is worth noting that the protection from a material to occur in two adjacent layers can be enabled/disabled with the `CSS_OPT_ADJL_SAME_MAT` environment variable, ref. editable section in the scripts. When the protection is disabled, the indexes are no more encoded, i.e. for ALL layers their value maps directly to a specific material in the materials list.

#### Shield trimming (by thickness, by weight)
[1.0.7] It is guaranteed that no shield exceeding the max_shield_weight constraint can be created with this builder, as the exceeding part is trimmed off.
[1.0.6] It is guaranteed that no shield exceeding the max_shield_thickness constraint can be created with this builder, as the exceeding part is trimmed off.

Note that this is implemented by means of a 'repair function', a well known concept in mathematics. Such repair function, however, may cause indirect violation of other constraints the search space would protect you fromviolating. Currently, this risk is present for: min. number of layers, min. thickness (per layer and global). Proper warnings inform the user when this happens, eg:

```
WARNING (..) The shield was TRIMMED in pre-sim phase to avoid constraints violation: (Num. layers, Thickness): (4, 15.627954072503424) ---> (2, 3.8636509448033394)
WARNING (..) Repair function warning: Trimming-induced constraint violations occurred: min_layer_thick (0.6389097341273358)
```

### Notes about the other search space builders

* `searchsp_adv250813.SearchSpaceBuilderAdv250813`: same as the default one, except it does not offer the protection from same material in adjacent layers. Also for this search space builder the materials are represented by plain numeric indexes, i.e. no rotation and no encoding. This builder, too, offers shield trimming (by thickness, by weight - ref. above for the meaning).

* `searchsp_base250801.SearchSpaceBuilderBase250801`: the first one we developed. Materials are represented by strings, i.e. material names. It does offer no shield trimming of any sort, it does not offer the protection from same material in adjacent layers.

### Guidelines for writing your custom Search Space Builder

Average Python and [Scikit-Optimize / gp_minimize][wr_gp_minimize] knowledge is required in order to build a custom search space builder. All you need is to write a class which implements the methods listed in the table below.

|Method|Purpose|
|:-|:-|
`init`|Initializes the builder with the needed parameters|
`decode_x_point`|Translates a domain data point from the raw format to the readable/understandable one|
`getMaterialsRawList`|Encodes a readable list of materials into the numeric indexes list needed for processing|
`getValidRawMaterialPlaceholder`|To be used when filling unused layers|
`hasShieldTrimming`|True/False, must return `True` if the search space builder in question implements the shield trimming by thickness. Utilized by other modules in the framework|
`hasShieldTrimming_Wgt`|True/False, must return `True` if the search space builder in question implements the shield trimming by weight. Utilized by other modules in the framework|
`adjacentSameMaterialAllowed`|True/False, utilized by other modules in the framework|
`materialsByIndex`|True/False, utilized by other modules in the framework|
`getSearchSpace`|Returns the search space object|
`getLayersData`|Return layers data in a utilizable form|

Recommendation: in order to effectively and rapidly develop one of your own, the fastest way is to take inspiration from any of the existing ones!

### Guidelines for writing your custom Objective Function Evaluator

Average Python knowledge and good knowledge of the problem at hand are needed in order to build a custom objective function evaluator. All you need is to write a class which implements the methods listed in the table below.

|Method|Purpose|
|:-|:-|
|`setParams` (*)|Initializes the evaluator with the needed parameters|
|`setProblemRef` (*)|Initializes the evaluator with the references of the problem at hand|
|`evalObjFun`|Core method, where the objective function is actually evaluated|

Recommendation: in order to effectively and rapidly develop one of your own, the fastest way is to take inspiration from any of the existing ones!
Note also that, typically, the implementation of the methods marked by (*) can be seamlessly copied from one implementation to another.

### Guidelines for writing your custom Target Reached Assessor

Average Python knowledge and good knowledge of the problem at hand are needed in order to build a custom target reached assessor. All you need is to write a class which implements the methods listed in the table below.

|Method|Purpose|
|:-|:-|
|`setTargets` (*)|Used internally, upon initialization|
|`isTargetMet`|True/False, must return `True` when the target is met|

Recommendation: in order to effectively and rapidly develop one of your own, the fastest way is to take inspiration from any of the existing ones!
Note also that, typically, the implementation of the methods marked by (*) can be seamlessly copied from one implementation to another.

## Installation

NOTE: in all the following, ALL the scripts we prescribe to launch, need to be launched from within the directory containing them.

1. Deflate the archive you received, or clone the GIT repository if any, etc.

2. Configure the environment script: edit the `bin/env.sh` so that to match your environment (Python, CSS project root directory, log level, etc.).

3. Create the Python virtual environment (launch the `./create_env.sh`)

4. (Optional) Configure the materials database: edit the `config/materials_db.json`. These are NOT the materials in consideration for the optimization. These are ALL the possible materials, it is a catalog. Never to be modified. Up to the user to enter any missing item, such as custom materials, etc.

5. Configure the materials list in scope for the optimization run: edit the `config/materials.txt` accordingly to your needs. You can comment out lines by prepending them with `#`.

6. Configure the geometry template: edit the `config/geometry_template.json` accordingly to your needs (the `layers` element must contain ONLY the detector).

7. (Optional) Configure the initial shield configuration: : edit the `config/init_shield_x0.json` (detector has NOT to be included). USE THIS FILE AS A REFERENCE as its syntax is NOT exactly the same as the simulator's geometry configuration file.

8. Configure the layer common parameters: edit the `config/layer_config.json` accordingly to your needs (it contains the parameters that are common to all layers).

9. Configure the optimization loop parameters (number of max runs, optimizer verbosity, constraints, directories, etc.) in the `css-optimizer.sh` script.

10. Configure the core optimization parameters: edit the `config/optimizer_conf.json` accordingly to your needs. Ref. to [Scikit-Optimize / gp_minimize][wr_gp_minimize] for full details about the available parameters.

11. Check the launch script, `css-optimizer.sh`, and make sure you are using the right objective function evaluator and target reached assessor. Usually defaults are fine, but you never know. Note, also, that some of the objective function evaluators may use the `config/objfun_params.json` configuration file. If this is the case, check the parameters in there.


## Usage

PREMISE: ALL the scripts mentioned below have to be launched from a command shell in the same directory containing them.

* To run the optimization loop (in background):

```
./css-opt-launcher.sh
```

* To early terminate an optimization:

```
./kill_optimizer.sh <pid>
```

Note: this runs in a neverending loop, `CTRL+C` is safe.

* To upgrade a pre-1.0.9 materials database JSON file to one compliant with v. 1.0.10 or later:

```
./upgrade_mat_db_1.0.10.sh <file>
```

* As per the history management, it is VERY important to remember that if you change any constraints' limits, or any configuration, the history file CANNOT be loaded by the optimizer, i.e. you will have to delete it and to restart from scratch (or weird errors will show up...).

* To stop the optimization BEFORE the end of its natural loop, you can kill it GRACEFULLY (i.e. without the `-9`), or you can create an appropriate stop file the optimizer periodically check on. Ref. instructionsthat will be readable in the log.

### Considerations over materials database, also in relation to materials list
* If the materials database is used, the framework is more efficient, as the total weight is checked BEFORE the simulation, and the simulation won't start if the threshold is exceeded. Additionally, since the post-simulation weight is calculated regardless, a warning will show up if the two differ. If the database is not configured, or if it is misconfigured and fails its initialization, the framework will work without it.

* The materials list (TXT file) is what ACTUALLY defines the materials data domain for the optimizer, i.e. the materials which are considered to create the shield. The materials database (JSON file) is there for density resolution. As long as ALL materials listed in the materials list (TXT file) are contained in the materials database, the optimizer will work. Both will be loaded in memory at the beginning of the optimizer operations. But, note, the in-memory replica of the materials database (JSON) will be retained in REDUCED form, i.e. only the needed items. So, do not bother reducing the actual size of it. It's pointless. Actually: just for safety in case you extend the materials list (TXT) at some point in future, we recommend to keep it as is.

### Considerations over the initial point (X0)
* Loading from history takes precedence.
* Then, the X0 file.
* Last option, if history was not specified or not found or loading it fails, and the same stands for the X0 file: custom randomic generation. There is a reason why we do not rely on the X0 randomically generated by `gp_minimize` in case none is specified, ref. other notes in this document.

### Considerations over the optional features
* If the user does not specify an initial solution, i.e. an initial shield layout to get the optimizer starting with, the optimizer will pick randomly.

### Usage warnings
* Pay EXTREME attention in modifying configurations or scripts. Proceed VERY carefully, with minimal changes at once, and backup IMMEDIATELY as soon as you have something working. The Scikit-Optimize library has shown very convoluted and unfriendly error messages, therefore it is easy to get lost.

* Creating the stop file, or killing smoothly the process (i.e. just `kill` and not `kill -9`) may take some time. This is perfectly normal. However: should the process really not stop, you may kill abruptly the `python` process and also any `CosmicShieldSimulation` process you see with command `top` or alike. Other than potential loss for the saved history, there is no other harm.

## Search Space Architecture and Search Space Builders

### Maintenance notes
* Pay attention to the `opttrace` string. It has special meaning (the launch script prompts to use it for smart log filtering, so be careful as to its management in the code).

## Open Points

### Most urgent

* F. M. Soccorsi, Aug. 19, 2025: also threshold on min Eff and Peff for each layer should be established

* F. M. Soccorsi, Aug. 12, 2025: to extend the COST evaluation constraint (which now is there only as a placeholder with no actual calculation) to an array of parameters to be utilized for constraint evaluation. Say Young Module (E), etc. To be well thought, as there may be many exceptions which then defeat the purpose.

* More testing of the 1.1.0, pending since 1.0.6 (tests on the old search space builders are needed, and more)

* Tool to generate X0 out of a history file, allowing slice selection etc.

* Print X0 at the end of the run, with the best point? Or alike

* Generating a csv iter-objvalue-eeff-peff?

* A tkinter-based tool to view the csv mentioned in the point above, or to view the history file?

* High quality debugging for the encode/decode of the rotating indexes

* To save some written report in the end? With the summary, or alike

### Others

* properties dictionaries to be passed to the search space builders? To minimize the effort of continuously updating method signatures.

* F. M. Soccorsi, Aug. 12, 2025: to add the possibility of specifying that a triplet m1-gap-m1 is always present in the shield, at any point, where m1 is a given material, of a given thickness, and the gap has fixed thickness. Variant A: the gap is made of varying number of layers, each of varying material. Variant B: the gap is made of a single fixed material.

* F. M. Soccorsi, multiple occurrences, related to the previous one: To introduce simple constraints such as 'I want this layer in first position', things of this nature.

* As the constraints, in the current implementation, introduce high non-linearities, alternate approaches are under exam in order to constrain the search space in the first place. A possibly interesting one to investigate is [Constrained version of Scikit-Optimize / gp_minimize][wr_gp_minimize_constrained_1].

* Related to the point just above: to explore normalization options for the search space, ref. [ChatGPT thread of Aug. 11, 2025][wr_chatgpt_search_sp_1]

* To introduce the global metrics helper? Or to improve it if it exists. For example, by counting all the different constraint violations etc.

* Also the result data returned by the `gp_minimize` call could be better utilized and explored? TBD, ref. again [Scikit-Optimize / gp_minimize][wr_gp_minimize] .

* Reviewing code lines with `opttrace`, some more may be needed

## Troubleshooting

* ANY ERROR: check if the cause is the history file.

Any slight change in any configuration may cause errors upon history loading. Restart from scratch eventually.

* Error: '<=' not supported between instances of 'int' and 'str'. Often times the following error was solved by erasing history.

```
    check_x_in_space(x, self.space)
  File <home>/.py_venvs/css-opt-venv/lib64/python3.9/site-packages/skopt/utils.py, line 183, in check_x_in_space
    if not np.all([p in space for p in x]):
  File <home>/.py_venvs/css-opt-venv/lib64/python3.9/site-packages/skopt/utils.py, line 183, in <listcomp>
    if not np.all([p in space for p in x]):
  File <home>/.py_venvs/css-opt-venv/lib64/python3.9/site-packages/skopt/space/space.py, line 1309, in __contains__
    if component not in dim:
  File <home>/.py_venvs/css-opt-venv/lib64/python3.9/site-packages/skopt/space/space.py, line 725, in __contains__
    return self.low <= point <= self.high
TypeError: '<=' not supported between instances of 'int' and 'str'
```

It was probably caused by saving the history with a search space builder, and retrieving it with a different one. This has to be avoided.

* ERROR `Optimization space and initial points in x0 use inconsistent dimensions`. If you ever meet this error, aside of well checking all your data and configurations, you have to consider the possibility of having occurred into the issue described in [Scikit-Optimize / gp_minimize issue 1178][wr_gp_issue_1178]. The remediation to that is: make sure that, if you do not specify a history file, and if you do not specify an X0 file, do NOT let the `gp_minimize` function create the X0 by itself. Check your command line options.

* ERROR `ValueError: Expected 'n_calls' ...` or `Too low MAX RUNS`. In case of an error like the following:

```
  File ".... /site-packages/skopt/optimizer/base.py", line 268, in base_minimize
    raise ValueError("Expected 'n_calls' >= %d, got %d" % (required_calls, n_calls))
ValueError: Expected 'n_calls' >= ..., got ...
```

or like:

```
ERROR. ValueError: ERROR. Too low MAX RUNS ! It should be incremented to ... at least.
```

you need to increase the `max-runs` parameter (which value needs to be at least `initial-points + 1`).

* ERROR `ModuleNotFoundError: No module named 'skopt' ...`. In case of an error like the following:
```
./css-optimizer.sh: line 4: ./css-opt-venv/bin/activate: No such file or directory
Traceback (most recent call last):
  File "... /src/shield_optimizer.py", line 7, in <module>
    from skopt import gp_minimize
ModuleNotFoundError: No module named 'skopt'
```

* ERROR `ValueError: Anisotropic kernel must have the same number of dimensions as data ..`. In case of an error like this, you need to check thoroughly all the configurations, making sure that items supposed to be distinct are not duplicated, etc.


you need to create the environment, as per installation instructions above.

## Change Log

### [1.1.0] - 2025-09-10 (M. Picciau)

#### Added

* Internal reenginering made the command line interface more readable and easy. This also brought higher modularization.

* Additional higher modularization also in many other points, greater readability and maintainability.

#### Changed

* The command line parameter for the history slicing now has '_' instead of '-'.

* The CF factory (for the stiffness calculation is no longer an environment variable, it is a command line parameter.

#### Fixed

* A bug in the advanced objective function caused the max total thickness miscalculated. This has been fixed (F. M. Soccorsi, Sep. 9, 2025).

### [1.0.10] - 2025-08-20 (M. Picciau)

#### Added

* Now the materials database (JSON file) contains also the young modulus of the material, and you can define shield stiffness range and CF factor in the command line. Violations of the range will result in WARNINGS in the log. Example:

`WARNING (...) Shield stiffness out of range: ... (range: ...)`

* IMPORTANT: as a consequence of the above mentioned enhancement, you need to upgrade the materials database(s) you are eventually using. For that purpose, you will launch the `./upgrade_mat_db_1.0.10.sh <file name>` for each json file you want to make compatible with the v. 1.0.10. Materials list (TXT) is ok and does not need any change.

### [1.0.9] - 2025-08-19 (M. Picciau)

#### Added

* As the shield trimming 'repair function' may cause, indirectly, the violation of constraints otherwise well protected by the raw search space data (namely: min. number of layers, min. layer thickness, min. shield thickness), now WARNINGS will be printed, in the log, when this occurs.

* Now the optimizer performs an initial assessment of the problem's consistency, and exits if the problem seems inconsistent.

* Now the scripts for Python virtual environment management are more robust and flexible (you can also easily choose whether you want a centralized virt. env. or a per-version, dedicated one, added also a script for the virtual environment deletion).

* Added precious information to troubleshooting section.

#### Changed

* ALL the wording, in the code and in the documentation, about shield clipping or slicing, is now converted to shield TRIMMING (more appropriate).

* As a direct consequence of the point above, the two environment variables `CSS_OPT_SHIELD_WGT_CLIPPING` and `CSS_OPT_SHIELD_CLIPPING` have been renamed to `CSS_OPT_SHIELD_WGT_TRIMMING` and `CSS_OPT_SHIELD_TRIMMING`.

#### Fixed

* Fixed a minor bug in a script

### [1.0.8] - 2025-08-17 (M. Picciau)

#### Added

* Now the logic for evaluating the objective function is pluggable, and there is also a specific configuration file to set its parameters. Ref. usage notes above, and also section about the available evaluators, and the guidelines to write one of your own.

* Now the logic for assessing whether or not the target is reached is pluggable. Ref. usage notes above, and also section about the available assessors, and the guidelines to write one of your own.

### [1.0.7] - 2025-08-17 (M. Picciau)

#### Added

* The two newest search space builders, now, are also equipped with tail-trimming of the shield if max shield weight is exceeded. This takes away another discontinuity from the optimization scenario.

* Improved documentation as it relates to algorithm description.

### [1.0.6] - 2025-08-16 (M. Picciau)

#### Added
* Now the search space builder is loaded dynamically, allowing easy swap, driven by configuration only, between different implementations. As a consequence, there is one parameter more in the command line. Its default points to a NEW search space builder which brings these additional features: tail-trimming of the shield if max shield thickness is exceeded, no consecutive layers with same material can be presented. These two features take away part of the discontinuities in the scenario.
* Related to the above: the new search space builder utilizes an encoded data format. It is very important for you to read the new section `Search Space Architecture and Search Space Builders`.
* Related to the point above: the old search space builder is still available, ready for use if so desired, ref. launch script new argument.
* Now the optimizer, in case an X0 is not found in the history nor in a user-provided X0 file, will create a random X0 with custom logic. This was needed as it turned out that the X0 which was automatically created by the framework in case none was specified may occasionally violate the constraints defined in the search space! Ref. [Scikit-Optimize / gp_minimize issue 1178][wr_gp_issue_1178].
* Now the history file (or the preloaded X0) is validated against the constraints upon loading.
* A new command line parameter is available to load only a SLICE of the history, instead of the whole.

* Now the environment creation script writes a log. As the tool becomes more complex, this may come handy.
* Now the launch scripts inform the user with more clarity in case the environment is missing.
* Logging HIGHLY improved with readable and compact execution summary, with details about the best solution found (both encoded and decoded) and other interesting metrics. Also, elapsed time is visible now.
* The excessively verbose optimization result returned by `gp_minimize` is no longer logged by default, it is visible only in debug mode.
* README improved with new sections and new contents.

#### Fixed
* The `kill` now works better, a minor inaccuracy was fixed in the script: the PID displayed was the PARENT of the true one. This has been amended (now the python program is launched with `exec`). And the slow responsiveness (for both `kill` and stop file mechanisms) has an explanation. Ref. notes above.

### [1.0.5] - 2025-08-13 (M. Picciau)

#### Added
* Added min tot thickness constraint (before, we had only the MAX, for this dimension)
* Added a script for terminating an optimization run. Launch `./kill_optimizer.sh <pid>`. Note, this script runs endlessly, you can interrupt it safely with `CTRL+C` if you like. IMPORTANT: note, however, that even this script may be not enough, ref. notes in open points.

#### Changed
* Internal rearchitecting to modularize the search space definition, in the hope of a future replacement with a better model, i.e. one with no or less non-linearities, ref. point above in the open points.
* Highly improved logging
* Internal rearchitecting for better modularization in general


### [1.0.4] - 2025-08-12 (M. Picciau)

#### Added
* Now ALL the `gp_minimize` parameters are accessible for configuration, by means of a new JSON file to edit: `config/optimizer_conf.json`

#### Changed
* The placeholder for `initial-points` parameter has been moved to the above mentioned new JSON file. Also, its default has been updated, now it is `200` (but, of course, it is still configurable). 

* The materials database (JSON) is no longer entirely retained in memory. The optimizer now loads in memory ONLY what is needed for the optimization run at hand.

* Logging improved

* Added two IMPORTANT open points about the `kill` and stop file mechanisms to obtain optimizator early shutdown. Please read carefully.

* Improved documentation (added credits to F. M. Soccorsi, added additional notes about materials database vs list, added an open point for future extension to an array of constraints, added open points about future constrained versions)

### [1.0.3] - 2025-08-11 (M. Picciau)

#### Added
* Now it is possible to configure a materials database, to get the weight related constraints checked in the pre-simulation phase. This is optional. If not used, the optimizer works as in previous versions. Ref. the above installation and usage notes for additional details.

* In order to get the optimizer spanning more widely the search space at the beginning of the run, a new parameter is now available (initial point), which sets the number of the initial randomic attempts.

* Now the user can specify an X0, i.e. an initial geometry to start with, ref. details in the installation notes above. This is optional. If not done the X0 is chosen randomly as it was before.

* Now the constraint over the max layer thickness is evaluated also in the post-simulation phase, to catch consecutive layers made of the same material eventually crossing the limit. Edited in 1.0.4: as a consequence, the constraint over the consecutiveness of same material layers has been removed.

* Now the user has a possibility to stop the optimizer also BEFORE the end of its natural cycle. Ref. details in the usage notes above.

* Now the code is ready for the introduction of echonomical constraints.

* Improved input data checks. For example, the duplications of materials in the materials list is detected and resolved at runtime.

* Improved error handling

* Improved documentation (added sections and notes).

### [1.0.2] - 2025-08-05 (M. Picciau)

#### Added
* A launcher is now being provided, to launch the optimizer in nohup/background mode.
* Logging has been simplified (`rich` dependency removed) and improved.

### [1.0.1] - 2025-08-04 (M. Picciau)

#### Added
* This README
* The `css-optimizer.sh` has a bigger editable section with interesting parameters.

#### Changed
* The timestamp format is now aligned to the one in use with the CSS (the year is now represented as `yy` instead of `yyyy`).

### [1.0.0] - 2025-08-01 (M. Picciau)

#### Added
* First version created

## References

1. [Python][wr_python]
2. [Scikit-Optimize / gp_minimize][wr_gp_minimize]
3. [Geant4][wr_geant4]
4. [ChatGPT thread of Aug. 11, 2025][wr_chatgpt_search_sp_1]
5. [Constrained version of Scikit-Optimize / gp_minimize][wr_gp_minimize_constrained_1]
6. [Scikit-Optimize / gp_minimize issue 1178][wr_gp_issue_1178]

[wr_python]: https://www.python.org/downloads/
[wr_gp_minimize]: https://scikit-optimize.github.io/stable/modules/generated/skopt.gp_minimize.html
[wr_geant4]: https://geant4.org
[wr_chatgpt_search_sp_1]: https://chatgpt.com/c/689910c9-9c34-8330-b242-6561d658aa7c
[wr_gp_minimize_constrained_1]: https://github.com/SaeednHT/scikit-optimize-constrained/
[wr_gp_issue_1178]: https://github.com/scikit-optimize/scikit-optimize/issues/1178
