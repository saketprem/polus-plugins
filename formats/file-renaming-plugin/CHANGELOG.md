## File Renaming(v0.1.18-dev1)

1. This plugin is updated only to the new plugin standards and no additional functionality is added.
2. This plugin is now installable with pip.
3. Argparse package is replaced with Typer package for command line arguments.
4. `baseCommand` added in a plugin manifiest.
5. `--preview` flag is added which shows outputs to be generated by this plugin along with the outFilePattern used.
6. Use `python -m python -m polus.plugins.formats.ome_converter` to run plugin from command line.
7. Replaced `Unittest` with `pytest` package.
8. Code is optimized for parallel execution of tasks
9. New feature/input argument `mapDirectory` implemented to include directory name in renamed files. It is optional if `raw` selected then orignal directory name is added in renamed files and `map` for mapped values for subdirectories `d0, d1, d2, ... dn`. If no value is passed then it rename files only for the selected directory.
