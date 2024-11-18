"""Classes to print info, warnings and errors to standard output during the simulation."""

# This file is part of i-PI.
# i-PI Copyright (C) 2014-2015 i-PI developers
# See the "licenses" directory for full license information.


import traceback
import sys
import os

__all__ = [
    "Verbosity",
    "verbosity",
    "banner",
    "info",
    "warning",
    "get_identification_info",
]


VERB_QUIET = 0
VERB_LOW = 1
VERB_MEDIUM = 2
VERB_HIGH = 3
VERB_DEBUG = 4
VERB_TRACE = 5


class Verbosity(object):
    """Class used to determine what to print to standard output.

    Attributes:
        level: Determines what level of output to print.
    """

    lock = False
    level = VERB_LOW

    def __getattr__(self, name):
        """Determines whether a certain verbosity level is
        less than or greater than the stored value.

        Used to decide whether or not a certain info or warning string
        should be output.

        Args:
            name: The verbosity level at which the info/warning string
                will be output.
        """

        if name == "quiet":
            return self.level >= VERB_QUIET
        elif name == "low":
            return self.level >= VERB_LOW
        elif name == "medium":
            return self.level >= VERB_MEDIUM
        elif name == "high":
            return self.level >= VERB_HIGH
        elif name == "debug":
            return self.level >= VERB_DEBUG
        elif name == "trace":
            return self.level >= VERB_TRACE
        else:
            return super(Verbosity, self).__getattr__(name)

    def __setattr__(self, name, value):
        """Sets the verbosity level

        Args:
            name: The name of what to set. Should always be 'level'.
            value: The value to set the verbosity to.

        Raises:
            ValueError: Raised if either the name or the level is not
                a valid option.
        """

        if name == "level":
            if self.lock:
                # do not set the verbosity level if this is locked
                return
            if value == "quiet":
                level = VERB_QUIET
            elif value == "low":
                level = VERB_LOW
            elif value == "medium":
                level = VERB_MEDIUM
            elif value == "high":
                level = VERB_HIGH
            elif value == "debug":
                level = VERB_DEBUG
            elif value == "trace":
                level = VERB_TRACE
            else:
                raise ValueError(
                    "Invalid verbosity level " + str(value) + " specified."
                )
            super(Verbosity, self).__setattr__("level", level)
        else:
            super(Verbosity, self).__setattr__(name, value)


verbosity = Verbosity()


def read_git_file(filepath):
    """Reads and returns the content of a Git-related file."""
    try:
        with open(filepath, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def get_git_info():
    """
    Retrieves basic Git repository information by reading .git directory files.

    Returns
    -------
    dict or None
        A dictionary containing Git information or None if unable to read Git data.
    """
    base_path = os.path.abspath(os.path.join(__file__, "..", "..", "..")) + "/"
    git_dir = os.path.join(base_path, ".git")
    if not os.path.isdir(git_dir):
        return None

    # Read HEAD to get the current branch or commit hash
    head_content = read_git_file(os.path.join(git_dir, "HEAD"))
    if not head_content:
        return None

    branch_name = "unknown"
    last_commit = "unknown"
    remote_url = "unknown"

    # Parse the current branch name
    try:
        if head_content.startswith("ref:"):
            ref_path = os.path.join(git_dir, head_content.split(" ")[1])
            branch_name = os.path.basename(ref_path)
            last_commit = read_git_file(ref_path)
        else:
            # Detached HEAD state
            branch_name = "DETACHED"
            last_commit = head_content
    except:
        pass

    try:
        # Get remote URL from the config file
        config_path = os.path.join(git_dir, "config")
        # remote_url = None
        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                for line in config_file:
                    if line.strip().startswith("url ="):
                        remote_url = line.split("=")[1].strip()
                        break
    except:
        pass

    return {
        "branch_name": branch_name,
        "last_commit": last_commit,
        "remote_url": remote_url,
    }


def get_system_info():
    """
    Collects and returns basic system information.

    This function gathers details such as the current working directory and the machine
    name (hostname). Additional information such as the fully qualified domain name (FQDN),
    operating system details, CPU information, and user information can be uncommented and
    added as needed.

    Returns
    -------
    dict
        A dictionary containing:
        - "current_folder": str, the current working directory.
        - "machine_name": str, the machine's hostname.
        # - "fqdn": str, the fully qualified domain name (currently a fallback to machine name).
        # - "os_name": str, the name of the operating system.
        # - "os_version": str, the version of the operating system.
        # - "processor": str, the processor model.
        # - "num_nodes": int, the number of CPU cores.
        # - "user_name": str, the user name running the script.
    """

    # Get the current working directory
    current_folder = os.getcwd()

    # Get the machine name (hostname)
    try:
        with open("/etc/hostname", "r") as file:
            machine_name = file.read().strip()
    except FileNotFoundError:
        machine_name = "Unknown"  # Fallback in case the file is not found

    # Return the collected information as a dictionary
    return {
        "current_folder": current_folder,
        "machine_name": machine_name,
    }


def get_identification_info():
    """
    Collects and formats both Git and system information into a human-readable string.

    This function retrieves information from the Git repository and the system where
    it is executed. It formats the gathered data into a structured, readable string
    with appropriate headings and labels, which can be used for logging or documentation.

    Returns
    -------
    str
        A formatted string that includes Git information (e.g., remote URL, branch name,
        last commit details) and system information (e.g., current folder, machine name).
        If any information cannot be retrieved, the output will include an appropriate
        message indicating that.
    """

    # Retrieve Git information using a helper function
    git_info = get_git_info()

    # Retrieve system information using another helper function
    system_info = get_system_info()

    # Initialize the string that will hold all formatted information
    info_string = ""

    # Format and add Git information if it is successfully retrieved
    if git_info:
        info_string += "# Git information:\n"
        info_string += f"#      Remote URL: {git_info['remote_url']:<24}\n"
        info_string += f"#          Branch: {git_info['branch_name']:<24}\n"
        info_string += f"#     Last Commit: {git_info['last_commit']:<24}\n"
    else:
        # Inform the user if Git information could not be retrieved
        info_string += "# Unable to retrieve Git information.\n"

    # Add a separator line for clarity between Git and system information
    info_string += "#\n"

    # Format and add system information if it is successfully retrieved
    if system_info:
        info_string += "# System information:\n"
        info_string += f"#     Current Folder: {system_info['current_folder']}\n"
        info_string += f"#       Machine Name: {system_info['machine_name']}\n"
    else:
        # Inform the user if system information could not be retrieved
        info_string += "# Unable to retrieve system information.\n"

    # Return the final formatted string
    return info_string


def banner():
    """Prints out a banner."""

    print(
        r"""
 ____       ____       ____       ____
/    \     /    \     /    \     /    \
|  #################################  |
\__#_/     \____/     \____/     \_#__/
   #    _        _______  _____    #
   #   (_)      |_   __ \|_   _|   #      -*-       v 3.0      -*-
   #   __  ______ | |__) | | |     #
   Y  [  ||______||  ___/  | |     #      A Universal Force Engine
  0 0  | |       _| |_    _| |_    #
   #  [___]     |_____|  |_____|   #
 __#_       ____       ____       _#__
/  # \     /    \     /    \     / #  \
|  #################################  |
\____/     \____/     \____/     \____/

    """
    )

    info_string = get_identification_info()
    print(info_string)


def info(text="", show=True):
    """Prints a message.

    Args:
        text: The text of the information message.
        show: A boolean describing whether or not the message should be
            printed.
    """

    if not show:
        return
    print(text)


def warning(text="", show=True):
    """Prints a warning message.

    Same as info, but with a "!W!" prefix and optionally printing a stack trace.

    Args:
        text: The text of the information message.
        show: A boolean describing whether or not the message should be
            printed.
    """

    if not show:
        return
    if verbosity.trace:
        traceback.print_stack(file=sys.stdout)
    print((" !W! " + text))
