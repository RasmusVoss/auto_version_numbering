# get_version_number.py
## Modifications to the script

Execute the following commands 
```bash 
python3 -m pip install -r requirements.txt
coverage run -m pytest -o log_cli=True --noconftest --junitxml=test-results-unit.xml --html=report.html  test_get_version_number.p
coverage html
```
Now you have executed all the unit-test test, keep them passing. 
### Ideas
1. Support semantic versioning format 

## Introduction / Problem
We want a script that can be executed in a repository and generate a version number based on

1. Which branch is building
2. Which tags are in the repository
3. Which release branches are in the repository

The script has to support a scenario like this

1. Current mainline build is 4.8.0.12
   1. The first build on the release branch 4.8.0 should be 4.8.0.13
   2. The next build on mainline should be 4.9.0.1

We want to be able to do this automatic without any user interaction by default.
BUT !! At the same time we want to enable marketing making version numbering decisions, i.e. moving
CWB from 4.8 to 5.0 version.

### Example's
**The first build on mainline**
So not tags, no release branches, the very first build on mainline.
The script would expect this version number to end up as a tag.
```bash
python3 get_version_number.py --directory '~/repos/DEVOPS/jenkinsscripts/' --branch main
0.1.0.1
```

**A build on a developer branch**
Here we "hash" the branch name to an 8-digit and the version number is 99.hashed_number.0.build_number
1. build_number, would be expected to come from the build system.

```bash
python3 get_version_number.py --directory '~/repos/DEVOPS/jenkinsscripts/' --branch TOOLS-1234
99.76319135.0.1
```

## Specifics & Expectations by the script

The script looks for tags in the repository following the pattern

digit(s).digit(s).digit(s).digit(s)

With nothing before or after
``` python
r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'
```

The script finds the release branches from the remote to use for calculating the next version number

['release/1.2.0', 'release/1.2.1', 'release/2.3.0']

If you are on mainline a combination of avavilable tags and release branches determine what the next version number is supposed to be.

## parameters / usage

### Example
```bash
usage: get_version_number.py [-h] -d DIRECTORY -b BRANCH [-m MAJOR_MINOR_PATCH] [-p INCREMENT_POSITION] [-n BUILD_NUMBER]
get_version_number.py: error: the following arguments are required: -d/--directory, -b/--branch
```

### Descriptions

1. -d, --directory
   1. Which directory is the git repository located in, usually ${WORKSPACE} in a JenkinsFile
2. -b, --branch
   1. Which branch is the current branch, usually ${GIT_BRANCH} in a JenkinsFile
3. -m, --major_minor_patch
   1. The variable to overwrite the next version number scheme on mainline, could be set to 5.0.0 and if this is the higher than current mainline version number the next version number will be 5.0.0.1
4. -p, --increment_position
   1. Which position of the version number should be incremented on mainline when a release branch with same current major.minor.patch is created. Default to the second digit. (Minor)
5. -n, --build_number
   1. Which build_number is building. This is only used for developer branches, defaults to 0, but the script will try and read BUILD_NUMBER from the environment
6. -l, --branch_number_length
   1. How long should the unique version number be, defaults to 8

So in a pipeline you can do as in the example below.
This will return a usable version number for all types of branches.

### Jenkins Pipeline example

```groovy
steps{script { env.VERSION_NUMBER = getVersionNumber()}}
def getVersionNumber(){
	checkoutJenkinsScriptsSvnRepo()
	return sh(script: 'python3 JenkinsScripts/common/get_version_number.py -d "${WORKSPACE}" -b ${BRANCH_NAME}', returnStdout: true).trim()
}
```

## Scenario testing using unit-test

### First mainline build in the repository
No tags, or branches are available in the repository

![mainlineOnlyFirstBuilds][mainlineOnlyFirstBuilds]

#### Unit-Test
```python
def test_return_next_version_number_mainline_main_no_tags_no_release_branches():
   expected_result = '0.1.0.1'
   tags = []
   branches = []
   current_branch = 'main'
   major_minor_patch = ''
   increment_position = 1
   build_number = 1
   result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
   assert result == expected_result
```

### Mainline currently at 1.0.0.X then a release branch is created release/1.0.0

![standardMainlIneContinuousReleaseBranch][standardMainlIneContinuousReleaseBranch]

#### Unit-Test

```python
def test_bump_minor_when_release_branch_exist_without_tag():
    expected_result = '1.1.0.1'
    tags = ['1.0.0.1', '1.0.0.2', '1.0.0.3']
    branches = ['release/1.0.0']
    current_branch = 'main'
    major_minor_patch = '0.1.0'
    increment_position = 2
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result
```

```python
def test_continue_mainline_number_on_release_branch():
    expected_result = '1.0.0.4'
    tags = ['1.0.0.1', '1.0.0.2', '1.0.0.3']
    branches = ['release/1.0.0']
    current_branch = 'release/1.0.0'
    major_minor_patch = '0.1.0'
    increment_position = 2
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result
```

### Feature branch builds

![featureFishtank][featureFishtank]

A feature branch is treated like mainline and release branches so it is expected that the version number will result in a tag.

The version number starts with 0.0 to make sure it is always the lowest version number

The version unique part of the version number is generated by "hashing" the name of the branch into 8 digits. This way the uniqness of the branch version number remains the same.

```python
def test_return_first_version_number_feature_branch():
    expected_result = '0.0.70988576.1'
    tags = ['4.7.8.21']
    branches = []
    current_branch = 'feature/fishtank'
    major_minor_patch = '5.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result
```

```python
def test_return_next_version_number_feature_branch():
    expected_result = '0.0.70988576.2'
    tags = ['0.0.70988576.1']
    branches = []
    current_branch = 'feature/fishtank'
    major_minor_patch = '5.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result
```

### Developer branch
A developer branch is a branch that a developer creates that is not named feature/\*, release/\* or any of the mainline names, main, develop, master.

Basically any name

Developer branches is also the only type of branch where we rely on the build number from the build system, as developer branches shouldn't result in a tag.

To distinguish a developer branch from a feature branch the version starts with 99.unique.0.BUILD_NUMBER

![DeveloperBranches][DeveloperBranches]

```python
def test_developer_branch_tools_1234():
    expected_result = '99.76319135.0.1'
    tags = ['1.0.0.1', '1.0.0.2', '1.0.0.3']
    branches = ['release/1.0.0']
    current_branch = 'TOOLS-1234'
    major_minor_patch = '0.1.0'
    increment_position = 2
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result
```

```python
def test_developer_branch_cwb_1234():
    expected_result = '99.53736618.0.1'
    tags = ['1.0.0.1', '1.0.0.2', '1.0.0.3']
    branches = ['release/1.0.0']
    current_branch = 'CWB-1234'
    major_minor_patch = '0.1.0'
    increment_position = 2
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result
```

### Marketing version bump on mainline

We are releasing from mainline but marketing wants to go to version 1.0.0.X for the next release from mainline

This is where the flag --major_minor_patch comes, in by calling the script with --major_minor_patch 1.0.0 you ask the script to create a version 1.0.0.1 but only if something larger doesn't exist. By doing so you don't have to update the pipeline after you have the right version number. 

These use-cases are covered by the unit-test below

![marketingVersion][marketingVersion]

#### Pipeline example with next_marketing
```groovy
steps{script { env.VERSION_NUMBER = getVersionNumber()}}
def getVersionNumber(next_marketing){
	checkoutJenkinsScriptsSvnRepo()
	return sh(script: "python3 JenkinsScripts/common/get_version_number.py --major_minor_patch ${next_marketing} -d "${WORKSPACE}" -b ${BRANCH_NAME}", returnStdout: true)
}
```

#### Unit-tests

```python 
def test_return_next_version_number_mainline_tags_in_place_and_new_major_minor_patch_variable_higher_low_version_numbers():
    expected_result = '1.0.0.1'
    tags = ['0.1.0.1', '0.1.0.2']
    branches = []
    current_branch = 'main'
    major_minor_patch = '1.0.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result
```

Now in this scenario we are still calling the script with a marketing version 1.0.0 but there is a release/2.0.0 branch

So we cannot force the version number on mainline to be lower than the highest available version number

![marketingWithReleaseBranch][marketingWithReleaseBranch]

```python 
def test_return_next_version_number_mainline_tags_in_place_and_new_major_minor_patch_variable_ignored_with_release_branch():
    expected_result = '2.1.0.1'
    tags = ['0.1.0.1', '0.1.0.2']
    branches = []
    current_branch = 'main'
    major_minor_patch = '1.0.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result
```

``` python
def test_return_next_version_number_release_branch_tags_in_place_and_new_major_minor_patch_variable_ignored_with_release_branch():
    expected_result = '2.0.0.1'
    tags = ['0.1.0.1', '0.1.0.2']
    branches = ['release/2.0.0']
    current_branch = 'release/2.0.0'
    major_minor_patch = '1.0.0'
    increment_position = 2
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result
```

### Short unique version number

Some projects only supports a shorter version number so you can use --branch_number_length flag to set the limit on how many digits the unique number can be. 

![unique_4_digits][unique_4_digits]



```groovy
steps{script { env.VERSION_NUMBER = getVersionNumber()}}
def getVersionNumber(){
	checkoutJenkinsScriptsSvnRepo()
	return sh(script: 'python3 JenkinsScripts/common/get_version_number.py -l 4 -d "${WORKSPACE}" -b ${BRANCH_NAME}', returnStdout: true)
}
```
```python

def test_return_branch_version_number_unique_4_digits():
    expected_result = '0.0.8576.1'
    tags = ['0.0.9999.1']
    branches = []
    current_branch = 'feature/fishtank'
    major_minor_patch = '1.0.0'
    increment_position = 2
    build_number = 1
    unique_length = 4
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number, unique_length)
    assert result == expected_result
```

[mainlineOnlyFirstBuilds]: ./images/mainlineOnlyFirstBuilds.png "mainlineOnlyFirstBuilds"
[BumpMajorOnMainline]: ./images/BumpMajorOnMainline.png "BumpMajorOnMainline"
[BumpPatchOnMainline]: ./images/BumpPatchOnMainline.png "BumpPatchOnMainline"
[PatchBranch]: ./images/PatchBranch.png "PatchBranch"
[standardMainlIneContinuousReleaseBranch]: ./images/standardMainlIneContinuousReleaseBranch.png "standardMainlIneContinuousReleaseBranch"
[standardMainlIneContinuousReleaseBranchLargernumber]: ./images/standardMainlIneContinuousReleaseBranchLargernumber.png "standardMainlIneContinuousReleaseBranchLargernumber"
[featureFishtank]: ./images/featureFishtank.png "featureFishtank"
[DeveloperBranches]: ./images/DeveloperBranches.png "DeveloperBranches"
[marketingVersion]: ./images/marketingVersion.png "marketingVersion"
[marketingWithReleaseBranch]: ./images/marketingWithReleaseBranch.png "marketingWithReleaseBranch"
[unique_4_digits]: ./images/unique_4_digits.png "unique_4_digits"
