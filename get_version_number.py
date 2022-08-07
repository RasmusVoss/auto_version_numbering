"""get_version_number
This script takes up to 6 arguments:
1. Mandatory:
    1. -d/--directory - The directory of the git repository.
    2. -b/--branch - The current branch name
2. Optional:
    1. -m/--major_minor_patch - What should the minimum version be (Example 1.0.0) Defaults to 0.1.0
    2. -i/--increment_position - What digit should be incremented are we bumping (1, Major), (2, Minor), (3, Patch), or (4, Build)
        when mainline is currently using the same version number as a release branch.
    3. -n/--build_number - The current build number, will be read from the environment variable BUILD_NUMBER if not specified.
    4. -l/--branch_number_length - For any branch that is not a release branch or mainline branch a unique version number will be created,
        this parameter speciefies the length of the unique number.

By Default:
If branch is mainline (master, develop, main) it will bump the fourth digit of the highest version number (Git tag)
- if the highest number matches a release branch the second digit will be bumbed, unless --increment_position parameter is used.

For release branches it will bumb the fourth digit of the version number matching the release branch

If no tags exist in the repository it will return 0.1.0.1 as version number

Scenario 1:
No tags in the repository and branch is mainline
- returns version number 0.1.0.1 as it must be the first version number

Scenario 2:
Tags exists [1.0.2.1, 1.0.2.2, 1.0.2.3] in the repository and branch is mainline
- returns version number 1.0.2.4 as we bump the fourth digit

Scenario 3:
Tags exists [1.0.2.1, 1.0.2.2, 1.0.2.3] Release branch release/1.0.2 exists in the repository and branch is mainline
- returns version number 1.1.0.1 as we bump the second digit and it is the first build on main line after the release branch was created.

Assumptions:
The version number returned by the script for the following branches
1. mainlines - master, develop, main
2. Advance feature development branches - feature/*
3. Release branches - release/*
Is expected to end up as a TAG in the repository, this script so far does to any tagging.
"""
import os
import re
import git
import sys
import argparse

from packaging import version
import hashlib

DEFAULT_MAJOR_MINOR_PATCH = '0.1.0'

def hash_text_to_8_digits(branch_name:str, length:int=8):
    """Returns an length specified hash of a branch name using numbers only

    Args:
        branch_name (str): Branch name to hash.
        length (int, optional): How many digits should the returned number have ? Defaults to 8.

    Returns:
        int: The hashed branch_name as an x digit integer.
    """
    return int(hashlib.sha1(branch_name.encode("utf-8")).hexdigest(), 16) % (10 ** length)

def get_tags_as_list_from_repository(repository_directory:str):
    """Returns a list of tags in the repository

    Args:
        repository_directory (str): Path to the git repository.

    Returns:
        tags (list): A list of tags for a repository.
    """
    repo = git.Repo(repository_directory)
    tags = []
    for tag in repo.tags:
        tags.append(tag.name)
    return tags

def return_filtered_tag_list(tags:list):
    """Returns a list of tags matching the regex.

    Args:
        tags (list): A list of git tags

    Returns:
        tags (list): Without tags not matching the specified pattern.
    """
    filtered_tag_list = []
    for tag in tags:
        if match_regex_to_version_number(tag, r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'):
            filtered_tag_list.append(tag)
    return filtered_tag_list

def match_regex_to_version_number(version:str, regex:str):
    """Returns True if the version number matches the regex.

    Args:
        version (str): Version number
        regex (str): Regex to executed

    Returns:
        bool: True if the version number matches the regex.
    """
    if re.match(regex, version) == None:
        return False
    return True


def get_remote_branches_from_repository(repository_directory:str):
    """Returns a list of remote branches in the repository

    Args:
        repository_directory (str): Path to the git repository.

    Returns:
        remote_branches (list): returns a list of remote branches
    """
    repo = git.Repo(repository_directory)
    remote_branches = []
    for branch in repo.remotes.origin.refs:
        remote_branches.append(branch.name.replace('origin/', ''))
    return remote_branches


def return_version_variables(version:str):
    """Return the version number as a list of variables.

    Args:
        version (str): Version number

    Returns:
        separated_integers (list): 4.5.6.7 will result in ['4', '5', '6', '7']
    """
    return version.split('.')


def return_highest_version_number_from_list(versions:list):
    """Return the highest version number from a list of version numbers.

    Args:
        versions (list): List of versions to find the highest version number from

    Returns:
        str: The highest version number
    """

    for n, i in enumerate(versions):
        versions[n] = version.parse(i)
    return max(versions).__str__()


def increment_last_digit_in_version(version:str, increment:int):
    """Add a number to the last digit in a version number.

    Args:
        version (str):Version Number
        increment (int): How much should we increment the version

    Returns:
        str: New version number
    """
    
    version_list = return_version_variables(version)
    version_list[-1] = str(int(version_list[-1]) + increment)
    return '.'.join(version_list)


def return_release_branches_from_branch_list(branches:list):
    """Returns a list of release branches from a list of branches.

    Args:
        branches (list): List of branchs

    Returns:
        branches (list): List of release branches
    """
    release_branches = []
    for branch in branches:
        if branch.startswith('release/'):
            release_branches.append(branch)
    return release_branches


def is_highest_version_number_matching_release_branch(version:str, branches:list):
    """Returns True if the highest version number is matching the release branch.

    Args:
        version (str): Version number
        branches (list): List of branches

    Returns:
        bool: True if the highest version number is matching a release branch.
    """
    release_branches = return_release_branches_from_branch_list(branches)
    for branch in release_branches:
        if version.startswith(branch.replace('release/', '')):
            return True
    return False

def increment_version_digit(version:str, increment:int, position:int):
    """Bump a digit in a version number.
    Any number after the bumped digit will be reset to 0.

    Args:
        version (str): Version number
        increment (int): How much to increment the digit
        position (int): Which digit to increment

    Returns:
        version_nuber (str): Returns a new version number with the correct increment.
    """
    version_list = return_version_variables(version)
    version_list[position - 1] = str(int(version_list[position - 1]) + increment)
    if len(version_list) == 4: # 4 digit version number
        if position == 2:
            version_list[-2] = '0'
        if position == 1:
            version_list[-3] = '0'
            version_list[-2] = '0'
    version_list[-1] = '1'
    return '.'.join(version_list)

def return_tag_list_starting_with(tags:list, pattern:str):
    """Returns a list of tags that start with a pattern.

    Args:
        tags (list): List of tags
        pattern (str): Pattern to match 

    Returns:
        tags (list): Matching tags
    """
    tag_list = []
    for tag in tags:
        if tag.startswith(pattern):
            tag_list.append(tag)
    return tag_list


def return_list_of_tags_matching_release_branches(tags:list, branches:list):
    """Returns a list of tags that match the release branches.

    Args:
        tags (list): List of tags
        branches (list): Pattern to match 

    Returns:
        tags (list): Matching tags
    """
    release_branches = return_release_branches_from_branch_list(branches)
    tag_list = []
    for branch in release_branches:
        if branch.replace('release/', '') not in tags:
            tag_list.append("{}.1".format(branch.replace('release/', '')))
        for tag in tags:
            if tag.startswith(branch.replace('release/', '')):
                tag_list.append(tag)
    return tag_list


def return_next_version_number(tags:list, branches:list, current_branch:str, major_minor_patch:str, increment_position:str, build_number:int, length:int=8):
    """ Returns the next version number.

    Args:
        tags (list): List of tags
        branches (list): List of branches
        current_branch (str): Current branch
        major_minor_patch (str): Expectation for highest starting major_minor_patch
        increment_position (str): Which position to increment in case of conflict between mainline and release branches
        build_number (int): Build number (Used for developer branches). Defaults to str.
        length (int, optional): Length of unique numbers. Defaults to 8.

    Returns:
        version_number (str): Returns the next version number, for the branch. 
    """
    _build_number = os.environ.get("BUILD_NUMBER",build_number)
    release_branch_indicator = 'release/'
    feature_branch_indicator = 'feature/'
    feature_branch_version_start = '0.0'
    filtered_tags = return_filtered_tag_list(tags)
    if current_branch in ['main', 'develop', 'master']:
        if len(filtered_tags) == 0:
            if major_minor_patch != '':
                return "{}.1".format(major_minor_patch)
            return '{}.1'.format(DEFAULT_MAJOR_MINOR_PATCH)
        tag_list_from_releases = return_list_of_tags_matching_release_branches(filtered_tags, branches)
        highest_version_number = return_highest_version_number_from_list(tag_list_from_releases+filtered_tags)
        highest_version_number_short = '.'.join(highest_version_number.split('.')[:-1])
        if version.parse(highest_version_number_short) < version.parse(major_minor_patch):
            # print ("Major_Minor_Patch -{}- is higher than -{}-".format(major_minor_patch, highest_version_number))
            return ("{}.1".format(major_minor_patch))
        if is_highest_version_number_matching_release_branch(highest_version_number, branches):
            # print ('Mainline build - Release Branch has reserved highest number -{}-, Bumping {}. digit'.format(highest_version_number,
            #                                                                                                    increment_position))
            return (increment_version_digit(highest_version_number, 1, int(increment_position)))
        else:
            # print('Mainline build - Bumbing last digit')
            return (increment_last_digit_in_version(highest_version_number, 1))
    elif current_branch.startswith(release_branch_indicator):
        tag_list = return_tag_list_starting_with(filtered_tags,current_branch.replace(release_branch_indicator, ''))
        if tag_list:
            return increment_last_digit_in_version(return_highest_version_number_from_list(tag_list), 1)
        else:
            return ('{}.1'.format(current_branch.replace(release_branch_indicator, '')))
    elif current_branch.startswith(feature_branch_indicator):
        third_digit = hash_text_to_8_digits(current_branch, length)
        tag_list = return_tag_list_starting_with(filtered_tags, "{}.{}".format(feature_branch_version_start, third_digit))
        if tag_list:
            return increment_last_digit_in_version(return_highest_version_number_from_list(tag_list), 1)
        else:
            third_digit = hash_text_to_8_digits(current_branch, length)
            return ('{}.{}.1'.format(feature_branch_version_start, third_digit))
    else:
        # Making the assumption that we are on a developer branch
        second_digit = hash_text_to_8_digits(current_branch, length)
        return ('99.{}.0.{}'.format(second_digit, _build_number))


def parse_arguments(args):
    argparser = argparse.ArgumentParser(description='Get a version number to use for a new release.')
    argparser.add_argument('-d', '--directory', help='The directory of the git repository.', required=True)
    argparser.add_argument('-b', '--branch', help='Current branch', required=True)
    argparser.add_argument('-m', '--major_minor_patch', help='What is the current major minor patch configured as?', required=False, default=DEFAULT_MAJOR_MINOR_PATCH)
    argparser.add_argument('-p', '--increment_position', help='What is the position of the version number to increment? When release and mainline version matches.', required=False, default=2)
    argparser.add_argument('-n', '--build_number', help='Current Build_Number, if not configured the environment variable will be used', required=False, default=0)
    argparser.add_argument('-l', '--branch_number_length', help='Current Build_Number, if not configured the environment variable will be used', type=int, required=False, default=8)
    return argparser.parse_args(args)


def main():
    arguments = parse_arguments(sys.argv[1:])
    available_tags = get_tags_as_list_from_repository(arguments.directory)
    current_remote_branches = get_remote_branches_from_repository(arguments.directory)

    print (return_next_version_number(available_tags, current_remote_branches, arguments.branch, arguments.major_minor_patch, arguments.increment_position, arguments.build_number, arguments.branch_number_length))

if __name__ == "__main__":
    main()