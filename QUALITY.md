# Coding Conventions

## Naming

- **Functions**: CamelCase (except internal helpers nested inside functions)
- **Variables**: snake_case (except global variables and paths use CAPITALIZED)
- **Paths**: Always `Path` objects from `pathlib`, named `INDIR_*` or `OUTDIR_*` (or `INDIR`/`OUTDIR`)
- **Typing**: Don't implement typing
- **Comments**: Exclude comments unless the code would be unclear without them.
- **Organization**: All functions should have a `Main()` function that takes no input, and relies on helper functions throughout the rest of the script, unless it is purely a helper script.
- **PYTHONPATH**: Assume `export PYTHONPATH=.` is done, so you should always import project-specific dependencies from the root.
- **ORDERING**: Functions should be in the order they are called, with `Main()` first
- **SAVING DATA**: All data should be saved with `SaveData`, always passing `log_file=` (same path as the CSV but `.log` extension). For loops, use a single shared log with `append=True` on all but the first call — unless the loop runs in parallel (e.g. per-state via `scons -j`), then use per-file logs with `append=False`.
  - **Checkpoint exception**: Long-running scrapers that write one result per iteration should use append-to-CSV or pickle for crash-safe checkpointing, not `SaveData`. Add a one-line comment at the append site explaining why (e.g., `# checkpoint: append each row so a crash doesn't lose prior results`).
- **MODULARIZATION**: Scripts must be broken into named sub-functions, one per logical pipeline step. Function names describe the step semantically (`GroupByAncestryMatchIndex`, not `Step4`). Section heading comments (`# ## Section Title`) should become function names, not inline comments.

## SConscript

- Every `source/` subdirectory with scripts has its own `SConscript`. Parent files only call children via `SConscript('child/SConscript')` — no build targets in parent files.
- Use `env.Python(target, source)` for Python scripts, which is the primary programming language of this project. Pass command-line arguments via `CL_ARG=value`; the script reads them from `sys.argv`.
- To parallelize across entities (e.g. states) with `scons -j N`, create one `env.Python` per entity in a loop with `CL_ARG=entity`.
