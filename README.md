# labchecker

Automatic code checker made in competition programming manner.

![GitHub top language](https://img.shields.io/github/languages/top/devepodete/labchecker?color=green)
![GitHub license](https://img.shields.io/github/license/devepodete/labchecker)
![Platform linux](https://img.shields.io/badge/platform-linux-yellow)

### Idea

1. Get new messages from mail
2. Check each submit
3. Reply with verdict

### Main definitions

1. `IPipelineElement` - one step in program testing
2. `Gate` - container for multiple `IPipelineElement` entities
3. `GateHolder` - container for multiple `Gate` entities

All you need is to create Gates which are basic steps for your programs testing and fill each gate with
PipelineElements.

Example (schematic):

* `Gate 1 (Build): [Build]`
* `Gate 2 (Test): [Run simple tests, Run advanced tests]`
* `Gate 3 (Antiplagiarism): [Check code for plagiarism]`
* `Generate ans send report`

As you can see, each Gate contains several consecutive pipeline elements (like `Build` or `Run simple tests`).

One also may notice that some Gates are meaningless if previous gates are failed. For example, if `Gate 1` failed and
program did not build, we can not run `Gate 2` for testing. The library contains functionality for controlling such
cases.

Reports may be generated in HTML or TXT format.