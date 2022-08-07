import get_version_number
import pytest
import shutil
import git
import os

def __initialize_git_repo(repository_path='./tmp/test_repository'):
    filename = "repostory_filename.txt"
    shutil.rmtree(repository_path, ignore_errors=True)
    os.makedirs(repository_path, exist_ok=True)
    repository = git.Repo.init(repository_path)
    with open('{}/{}'.format(repository_path, filename), 'w') as writer:
        writer.write("Hello World")
    repository.git.add(all=True)
    repository.index.commit("Initial commit")
    return repository

def test_hash_text_to_8_digits():
    expected_result = 90920209
    result = get_version_number.hash_text_to_8_digits('TOOLS-12345')
    assert expected_result == result

def test_hash_text_to_8other_digits():
    expected_result = 3016135
    result = get_version_number.hash_text_to_8_digits('TOOLS-54321')
    assert expected_result == result

def test_get_tags_as_list_from_repository():
    expected_result = ['4.5.0.1', '4.6.0.1']
    repository = __initialize_git_repo()
    repository.create_tag("4.5.0.1")
    repository.create_tag("4.6.0.1")
    result = get_version_number.get_tags_as_list_from_repository(repository.working_dir)
    assert result == expected_result

def test_get_tags_as_list_from_repository_with_odd_tags():
    expected_result = ['4.5.0.1', '4.6.0.1']
    repository = __initialize_git_repo()
    repository.create_tag("4.5.0.1")
    repository.create_tag("4.6.0.1")
    result = get_version_number.get_tags_as_list_from_repository(repository.working_dir)
    assert result == expected_result

def test_get_remote_branches_as_list_from_repoitory():
    expected_result = ['HEAD', 'main', 'master', 'release/4.5.0']
    repository1 = __initialize_git_repo('./tmp/test_repository1')
    repository2_path = "./tmp/test_repository2"
    shutil.rmtree(repository2_path, ignore_errors=True)
    repository1.create_head("release/4.5.0")
    repository1.create_head("main")
    git.Repo.clone_from(repository1.working_dir, repository2_path)
    result = get_version_number.get_remote_branches_from_repository(repository2_path)
    assert result == expected_result

def test_return_highest_version_number_from_list_4digits_same_versions():
    expected_result = '4.7.0.200'
    versions = ['4.7.0.197', '4.7.0.198', '4.7.0.199', '4.7.0.200']
    result = get_version_number.return_highest_version_number_from_list(versions)
    assert result == expected_result

def test_return_highest_version_number_from_list_3digits_same_versions():
    expected_result = '4.7.200'
    versions = ['4.7.197', '4.7.198', '4.7.199', '4.7.200']
    result = get_version_number.return_highest_version_number_from_list(versions)
    assert result == expected_result

def test_return_highest_version_number_from_list_4digits_same_versions_high2digit_number():
    expected_result = '4.111.0.199'
    versions = ['4.98.0.197', '4.7.0.198', '4.111.0.199', '4.7.0.200']
    result = get_version_number.return_highest_version_number_from_list(versions)
    assert result == expected_result

def test_increment_last_digit_in_version():
    expected_result = '4.7.0.201'
    result = get_version_number.increment_last_digit_in_version('4.7.0.200', 1)
    assert result == expected_result

def test_return_release_branches_from_branch_list():
    expected_result = ['release/4.5.0', 'release/4.6.0']
    branches = ['release/4.5.0', 'release/4.6.0', 'main', 'master']
    result = get_version_number.return_release_branches_from_branch_list(branches)
    assert result == expected_result

def test_return_version_4digits_variables():
    expected_result = ['4', '7', '0', '200']
    result = get_version_number.return_version_variables('4.7.0.200')
    assert result == expected_result

def test_return_version_3digits_variables():
    expected_result = ['4', '7', '0']
    result = get_version_number.return_version_variables('4.7.0')
    assert result == expected_result

def test_return_version_2digits_variables():
    expected_result = ['4', '7']
    result = get_version_number.return_version_variables('4.7')
    assert result == expected_result

def test_is_highest_version_number_matching_release_branch_true():
    expected_result = True
    version = '4.7.0'
    release_branch_list = ['release/4.5.0', 'release/4.6.0', 'release/4.7.0']
    result = get_version_number.is_highest_version_number_matching_release_branch(version, release_branch_list)
    assert result == expected_result

def test_is_highest_version_number_matching_release_branch_false():
    expected_result = False
    version = '4.8.0'
    release_branch_list = ['release/4.5.0', 'release/4.6.0', 'release/4.7.0']
    result = get_version_number.is_highest_version_number_matching_release_branch(version, release_branch_list)
    assert result == expected_result

def test_increment_version_digit_1st():
    expected_result = '5.0.0.1'
    version = '4.9.0.21'
    result = get_version_number.increment_version_digit(version, 1, 1)
    assert result == expected_result

def test_increment_version_digit_2nd():
    expected_result = '4.10.0.1'
    version = '4.9.0.21'
    result = get_version_number.increment_version_digit(version, 1, 2)
    assert result == expected_result

def test_increment_version_digit_3rd():
    expected_result = '4.9.1.1'
    version = '4.9.0.21'
    result = get_version_number.increment_version_digit(version, 1, 3)
    assert result == expected_result

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

def test_return_next_version_number_mainline_develop_no_tags_no_release_branches():
    expected_result = '0.1.0.1'
    tags = []
    branches = []
    current_branch = 'develop'
    major_minor_patch = ''
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_mainline_master_no_tags_no_release_branches():
    expected_result = '0.1.0.1'
    tags = []
    branches = []
    current_branch = 'master'
    major_minor_patch = ''
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_mainline_tags_in_place_no_release_branches():
    expected_result = '4.7.0.21'
    tags = ['4.7.0.20']
    branches = []
    current_branch = 'main'
    major_minor_patch = ''
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_mainline_tags_in_place_and_release_branches_bump_digit1():
    expected_result = '5.0.0.1'
    tags = ['4.7.0.20']
    branches = ['release/4.7.0']
    current_branch = 'main'
    major_minor_patch = ''
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_mainline_tags_in_place_and_release_branches_bump_digit2():
    expected_result = '4.8.0.1'
    tags = ['4.7.0.20']
    branches = ['release/4.7.0']
    current_branch = 'main'
    major_minor_patch = ''
    increment_position = 2
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_mainline_tags_in_place_and_release_branches_bump_digit3():
    expected_result = '4.7.1.1'
    tags = ['4.7.0.20']
    branches = ['release/4.7.0']
    current_branch = 'main'
    major_minor_patch = ''
    increment_position = 3
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_mainline_tags_in_place_and_new_major_minor_patch_variable_higher():
    expected_result = '5.6.0.1'
    tags = ['4.7.0.20', '4.8.0.21']
    branches = []
    current_branch = 'main'
    major_minor_patch = '5.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

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

def test_return_next_version_number_mainline_tags_in_place_and_new_major_minor_patch_variable_lower():
    expected_result = '4.7.0.21'
    tags = ['4.7.0.20']
    branches = []
    current_branch = 'main'
    major_minor_patch = '4.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_release_branch_no_tags():
    expected_result = '4.7.0.1'
    tags = []
    branches = []
    current_branch = 'release/4.7.0'
    major_minor_patch = '4.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_release_branch_with_many_tags():
    expected_result = '4.7.0.23'
    tags = ['4.7.0.20', '4.7.0.21', '4.7.0.22', '4.9.0.2']
    branches = []
    current_branch = 'release/4.7.0'
    major_minor_patch = '4.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_release_branch_with_1tag():
    expected_result = '4.7.0.21'
    tags = ['4.7.0.20']
    branches = []
    current_branch = 'release/4.7.0'
    major_minor_patch = '4.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result


def test_return_next_version_number_release_branch_with_1tag_doubledigits():
    expected_result = '4.61.0.23'
    tags = ['4.7.0.20', '4.61.0.22']
    branches = []
    current_branch = 'main'
    major_minor_patch = '4.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_next_version_number_high_major_minor_path_ow_release_branch():
    expected_result = '4.7.0.21'
    tags = ['4.7.0.20']
    branches = []
    current_branch = 'release/4.7.0'
    major_minor_patch = '5.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result


def test_parse_arguments_double_dash_missing_parameter_directory():
    commandline_parameters = ['--branch', 'release/4.7.0', '--major_minor_patch', '4.6.0', '--increment_position', '1', '-n', '1']
    with pytest.raises(SystemExit) as e:
        get_version_number.parse_arguments(commandline_parameters)
        assert e.type == SystemExit
        assert e.value.code == 2

def test_parse_arguments_single_dash_missing_parameter_directory():
    commandline_parameters = ['-b', 'release/4.7.0', '-m', '4.6.0', '-p', '1', '-n', '1']
    with pytest.raises(SystemExit) as e:
        get_version_number.parse_arguments(commandline_parameters)
        assert e.type == SystemExit
        assert e.value.code == 2

def test_parse_arguments_single_dash_parameter():
    commandline_parameters = ['-b', 'release/4.7.0', '-m', '4.6.0', '-p', '1', '-d', '1', '-n', '1']
    expected_result = ['1', 'release/4.7.0', '4.6.0', '1', '1']
    result = get_version_number.parse_arguments(commandline_parameters)
    result_list = [result.directory, result.branch, result.major_minor_patch, result.increment_position, result.build_number]
    assert result_list == expected_result

def test_return_next_version_number_feature_branch():
    expected_result = '0.0.70988576.2'
    tags = ['0.0.70988576.1', '0.0.90988576.1']
    branches = []
    current_branch = 'feature/fishtank'
    major_minor_patch = '5.6.0'
    increment_position = 1
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

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

def test_return_apple_release_branch_version():
    expected_result = '1.1.0.1'
    tags = ['1.0.0.1', '1.0.0.2', '1.0.0.3']
    branches = ['release/1.0.1', 'TOOLS-1234']
    current_branch = 'main'
    major_minor_patch = '1.0.0'
    increment_position = 2
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

def test_return_apple_release_branch_version_with_a_release_branch_tag():
    expected_result = '1.1.0.1'
    tags = ['1.0.0.1', '1.0.0.2', '1.0.0.3', '1.0.1.1', 'TEST-1234']
    branches = ['release/1.0.1', 'TOOLS-1234']
    current_branch = 'main'
    major_minor_patch = '1.0.0'
    increment_position = 2
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

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

def test_match_regex_to_version_number_return_false():
    result = get_version_number.match_regex_to_version_number('TEST-12234', r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$')
    assert result == False

def test_match_regex_to_version_number_return_true():
    result = get_version_number.match_regex_to_version_number('1.0.222.0', r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$')
    assert result == True

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

def test_return_next_version_number_mainline_tags_in_place_and_new_major_minor_patch_variable_ignored_with_release_branch():
    expected_result = '2.1.0.1'
    tags = ['0.1.0.1', '0.1.0.2']
    branches = ['release/2.0.0']
    current_branch = 'main'
    major_minor_patch = '1.0.0'
    increment_position = 2
    build_number = 1
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number)
    assert result == expected_result

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

def test_developer_branch_tools_1234_unique_4_digits():
    expected_result = '99.9135.0.1'
    tags = ['1.0.0.1', '1.0.0.2', '1.0.0.3']
    branches = ['release/1.0.0']
    current_branch = 'TOOLS-1234'
    major_minor_patch = '0.1.0'
    increment_position = 2
    build_number = 1
    unique_length = 4
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number, unique_length)
    assert result == expected_result

def test_developer_branch_cwb_1234_unique_4_digits():
    expected_result = '99.6618.0.1'
    tags = ['1.0.0.1', '1.0.0.2', '1.0.0.3']
    branches = ['release/1.0.0']
    current_branch = 'CWB-1234'
    major_minor_patch = '0.1.0'
    increment_position = 2
    build_number = 1
    unique_length = 4
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number, unique_length)
    assert result == expected_result

def test_major_minor_patch_in_fresh_repository():
    expected_result = '0.0.0.1'
    tags = []
    branches = []
    current_branch = 'main'
    major_minor_patch = '0.0.0'
    increment_position = 2
    build_number = 1
    unique_length = 4
    result = get_version_number.return_next_version_number(tags, branches, current_branch, major_minor_patch, increment_position, build_number, unique_length)
    assert result == expected_result    

def test_hash_text_to_8_digits_branch_with_similar_names_does_not_colide():
    first = get_version_number.hash_text_to_8_digits('HERMESSW-1234')
    second = get_version_number.hash_text_to_8_digits('HERMESSW-4321')
    assert first != second