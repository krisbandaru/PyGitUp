# System imports
import os
from os.path import join

# 3rd party libs
from nose.tools import *
from git import *

# PyGitup imports
from PyGitUp.git_wrapper import GitError
from tests import basepath, write_file, init_master, testfile_name, update_file

test_name = 'diverged'

repo_path = join(basepath, test_name + os.sep)


def setup():
    master_path, master = init_master(test_name)

    # Prepare master repo
    master.git.checkout(b=test_name)

    # Clone to test repo
    path = join(basepath, test_name)

    master.clone(path, b=test_name)
    repo = Repo(path, odbt=GitCmdObjectDB)

    assert repo.working_dir == path

    # Set git-up.rebase.auto to false
    repo.git.config('git-up.rebase.auto', 'false')

    # Modify file in master
    master_path_file = join(master_path, testfile_name)
    write_file(master_path_file, 'line 1\nline 2\ncounter: 2')
    master.index.add([master_path_file])
    master.index.commit(test_name)

    # Modify file in our repo
    repo_path_file = join(path, testfile_name)
    write_file(repo_path_file, 'line 1\nline 2\ncounter: 3')
    repo.index.add([repo_path_file])
    repo.index.commit(test_name)


def test_ahead_of_upstream():
    """ Run 'git up' with result: diverged """
    os.chdir(repo_path)

    from PyGitUp.gitup import GitUp
    gitup = GitUp()
    gitup.run(testing=True)

    assert_equal(len(gitup.states), 1)
    assert_equal(gitup.states[0], 'diverged')
