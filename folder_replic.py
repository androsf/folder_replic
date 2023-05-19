import filecmp
import logging
import os
import shutil
import sys
import time


def main(argv):

    # Diff lists
    files_for_deletion = []
    files_for_copying = []
    folders_common = []

    # Replaces source path with destination path in pathlike string
    def path_replace(path):
        return path.replace(path_src, path_dst, 1)

    # Stores file_cmp.dircmp results in diff lists
    def parse_cmp_result(p_result, path):
        [files_for_copying.append(y) for y in [os.path.join(path, x) for x in p_result.left_only]]
        [files_for_copying.append(y) for y in [os.path.join(path, x) for x in p_result.diff_files]]
        [files_for_deletion.append(y) for y in [os.path.join(path_replace(path), x) for x in p_result.right_only]]
        [folders_common.append(y) for y in [os.path.join(path_src, x) for x in p_result.common_dirs]]

    # Copies items from source directory to destination directory using files_for_copying list
    def replica_copy(path):
        if os.path.isfile(path):
            shutil.copy2(path, path_replace(path))
            logging_file_manipulation('Copied file: ' + path + ' to destination: ' + path_replace(path))
        elif os.path.isdir(path):
            shutil.copytree(path, path_replace(path))
            logging_file_manipulation('Directory copied: ' + path + ' to destination: ' + path_replace(path))
        else:
            logging_file_manipulation('Not valid path : ' + path)

    # Deletes items from destination directory using files_for_deletion list
    def replica_delete(path):
        if os.path.isfile(path):
            os.remove(path)
            logging_file_manipulation('Removed file: ' + path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
            logging_file_manipulation('Removed directory : ' + path)
        else:
            logging_file_manipulation('Not valid path : ' + path)

    # Print and log info messages
    def logging_file_manipulation(message):
        print(message)
        logging.info(message)

    # Print and log debug messages
    def logging_debug_msg(message):
        if logging.root.manager.getLogger('basic').getEffectiveLevel() == logging.DEBUG:
            print(message)
        logging.debug(message)

    # Starts replication process
    def replicate():

        # Getting diffs between source and destination
        result = filecmp.dircmp(path_src, path_dst)
        parse_cmp_result(result, path_src)

        # End iteration if no diffs founded
        if len(result.diff_files) == 0 and len(result.left_only) == 0 and len(result.right_only) == 0:
            logging_debug_msg('No diffs')
        else:
            logging_debug_msg('There are diffs')

            # Getting diffs sequentially between common directories of source and destination
            for i in folders_common:
                working_dir_src = i
                result_i = filecmp.dircmp(working_dir_src, path_replace(i))
                parse_cmp_result(result_i, working_dir_src)

            # Debug logging
            logging_debug_msg('For delete: ')
            [logging_debug_msg(x) for x in files_for_deletion]
            [replica_delete(item) for item in files_for_deletion]

            logging_debug_msg('For copy: ')
            [logging_debug_msg(x) for x in files_for_copying]
            [replica_copy(item) for item in files_for_copying]

            logging_debug_msg('Common dir list: ')
            [logging_debug_msg(x) for x in folders_common]

        # Clear iteration results
        files_for_deletion.clear()
        files_for_copying.clear()
        folders_common.clear()

    # Main flow
    # Parsing args
    path_src = sys.argv[1]
    if not os.path.exists(path_src):
        sys.exit(argv[0] + ': Not valid source path')
    path_dst = sys.argv[2]
    if not os.path.exists(path_dst):
        sys.exit(argv[1] + ': Not valid destination path')
    path_log = sys.argv[3]
    if not os.path.exists(os.path.dirname(path_log)):
        sys.exit(argv[2] + ': Not valid logfile path')
    sync_interval = float(sys.argv[4])
    if not sync_interval > 0:
        sys.exit(argv[3] + ': Interval must be positive float')

    # Setting up logging options
    logging.basicConfig(filename=path_log,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    # Starting main loop
    while True:
        replicate()
        time.sleep(sync_interval)


if __name__ == '__main__':
    main(sys.argv[1:])
