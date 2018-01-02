import importlib
import logging
import sys
import time

from torrentbro.lib.utilities.Config import Config


class CrossSite(Config):
    def __init__(self, title, page_limit):
        Config.__init__(self)
        self.title = title
        self.pages = page_limit
        self.logger = logging.getLogger('log1')
        self.masterlist = []
        self.mapper = []
        self.total_time = 0
        self.headers = ["NAME (UPLOADER)", "INDEX", "SIZE", "SE/LE", "UPLOADED"]
        self.api_sites = ['rarbg', 'xbit']
        self.class_list = []
        self.class_name = None
        self.args = None
        self.valid_args = [
                        'sorted',
                        'no_merge',
                        'thepiratebay',
                        'skytorrents',
                        'x1337',
                        'idope',
                        'kickasstorrent',
                        'nyaa',
                        'xbit',
                        'rarbg',
                        'limetorrents'
                        ]
    
    def stage_one(self, sites):
        """
        Stage one of cross-site search

        In this stage, the site to be used is selected,
        it's module is imported and results are fetched.

        The `masterlist` consists of the final result.
        And `mapper` to map results with corresponding torrent details (links, magnets)

        Once results are fetched, stage_two() begins.
        """
        self.logger.debug("Stage one begins.")
        index = 0
        masterlist = []
        mapper = []
        for site in sites:
            site_name = self.colorify("red", "[{}]".format(site.upper()))
            print("\n{}\n".format(site_name))
            print("Obtaining proxies...")
            module = importlib.import_module("torrentbro.lib.modules.{}".format(site))
            module_obj = module.cross_site(self.title, self.pages)
            self.logger.debug("Using module {}".format(self.class_name))
            self.class_name = module_obj.class_name
            self.class_list.append(self.class_name)
            self.class_name_color = self.colorify("red", self.class_name)
            module_obj.index = index
            try:
                module_obj.check_proxy()
                self.logger.debug("check_proxy() complete.")
            except AttributeError as e:
                self.logger.debug("check_proxy() not present. Skipping.")
                pass
            if self.class_name in self.api_sites:
                self.logger.debug("Site is one of API sites. Starting search_torrent()")
                module_obj.search_torrent()
            else:
                self.logger.debug("Starting get_html() and parse_html()")
                module_obj.get_html()
                module_obj.parse_html()
            if self.args.no_merge:
                self.logger.debug("Not merging results into one table.")
                index = 0
            else:
                self.logger.debug("Merging results into one table.")
                index = module_obj.index
            self.total_time += module_obj.total_fetch_time
            masterlist.append(module_obj.masterlist_crossite)
            mapper.append(module_obj.mapper)
            if len(module_obj.mapper) == 0:
                print("(no results)")
            else:
                print("({} results)".format(len(module_obj.mapper)))
            time.sleep(0.5)
        if self.args.no_merge:
            self.stage_two_no_merge(masterlist, mapper)
        else:
            self.stage_two(masterlist, mapper)
    
    def stage_two_no_merge(self, mlist, mapper):
        """
        Stage two (No merge)

        Stage tow begins once results are fetched.
        The `mlist` is the masterlist and `mapper` is mapper.

        `No merge` means the results are not merged into one table.

        Instead, all tables are displayed separately.
        The user can select which site (table) to use, and then
        proceed with torrent selection.

        TODO: Add (r = return) to return to site choices.
        Once site is selected, the user is unable to return to site choices.
        Needs fix.
        """
        self.logger.debug("In stage_two_no_merge() method")
        index_no_merge = 0
        temp = 0
        mapper_no_merge = []
        
        # Show output results and map mlist, mapper and self.class_name with self.class_name index.
        self.logger.debug("Displaying output tables")
        for i, j, k in zip(mlist, mapper, self.class_list):
            mapper_no_merge.insert(index_no_merge, (i, j, k))
            self.masterlist = mapper_no_merge[temp][0]
            if self.masterlist == []:
                del mapper_no_merge[index_no_merge]
                pass
            else:
                self.colorify_seeds_leeches()
                self.show_output()
                temp += 1
                index_no_merge += 1
        if self.masterlist == []:
            print("\nNo results found for given input!")
            self.logger.debug("No results found for given input! Exiting!")
            sys.exit(2)
        # Select website, and proceed further with index selection...
        while True:
            try:
                print()
                for i, j in zip(range(len(mapper_no_merge)), mapper_no_merge):
                    print("[{}] {}".format(i+1, j[2].upper()))
                self.logger.debug("Selecting site")
                opt = int(input("\nSelect Site > "))
                self.logger.debug("Option entered: {}".format(opt))
                if opt > 0:
                    self.masterlist = mapper_no_merge[opt-1][0]
                    self.mapper = mapper_no_merge[opt-1][1]
                    self.show_output()
                    site_name = mapper_no_merge[opt-1][2]
                    print("\n[{}]\n".format(site_name.upper()))
                    self.logger.debug("Selected site [{}]: {}".format(opt, site_name))
                    while True:
                        index = self.select_index(len(self.mapper))
                        self.logger.debug("Got index: {}".format(index))
                        if index == 0:
                            continue
                        elif index == 'r':
                            break
                        else:
                            self.select_option(index)
            except (ValueError, UnboundLocalError, Exception) as e:
                self.logger.exception(e)
                print("Bad Input")
                continue

    def stage_two(self, mlist, mapper):
        """
        Stage two (Merge) (default)

        Stage tow begins once results are fetched.
        The `mlist` is the masterlist and `mapper` is mapper.

        `Merge` means the results from multiple sites are merged into one table.
        This is the default method of showing results.

        Use --no-merge to show results individually for all sites.

        By default the results are merged on the basis of order of fetch.
        Eg: If TPB is fetched first followed by KAT, final table will have all results
        of TPB followed by KAT.

        To sort results, use --sort argument. Results are sorted on basis of seeds.
        """
        self.logger.debug("In stage_two() method")
        self.logger.debug("Merging `masterlist` and `mapper`")
        for i, j in zip(mlist, mapper):
            self.masterlist += i
            self.mapper += j
        self.logger.debug("Merge complete.")
        if self.masterlist == []:
            print("\nNo results found for given input!")
            self.logger.debug("No results found for given input! Exiting!")
            sys.exit(2)
        if self.args.sorted:
            try:
                self.masterlist.sort(key=lambda x: int(x[3].split('/')[0]), reverse=True)
                temp_mapper = []
                index = 1
                for i in range(len(self.masterlist)):
                    temp = self.masterlist[i][1]
                    temp_mapper.insert(index, self.mapper[temp-1])
                    self.masterlist[i][1] = index
                    index += 1
                self.mapper = temp_mapper
            except Exception as e:
                print("Something went wrong! See logs for details.")
                self.logger.debug(e)
                sys.exit(2)
        self.colorify_seeds_leeches()
        self.show_output()
        print("\nTotal {} torrents in {:.2f} sec.\n".format(len(self.masterlist), self.total_time))
        self.logger.debug("\nTotal {} torrents in {:.2f} sec.\n".format(len(self.masterlist), self.total_time))
        while True:
            ind = self.select_index(len(self.mapper))
            self.logger.debug("Got index: {}".format(ind))
            if ind == 0:
                continue
            elif ind == 'r':
                break
            else:
                self.select_option(ind)

    def colorify_seeds_leeches(self):
        """
        Colorify seeds/leeches

        By default teh seeds and leeches are integers.
        This function colorifies them and add them to masterlist
        """
        for i in range(len(self.masterlist)):
            seeds = str(self.masterlist[i][3].split('/')[0])
            leeches = str(self.masterlist[i][3].split('/')[1])
            if seeds == '-1':
                seeds = 'NA'
            if leeches == '-1':
                leeches = 'NA'
            leeches = self.colorify("red", leeches)
            seeds = self.colorify("green", seeds)
            final = seeds+'/'+leeches
            self.masterlist[i][3] = final


def main(args):
    """Cross-site execution begins here"""
    print("\n[Cross-Site Search]\n")
    title = args.search
    pages = args.limit
    cs = CrossSite(title, pages)
    try:
        if not cs.file_exists():
            print("\nConfig file not configured. Configure to continue. Read docs for more info.")
            print("Config file either does not exist or is not enabled! Exiting!\n")
            cs.logger.error("Config file not configured! Terminating.")
            sys.exit(2)
        cs.args = args
        verify_input(cs)
        cs.title = cs.title.replace("'", "")
        cs.logger.debug("Input title: {} ; page_limit: {}".format(title, pages))
        r = vars(args)
        arguments = [a for a, b in r.items() if b is True]
        cs.logger.debug("Original arguments: {}".format(arguments))
        arguments.remove('cross_site')
        if 'no_merge' in arguments and 'sorted' in arguments:
            print("Error: `--sorted` not allowed with `--no-merge`. Terminating.")
            sys.exit(2)
        if 'no_merge' in arguments:
            arguments.remove('no_merge')
        if 'sorted' in arguments:
            arguments.remove('sorted')
        for arg in arguments:
            if arg not in cs.valid_args:
                print("`{}` argument is not allowed.".format(arg))
                cs.logger.debug("`--{}` argument is not allowed. Removed it.".format(arg))
                arguments.remove(arg)
        cs.logger.debug("Stripped arguments: {}".format(arguments))
        cs.logger.debug("starting stage_one().")
        cs.stage_one(arguments)
    except KeyboardInterrupt as e:
        cs.logger.exception(e)
        print("\nAborted!")
        sys.exit(2)


def verify_input(obj):
    """To verify if input given is valid or not."""
    if obj.args.search is None:
        obj.logger.debug("Bad input! Input string expected! Got 'None'")
        print("\nInput string expected.\nUse --help for more\n")
        sys.exit(2)

    if obj.args.limit <= 0 or obj.args.limit > 50:
        obj.logger.debug("Invalid page_limit entered: %d" % (obj.page_limit))
        print("Enter valid page input [0<p<=50]")
        sys.exit(2)
